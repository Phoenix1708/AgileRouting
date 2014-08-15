

class AuthHandler(object):
    """
    Interface which all Auth handlers need to implement.
    """

    capability = []

    def __init__(self, config):
        """Constructs the handlers.

        :type config: etc.configuration.Config
        :param config: configuration.
        """

        self.access_key = config.get('Default', 'AWS_ACCESS_KEY')
        self.secret_key = config.get('Default', 'AWS_SECRET_KEY')

        pass

    def add_auth_info(self, http_request):
        """Invoked to add authentication details to request.

        :type http_request: connection.HTTP.HTTPRequest
        :param http_request: HTTP request that needs to be authenticated.
        """
        pass

    @classmethod
    def is_capable(cls, requested_capability):
        """Returns true if this handler instance is for
        the required AWS authentication (e.g Route53 Authentication)
        """
        for c in requested_capability:
            if not c in cls.capability:
                return False
        return True
