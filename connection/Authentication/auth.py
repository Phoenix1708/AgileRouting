import base64
import copy
import datetime
from email.utils import formatdate
import hmac
import os
import urllib
import posixpath

from connection.Authentication.auth_handler import AuthHandler
from connection.Authentication import auth_handler
from etc.configuration import log, cfg
from utilities import utils
from utilities.exception import GeneralError
from utilities.request_headers import AUTH_HEADER_KEY, HeaderInfoMap
from utilities.utils import canonical_string


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
        self.update_hmac()

    def update_hmac(self):
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

    def _get_hmac(self):
        if self._hmac_256:
            digestmod = sha256
        else:
            digestmod = sha
        return hmac.new(self.secret_key,
                        digestmod=digestmod)

    def sign_string(self, string_to_sign):
        new_hmac = self._get_hmac()
        new_hmac.update(string_to_sign)
        return base64.encodestring(new_hmac.digest()).strip()

    def __getstate__(self):
        pickled_dict = copy.copy(self.__dict__)
        del pickled_dict['_hmac']
        del pickled_dict['_hmac_256']
        return pickled_dict


class S3HmacAuthHandler(AuthHandler, HmacKeys):
    """ HMAC request signing of S3."""

    capability = ['s3']

    def __init__(self, host, config):
        AuthHandler.__init__(self, config)
        HmacKeys.__init__(self, host, config)
        self._hmac_256 = None

    # def update_provider(self, provider):
    # super(HmacAuthV1Handler, self).update_provider(provider)
    #     self._hmac_256 = None

    def add_auth_info(self, http_request, **kwargs):
        headers = http_request.headers
        method = http_request.method
        auth_path = http_request.auth_path
        if 'Date' not in headers:
            headers['Date'] = formatdate(usegmt=True)

        # if self._provider.security_token:
        #     key = self._provider.security_token_header
        #     headers[key] = self._provider.security_token

        string_to_sign = canonical_string(method, auth_path, headers, None)

        b64_hmac = self.sign_string(string_to_sign)
        auth_hdr = HeaderInfoMap[AUTH_HEADER_KEY]
        auth = ("%s %s:%s" % (auth_hdr, self.access_key, b64_hmac))
        log.debug('Signature:\n%s' % auth)
        headers['Authorization'] = auth


class R53HmacAuthHandler(AuthHandler, HmacKeys):
    """ HMAC request signing of Route53."""

    capability = ['route53']

    def __init__(self, host, config):
        AuthHandler.__init__(self, config)
        HmacKeys.__init__(self, host, config)

    def add_auth_info(self, http_request, **kwargs):
        headers = http_request.headers
        # set Date in header
        if 'Date' not in headers:
            headers['Date'] = formatdate(usegmt=True)

        # if self._provider.security_token:
        # key = self._provider.security_token_header
        #     headers[key] = self._provider.security_token

        b64_hmac = self.sign_string(headers['Date'])
        s = "AWS3-HTTPS AWSAccessKeyId=%s," % self.access_key
        s += "Algorithm=%s,Signature=%s" % (self.algorithm(), b64_hmac)
        headers['X-Amzn-Authorization'] = s


def _sign(key, msg, hex=False):
    if hex:
        sig = hmac.new(key, msg.encode('utf-8'), sha256).hexdigest()
    else:
        sig = hmac.new(key, msg.encode('utf-8'), sha256).digest()
    return sig


