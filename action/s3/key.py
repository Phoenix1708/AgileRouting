import errno
import re

from etc.configuration import cfg
from utilities.exception import S3Exception, UnsuccessfulRequestError


class Key(object):
    """
    Represents a key object (metadata) in an S3 bucket.
    """

    DefaultContentType = 'application/octet-stream'

    BufferSize = cfg.get_int('s3', 'key_buffer_size', 8192)

    def __init__(self, bucket=None, name=None):
        self.bucket = bucket
        self.name = name
        self.content_type = self.DefaultContentType
        self.entity_tag = None
        self.last_modified = None
        self.accept_ranges = None
        self.response = None
        self.size = None

    def __repr__(self):
        if self.bucket:
            return '<Key: %s,%s>' % (self.bucket.name, self.name)
        else:
            return '<Key: None,%s>' % self.name

    def __iter__(self):
        return self

    def next(self):
        """
        Make Key object iterable such that large content can be
        read pieces by pieces depends on buffer size
        """
        self.open_read()
        data = self.response.read(self.BufferSize)
        if not data:
            self.close()
            raise StopIteration
        return data

    def get_contents_to_file(self, fp):

        self.open_read()
        data_size = 0

        try:
            for content_fragment in self:
                fp.write(content_fragment)
                data_size += len(content_fragment)

        except IOError, e:
            if e.errno == errno.ENOSPC:
                raise S3Exception('Out of space for saving file '
                                  '%s' % fp.name)
            raise

        if self.size is None:
            self.size = data_size

        self.close()

    def open_read(self, headers=None, query_args=''):
        """
        GET the S3 bucket key content

        :param headers: Headers to pass in the web request

        :param query_args: Arguments of the query string

        """
        if self.response:
            return

        self.response = self.bucket.connection.make_request(
            'GET', self.bucket.name, self.name, headers,
            query_args=query_args)

        if self.response.status < 199 or self.response.status > 299:
            body = self.response.read()
            raise UnsuccessfulRequestError(self.response.status,
                                           self.response.reason, body)

        # process response header
        response_headers = self.response.msg
        # self.metadata = utils.get_aws_metadata(response_headers)

        for name, value in response_headers.items():
            # Get size from Content-Range or Content-Length
            # header depends on what server actually returned
            if (name.lower() == 'content-length' and
               'Content-Range' not in response_headers):
                self.size = int(value)
            elif name.lower() == 'content-range':
                end_range = re.sub('.*/(.*)', '\\1', value)
                self.size = int(end_range)
            elif name.lower() == 'etag':
                self.entity_tag = value
            elif name.lower() == 'content-type':
                self.content_type = value
            elif name.lower() == 'last-modified':
                self.last_modified = value
            elif name.lower() == 'accept_ranges':
                self.accept_ranges = value

    def close(self, consume=False):
        """
        Close the HTTP response.

        :param consume: Flag to indicate whether to simply consume the response
                        from S3 connection without processing it. Since HTTP
                        response has to be consumed before next request
        """

        if self.response and not consume:
            self.response.read()

        self.response = None