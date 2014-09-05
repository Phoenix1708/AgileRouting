from __future__ import division
import logging
import os
import threading
import time
import urllib
import math

from datetime import datetime, timedelta
import paramiko

from etc.configuration import cfg
from utilities.exception import GeneralError
from utilities.request_headers import HEADER_PREFIX_KEY, \
    HeaderInfoMap


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


def get_available_stations():
    # TODO: needs to be dynamic in the future
    return ['xueshi-station-1', 'xueshi-station-2']


def get_available_clients():
    # TODO: needs to be dynamic in the future
    # return ['ap_south_1_client_1', 'us_east_1_client_1']
    return ['ap_south_1_client_1', 'us_west_1_client_1']


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

    logging_time = cfg.get_int('s3', 'log_emitting_time', 5)
    expected_logs_to_obtain = math.floor(measurement_interval / logging_time)

    return expected_logs_to_obtain


def get_next_nth_elb_log_time(n, last_expected_time):
    """
    Get the next minutes e.g 5 or 10 or 15 that the S3 will emit ELB access
    log. It can also get the time of next nth log base on current time

    :return:
    """

    current_time = datetime.utcnow()

    print_message('Current UTC Time: %s'
                  % '-'.join([str(current_time.year),
                              str('%02d' % current_time.month),
                              str('%02d' % current_time.day),
                              str('%02d' % current_time.hour),
                              str('%02d' % current_time.minute)]))

    # [year, month, day, hour, minute] = \
    #     current_time.year, current_time.month, current_time.day, \
    #     current_time.hour, current_time.minute
    #
    # print_message('Current UTC Time: %s' % '-'.join([str(year),
    #                                                  str('%02d' % month),
    #                                                  str('%02d' % day),
    #                                                  str('%02d' % hour),
    #                                                  str('%02d' % minute)]))

    # Calculate the next expected log file emitted by S3.
    # With 5 minute logging interval, logs are emitted every 5 minutes
    # at each hour, hence the ceiling of the division of current minute
    # with 5 (minutes) should be the next expected minute at which a new
    # log will be emitted

    logging_interval = cfg.get_int('s3', 'log_emitting_time', 60)

    if not last_expected_time:
        interval_covered = math.ceil(current_time.minute / logging_interval)
        reminder = current_time.minute % logging_interval

        time_delta = \
            logging_interval * interval_covered + logging_interval * (n - 1) -\
            current_time.minute

        next_expected_time = current_time + timedelta(minutes=time_delta)

        # next_expected_minute = \
        #     logging_interval * interval_covered + logging_interval * (n - 1)

        # it the current minute is happen to be a logging time
        # i.e 5, 10, 15 etc.
        if reminder == 0:
            time_delta = n * logging_interval
            next_expected_time = current_time + timedelta(minutes=time_delta)
            # next_expected_minute = minute + n * logging_interval
    else:
        min_delta = n * logging_interval
        next_expected_time = last_expected_time + timedelta(minutes=min_delta)

        # next_expected_minute = \
        #     last_expected_minutes + n * logging_interval

        # .seconds // 60) % 60

    # (timespot - lasttime).days * 24 * 60 * 60 + (timespot - lasttime).seconds
    # 10863
    # timedelta(seconds=10863)

    if next_expected_time < current_time:
        t_delta = current_time - next_expected_time
        over_due_sec = t_delta.days * 24 * 60 * 60 + t_delta.seconds

        if over_due_sec <= logging_interval * 60:
            waiting_td = \
                next_expected_time + timedelta(seconds=logging_interval * 60) \
                - current_time

            max_waiting_time = \
                waiting_td.days * 24 * 60 * 60 + waiting_td.seconds
        else:
            max_waiting_time = 0
            print_message('[Fatal!] Waiting for too long\n'
                          'Current expected logging time %s\n'
                          'Current time: %s'
                          % (next_expected_time, current_time))

    elif next_expected_time > current_time:
        waiting_td = next_expected_time - current_time
        max_waiting_time = waiting_td.days * 24 * 60 * 60 + \
                           waiting_td.seconds + logging_interval * 60
    else:
        max_waiting_time = logging_interval * 60

    print_message('Next expected time (UTC) %s'
                  % '-'.join([str(next_expected_time.year),
                              str('%02d' % next_expected_time.month),
                              str('%02d' % next_expected_time.day),
                              str('%02d' % next_expected_time.hour),
                              str('%02d' % next_expected_time.minute)]))

    # if next_expected_logging_minute < minute:
    #     max_waiting_minutes = \
    #         60 - minute + next_expected_logging_minute + logging_interval
    # else:
    #     max_waiting_minutes = \
    #         next_expected_logging_minute - minute + logging_interval

    print_message('[Debug]: max_waiting_minutes: %s' % (max_waiting_time / 60))

    return next_expected_time, max_waiting_time
    # [year, month, day, hour, minute] = \
    #     current_time.year, current_time.month, current_time.day, \
    #     current_time.hour, current_time.minute
    #
    # return day, new_hour, month, next_expected_minute, year, \
    #        max_waiting_minutes