# class HmacAuthV4Handler(AuthHandler, HmacKeys):
#     """
#     Implements the new Version 4 HMAC authorization.
#     """
#
#     capability = ['hmac-v4']
#
#     def __init__(self, host, config,
#                  service_name=None, region_name=None):
#         AuthHandler.__init__(self, config)
#         HmacKeys.__init__(self, host, config)
#         # You can set the service_name and region_name to override the
#         # values which would otherwise come from the endpoint, e.g.
#         # <service>.<region>.amazonaws.com.
#         self.service_name = service_name
#         self.region_name = region_name
#
#     def headers_to_sign(self, http_request):
#         """
#         Select the headers from the request that need to be included
#         in the StringToSign.
#         """
#         host_header_value = self.host_header(self.host, http_request)
#         headers_to_sign = {}
#         headers_to_sign = {'Host': host_header_value}
#         for name, value in http_request.headers.items():
#             lname = name.lower()
#             if lname.startswith('x-amz'):
#                 headers_to_sign[name] = value
#         return headers_to_sign
#
#     def host_header(self, host, http_request):
#         port = http_request.port
#         secure = http_request.protocol == 'https'
#         if (port == 80 and not secure) or (port == 443 and secure):
#             return host
#         return '%s:%s' % (host, port)
#
#     def query_string(self, http_request):
#         parameter_names = sorted(http_request.params.keys())
#         pairs = []
#         for pname in parameter_names:
#             pval = utils.get_utf8_value(http_request.params[pname])
#             pairs.append(urllib.quote(pname, safe='') + '=' +
#                          urllib.quote(pval, safe='-_~'))
#         return '&'.join(pairs)
#
#     def canonical_query_string(self, http_request):
#         # POST requests pass parameters in through the
#         # http_request.body field.
#         if http_request.method == 'POST':
#             return ""
#         l = []
#         for param in sorted(http_request.params):
#             value = utils.get_utf8_value(http_request.params[param])
#             l.append('%s=%s' % (urllib.quote(param, safe='-_.~'),
#                                 urllib.quote(value, safe='-_.~')))
#         return '&'.join(l)
#
#     def canonical_headers(self, headers_to_sign):
#         """
#         Return the headers that need to be included in the StringToSign
#         in their canonical form by converting all header keys to lower
#         case, sorting them in alphabetical order and then joining
#         them into a string, separated by newlines.
#         """
#         canonical = []
#
#         for header in headers_to_sign:
#             c_name = header.lower().strip()
#             raw_value = headers_to_sign[header]
#             if '"' in raw_value:
#                 c_value = raw_value.strip()
#             else:
#                 c_value = ' '.join(raw_value.strip().split())
#             canonical.append('%s:%s' % (c_name, c_value))
#         return '\n'.join(sorted(canonical))
#
#     def signed_headers(self, headers_to_sign):
#         l = ['%s' % n.lower().strip() for n in headers_to_sign]
#         l = sorted(l)
#         return ';'.join(l)
#
#     def canonical_uri(self, http_request):
#         path = http_request.auth_path
#         # Normalize the path
#         # in windows normpath('/') will be '\\' so we chane it back to '/'
#         normalized = posixpath.normpath(path).replace('\\', '/')
#         # Then urlencode whatever's left.
#         encoded = urllib.quote(normalized)
#         if len(path) > 1 and path.endswith('/'):
#             encoded += '/'
#         return encoded
#
#     def payload(self, http_request):
#         body = http_request.body
#         if hasattr(body, 'seek') and hasattr(body, 'read'):
#             return utils.compute_hash(body, hash_algorithm=sha256)[0]
#         return sha256(http_request.body).hexdigest()
#
#     def canonical_request(self, http_request):
#         cr = [http_request.method.upper(), self.canonical_uri(http_request),
#               self.canonical_query_string(http_request)]
#         headers_to_sign = self.headers_to_sign(http_request)
#         cr.append(self.canonical_headers(headers_to_sign) + '\n')
#         cr.append(self.signed_headers(headers_to_sign))
#         cr.append(self.payload(http_request))
#         return '\n'.join(cr)
#
#     def scope(self, http_request):
#         scope = [self.access_key, http_request.timestamp,
#                  http_request.region_name, http_request.service_name,
#                  'aws4_request']
#         return '/'.join(scope)
#
#     def split_host_parts(self, host):
#         return host.split('.')
#
#     def determine_region_name(self, host):
#         parts = self.split_host_parts(host)
#         if self.region_name is not None:
#             region_name = self.region_name
#         elif len(parts) > 1:
#             if parts[1] == 'us-gov':
#                 region_name = 'us-gov-west-1'
#             else:
#                 if len(parts) == 3:
#                     region_name = 'us-east-1'
#                 else:
#                     region_name = parts[1]
#         else:
#             region_name = parts[0]
#
#         return region_name
#
#     def determine_service_name(self, host):
#         parts = self.split_host_parts(host)
#         if self.service_name is not None:
#             service_name = self.service_name
#         else:
#             service_name = parts[0]
#         return service_name
#
#     def credential_scope(self, http_request):
#         scope = []
#         http_request.timestamp = http_request.headers['X-Amz-Date'][0:8]
#         scope.append(http_request.timestamp)
#         # The service_name and region_name either come from:
#         # * The service_name/region_name attrs or (if these values are None)
#         # * parsed from the endpoint <service>.<region>.amazonaws.com.
#         region_name = self.determine_region_name(http_request.host)
#         service_name = self.determine_service_name(http_request.host)
#         http_request.service_name = service_name
#         http_request.region_name = region_name
#
#         scope.append(http_request.region_name)
#         scope.append(http_request.service_name)
#         scope.append('aws4_request')
#         return '/'.join(scope)
#
#     def string_to_sign(self, http_request, canonical_request):
#         """
#         Return the canonical StringToSign as well as a dict
#         containing the original version of all headers that
#         were included in the StringToSign.
#         """
#         sts = ['AWS4-HMAC-SHA256']
#         sts.append(http_request.headers['X-Amz-Date'])
#         sts.append(self.credential_scope(http_request))
#         sts.append(sha256(canonical_request).hexdigest())
#         return '\n'.join(sts)
#
#     def signature(self, http_request, string_to_sign):
#         key = self.secret_key
#         k_date = _sign(('AWS4' + key).encode('utf-8'),
#                             http_request.timestamp)
#         k_region = _sign(k_date, http_request.region_name)
#         k_service = _sign(k_region, http_request.service_name)
#         k_signing = _sign(k_service, 'aws4_request')
#         return _sign(k_signing, string_to_sign, hex=True)
#
#     def add_auth(self, req, **kwargs):
#         """
#         Add AWS4 authentication to a request.
#
#         :type req: :class`connection.HTTP.HTTPRequest`
#         :param req: The HTTPRequest object.
#         """
#         # This could be a retry.  Make sure the previous
#         # authorization header is removed first.
#         if 'X-Amzn-Authorization' in req.headers:
#             del req.headers['X-Amzn-Authorization']
#         now = datetime.datetime.utcnow()
#         req.headers['X-Amz-Date'] = now.strftime('%Y%m%dT%H%M%SZ')
#
#         # if self._provider.security_token:
#         # req.headers['X-Amz-Security-Token'] = self._provider.security_token
#
#         qs = self.query_string(req)
#         if qs and req.method == 'POST':
#             # Stash request parameters into post body
#             # before we generate the signature.
#             req.body = qs
#             req.headers[
#                 'Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
#             req.headers['Content-Length'] = str(len(req.body))
#         else:
#             # Safe to modify req.path here since
#             # the signature will use req.auth_path.
#             req.path = req.path.split('?')[0]
#
#             if qs:
#                 # Don't insert the '?' unless there's actually a query string
#                 req.path = req.path + '?' + qs
#
#         canonical_request = self.canonical_request(req)
#         log.debug('CanonicalRequest:\n%s' % canonical_request)
#         string_to_sign = self.string_to_sign(req, canonical_request)
#         log.debug('StringToSign:\n%s' % string_to_sign)
#         signature = self.signature(req, string_to_sign)
#         log.debug('Signature:\n%s' % signature)
#
#         headers_to_sign = self.headers_to_sign(req)
#         l = ['AWS4-HMAC-SHA256 Credential=%s' % self.scope(req),
#              'SignedHeaders=%s' % self.signed_headers(headers_to_sign),
#              'Signature=%s' % signature]
#         req.headers['Authorization'] = ','.join(l)


