import base64
import hashlib
import os
import re
import threading
import time
import urllib
import urllib2

from etc.configuration import log, cfg
from utilities.exception import GeneralError
from utilities.request_headers import HEADER_PREFIX_KEY, DATE_HEADER_KEY, \
    HeaderInfoMap, METADATA_PREFIX_KEY


time_format = '%Y-%m-%dT%H:%M:%SZ'

# List of Query String Arguments of Interest
qsa_of_interest = ['acl', 'cors', 'defaultObjectAcl', 'location', 'logging',
                   'partNumber', 'policy', 'requestPayment', 'torrent',
                   'versioning', 'versionId', 'versions', 'website',
                   'uploads', 'uploadId', 'response-content-type',
                   'response-content-language', 'response-expires',
                   'response-cache-control', 'response-content-disposition',
                   'response-content-encoding', 'delete', 'lifecycle',
                   'tagging', 'restore',
                   # storageClass is a QSA for buckets in Google Cloud Storage.
                   # (StorageClass is associated to individual keys in S3, but
                   # having it listed here should cause no problems because
                   # GET bucket?storageClass is not part of the S3 API.)
                   'storageClass',
                   # websiteConfig is a QSA for buckets in Google Cloud
                   # Storage.
                   'websiteConfig',
                   # compose is a QSA for objects in Google Cloud Storage.
                   'compose']

_first_cap_regex = re.compile('(.)([A-Z][a-z]+)')
_number_cap_regex = re.compile('([a-z])([0-9]+)')
_end_cap_regex = re.compile('([a-z0-9])([A-Z])')


def get_env(env_var_name):
    """
    Function to ensuring the retrieval of environment variable

    :param env_var_name: Name of the environment variable
    :return:             The environment variable value
    """

    env_var = os.environ[env_var_name]
    if not env_var:
        raise GeneralError(msg="No environment variable \'%s\' found. Please " +
                               "set it up first " % env_var_name)

    return env_var


def get_ip(host_name):
    ip = cfg.get('IPs', host_name, None)
    if not ip:
        raise GeneralError(msg="No IP configuration found for host name \'%s\'."
                               % host_name)
    return ip

# TODO: when the number of servers increases this needs to be more generic
# e.g adding function to dynamically building the metadata map
observer_1_ip = get_ip('CSPARQL_STATION_1_OBSERVER_IP')
observer_2_ip = get_ip('CSPARQL_STATION_2_OBSERVER_IP')

station_metadata_map = {
    'region': {
        'xueshi-station-1': 'eu-west-1',
        'xueshi-station-2': 'us-east-1'
    },

    'ip': {
        'xueshi-station-1': observer_1_ip,
        'xueshi-station-2': observer_2_ip
    }
}


def get_stations():
    # Test
    return ['xueshi-station-1']
    # return ['xueshi-station-1', 'xueshi-station-2']


def get_station_region():
    """
    The dictionary store the mapping between service station and its region
    in order to further match with other metrics for the same service station

    :return: station region mapping
    """

    available_stations = get_stations()
    station_region_map = station_metadata_map['region']

    available_station_region_map = dict()
    for avail_station in available_stations:
        if station_region_map[avail_station]:
            available_station_region_map.update(
                {avail_station: station_region_map[avail_station]})

    return available_station_region_map


def get_station_csparql():
    """
    One csparql observer in charge of one service station.
    The dictionary store the mapping between service station and observer
    in order to further match with other metrics for the same service station

    :return: station observer ip mapping
    """

    available_stations = get_stations()
    station_ip_map = station_metadata_map['ip']

    available_station_ip_map = dict()
    for avail_station in available_stations:
        available_station_ip_map.update(
            {avail_station: station_ip_map[avail_station]})

    return available_station_ip_map


