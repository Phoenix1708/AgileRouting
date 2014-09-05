

class AuthHandler(object):
    """
    Interface for picking authentication handlers dynamically at runtime
    """

    target_aws_services = []

    def __init__(self, config):

        self.access_key = config.get('Default', 'AWS_ACCESS_KEY')
        self.secret_key = config.get('Default', 'AWS_SECRET_KEY')

        pass

    def sign_request(self, http_request):
        """ Sign the http request
        :type http_request: connection.http_communication.HTTPRequest
        """
        pass

    @classmethod
    def is_for(cls, aws_services):
        """Returns true if this handler instance is for the required AWS
        authentication (e.g Route53)
        """
        for service in aws_services:
            if not service in cls.target_aws_services:
                return False

        return True
