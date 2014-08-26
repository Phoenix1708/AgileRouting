from __future__ import division
import base64
import hashlib
import logging
import os
import re
import threading
import time
import urllib
import urllib2
import math

from datetime import datetime
import paramiko
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


# def get_ip(host_name):
# ip = cfg.get('IPs', host_name, None)
# if not ip:
# raise GeneralError(msg="No IP configuration
# found for host name \'%s\'."
#                                % host_name)
#     return ip
#
#
# def get_elb_bucket(station_name):
#     elb_bucket = cfg.get('ELBBucket', station_name, None)
#     if not elb_bucket:
#         raise GeneralError(msg="No access log location (S3 buckets) "
#                                "configuration found for station "
#                                "\'%s\'." % station_name)
#     return elb_bucket


# def get_config_value(section, entry_key):
#     cfg_value = cfg.get(section, entry_key, None)
#     if not cfg_value:
#         raise GeneralError(msg="No %s configuration found for "
#                                "\'%s\' " % (section, entry_key))
#     return cfg_value


def get_available_stations():
    # TODO: needs to be dynamic in the future
    return ['xueshi-station-1', 'xueshi-station-2']


def get_available_clients():
    # TODO: needs to be dynamic in the future
    return ['ap_south_1_client_1', 'us_east_1_client_1']


def get_stations_bandwidth(client):
    """
    Get the in and out bandwidth between a particular client (in a
    particular region) and all service stations

    :param client:  Name / Identifier of the client
    :return:
    """

    available_stations = get_available_stations()

    station_in_band_map = station_metadata_map['in_bandwidths']
    station_out_band_map = station_metadata_map['out_bandwidths']

    available_station_in_band_map = dict()
    available_station_out_band_map = dict()

    for client_station_pair, in_band_val in station_in_band_map.iteritems():
        if client in client_station_pair:
            for avail_station in available_stations:
                if avail_station in client_station_pair:
                    available_station_in_band_map.update(
                        {avail_station: in_band_val})

    for client_station_pair, out_band_val in station_out_band_map.iteritems():
        if client in client_station_pair:
            for avail_station in available_stations:
                if avail_station in client_station_pair:
                    available_station_out_band_map.update(
                        {avail_station: out_band_val})

    # for avail_station in available_stations:
    #
    #     if station_in_band_map[avail_station]:
    #         available_station_in_band_map.update(
    #             {avail_station: station_in_band_map[avail_station]})
    #
    #     if station_out_band_map[avail_station]:
    #         available_station_out_band_map.update(
    #             {avail_station: station_out_band_map[avail_station]})

    return available_station_in_band_map, available_station_out_band_map


def get_elb_buckets_map():
    """
    The dictionary store the mapping between service station and the S3
    buckets name of the ELB used by this station in order to further match
    with other metrics for the same service station

    :return: station elb log s3 bucket mapping
    """
    available_stations = get_available_stations()
    station_elb_log_map = station_metadata_map['s3_bucket']

    available_station_elb_log_map = dict()
    for avail_station in available_stations:
        if station_elb_log_map[avail_station]:
            available_station_elb_log_map.update(
                {avail_station: station_elb_log_map[avail_station]})

    return available_station_elb_log_map


def get_station_region():
    """
    The dictionary store the mapping between service station and its region
    in order to further match with other metrics for the same service station

    :return: station region mapping
    """

    available_stations = get_available_stations()
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

    available_stations = get_available_stations()
    station_ip_map = station_metadata_map['ip']

    available_station_ip_map = dict()
    for avail_station in available_stations:
        key_str = '%s_observer' % avail_station
        available_station_ip_map.update(
            {avail_station: station_ip_map[key_str]})

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
    string_to_print = '[%s]: %s' % (thread_id, msg)
    print string_to_print
    log_info('running_log.txt', string_to_print + '\n')


def log_info(log_file_name, data_to_write):
    with open(log_file_name, 'a+') as f:
        f.write('%s\n' % data_to_write)


def get_expected_num_logs():
    """
    Function to return the number of ELB access log expected.
    (For code re-usability)
    """
    measurement_interval = cfg.get_int('Default', 'measurement_interval', 10)

    print_message('')
    print_message('Measurement interval: %s' % measurement_interval)

    logging_time = cfg.get_int('s3', 'log_omitting_time', 5)
    expected_logs_to_obtain = math.floor(measurement_interval / logging_time)

    return expected_logs_to_obtain


