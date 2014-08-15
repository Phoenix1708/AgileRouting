import urllib
from action.s3.bucket import Bucket
from action.s3.key import Key
from connection.AWSConnection import AWSConnection
from etc.configuration import log
from utilities import utils
from utilities.exception import HostRequiredError, ServerError, ClientError, \
    GeneralError


def get_bucket_server(server, bucket):
    return '%s.%s' % (bucket, server)


def build_host(server, bucket):
    if bucket == '':
        return server
    else:
        return get_bucket_server(server, bucket)


def build_auth_path(bucket, key=''):
    key = utils.get_utf8_value(key)
    path = '/'
    if bucket != '':
        path = '/%s' % bucket
    if key:
        return path + '/%s' % urllib.quote(key)

    return path + '/'


def build_path_base(key=''):
    key = utils.get_utf8_value(key)
    if key:
        return '/%s' % urllib.quote(key)
    else:
        return '/'


def build_url_base(connection, protocol, server, bucket, key=''):
    url_base = '%s://' % protocol
    url_base += build_host(server, bucket)
    url_base += connection.get_path(build_path_base(key))
    return url_base


class S3Connection(AWSConnection):
    DefaultHost = 's3.amazonaws.com'

    def __init__(self, is_secure=True, port=None, host=None, anon=False):
        no_host_provided = False
        if not host:
            no_host_provided = True
            host = self.DefaultHost

        self.anon = anon
        super(S3Connection, self).__init__(host, is_secure, port)
        # We need to delay until after the call to ``super`` before checking
        # to see if SigV4 is in use.
        if no_host_provided:
            if 'hmac-v4-s3' in self._required_auth_capability():
                raise HostRequiredError(
                    "When using SigV4, you must specify a 'host' parameter."
                )

    def _required_auth_capability(self):
        return ['s3']

    def get_bucket(self, bucket_name, headers=None):
        """
        Function to check if a bucket exists by bucket name.

        :type bucket_name:  string
        :param bucket_name: The name of the bucket

        :type headers:      dict
        :param headers:     Headers to pass along with the request to AWS.

        :returns: A <Bucket> object
        """
        response = self.send_request('HEAD', bucket_name, headers=headers)

        # consume the response
        body = response.read()

        if response.status == 200:
            return Bucket(self, bucket_name)
        elif 400 <= response.status < 500:
            raise ClientError(status=response.status, reason=response.reason)
        elif 500 <= response.status < 600:
            raise ServerError(status=response.status, reason=response.reason,
                              body=body)
        else:
            raise GeneralError(msg=response.reason)

    def send_request(self, method, bucket='', key='', headers=None, data='',
                     query_args=None, response_class=None):
        """Build S3 specific HTTP URL with query parameters
        """

        # use key and bucket name to build query arguments.
        # If key and bucket are not passed in use default path
        if isinstance(bucket, Bucket):
            bucket = bucket.name
        if isinstance(key, Key):
            key = key.name

        path = build_path_base(key)
        log.debug('path=%s' % path)

        auth_path = build_auth_path(bucket, key)
        log.debug('auth_path=%s' % auth_path)

        host = build_host(self.server_name(), bucket)

        if query_args:
            path += '?' + query_args
            log.debug('path=%s' % path)
            auth_path += '?' + query_args
            log.debug('auth_path=%s' % auth_path)

        para = {'method': method,
                'path': path,
                'host': host,
                'auth_path': auth_path,
                'response_class': response_class,
                'headers': headers}

        return super(S3Connection, self).send_request(**para)