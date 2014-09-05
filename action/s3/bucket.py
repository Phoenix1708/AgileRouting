import urllib

from action.s3.key import Key
from utilities.exception import UnsuccessfulRequestError


class Bucket:
    """
    Represent S3 Bucket object and provide actions against S3 Buckets
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
            self.connection.make_request('GET', self.name,
                                         response_class='ListBucketResult',
                                         query_args=query_args)

        matching_keys = [common_prefix.prefix for common_prefix in
                         response.common_prefixes.data]

        return matching_keys

    def get_key(self, key_name):
        """
        Check whether a particular key exists in the bucket using 'HEAD'
        HTTP request which only return metadata

        :param key_name: The name of the key
        """

        response = self.connection.make_request('HEAD', self.name, key_name)
        body = response.read()

        # If the response was success
        # read metadata of the key which will be used for downloading later
        if response.status / 100 == 2:
            k = Key(self, key_name)

            k.name = key_name
            k.entity_tag = response.getheader('etag')
            k.content_type = response.getheader('content-type')
            k.last_modified = response.getheader('last-modified')
            content_len = response.getheader('content-length')
            if content_len:
                k.size = int(response.getheader('content-length'))
            else:
                k.size = 0

            return k
        else:
            if response.status == 404:
                return None, response
            else:
                raise UnsuccessfulRequestError(response.status,
                                               response.reason, body)