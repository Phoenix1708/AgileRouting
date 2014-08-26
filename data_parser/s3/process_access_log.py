from __future__ import division
import os
import time

from connection.s3_connection import S3Connection
from etc.configuration import cfg
from utilities.multi_threading import ThreadingManager
from utilities.utils import print_message, get_expected_num_logs, \
    get_next_nth_elb_log_time, get_available_clients, station_metadata_map


log_polling_interval = cfg.get_int('s3', 'log_polling_interval', 60)

log_file_dir = os.getcwd() + '/data_parser/s3/elb_access_logs/'


class DataAccumulatorManager(ThreadingManager):
    """
    Class that manage all thread that reading data from logs
    """

    def __init__(self):
        ThreadingManager.__init__(self)
        self.data_sum = 0
        self.client_sent = dict()
        self.client_receive = dict()
        self.available_client = get_available_clients()

        self.client_ips_name_pair = dict()
        for client_name in self.available_client:
            self.client_ips_name_pair.update(
                {station_metadata_map['ip'][client_name]: client_name})
            # initialisation
            self.client_sent.update({client_name: 0})
            self.client_receive.update({client_name: 0})

        self.total_sent = 0
        self.total_receive = 0

    def read_log(self, key, log_file_path, queue):

        client_in_dict = dict()
        client_out_dict = dict()

        for client_name in self.available_client:
            self.client_ips_name_pair.update(
                {station_metadata_map['ip'][client_name]: client_name})
            # initialisation
            client_in_dict.update({client_name: 0})
            client_out_dict.update({client_name: 0})

        # download the log content
        with open(log_file_path, 'w') as fp:
            key.get_contents_to_file(fp)

        # read log content
        total_sent = 0
        total_receive = 0
        with open(log_file_path, 'r') as lf:
            line = 1  # enable the loop
            while line:
                line = lf.readline()
                # example log entry (no line break):
                # 2014-02-15T23:39:43.945958Z my-test-loadbalancer
                # 192.168.131.39:2817 10.0.0.0.1 0.000073 0.001048 0.000057
                # 200 200 0 29 "GET http://www.example.com:80/HTTP/1.1"

                split_str = line.split(' ')

                if len(split_str) < 11:
                    continue

                # ip -> name -> record data for each name
                client_ip = split_str[2].split(":")[0]
                # occasionally we got ip not from any clients
                # Suspicious...
                if client_ip not in self.client_ips_name_pair.keys():
                    continue

                c_name = self.client_ips_name_pair[client_ip]

                received_byte = int(split_str[9])
                sent_byte = int(split_str[10])

                client_in_dict[c_name] += received_byte
                client_out_dict[c_name] += sent_byte

                total_receive += received_byte
                total_sent += sent_byte

        queue.put((client_in_dict, client_out_dict))
        # queue.put('%s,%s' % (total_receive, total_sent))

    def collect_results(self):
        queue = super(DataAccumulatorManager, self).collect_results()
        while not queue.empty():
            c_sent, c_receive = queue.get()

            for c_name, data_sent in c_sent.iteritems():
                self.client_sent[c_name] += data_sent

            for c_name, data_received in c_receive.iteritems():
                self.client_receive[c_name] += data_received

            # self.total_sent += int(sent)
            # self.total_receive += int(receive)

        # return '%s,%s' % (self.total_receive, self.total_sent)


