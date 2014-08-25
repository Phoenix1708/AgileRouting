from __future__ import with_statement
from datetime import datetime
import errno
import httplib
import random
import socket
import sys
import time
import urlparse

from connection.Authentication import auth
from etc.configuration import cfg, log
from connection import https_connection
from connection.ConnectionPool import ConnectionPool
from connection.HTTP import HTTPRequest, HTTPResponse
from models.xml_classes.xml_class import NoXMLBindingAvailableError
from models.xml_classes.xml_class_selector import get_xml_class
from utilities import utils
from utilities.exception import ClientError, ServerError, \
    PleaseRetryException, UnsuccessfulRequestError


HAVE_HTTPS_CONNECTION = True

PORTS_BY_SECURITY = {True: 443, False: 80}


class AWSConnection(object):
    def __init__(self, host, is_secure=True, port=None, debug=0,
                 https_connection_factory=None, path='/'):
        """
        :type host: str
        :param host: The host to make the connection to

        :keyword str aws_access_key_id: AWS Access Key ID
        :keyword str aws_secret_access_key: AWS Secret Access Key

        :keyword str security_token: The security token associated with
            temporary credentials issued by STS.  Optional unless using
            temporary credentials.  If none is specified, the environment
            variable ``AWS_SECURITY_TOKEN`` is used if defined.

        :type is_secure: boolean
        :param is_secure: Whether the connection is over SSL

        :type https_connection_factory: list or tuple
        :param https_connection_factory: A pair of an HTTP connection
            factory and the exceptions to catch.  The factory should have
            a similar interface to L{httplib.HTTPSConnection}.
        """

        self.access_key = cfg.get('Default', 'AWS_ACCESS_KEY')
        self.secret_key = cfg.get('Default', 'AWS_SECRET_KEY')

        # default number of retries value
        self.num_retries = 6

        self.is_secure = is_secure

        if port:
            self.port = port
        else:
            self.port = PORTS_BY_SECURITY[is_secure]

        # define exceptions from httplib that we want to catch and retry
        self.http_exceptions = (httplib.HTTPException, socket.error,
                                socket.gaierror, httplib.BadStatusLine)
        # define subclasses of the above that are not retryable.
        self.http_unretryable_exceptions = []
        if HAVE_HTTPS_CONNECTION:
            self.http_unretryable_exceptions.append(
                https_connection.InvalidCertificateException)

        # define values in socket exceptions we don't want to catch
        self.socket_exception_values = (errno.EINTR,)
        if https_connection_factory is not None:
            self.https_connection_factory = https_connection_factory[0]
            self.http_exceptions += https_connection_factory[1]
        else:
            self.https_connection_factory = None
        if is_secure:
            self.protocol = 'https'
        else:
            self.protocol = 'http'
        self.host = host
        self.path = path
        # if the value passed in for debug
        if not isinstance(debug, (int, long)):
            debug = 0
        self.debug = cfg.get_int('Default', 'debug', debug)
        self.host_header = None

        #TODO: default time out
        # Timeout used to tell httplib how long to wait for socket timeouts.
        # Default is to leave timeout unchanged, which will in turn result in
        # the socket's default global timeout being used. To specify a
        # timeout, set http_socket_timeout in config. Regardless,
        # timeouts will only be applied if Python is 2.6 or greater.
        self.http_connection_kwargs = {}
        if (sys.version_info[0], sys.version_info[1]) >= (2, 6):
            # If timeout isn't defined in config file, use 70 second
            # default as recommended by
            # http://docs.aws.amazon.com/amazonswf/latest/
            # apireference/API_PollForActivityTask.html
            self.http_connection_kwargs['timeout'] = cfg.get_int(
                'HTTPConnection', 'http_socket_timeout', 70)

        self._pool = ConnectionPool()
        self._connection = (self.host, self.port, self.is_secure)
        # self._last_rs = None
        self.auth_handler = auth.get_auth_handler(
            host, cfg, self._required_auth_capability())

        # if getattr(self, 'AuthServiceName', None) is not None:
        #     self.auth_service_name = self.AuthServiceName

            # self.request_hook = None

    def __repr__(self):
        return '%s:%s' % (self.__class__.__name__, self.host)

    def _required_auth_capability(self):
        return []

    def _get_auth_service_name(self):
        return getattr(self.auth_handler, 'service_name')

    # For Sigv4, the auth_service_name/auth_region_name properties allow
    # the service_name/region_name to be explicitly set instead of being
    # derived from the endpoint url.
    # def _set_auth_service_name(self, value):
    #     self.auth_handler.service_name = value
    #
    # auth_service_name = property(_get_auth_service_name, _set_auth_service_name)
    #
    # def _get_auth_region_name(self):
    #     return getattr(self.auth_handler, 'region_name')
    #
    # def _set_auth_region_name(self, value):
    #     self.auth_handler.region_name = value
    #
    # auth_region_name = property(_get_auth_region_name, _set_auth_region_name)
    #
    # def connection(self):
    #     return self.get_http_connection(*self._connection)
    #
    # connection = property(connection)
    #
    # def profile_name(self):
    #     return self.profile_name
    #
    # profile_name = property(profile_name)

    def get_path(self, path='/'):
        # The default behavior is to suppress consecutive slashes for reasons

        # if not self.suppress_consec_slashes:
        # return self.path + re.sub('^(/*)/', "\\1", path)
        pos = path.find('?')
        if pos >= 0:
            params = path[pos:]
            path = path[:pos]
        else:
            params = None
        if path[-1] == '/':
            need_trailing = True
        else:
            need_trailing = False
        path_elements = self.path.split('/')
        path_elements.extend(path.split('/'))
        path_elements = [p for p in path_elements if p]
        path = '/' + '/'.join(path_elements)
        if path[-1] != '/' and need_trailing:
            path += '/'
        if params:
            path += params
        return path

    def server_name(self, port=None):
        if not port:
            port = self.port
        if port == 80:
            signature_host = self.host
        else:
            # This unfortunate little hack can be attributed to
            # a difference in the 2.6 version of httplib.  In old
            # versions, it would append ":443" to the hostname sent
            # in the Host header and so we needed to make sure we
            # did the same when calculating the V2 signature.  In 2.6
            # (and higher!)
            # it no longer does that.  Hence, this kludge.
            if (sys.version[:3] in ('2.6', '2.7')) and port == 443:
                signature_host = self.host
            else:
                signature_host = '%s:%d' % (self.host, port)
        return signature_host

    def get_http_connection(self, host, port, is_secure):
        conn = self._pool.get_http_connection(host, port, is_secure)
        if conn is not None:
            return conn
        else:
            return self.new_http_connection(host, port, is_secure)

    def new_http_connection(self, host, port, is_secure):
        # if host is None:
        #     host = self.server_name()

        # excluding the port number in case it is added
        host = host.split(':', 1)[0]

        http_connection_kwargs = self.http_connection_kwargs.copy()

        # Connection factories below expect a port keyword argument
        http_connection_kwargs['port'] = port

        if is_secure:
            log.debug(
                'establishing HTTPS connection: host=%s, kwargs=%s',
                host, http_connection_kwargs)
            # if self.use_proxy and not self.skip_proxy(host):
            #     connection = self.proxy_ssl(host, is_secure and 443 or 80)
            if self.https_connection_factory:
                connection = self.https_connection_factory(host)
            # elif self.https_validate_certificates and HAVE_HTTPS_CONNECTION:
            #     connection = https_connection.CertValidatingHTTPSConnection(
            #         host, ca_certs=self.ca_certificates_file,
            #         **http_connection_kwargs)
            else:
                connection = httplib.HTTPSConnection(host,
                                                     **http_connection_kwargs)
        else:
            log.debug('establishing HTTP connection: kwargs=%s' %
                      http_connection_kwargs)
            if self.https_connection_factory:
                # even though the factory says https, this is too handy
                # to not be able to allow overriding for http also.
                connection = self.https_connection_factory(
                    host, **http_connection_kwargs)
            else:
                connection = httplib.HTTPConnection(host,
                                                    **http_connection_kwargs)
        if self.debug > 1:
            connection.set_debuglevel(self.debug)
        # self.connection must be maintained for backwards-compatibility
        # however, it must be dynamically pulled from the connection pool
        # set a private variable which will enable that
        if host.split(':')[0] == self.host and is_secure == self.is_secure:
            self._connection = (host, port, is_secure)
        # Set the response class of the http connection to use our custom
        # class.
        connection.response_class = HTTPResponse
        return connection

    def put_http_connection(self, host, port, is_secure, connection):
        self._pool.put_http_connection(host, port, is_secure, connection)

    def set_host_header(self, request):
        try:
            request.headers['Host'] = \
                self.auth_handler.host_header(self.host, request)
        except AttributeError:
            request.headers['Host'] = self.host.split(':', 1)[0]

    def _make_request(self, request, retry_handler=None):
        """
        executing the HTTP request and retry request in case of
        temporary connection failure
        """

        log.debug('Executing requests...')
        log.debug('Method: %s' % request.method)
        log.debug('Path: %s' % request.path)
        log.debug('Data: %s' % request.body)
        log.debug('Headers: %s' % request.headers)
        log.debug('Host: %s' % request.host)
        log.debug('Port: %s' % request.port)
        log.debug('Params: %s' % request.params)

        response = None
        body = None
        e = None

        num_retries = cfg.get_int('HTTPConnection', 'num_retries',
                                  self.num_retries)
        #TODO: Connection pool
        connection = self.get_http_connection(request.host, request.port,
                                              self.is_secure)
        counter = 0
        while counter <= num_retries:
            # Use binary exponential backoff to avoid traffic congestion
            max_retry_delay = cfg.get('HTTPConnection', 'max_retry_delay', 60)
            wait_time = min(random.random() * (2 ** counter), max_retry_delay)

            try:
                # sign the request with AWS access key
                request.authorize(connection=self)
                # TODO: S3 authentication
                # Only force header for non-s3 connections, because s3 uses
                # an older signing method + bucket resource URLs that include
                # the port info. All others should be now be up to date and
                # not include the port.
                if 's3' not in self._required_auth_capability():
                    if not getattr(self, 'anon', False):
                        self.set_host_header(request)

                request.start_time = datetime.now()

                connection.request(request.method, request.path,
                                   request.body, request.headers)
                response = connection.getresponse()

                location = response.getheader('location')

                # -- gross hack --
                # httplib gets confused with chunked responses to HEAD requests
                # so I have to fake it out
                if request.method == 'HEAD' and getattr(response,
                                                        'chunked', False):
                    response.chunked = 0

                # checking response code - check 400 first
                if callable(retry_handler):
                    status = retry_handler(response, counter)
                    if status:
                        msg, counter = status
                        if msg:
                            log.debug(msg)
                        time.sleep(wait_time)
                        continue

                if response.status in [500, 502, 503, 504]:
                    msg = 'Received %d HTTP response.  ' % response.status
                    msg += 'Retrying in %3.1f seconds' % wait_time
                    log.debug(msg)
                    # response has to be consumed
                    body = response.read()

                elif response.status < 300 or response.status >= 400 or \
                        not location:
                    # close the connection if it is set
                    # to be closed by the other end
                    conn_header_value = response.getheader('connection')
                    if conn_header_value == 'close':
                        connection.close()
                    else:
                        # put connection into connection pool
                        #TODO: connection pool
                        self.put_http_connection(request.host, request.port,
                                                 self.is_secure, connection)
                    # if self.request_hook is not None:
                    #   self.request_hook.handle_request_data(request, response)
                    return response
                # TODO: not necessary
                else:
                    scheme, request.host, request.path, \
                    params, query, fragment = urlparse.urlparse(location)
                    if query:
                        request.path += '?' + query
                    # urlparse can return both host and port in netloc, so if
                    # that's the case we need to split them up properly
                    if ':' in request.host:
                        request.host, request.port = request.host.split(':', 1)
                    msg = 'Redirecting: %s' % scheme + '://'
                    msg += request.host + request.path
                    log.debug(msg)
                    connection = self.get_http_connection(request.host,
                                                          request.port,
                                                          scheme == 'https')
                    response = None
                    continue
            except PleaseRetryException, e:
                log.debug('encountered a retry exception: %s' % e)
                connection = self.new_http_connection(request.host,
                                                      request.port,
                                                      self.is_secure)
                response = e.response
            except self.http_exceptions, e:
                for unretryable in self.http_unretryable_exceptions:
                    if isinstance(e, unretryable):
                        log.debug(
                            'encountered unretryable %s exception, re-raising' %
                            e.__class__.__name__)
                        raise
                log.debug('encountered %s exception, reconnecting' % \
                          e.__class__.__name__)
                connection = self.new_http_connection(request.host,
                                                      request.port,
                                                      self.is_secure)
            time.sleep(wait_time)
            counter += 1
        # If we made it here, it's because we have exhausted our retries
        # and stil haven't succeeded.  So, if we have a response object,
        # use it to raise an exception.
        # Otherwise, raise the exception that must have already happened.
        # if self.request_hook is not None:
        #   self.request_hook.handle_request_data(request, response, error=True)
        if response:
            raise ServerError(response.status, response.reason, body)
        elif e:
            raise
        else:
            raise ClientError(response.status, response.reason)

    def build_base_http_request(self, method, path, auth_path,
                                params=None, headers=None, data='', host=None):

        # path = self.get_path(path)
        # if auth_path is not None:
        #     auth_path = self.get_path(auth_path)

        if params is None:
            params = {}
        else:
            params = params.copy()
        if headers is None:
            headers = {}
        else:
            headers = headers.copy()

        # in case host header not set
        if (self.host_header and
                not utils.find_matching_headers('host', headers)):
            headers['host'] = self.host_header

        host = host or self.host
        return HTTPRequest(method, self.protocol, host, self.port,
                           path, auth_path, params, headers, data)

    def send_request(self, method, path, response_class=None, headers=None,
                     data='', host=None, auth_path=None, params=None,
                     retry_handler=None):
        """ send request to AWS with multiple-retry

        :param method:          HTTP request method
        :param path:            HTTP request url
        :param response_class:  The name of class used to bind response xml
        :param headers:         Request headers
        :param data:            Request body
        :param host:
        :param auth_path:
        :param params:
        :param retry_handler:
        :return:                The corresponding XML binding object or pure
                                response XML
        """

        if params is None:
            params = {}

        http_request = self.build_base_http_request(method, path, auth_path,
                                                    params, headers, data, host)
        response = self._make_request(http_request, retry_handler=retry_handler)

        if not response_class:
            return response

        body = response.read()
        log.debug(body)

        if response.status >= 300:
            raise UnsuccessfulRequestError(response.status,
                                           response.reason, body)

        # de-serialise the xml response with corresponding xml class
        xml_class = get_xml_class(response_class)

        if not xml_class:
            raise NoXMLBindingAvailableError('No xml binding class found for '
                                             '%s' % response_class)

        response_object = xml_class.fromXml(body)
        return response_object

    def close(self):
        """(Optional) Close any open HTTP connections.  This is non-destructive,
        and making a new request will open a connection again."""

        log.debug('closing all HTTP connections')
        self._connection = None  # compat field