def sync_files(host_ip, username, host_file_path, pk_path, dst_loc,
               multi_retry=False, max_retries=5):
    """
    Retrieve remote file with rsync with multiple retries

    :param host_ip:         Remote Host IP
    :param username:        Username used to login to remote machine
    :param host_file_path:  Path of the targeted file on remote machine
    :param pk_path:         Private key used to login
    :param dst_loc:         Path to store file locally
    :param multi_retry:     Flag for enabling multiple retries upon fail
    :param max_retries:     The maximum number of retries
    """

    # number of retries
    num_retries = 0
    # error message if failed
    error_msg = None
    while num_retries <= max_retries:

        # ssh command used to log into host
        ssh_cmd = '\"ssh -i ' + pk_path + '\"'
        # source and target location of files
        from_loc = '%s@%s:%s' % (username, host_ip, host_file_path)

        # copy disk file from source to destination
        rsync_cmd = ["/usr/bin/rsync", "-e", ssh_cmd,
                     '-avz', '--sparse', '--progress', from_loc, dst_loc]
        rsync_cmd_str = ' '.join(rsync_cmd)

        try:
            print_message('[Debug] executing %s' % rsync_cmd_str)
            os.system(rsync_cmd_str)
            # successful execution should break the loop from here
            return
        except Exception as e:
            print 'Fail to synchronise remote file with \'rsync\' command.\n' \
                  'Details: %s\n' % e
            error_msg = e

            if not multi_retry:
                break

            # pause for 2 sec
            time.sleep(2)
            print_message('Re-attempting synchronisation...')
            num_retries += 1

    if error_msg:
        print error_msg


def print_message(msg):
    thread_id = threading.current_thread().name
    print '[%s]: %s' % (thread_id, msg)


def pythonize_name(name):
    """Convert camel case to a "pythonic" name.

    Examples::

        pythonize_name('CamelCase') -> 'camel_case'
        pythonize_name('already_pythonized') -> 'already_pythonized'
        pythonize_name('HTTPRequest') -> 'http_request'
        pythonize_name('HTTPStatus200Ok') -> 'http_status_200_ok'
        pythonize_name('UPPER') -> 'upper'
        pythonize_name('') -> ''

    """

    s1 = _first_cap_regex.sub(r'\1_\2', name)
    s2 = _number_cap_regex.sub(r'\1_\2', s1)
    return _end_cap_regex.sub(r'\1_\2', s2).lower()


