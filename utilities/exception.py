import base64
import xml.sax
from utilities import xml_handler
import simplejson as json


class GeneralError(Exception):
    """
    Exception class that encapsulate unclassified errors
    """
    def __init__(self, msg, *args):
        super(GeneralError, self).__init__(msg, *args)
        self.msg = msg

    def __repr__(self):
        return 'Unknown Error: %s' % self.msg

    def __str__(self):
        return 'Unknown Error: %s' % self.msg


class ClientError(StandardError):
    """
    Exception class that represent HTTP 4xx client error (error accessing AWS)
    """
    def __init__(self, status='unknown', reason='unknown', *args):
        super(ClientError, self).__init__(reason, *args)
        self.reason = reason
        self.status = status

    def __repr__(self):
        return 'HTTP Client Error: %s %s' % (self.status, self.reason)

    def __str__(self):
        return 'HTTP Client Error: %s %s' % (self.status, self.reason)


class S3Exception(GeneralError):
    pass


class HostRequiredError(GeneralError):
    pass


class ServerError(StandardError):
    """
    Exception class that represent HTTP response error related to server
    """

    def __init__(self, status, reason, body=None, *args):
        super(ServerError, self).__init__(status, reason, body, *args)
        self.status = status
        self.reason = reason
        self.body = body or ''
        self.request_id = None
        self.error_code = None
        self._error_message = None
        self.box_usage = None

        # Attempt to parse the error response. If body isn't present,
        # then just ignore the error response.
        if self.body:
            # Check if it looks like a ``dict``.
            if hasattr(self.body, 'items'):
                # It's not a string, so trying to parse it will fail.
                # But since it's data, we can work with that.
                self.request_id = self.body.get('RequestId', None)

                if 'Error' in self.body:
                    # XML-style
                    error = self.body.get('Error', {})
                    self.error_code = error.get('Code', None)
                    self.message = error.get('Message', None)
                else:
                    # JSON-style.
                    self.message = self.body.get('message', None)
            else:
                try:
                    h = xml_handler.XmlHandlerWrapper(self, self)
                    h.parseString(self.body)
                except (TypeError, xml.sax.SAXParseException), pe:
                    #TODO: What if it's JSON? Let's try that.
                    try:
                        parsed = json.loads(self.body)

                        if 'RequestId' in parsed:
                            self.request_id = parsed['RequestId']
                        if 'Error' in parsed:
                            if 'Code' in parsed['Error']:
                                self.error_code = parsed['Error']['Code']
                            if 'Message' in parsed['Error']:
                                self.message = parsed['Error']['Message']

                    except (TypeError, ValueError):
                        self.message = self.body
                        self.body = None

    def __getattr__(self, name):
        if name == 'error_message':
            return self.message
        if name == 'code':
            return self.error_code
        raise AttributeError

    def __setattr__(self, name, value):
        if name == 'error_message':
            self.message = value
        else:
            super(ServerError, self).__setattr__(name, value)

    def __repr__(self):
        return '%s: %s %s\n%s' % (self.__class__.__name__,
                                  self.status, self.reason, self.body)

    def __str__(self):
        return '%s: %s %s\n%s' % (self.__class__.__name__,
                                  self.status, self.reason, self.body)

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name in ('RequestId', 'RequestID'):
            self.request_id = value
        elif name == 'Code':
            self.error_code = value
        elif name == 'Message':
            self.message = value
        elif name == 'BoxUsage':
            self.box_usage = value
        return None

    def _cleanupParsedProperties(self):
        self.request_id = None
        self.error_code = None
        self.message = None
        self.box_usage = None


class ConsoleOutput(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.instance_id = None
        self.timestamp = None
        self.comment = None
        self.output = None

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'instanceId':
            self.instance_id = value
        elif name == 'output':
            self.output = base64.b64decode(value)
        else:
            setattr(self, name, value)


class UnsuccessfulRequestError(ServerError):
    """
    Class used to represent HTTP response other than 2xx
    """
    pass


class JSONResponseError(ServerError):
    """
    This exception expects the fully parsed and decoded JSON response
    body to be passed as the body parameter.

    :ivar status: The HTTP status code.
    :ivar reason: The HTTP reason message.
    :ivar body: The Python dict that represents the decoded JSON
        response body.
    :ivar error_message: The full description of the AWS error encountered.
    :ivar error_code: A short string that identifies the AWS error
        (e.g. ConditionalCheckFailedException)
    """
    def __init__(self, status, reason, body=None, *args):
        self.status = status
        self.reason = reason
        self.body = body
        if self.body:
            self.error_message = self.body.get('message', None)
            self.error_code = self.body.get('__type', None)
            if self.error_code:
                self.error_code = self.error_code.split('#')[-1]


class InvalidUriError(Exception):
    """Exception raised when URI is invalid."""

    def __init__(self, message):
        super(InvalidUriError, self).__init__(message)
        self.message = message

class InvalidAclError(Exception):
    """Exception raised when ACL XML is invalid."""

    def __init__(self, message):
        super(InvalidAclError, self).__init__(message)
        self.message = message

class InvalidCorsError(Exception):
    """Exception raised when CORS XML is invalid."""

    def __init__(self, message):
        super(InvalidCorsError, self).__init__(message)
        self.message = message

class NoAuthHandlerFound(Exception):
    """Is raised when no auth handlers were found ready to authenticate."""
    pass

class InvalidLifecycleConfigError(Exception):
    """Exception raised when GCS lifecycle configuration XML is invalid."""

    def __init__(self, message):
        super(InvalidLifecycleConfigError, self).__init__(message)
        self.message = message


class TooManyRecordsException(Exception):
    """
    Exception raised when a search of Route53 records returns more
    records than requested.
    """

    def __init__(self, message):
        super(TooManyRecordsException, self).__init__(message)
        self.message = message


class PleaseRetryException(Exception):
    """
    Indicates a request should be retried.
    """
    def __init__(self, message, response=None):
        self.message = message
        self.response = response

    def __repr__(self):
        return 'PleaseRetryException("%s", %s)' % (
            self.message,
            self.response
        )
