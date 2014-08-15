import errno
import math
import re
import urllib

from etc.configuration import cfg
from utilities import utils
from utilities.exception import S3Exception, UnsuccessfulRequestError
from utilities.request_headers import HeaderInfoMap, VERSION_ID_HEADER_KEY, \
    COPY_SOURCE_VERSION_ID_HEADER_KEY, DELETE_MARKER_HEADER_KEY, \
    SERVER_SIDE_ENCRYPTION_KEY, RESTORE_HEADER_KEY


try:
    from hashlib import md5
except ImportError:
    from md5 import md5


class Key(object):
    """
    Represents a key object (metadata) in an S3 bucket.
    """

    DefaultContentType = 'application/octet-stream'

    #
    # RestoreBody = """<?xml version="1.0" encoding="UTF-8"?>
    # <RestoreRequest xmlns="http://s3.amazonaws.com/doc/2006-03-01">
    #     <Days>%s</Days>
    #   </RestoreRequest>"""

    BufferSize = cfg.get_int('s3', 'key_buffer_size', 8192)

    def __init__(self, bucket=None, name=None):
        self.bucket = bucket
        self.name = name
        self.metadata = {}
        self.cache_control = None
        self.content_type = self.DefaultContentType
        self.content_encoding = None
        self.content_disposition = None
        self.content_language = None
        self.filename = None
        self.etag = None
        self.is_latest = False
        self.last_modified = None
        self.owner = None
        self.storage_class = 'STANDARD'
        self.path = None
        self.resp = None
        self.size = None
        self.version_id = None
        self.source_version_id = None
        self.delete_marker = False
        self.encrypted = None
        self.ongoing_restore = None
        self.expiry_date = None
        self.local_hashes = {}

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
        data = self.resp.read(self.BufferSize)
        if not data:
            self.close()
            raise StopIteration
        return data

    def get_contents_to_file(self, fp, headers=None, cb=None, num_cb=10,
                             response_headers=None, hash_algs=None,
                             query_args=None):
        if headers is None:
            headers = {}
        save_debug = self.bucket.connection.debug
        if self.bucket.connection.debug == 1:
            self.bucket.connection.debug = 0

        query_args = query_args or []

        if hash_algs is None:
            hash_algs = {'md5': md5}

        digesters = dict((alg, hash_algs[alg]()) for alg in hash_algs or {})

        if response_headers:
            for key in response_headers:
                query_args.append('%s=%s' % (
                    key, urllib.quote(response_headers[key])))

        query_args = '&'.join(query_args)
        self.open_read(headers, query_args=query_args)

        data_len = 0
        if cb:
            if self.size is None:
                cb_size = 0
            else:
                cb_size = self.size
            if self.size is None and num_cb != -1:
                # If size is not available due to chunked transfer for example,
                # we'll call the cb for every 1MB of data transferred.
                cb_count = (1024 * 1024) / self.BufferSize
            elif num_cb > 1:
                cb_count = int(
                    math.ceil(cb_size / self.BufferSize / (num_cb - 1.0)))
            elif num_cb < 0:
                cb_count = -1
            else:
                cb_count = 0
            i = 0
            cb(data_len, cb_size)
        try:
            for content_fragment in self:
                fp.write(content_fragment)
                data_len += len(content_fragment)
                for alg in digesters:
                    digesters[alg].update(content_fragment)
                if cb:
                    if 0 < cb_size <= data_len:
                        break
                    i += 1
                    if i == cb_count or cb_count == -1:
                        cb(data_len, cb_size)
                        i = 0
        except IOError, e:
            if e.errno == errno.ENOSPC:
                raise S3Exception('Out of space for destination file '
                                  '%s' % fp.name)
            raise
        if cb and (cb_count <= 1 or i > 0) and data_len > 0:
            cb(data_len, cb_size)
        for alg in digesters:
            self.local_hashes[alg] = digesters[alg].digest()
        if self.size is None and "Range" not in headers:
            self.size = data_len
        self.close()
        self.bucket.connection.debug = save_debug

    def open_read(self, headers=None, query_args=''):
        """
        Open this S3 bucket key for reading

        :type headers: dict
        :param headers: Headers to pass in the web request

        :type query_args: string
        :param query_args: Arguments of the query string

        """
        if self.resp is None:
            self.resp = self.bucket.connection.send_request(
                'GET', self.bucket.name, self.name, headers,
                query_args=query_args)

            if self.resp.status < 199 or self.resp.status > 299:
                body = self.resp.read()
                raise UnsuccessfulRequestError(self.resp.status,
                                               self.resp.reason, body)

            # process response header
            response_headers = self.resp.msg
            self.metadata = utils.get_aws_metadata(response_headers)

            for name, value in response_headers.items():
                # To get correct size for Range GETs, use Content-Range
                # header if one was returned. If not, use Content-Length
                # header.
                if (name.lower() == 'content-length' and
                   'Content-Range' not in response_headers):
                    self.size = int(value)
                elif name.lower() == 'content-range':
                    end_range = re.sub('.*/(.*)', '\\1', value)
                    self.size = int(end_range)
                elif name.lower() == 'etag':
                    self.etag = value
                elif name.lower() == 'content-type':
                    self.content_type = value
                elif name.lower() == 'content-encoding':
                    self.content_encoding = value
                elif name.lower() == 'content-language':
                    self.content_language = value
                elif name.lower() == 'last-modified':
                    self.last_modified = value
                elif name.lower() == 'cache-control':
                    self.cache_control = value
                elif name.lower() == 'content-disposition':
                    self.content_disposition = value
            self.handle_version_headers(self.resp)
            self.handle_encryption_headers(self.resp)
            self.handle_restore_headers(self.resp)
            self.handle_addl_headers(self.resp.getheaders())

    def handle_encryption_headers(self, resp):
        if HeaderInfoMap[SERVER_SIDE_ENCRYPTION_KEY]:
            self.encrypted = resp.getheader(
                HeaderInfoMap[SERVER_SIDE_ENCRYPTION_KEY], None)
        else:
            self.encrypted = None

    def handle_version_headers(self, resp, force=False):
        # If the Key object already has a version_id attribute value, it
        # means that it represents an explicit version and the user is
        # doing a get_contents_*(version_id=<foo>) to retrieve another
        # version of the Key.  In that case, we don't really want to
        # overwrite the version_id in this Key object.  Comprende?
        if self.version_id is None or force:
            self.version_id = resp.getheader(
                HeaderInfoMap[VERSION_ID_HEADER_KEY], None)

        self.source_version_id = resp.getheader(
            HeaderInfoMap[COPY_SOURCE_VERSION_ID_HEADER_KEY], None)

        if resp.getheader(
                HeaderInfoMap[DELETE_MARKER_HEADER_KEY], 'false') == 'true':
            self.delete_marker = True
        else:
            self.delete_marker = False

    def handle_restore_headers(self, response):
        header = response.getheader(HeaderInfoMap[RESTORE_HEADER_KEY])
        if header is None:
            return
        parts = header.split(',', 1)
        for part in parts:
            key, val = [i.strip() for i in part.split('=')]
            val = val.replace('"', '')
            if key == 'ongoing-request':
                self.ongoing_restore = True if val.lower() == 'true' else False
            elif key == 'expiry-date':
                self.expiry_date = val

    def handle_addl_headers(self, headers):
        """
        Used by Key subclasses to do additional, provider-specific
        processing of response headers. No-op for this base class.
        """
        pass

    def close(self, fast=False):
        """
        Close this key.

        :type fast: bool
        :param fast: True if you want the connection to be closed without first
        reading the content. This should only be used in cases where subsequent
        calls don't need to return the content from the open HTTP connection.
        Note: As explained at
        http://docs.python.org/2/library/httplib.html#httplib.HTTPConnection.getresponse,
        callers must read the whole response before sending a new request to the
        server. Calling Key.close(fast=True) and making a subsequent request to
        the server will work because we will get an httplib exception and
        close/reopen the connection.

        """
        if self.resp and not fast:
            self.resp.read()
        self.resp = None
        self.closed = True