def calculate_waiting_time():
    # record the start time to calculate time elapsed
    # start_time = time.time()
    # get expected ELB access logs based on measurement interval
    expected_logs = get_expected_num_logs()

    # calculate the time for which the last expected access log is
    next_expected_time, max_waiting_time \
        = get_next_nth_elb_log_time(expected_logs, None)

    # year, month, day, hour, minute = next_expected_time.year, \
    #                                  next_expected_time.month, \
    #                                  next_expected_time.day, \
    #                                  next_expected_time.hour, \
    #                                  next_expected_time.minute

    # day, hour, month, next_expected_logging_minute, year, max_waiting_minutes \
    #     = get_next_nth_elb_log_time(expected_logs, None)

    # # from UTC to GMT hour + 1
    # time_str = ''.join([str(year), str(month), str(day), str(hour + 1),
    #                     str(int(minute))])
    # date = datetime.strptime("".join(time_str), '%Y%m%d%H%M')
    # date_milli = time.mktime(date.timetuple()) + date.microsecond
    # # calculate waiting time
    # waiting_time = (date_milli - start_time)
    waiting_time = max_waiting_time
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


def make_qualified(value):
    """
    Ensure domain names end with "." character, which makes a domain
    fully qualified.
    """
    if type(value) in [list, tuple, set]:
        new_list = []
        for record in value:
            if record and not record[-1] == '.':
                new_list.append("%s." % record)
            else:
                new_list.append(record)
        return new_list
    else:
        value = value.strip()
        if value and not value[-1] == '.':
            value = "%s." % value
        return value


def get_utf8_value(value):
    if not isinstance(value, basestring):
        value = str(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value


def find_matching_headers(name, headers):

    return [h for h in headers if h.lower() == name.lower()]


def unquote_v(nv):
    if len(nv) == 1:
        return nv
    else:
        return nv[0], urllib.unquote(nv[1])


def s3_canonical_string(method, path, headers):

    """
    Generates the S3 canonical string for signing request
    """
    interesting_headers = {}
    for key in headers:
        lk = key.lower()
        if headers[key] is not None and \
                (lk in ['content-md5', 'content-type', 'date'] or
                     lk.startswith(HeaderInfoMap[HEADER_PREFIX_KEY])):
            interesting_headers[lk] = str(headers[key]).strip()

    if 'content-type' not in interesting_headers:
        interesting_headers['content-type'] = ''
    if 'content-md5' not in interesting_headers:
        interesting_headers['content-md5'] = ''

    sorted_header_keys = sorted(interesting_headers.keys())

    buf = "%s\n" % method
    for key in sorted_header_keys:
        val = interesting_headers[key]
        if key.startswith(HeaderInfoMap[HEADER_PREFIX_KEY]):
            buf += "%s:%s\n" % (key, val)
        else:
            buf += "%s\n" % val

    # remove query parameters
    # http://docs.aws.amazon.com/AmazonS3/latest/dev/
    # RESTAuthentication.html#ConstructingTheCanonicalizedResourceElement
    t = path.split('?')
    buf += t[0]

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

in_bandwidth = dict(cfg.items('InBandwidths'))
for k, v in in_bandwidth.iteritems():
    station_metadata_map['in_bandwidths'].update({k: v})

out_bandwidth = dict(cfg.items('OutBandwidths'))
for k, v in out_bandwidth.iteritems():
    station_metadata_map['out_bandwidths'].update({k: v})
