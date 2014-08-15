import math
import os
import time
from datetime import datetime
from etc.configuration import cfg
from utilities.multi_threading import ThreadingManager

s3_logging_interval = 5  # minute

log_polling_interval = cfg.get_int('s3', 'log_polling_interval', 180)

log_file_dir = os.getcwd() + '/data_parser/s3/elb_access_logs/'


class DataAccumulatorManager(ThreadingManager):
    """
    Class that manage all thread that reading data from logs
    """

    def __init__(self):
        ThreadingManager.__init__(self)
        self.data_sum = 0
        self.total_sent = 0
        self.total_receive = 0

    @staticmethod
    def read_log(key, log_file_path, queue):

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

                received_byte = int(split_str[9])
                sent_byte = int(split_str[10])

                total_receive += received_byte
                total_sent += sent_byte

        queue.put('%s,%s' % (total_receive, total_sent))

    def collect_results(self):
        queue = super(DataAccumulatorManager, self).collect_results()
        while not queue.empty():
            sent, receive = queue.get().split(',')
            self.total_sent += sent
            self.total_receive += receive

        return '%s,%s' % (self.total_receive, self.total_sent)


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
    total_sent = 0
    total_receive = 0

    # get measurement interval from config
    m_interval = cfg.get_int('Default', 'measurement_interval', 10)
    # record the start time to calculate time elapsed
    start_time = time.time()

    # check whether the it has reached the end of measurement interval
    while (time.time() - start_time) / 60 < m_interval:

        current_time = datetime.utcnow()
        [year, month, day, hour, minute] = \
            current_time.year, current_time.month, current_time.day, \
            current_time.hour, current_time.minute

        # Calculate the next expected log file omitted by S3.
        # With 5 minute logging interval, logs are omitted every 5 minutes
        # at each hour, hence the ceiling of the division of current minute
        # with 5 (minutes) should be the next expected minute at which a new
        # log will be omitted
        next_expected_logging_minute = \
            int(s3_logging_interval * math.ceil(minute / 5))

        # The time string that the expected log file should contain
        time_str = "%s%02d%02dT%02d%02dZ" % (year, month, day, hour,
                                             next_expected_logging_minute)
        aws_account_id = str(305933725014)
        region = elb_region
        load_balancer_name = elb_name
        end_time = time_str

        """for test"""""
        year = '2014'
        month = '07'
        day = '21'
        end_time = '20140721T2210Z'
        """ end of test data """

        key_prefix = 'AWSLogs/{0}/elasticloadbalancing/{1}/{2}/{3}/{4}/{5}' \
                     '_elasticloadbalancing_{6}_{7}_{8}' \
            .format(aws_account_id, region, year, month, day,
                    aws_account_id, region, load_balancer_name, end_time)

        response_headers = {'prefix': unicode(key_prefix), 'delimiter': '.log'}

        matching_keys = None
        # Wait for polling interval while the log is not available
        while not matching_keys:
            print 'Waiting for log to be omitted...'
            matching_keys = bucket.search_key(parameters=response_headers)
            if matching_keys:
                break
            # time.sleep(log_polling_interval)

        # Start new threads for downloading and reading each matching log file
        data_accumulator_manager = DataAccumulatorManager()

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
            data_accumulator_manager.start_tasks(
                data_accumulator_manager.read_log,
                'data_accumulator', (key, log_file_path))

        # Collect results from each threads
        sent, receive = data_accumulator_manager.collect_results().split(',')
        total_sent += sent
        total_receive += receive

        # wait for 2 minute before another poll
        time.sleep(120)

    return '%s,%s' % (total_receive, total_sent)