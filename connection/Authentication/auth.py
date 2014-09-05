import base64
import copy
from email.utils import formatdate
import hmac

from connection.Authentication.auth_handler import AuthHandler
from etc.configuration import log
from utilities.exception import GeneralError
from utilities.request_headers import AUTH_HEADER_KEY, HeaderInfoMap
from utilities.utils import s3_canonical_string


try:
    from hashlib import sha1 as sha
    from hashlib import sha256 as sha256
except ImportError:
    import sha

    sha256 = None


class HmacKeys(object):
    """Key based Auth handler helper."""

    def __init__(self, host, config):
        self.access_key = config.get('Default', 'AWS_ACCESS_KEY')
        self.secret_key = config.get('Default', 'AWS_SECRET_KEY')

        if self.access_key is None or self.secret_key is None:
            raise GeneralError('access key and secret key not available')
        self.host = host
        self._hmac = hmac.new(self.secret_key, digestmod=sha)
        if sha256:
            self._hmac_256 = hmac.new(self.secret_key, digestmod=sha256)
        else:
            self._hmac_256 = None

    def algorithm(self):
        if self._hmac_256:
            return 'HmacSHA256'
        else:
            return 'HmacSHA1'

    def _get_hmac_object(self):
        if self._hmac_256:
            digestmod = sha256
        else:
            digestmod = sha
        return hmac.new(self.secret_key,
                        digestmod=digestmod)

    def sign_string(self, string_to_sign):
        new_hmac = self._get_hmac_object()
        new_hmac.update(string_to_sign)
        return base64.encodestring(new_hmac.digest()).strip()

    def __getstate__(self):
        pickled_dict = copy.copy(self.__dict__)
        del pickled_dict['_hmac']
        del pickled_dict['_hmac_256']
        return pickled_dict


class S3HmacAuthHandler(AuthHandler, HmacKeys):
    """ HMAC request signing of S3."""

    target_aws_services = ['s3']

    def __init__(self, host, config):
        AuthHandler.__init__(self, config)
        HmacKeys.__init__(self, host, config)
        self._hmac_256 = None

    def sign_request(self, http_request, **kwargs):
        headers = http_request.headers
        method = http_request.method
        auth_path = http_request.auth_path
        if 'Date' not in headers:
            headers['Date'] = formatdate(usegmt=True)

        string_to_sign = s3_canonical_string(method, auth_path, headers)

        b64_hmac = self.sign_string(string_to_sign)
        auth_hdr = HeaderInfoMap[AUTH_HEADER_KEY]
        auth = ("%s %s:%s" % (auth_hdr, self.access_key, b64_hmac))
        log.debug('Signature:\n%s' % auth)
        headers['Authorization'] = auth


class R53HmacAuthHandler(AuthHandler, HmacKeys):
    """ HMAC request signing of Route53."""

    target_aws_services = ['route53']

    def __init__(self, host, config):
        AuthHandler.__init__(self, config)
        HmacKeys.__init__(self, host, config)

    def sign_request(self, http_request, **kwargs):
        headers = http_request.headers
        # set Date in header
        if 'Date' not in headers:
            headers['Date'] = formatdate(usegmt=True)

        b64_hmac = self.sign_string(headers['Date'])
        s = "AWS3-HTTPS AWSAccessKeyId=%s," % self.access_key
        s += "Algorithm=%s,Signature=%s" % (self.algorithm(), b64_hmac)
        headers['X-Amzn-Authorization'] = s


def get_auth_handler(host, cfg, aws_services=None):
    """Finds correct AuthHandler to authenticate corresponding AWS service.

    :param host:    The name of the host

    :param cfg:     app configuration

    :return:        An implementation of AuthHandler.

    Raises: exception.NoAuthHandlerFound
    """

    if not aws_services:
        aws_services = []

    auth_handlers = []
    for handler in AuthHandler.__subclasses__():
        if handler.is_for(aws_services):
            auth_handlers.append(handler(host, cfg))

    return auth_handlers[0]
