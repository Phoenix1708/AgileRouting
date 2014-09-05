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

        #TODO: map to XML binding class
        if self.body:
            print self.body

    def __repr__(self):
        return '%s: %s %s\n%s' % (self.__class__.__name__,
                                  self.status, self.reason, self.body)

    def __str__(self):
        return '%s: %s %s\n%s' % (self.__class__.__name__,
                                  self.status, self.reason, self.body)


class UnsuccessfulRequestError(ServerError):
    """
    Class used to represent HTTP response other than 2xx
    """
    pass


class PleaseRetryException(Exception):
    """
    HTTP requests that should be retried.
    """
    def __init__(self, message, response=None):
        self.message = message
        self.response = response

    def __repr__(self):
        return 'PleaseRetryException("%s", %s)' % (
            self.message,
            self.response
        )