def get_next_nth_elb_log_time(n, last_expected_minutes):
    """
    Get the next minutes e.g 5 or 10 or 15 that the S3 will omit ELB access
    log. It can also get the time of next nth log base on current time

    :return:
    """

    current_time = datetime.utcnow()
    [year, month, day, hour, minute] = \
        current_time.year, current_time.month, current_time.day, \
        current_time.hour, current_time.minute

    # Test
    print_message('Current UTC Time: %s' % '-'.join([str(year),
                                                     str('%02d' % month),
                                                     str('%02d' % day),
                                                     str('%02d' % hour),
                                                     str('%02d' % minute)]))

    # Calculate the next expected log file omitted by S3.
    # With 5 minute logging interval, logs are omitted every 5 minutes
    # at each hour, hence the ceiling of the division of current minute
    # with 5 (minutes) should be the next expected minute at which a new
    # log will be omitted

    logging_interval = cfg.get_int('s3', 'log_omitting_time', 60)

    next_expected_logging_minute = 0
    if not last_expected_minutes:
        interval_covered = math.ceil(minute / logging_interval)
        reminder = minute % logging_interval

        next_expected_logging_minute = \
            logging_interval * interval_covered + logging_interval * (n - 1)

        # it the current minute is happen to be a logging time
        # i.e 5, 10, 15 etc.
        if reminder == 0:
            next_expected_logging_minute += n * logging_interval

    else:
        next_expected_logging_minute += \
            last_expected_minutes + n * logging_interval

    if next_expected_logging_minute >= 60:
        hour += 1
        next_expected_logging_minute %= 60

    print_message('Next expected time (UTC) %02d:%02d'
                  % (hour, next_expected_logging_minute))

    if next_expected_logging_minute < minute:
        max_waiting_minutes = \
            60 - minute + next_expected_logging_minute + logging_interval
    else:
        max_waiting_minutes = \
            next_expected_logging_minute - minute + logging_interval

    print_message('[Debug]: max_waiting_minutes: %s' % max_waiting_minutes)

    return day, hour, month, next_expected_logging_minute, year, \
           max_waiting_minutes


def calculate_waiting_time():
    # record the start time to calculate time elapsed
    start_time = time.time()
    # get expected ELB access logs based on measurement interval
    expected_logs = get_expected_num_logs()

    # calculate the time for which the last expected access log is
    day, hour, month, next_expected_logging_minute, year, max_waiting_minutes \
        = get_next_nth_elb_log_time(expected_logs, None)

    # from UTC to GMT hour + 1
    time_str = ''.join([str(year), str(month), str(day), str(hour + 1),
                        str(int(next_expected_logging_minute))])
    date = datetime.strptime("".join(time_str), '%Y%m%d%H%M')
    date_milli = time.mktime(date.timetuple()) + date.microsecond
    # calculate waiting time
    waiting_time = (date_milli - start_time)
    return waiting_time


def execute_remote_command(host_address, command, username, password='',
                           private_key=None):
    # print private_key
    # connect to the host
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_address, username=username, password=password,
                key_filename=private_key)
    stdin, stdout, stderr = ssh.exec_command(command)

    print_message('')
    print_message("[Debug] Executing \'%s\' on host: %s\n"
                  % (command, host_address))

    logging.getLogger("paramiko").setLevel(logging.WARNING)

    # if output and standard error hasn't been read off before
    # buffer is full the host will hang
    output = None
    error = None
    output_str = ""
    error_str = ""

    while output != "":
        output = stdout.readline()
        # print output while reading
        if output:
            # print output
            output_str += output

    while error != "":
        error = stderr.readline()
        error_str += error

    # print error at the end
    if error_str:
        print_message(error_str)

    ssh.close()

    return [output_str, error_str]


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
# module_name = "%s.%s" % (module_name, class_name)
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


# TODO: when the number of servers increases this needs to be more generic
# Script that setup IPs when this module being imported so that the configure
#  will be checked before actually running any code
station_metadata_map = {
    'region': {
        'xueshi-station-1': 'eu-west-1',
        'xueshi-station-2': 'us-east-1'
    },

    'ip': {

    },

    's3_bucket': {

    },

    'in_bandwidths': {

    },

    'out_bandwidths': {

    },

    'StationELBDNS': {
        'xueshi-station-1': 'dualstack.xueshi-station-1-755376809.eu-west-1.elb'
                            '.amazonaws.com',
        'xueshi-station-2': 'dualstack.xueshi-station-2-1872136534.us-east-1'
                            '.elb.amazonaws.com'
    }
}

elb_bucket = dict(cfg.items('ELBBucket'))
for k, v in elb_bucket.iteritems():
    station_metadata_map['s3_bucket'].update({k: v})

ips = dict()
section = 'IPs'
options = cfg.options(section)
for option in options:
    try:
        ips[option] = cfg.get(section, option)
        if ips[option] == -1:
            print_message("skip: %s" % option)
    except:
        print("exception on %s!" % option)
        ips[option] = None

for k, v in ips.iteritems():
    station_metadata_map['ip'].update({k: v})
print ips

# in_bandwidth = get_config_value('InBandwidths', station)
in_bandwidth = dict(cfg.items('InBandwidths'))
for k, v in in_bandwidth.iteritems():
    station_metadata_map['in_bandwidths'].update({k: v})

# out_bandwidth = get_config_value('OutBandwidths', station)
out_bandwidth = dict(cfg.items('OutBandwidths'))
for k, v in out_bandwidth.iteritems():
    station_metadata_map['out_bandwidths'].update({k: v})

# print station_metadata_map

# if __name__ == '__main__':
#     results = get_stations_bandwidth('ap_south_1_client_1')
#     print results
