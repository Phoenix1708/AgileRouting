import httplib
import urllib


class HTTPRequest(object):
    def __init__(self, method, protocol, host, port, path, auth_path,
                 params, headers, body):
        """Represents an HTTP request.

        :param method: The HTTP method.

        :param protocol: 'http' or 'https'.

        :param host: The address of the host targeted by this request

        :param port: port to use to sent the request on

        :param path: URL of the resources that the request it trying access.

        :param path: Resource path from the URL that used to create
                     authentication string.

        :param params: HTTP url query parameters

        :param headers: HTTP request headers

        :param body: Body of the HTTP request.
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

        self.headers = headers
        self.body = body

    def __str__(self):
        return (('method:(%s) protocol:(%s) host(%s) port(%s) path(%s) '
                 'params(%s) headers(%s) body(%s)')
                % (self.method, self.protocol, self.host, self.port, self.path,
                   self.params, self.headers, self.body))

    def authorize(self, connection, **kwargs):
        # quoting the reserved characters in headers
        for key in self.headers:
            val = self.headers[key]
            if isinstance(val, unicode):
                safe = '!"#$%&\'()*+,/:;<=>?@[\\]^`{|}~'
                self.headers[key] = urllib.quote(val.encode('utf-8'), safe)

        connection.auth_handler.sign_request(self, **kwargs)

        # setting the content-length for POST requests.
        if 'Content-Length' not in self.headers:
            if 'Transfer-Encoding' not in self.headers or \
                            self.headers['Transfer-Encoding'] != 'chunked':
                self.headers['Content-Length'] = \
                    str(len(self.body) if self.body else 0)


class HTTPResponse(httplib.HTTPResponse):
    def __init__(self, *args, **kwargs):
        httplib.HTTPResponse.__init__(self, *args, **kwargs)
        self._cached_response = ''

    def read(self, buffer_size=None):
        """ Wrapper over httplib.HTTPResponse.read.

        If no buffer size specified it will return cached response from the
        first reading of this httplib.HTTPResponse

        if buffer size specified, response will be read buffer_size by
        buffer_size

        """
        if buffer_size is None:

            if not self._cached_response:
                self._cached_response = httplib.HTTPResponse.read(self)
            return self._cached_response
        else:
            return httplib.HTTPResponse.read(self, buffer_size)