def get_auth_handler(host, cfg, requested_capability=None):
    """Finds an AuthHandler that able to authenticate an AWS service.

    :type host:     string
    :param host:    The name of the host

    :type cfg:      Config
    :param cfg:     app configuration

    :return:        An implementation of AuthHandler.

    Raises:
        exception.NoAuthHandlerFound
    """

    if not requested_capability:
        requested_capability = []

    auth_handlers = []
    for handler in AuthHandler.__subclasses__():
        if handler.is_capable(requested_capability):
            auth_handlers.append(handler(host, cfg))

    return auth_handlers[0]


# def detect_potential_sigv4(func):
#     def _wrapper(self):
#         if os.environ.get('EC2_USE_SIGV4', False):
#             return ['hmac-v4']
#
#         if cfg.get('ec2', 'use-sigv4', False):
#             return ['hmac-v4']
#
#         if hasattr(self, 'region'):
#             if getattr(self.region, 'endpoint', ''):
#                 if '.cn-' in self.region.endpoint:
#                     return ['hmac-v4']
#
#         return func(self)
#
#     return _wrapper
#
#
# def detect_potential_s3sigv4(func):
#     def _wrapper(self):
#         if os.environ.get('S3_USE_SIGV4', False):
#             return ['hmac-v4-s3']
#
#         if cfg.get('s3', 'use-sigv4', False):
#             return ['hmac-v4-s3']
#
#         if hasattr(self, 'host'):
#             if '.cn-' in self.host:
#                 return ['hmac-v4-s3']
#
#         return func(self)
#
#     return _wrapper
