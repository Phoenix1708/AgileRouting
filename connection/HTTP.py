import httplib
import urllib


class HTTPRequest(object):
    def __init__(self, method, protocol, host, port, path, auth_path,
                 params, headers, body):
        """Represents an HTTP request.

        :type method: string
        :param method: The HTTP method name, 'GET', 'POST', 'PUT' etc.

        :type protocol: string
        :param protocol: The http protocol used, 'http' or 'https'.

        :type host: string
        :param host: Host to which the request is addressed. eg. abc.com

        :type port: int
        :param port: port on which the request is being sent. Zero means unset,
            in which case default port will be chosen.

        :type path: string
        :param path: URL path that is being accessed.

        :type auth_path: string
        :param path: The part of the URL path used when creating the
            authentication string.

        :type params: dict
        :param params: HTTP url query parameters, with key as name of
            the param, and value as value of param.

        :type headers: dict
        :param headers: HTTP headers, with key as name of the header and value
            as value of header.

        :type body: string
        :param body: Body of the HTTP request. If not present, will be None or
            empty string ('').
        """
        self.method = method
        self.protocol = protocol
        self.host = host
        self.port = port
        self.path = path
        if auth_path is None:
            auth_path = path
        self.auth_path = auth_path
        self.params = params

        # chunked Transfer-Encoding should act only on PUT request.
        # if headers and 'Transfer-Encoding' in headers and \
        # headers['Transfer-Encoding'] == 'chunked' and \
        # self.method != 'PUT':
        #     self.headers = headers.copy()
        #     del self.headers['Transfer-Encoding']
        # else:
        #     self.headers = headers

        self.headers = headers
        self.body = body

    def __str__(self):
        return (('method:(%s) protocol:(%s) host(%s) port(%s) path(%s) '
                 'params(%s) headers(%s) body(%s)') % (self.method,
                                                       self.protocol, self.host,
                                                       self.port, self.path,
                                                       self.params,
                                                       self.headers, self.body))

    def authorize(self, connection, **kwargs):
        # quoting the reserved characters in headers
        for key in self.headers:
            val = self.headers[key]
            if isinstance(val, unicode):
                safe = '!"#$%&\'()*+,/:;<=>?@[\\]^`{|}~'
                self.headers[key] = urllib.quote(val.encode('utf-8'), safe)

        connection.auth_handler.add_auth_info(self, **kwargs)

        # I'm not sure if this is still needed, now that add_auth is
        # setting the content-length for POST requests.
        if 'Content-Length' not in self.headers:
            if 'Transfer-Encoding' not in self.headers or \
                self.headers['Transfer-Encoding'] != 'chunked':
                self.headers['Content-Length'] = str(len(self.body) if
                                                     self.body else 0)


class HTTPResponse(httplib.HTTPResponse):
    def __init__(self, *args, **kwargs):
        httplib.HTTPResponse.__init__(self, *args, **kwargs)
        self._cached_response = ''

    def read(self, amt=None):
        """Read the response.

        This method does not have the same behavior as
        httplib.HTTPResponse.read.  Instead, if this method is called with
        no ``amt`` arg, then the response body will be cached.  Subsequent
        calls to ``read()`` with no args **will return the cached response**.

        """
        if amt is None:
            # The reason for doing this is that many places in call
            # response.read() and except to get the response body that they
            # can then process.  To make sure this always works as they expect
            # we're caching the response so that multiple calls to read()
            # will return the full body.  Note that this behavior only
            # happens if the amt arg is not specified.
            if not self._cached_response:
                self._cached_response = httplib.HTTPResponse.read(self)
            return self._cached_response
        else:
            return httplib.HTTPResponse.read(self, amt)