def calculate_key_prefix(elb_region, elb_name, last_expected_minutes):
    """Function that calculate the prefix for bucket key searching

    :param elb_region:
    :param elb_name:
    :return:
    """
    print_message('Retrieving access log for %s ...' % elb_name)

    day, hour, month, next_expected_logging_minute, year, max_waiting_minutes\
        = get_next_nth_elb_log_time(1, last_expected_minutes)

    last_expected_minutes = next_expected_logging_minute

    # convert month, day, hour and minute to 2 digit representation
    month = '%02d' % month
    day = '%02d' % day
    hour = '%02d' % hour
    next_expected_logging_minute = '%02d' % next_expected_logging_minute
    # The time string that the expected log file should contain
    time_str = "%s%s%sT%s%sZ" % (year, month, day, hour,
                                 next_expected_logging_minute)

    aws_account_id = str(305933725014)
    region = elb_region
    load_balancer_name = elb_name
    end_time = time_str

    # """for test"""""
    # year = '2014'
    # month = '07'
    # day = '21'
    # end_time = '20140721T2210Z'
    # """ end of test data """

    key_prefix = 'AWSLogs/{0}/elasticloadbalancing/{1}/{2}/{3}/{4}/{5}' \
                 '_elasticloadbalancing_{6}_{7}_{8}' \
        .format(aws_account_id, region, year, month, day,
                aws_account_id, region, load_balancer_name, end_time)

    request_headers = {'prefix': unicode(key_prefix), 'delimiter': '.log'}

    return request_headers, max_waiting_minutes, last_expected_minutes


def process_access_log(bucket, elb_region, elb_name):
    """
    function that retrieve access logs of ELB that stored in S3 buckets and
    calculate the total amount of data processed by the ELB

    log file format

    {Bucket}/{Prefix}/AWSLogs/{AWS AccountID}/elasticloadbalancing/{Region}/
    {Year}/{Month}/{Day}/{AWS Account ID}_elasticloadbalancing_{Region}_
    {Load Balancer Name}_{End Time}_{Load Balancer IP}_{Random String}.log

    :param bucket: the  S3 buckets that stores the access log of ELB
    :param elb_region:  region of the elastic load balancer of which
                        access logs are being retrieved
    :param elb_name:    name of the elastic load balancer
    :return:            total amount of data being processed by the elb
                        during the measurement interval
    """

    if not bucket:
        print 'S3 bucket object required'
        return

    # total amount of data processed by the elb within the measurement interval
    # total_data = 0
    # total_sent = 0
    # total_receive = 0

    # client_in_dict = dict()
    # client_out_dict = dict()
    #
    # available_client = get_available_clients()
    #
    # client_ips_name_pair = dict()
    # for client_name in available_client:
    #     client_ips_name_pair.update(
    #         {station_metadata_map['ip'][client_name]: client_name})
    #     # initialisation
    #     client_in_dict.update({client_name: 0})
    #     client_out_dict.update({client_name: 0})

    # Start new threads for downloading and reading each matching log file
    data_accumulator = DataAccumulatorManager()

    # record the start time to calculate time elapsed
    # start_time = time.time()

    # Since the actually log omission time varies we determine the time stop
    # waiting for log by the number of logs retrieved. Each log represents
    # elb access of either 5 minutes or 1 hour

    # Counter for the number of log obtained.
    logs_obtained = 0
    expected_logs_to_obtain = get_expected_num_logs()

    # maintain the last log omitting minutes that dealt with
    last_expected_minutes = None

    # check whether the it has reached the end of measurement interval
    # while (time.time() - start_time) / 60 <= m_interval:
    while logs_obtained < expected_logs_to_obtain:

        request_headers, max_waiting_minutes, last_expected_minutes \
            = calculate_key_prefix(elb_region, elb_name, last_expected_minutes)

        matching_keys = []
        # In case of total waiting time exceed the S3
        # logging interval (e.g 5 min) we need to recalculate the next
        # expected log name
        time_counter = 0
        # Wait for polling interval while the log is not available
        while not matching_keys or len(matching_keys) < 2:

            print_message('')
            print_message('Searching for bucket key(s) that start with: %s'
                          % request_headers['prefix'])
            matching_keys = bucket.search_key(parameters=request_headers)

            if matching_keys:
                for m_key in matching_keys:
                    print_message('Found %s' % m_key)
                if len(matching_keys) > 1:
                    break

            print_message('Time elapsed since current searching: %s min(s)'
                          % (time_counter / 60))

            # Check whether we need to wait for new log.
            # There could be up to 5 mins delay for actual log delivery
            # http://docs.aws.amazon.com/ElasticLoadBalancing/latest/
            # DeveloperGuide/access-log-collection.html
            # The next expected minus should be re calculated base on its
            # last value i.e the last "next expected minus"
            if time_counter / 60 > max_waiting_minutes:
                print_message('')
                print_message('Re-calculating expected log file...')
                request_headers, max_waiting_minutes, last_expected_minutes \
                    = calculate_key_prefix(elb_region, elb_name,
                                           last_expected_minutes)
                time_counter = 0
                continue

            print_message('Waiting for log to be omitted (polling interval %s '
                          'seconds) ...\n' % log_polling_interval)

            time.sleep(log_polling_interval)
            time_counter += log_polling_interval

        for key_name in matching_keys:
            key = bucket.get_key(key_name=key_name)

            # compose log file directory
            segment = key_name.split('/')
            log_file_name = segment[len(segment) - 1]
            log_file_path_dir = log_file_dir + bucket.name

            if not os.path.exists(log_file_path_dir):
                os.makedirs(log_file_path_dir)

            log_file_path = log_file_path_dir + '/' + log_file_name

            # download and process the each log file simultaneously
            data_accumulator.start_tasks(data_accumulator.read_log,
                                         'data_accumulator',
                                         (key, log_file_path))

        # Collect results from each threads
        data_accumulator.collect_results()

        # sent, receive = data_accumulator_manager.collect_results().split(',')
        #
        # total_sent += int(sent)
        # total_receive += int(receive)

        print_message('Total amount of data (bytes) received by \'%s\' from '
                      'clients so far: %s'
                      % (elb_name, data_accumulator.client_sent))
        print_message('Total amount of data (bytes) sent by \'%s\' to '
                      'clients so far: %s'
                      % (elb_name, data_accumulator.client_receive))

        # debug
        # print_message('Total amount of data (bytes) received by \'%s\' so far '
        #               ': %s' % (elb_name, total_receive))
        # print_message('Total amount of data (bytes) sent by \'%s\' so far '
        #               ': %s' % (elb_name, total_sent))

        # wait for 2 minute before another poll
        # time.sleep(120)
        logs_obtained += 1
        print_message('Access log of \'%s\' obtained so far : %s\n'
                      % (elb_name, logs_obtained))

    return data_accumulator.client_sent, data_accumulator.client_receive
    # return '%s,%s' % (total_receive, total_sent)


