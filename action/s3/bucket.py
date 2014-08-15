import urllib

from action.s3.key import Key
from utilities.exception import UnsuccessfulRequestError
from utilities.utils import get_aws_metadata


class Bucket:
    """
    Represent S3 Bucket object and provide actions aginest S3 Buckets
    """

    def __init__(self, connection=None, name=None):
        self.name = name
        self.connection = connection

    def search_key(self, parameters):
        """
        Function that search for S3 bucket keys

        :param parameters:  query parameter that can be used to search for
                            a key e.g. deliminator, prefix
        :return: The matching keys
        """

        query_para = []
        for k, v in parameters.iteritems():
            query_para.append('%s=%s' % (k, urllib.quote(v)))

        query_args = '&'.join(query_para) or None
        response = \
            self.connection.send_request('GET', self.name,
                                         response_class='ListBucketResult',
                                         query_args=query_args)

        matching_keys = [common_prefix.prefix for common_prefix in
                         response.common_prefixes.data]

        return matching_keys

    def get_key(self, key_name, headers=None, version_id=None,
                response_headers=None):
        """
        Check to see if a particular key exists within the bucket.  This
        method uses a HEAD request to check for the existence of the key.
        Returns: An instance of a Key object or None

        :param key_name: The name of the key to retrieve
        :type key_name: string

        :param headers: The headers to send when retrieving the key
        :type headers: dict

        :param version_id:
        :type version_id: string

        :param response_headers: A dictionary containing HTTP
            headers/values that will override any headers associated
            with the stored object in the response.
        :type response_headers: dict

        :rtype: :class:`action.s3.key.Key`
        :returns: A Key object from this bucket.
        """

        query_args_l = []
        if version_id:
            query_args_l.append('versionId=%s' % version_id)
        if response_headers:
            for rk, rv in response_headers.iteritems():
                query_args_l.append('%s=%s' % (rk, urllib.quote(rv)))

        key, resp = self._get_key(key_name, headers, query_args_l)
        return key

    def _get_key(self, key_name, headers, query_args_l):
        query_args = '&'.join(query_args_l) or None
        response = self.connection.send_request('HEAD', self.name, key_name,
                                                headers=headers,
                                                query_args=query_args)
        body = response.read()
        # If the response was success
        if response.status / 100 == 2:
            k = Key(self, key_name)

            k.metadata = get_aws_metadata(response.msg)
            k.etag = response.getheader('etag')
            k.content_type = response.getheader('content-type')
            k.content_encoding = response.getheader('content-encoding')
            k.content_disposition = response.getheader('content-disposition')
            k.content_language = response.getheader('content-language')
            k.last_modified = response.getheader('last-modified')
            # the following machinations are a workaround to the fact that
            # apache/fastcgi omits the content-length header on HEAD
            # requests when the content-length is zero.
            # See http://goo.gl/0Tdax for more details.
            content_len = response.getheader('content-length')
            if content_len:
                k.size = int(response.getheader('content-length'))
            else:
                k.size = 0
            k.cache_control = response.getheader('cache-control')
            k.name = key_name
            k.handle_version_headers(response)
            k.handle_encryption_headers(response)
            k.handle_restore_headers(response)
            k.handle_addl_headers(response.getheaders())
            return k, response
        else:
            if response.status == 404:
                return None, response
            else:
                raise UnsuccessfulRequestError(response.status,
                                               response.reason, body)