def get_utf8_value(value):
    if not isinstance(value, basestring):
        value = str(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value


# def find_class(module_name, class_name=None):
# if class_name:
#         module_name = "%s.%s" % (module_name, class_name)
#     modules = module_name.split('.')
#     c = None
#
#     try:
#         for m in modules[1:]:
#             if c:
#                 c = getattr(c, m)
#             else:
#                 c = getattr(__import__(".".join(modules[0:-1])), m)
#         return c
#     except:
#         return None


def get_aws_metadata(headers):
    metadata_prefix = HeaderInfoMap[METADATA_PREFIX_KEY]
    metadata = {}
    for hkey in headers.keys():
        if hkey.lower().startswith(metadata_prefix):
            val = urllib.unquote(headers[hkey])
            try:
                metadata[hkey[len(metadata_prefix):]] = unicode(val, 'utf-8')
            except UnicodeDecodeError:
                metadata[hkey[len(metadata_prefix):]] = val
            del headers[hkey]
    return metadata


def compute_hash(fp, buf_size=8192, size=None, hash_algorithm=hashlib):
    hash_obj = hash_algorithm()
    spos = fp.tell()
    if size and size < buf_size:
        s = fp.read(size)
    else:
        s = fp.read(buf_size)
    while s:
        hash_obj.update(s)
        if size:
            size -= len(s)
            if size <= 0:
                break
        if size and size < buf_size:
            s = fp.read(size)
        else:
            s = fp.read(buf_size)
    hex_digest = hash_obj.hexdigest()
    base64_digest = base64.encodestring(hash_obj.digest())
    if base64_digest[-1] == '\n':
        base64_digest = base64_digest[0:-1]
    # data_size based on bytes read.
    data_size = fp.tell() - spos
    fp.seek(spos)
    return hex_digest, base64_digest, data_size


def get_ts(ts=None):
    if not ts:
        ts = time.gmtime()
    return time.strftime(time_format, ts)


def find_matching_headers(name, headers):
    """
    Takes a specific header name and a dict of headers {"name": "value"}.
    Returns a list of matching header names, case-insensitive.

    """
    return [h for h in headers if h.lower() == name.lower()]


def retry_url(url, retry_on_404=True, num_retries=10):
    """
    Retry a url.  This is specifically used for accessing the metadata
    service on an instance.  Since this address should never be proxied
    (for security reasons), we create a ProxyHandler with a NULL
    dictionary to override any proxy settings in the environment.
    """
    for i in range(0, num_retries):
        try:
            proxy_handler = urllib2.ProxyHandler({})
            opener = urllib2.build_opener(proxy_handler)
            req = urllib2.Request(url)
            r = opener.open(req)
            result = r.read()
            return result
        except urllib2.HTTPError, e:
            # in 2.6 you use getcode(), in 2.5 and earlier you use code
            if hasattr(e, 'getcode'):
                code = e.getcode()
            else:
                code = e.code
            if code == 404 and not retry_on_404:
                return ''
        except Exception, e:
            pass

        log.exception('Caught exception reading instance data')
        # If not on the last iteration of the loop then sleep.
        if i + 1 != num_retries:
            time.sleep(min(2 ** i, cfg.get('HTTPConnection',
                                           'max_retry_delay', 60)))
        log.error('Unable to read instance data, giving up')
        return ''


def mklist(value):
    if not isinstance(value, list):
        if isinstance(value, tuple):
            value = list(value)
        else:
            value = [value]
    return value


def unquote_v(nv):
    if len(nv) == 1:
        return nv
    else:
        return nv[0], urllib.unquote(nv[1])


def canonical_string(method, path, headers, expires=None):
    """
    Generates the aws canonical string for the given parameters
    """
    interesting_headers = {}
    for key in headers:
        lk = key.lower()
        if headers[key] is not None and \
                (lk in ['content-md5', 'content-type', 'date'] or
                     lk.startswith(HeaderInfoMap[HEADER_PREFIX_KEY])):
            interesting_headers[lk] = str(headers[key]).strip()

    # these keys get empty strings if they don't exist
    if 'content-type' not in interesting_headers:
        interesting_headers['content-type'] = ''
    if 'content-md5' not in interesting_headers:
        interesting_headers['content-md5'] = ''

    # just in case someone used this.  it's not necessary in this lib.
    if DATE_HEADER_KEY in interesting_headers:
        interesting_headers['date'] = ''

    # if you're using expires for query string auth, then it trumps date
    # (and provider.date_header)
    if expires:
        interesting_headers['date'] = str(expires)

    sorted_header_keys = sorted(interesting_headers.keys())

    buf = "%s\n" % method
    for key in sorted_header_keys:
        val = interesting_headers[key]
        if key.startswith(HeaderInfoMap[HEADER_PREFIX_KEY]):
            buf += "%s:%s\n" % (key, val)
        else:
            buf += "%s\n" % val

    # don't include anything after the first ? in the resource...
    # unless it is one of the QSA of interest, defined above
    t = path.split('?')
    buf += t[0]

    if len(t) > 1:
        qsa = t[1].split('&')
        qsa = [a.split('=', 1) for a in qsa]
        qsa = [unquote_v(a) for a in qsa if a[0] in qsa_of_interest]
        if len(qsa) > 0:
            qsa.sort(cmp=lambda x, y: cmp(x[0], y[0]))
            qsa = ['='.join(a) for a in qsa]
            buf += '?'
            buf += '&'.join(qsa)

    return buf