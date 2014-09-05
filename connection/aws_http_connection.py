from __future__ import with_statement
import httplib
import random
import socket
import time

from datetime import datetime

from connection.Authentication import auth
from etc.configuration import cfg, log
from connection.http_communication import HTTPRequest, HTTPResponse
from models.xml_classes.xml_class import NoXMLBindingAvailableError
from models.xml_classes.xml_class_selector import get_xml_class
from utilities import utils
from utilities.exception import ClientError, ServerError, \
    PleaseRetryException, UnsuccessfulRequestError

PORTS = {True: 443, False: 80}


class AWSHTTPConnection(object):
    def __init__(self, host, is_secure=True, port=None, debug=0, path='/'):
        """
        :param host: The host to connection to

        :keyword str aws_access_key_id: AWS Access Key ID
        :keyword str aws_secret_access_key: AWS Secret Access Key

        :type is_secure: boolean
        :param is_secure: Whether the connection is over SSL
        """

        self.access_key = cfg.get('Default', 'AWS_ACCESS_KEY')
        self.secret_key = cfg.get('Default', 'AWS_SECRET_KEY')

        # default number of retries value
        self.num_retries = 6

        self.is_secure = is_secure

        if port:
            self.port = port
        else:
            self.port = PORTS[is_secure]

        # catch and retry on certain exceptions from httplib
        self.http_exceptions = (httplib.HTTPException, socket.error,
                                socket.gaierror, httplib.BadStatusLine)

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

        # Set default socket time out as suggested:
        # http://docs.aws.amazon.com/amazonswf/latest/apireference/
        # API_PollForActivityTask.html
        self.http_connection_kwargs = {'timeout': cfg.get_int(
            'HTTPConnection', 'http_socket_timeout', 70)}

        self._connection = (self.host, self.port, self.is_secure)

        self.auth_handler = auth.get_auth_handler(
            host, cfg, self._target_aws_service())

    def __repr__(self):
        return '%s:%s' % (self.__class__.__name__, self.host)

    def _target_aws_service(self):
        return []

    def new_http_connection(self, host, port):

        # excluding the port number in case it is added
        host = host.split(':', 1)[0]

        http_connection_kwargs = self.http_connection_kwargs.copy()

        # Connection factories below expect a port keyword argument
        http_connection_kwargs['port'] = port

        connection = httplib.HTTPSConnection(host, **http_connection_kwargs)

        if self.debug > 1:
            connection.set_debuglevel(self.debug)

        # Set the response class of the http connection to
        # use our customised class.
        connection.response_class = HTTPResponse
        return connection

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

        response = None
        body = None
        e = None   # exception to raise if any "unretriable"

        num_retries = cfg.get_int('HTTPConnection', 'num_retries',
                                  self.num_retries)

        connection = self.new_http_connection(request.host, request.port)
        counter = 0
        while counter <= num_retries:
            # Use binary exponential back-off to avoid traffic congestion
            max_retry_delay = cfg.get('HTTPConnection', 'max_retry_delay', 60)
            wait_time = min(random.random() * (2 ** counter), max_retry_delay)

            try:
                # sign the request with AWS access key
                request.authorize(connection=self)
                # add host to header except requests made to s3
                if 's3' not in self._target_aws_service():
                    self.set_host_header(request)

                request.start_time = datetime.now()

                connection.request(request.method, request.path,
                                   request.body, request.headers)
                response = connection.getresponse()

                location = response.getheader('location')

                if request.method == 'HEAD' and \
                        getattr(response, 'chunked', False):
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
                    msg = 'HTTP response: %s\nRe-attempting in %3.1f ' \
                          'seconds' % response.status, wait_time
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

                    return response

            except PleaseRetryException, e:
                log.debug('encountered a retry exception: %s' % e)
                connection = self.new_http_connection(request.host,
                                                      request.port)
                response = e.response
            except self.http_exceptions, e:
                log.debug('encountered %s exception, reconnecting'
                          % e.__class__.__name__)
                connection = self.new_http_connection(request.host,
                                                      request.port)
            time.sleep(wait_time)
            counter += 1

        if response:
            raise ServerError(response.status, response.reason, body)
        elif e:
            raise
        else:
            raise ClientError(response.status, response.reason)

    def build_base_http_request(self, method, path, auth_path,
                                params=None, headers=None, data='', host=None):

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