def counting_elb_data(bucket, elb, queue):
    """ S3 log processing thread content.

    :param bucket:      The bucket that stores access log
    :param elb          String representation of Elastic load balancer name
                        and region (elb_name:elb_region)
    :param queue:       A queue to store result for each buckets
    :return:            String representation of the total amount of data
                        processed by elb
    """

    elb_name, elb_region = elb.split(':')
    results = process_access_log(bucket, elb_region, elb_name)

    clients_sent, client_received = results

    # convert bucket name and total amount of data to string
    # so that the element in queue can have bucket name info
    data_tuple = (elb_name, (clients_sent, client_received))
    queue.put(data_tuple)


def process_elb_access_log(elb_buckets_dict, elb_data_manager, queue):
    """
    Primarily handle S3 log processing threads

    :param elb_buckets_dict:
    :param elb_data_manager:
    :param queue:
    :return:
    """

    for elb_region_str, bucket_name in elb_buckets_dict.iteritems():
        c = S3Connection()
        bucket = c.get_bucket(bucket_name)

        elb_data_manager.start_tasks(
            target_func=counting_elb_data,
            name="elb_data_collector",
            para=[bucket, elb_region_str]
        )

    # waiting for all threads to finish parsing S3 log
    # by which time it will be the end of measurement interval
    result_queue = elb_data_manager.collect_results()
    # collect the total data processed by each ELB
    data_in = dict()
    data_out = dict()

    while not result_queue.empty():
        data_tuple = result_queue.get()
        station = data_tuple[0]
        # the amount of data sent and received by each client
        # *of ONE station
        client_sent, client_received = data_tuple[1]

        data_in.update({station: client_sent})
        data_out.update({station: client_received})

    # debug
    print_message('Data in (bytes) from clients: %s' % data_in)
    print_message('Data out (bytes) from clients: %s' % data_out)

    queue.put((data_in, data_out))