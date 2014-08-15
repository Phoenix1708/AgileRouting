import os

import numpy
from scipy import stats

from data_parser.client_server.data_generation import generate_data

from utilities.utils import sync_files


def parse_monitor_log(input_files_dir, line_counter):
    if not input_files_dir:
        print 'Please supply the directory that contains observer results'
        return

    original_file_dir = input_files_dir
    parsed_file_dir = original_file_dir + "/parsed_results/"

    if not os.path.exists(parsed_file_dir):
        os.makedirs(parsed_file_dir)

    files = [f for f in os.listdir(original_file_dir)
             if f.startswith('logs')]

    for i in xrange(len(files)):
        file_name = files[i]
        sub_folder_name = file_name[0: file_name.rfind('.')]

        if not os.path.exists(sub_folder_name):
            os.makedirs(sub_folder_name)

        metric_name = None

        # keep track of last metric id
        # in order to save reading of last metric when
        # encounter new metric
        last_metric_id = None

        metric_value = None
        timestamps = None
        vm_id = None

        # In case the file begin with half of one record, use a flag to
        # indicate the next 'first line' of one record
        # e.g.
        # "f707d0a3-c7a3-4664-b74a-1fc7bcd5d7db	ObserverReceivedTimesampt
        # 1406112134817"
        # Then we can start reading data from this line afterwards
        need_to_skip_to_the_next = False

        # counter to skip to the last
        with open(os.path.abspath(original_file_dir + '/' + file_name)) as f:
            # with open(original_file_dir+'/'+file_name) as f:

            count = 0  # counter for skip to the line left over last time
            while count < line_counter:
                f.next()
                count += 1

            current_line = 1  # default to 1 to enable the while loop

            # skip to the line after ObserverReceivedTimestamp
            while not need_to_skip_to_the_next:
                current_line = f.readline()
                line_segments = current_line.split("\t")
                if len(line_segments) < 3:
                    continue

                if 'ObserverReceivedTimesampt' not in line_segments[1]:
                    continue
                else:
                    need_to_skip_to_the_next = True

            while current_line:
                # parse current line of the file
                current_line = f.readline()
                line_counter += 1
                # [metric_id, metric_prop, value, dump]
                # = current_line.split("\t")
                line_segments = current_line.split("\t")
                if len(line_segments) < 3:
                    continue

                metric_id = line_segments[0]
                metric_prop = line_segments[1]
                value = line_segments[2]

                # if the line is not about metric continue to read next line
                if 'MonitoringDatum' not in metric_id:
                    continue

                # For the first time
                if not last_metric_id:
                    last_metric_id = metric_id
                # save reading of last metric since following reading
                # will be of a new metric id
                elif last_metric_id != metric_id:
                    # check wether any of the 4 properties :
                    # vm_id, metric name, metric value, timestamp
                    # is none, which means that the very end of the file
                    # has one record that is only partially written, hence
                    # ignore this record
                    if not vm_id or not metric_name or not metric_value \
                       or not timestamps:
                        continue

                    result_dir_path = parsed_file_dir + sub_folder_name + \
                                      '/' + vm_id
                    if not os.path.exists(result_dir_path):
                        os.makedirs(result_dir_path)

                    result_file_path = result_dir_path + '/' + \
                                       metric_name + '.txt'
                    with open(result_file_path, 'a') as parsed_f:
                        parsed_f.write(metric_value + '\n')
                        parsed_f.write(timestamps + '\n')

                    # current metric become the last after finish
                    # processing its value
                    last_metric_id = metric_id

                if metric_prop == "isAbout":
                    vm_id = value.replace("Compute#", "")
                elif metric_prop == "hasMonitoredMetric":
                    metric_name = value.replace("QoSMetric#", "")
                elif metric_prop == "hasValue":
                    metric_value = value
                elif metric_prop == "hasTimeStamp":
                    timestamps = value

    return parsed_file_dir + 'logs/', line_counter


def calculate_metrics(data_list):
    """
    Function to calculate metrics needed for optimisation.

    What needs to be calculated:
    1. The total number of requests
    2. Requests arrival rate of the station (lambda)
    3. Service Rate of the station (mu)

    :param data_list:  list of data for each server in current service station
    :return:           tuple of metric (total_request, lambda, mu)
    """
    total_requests = 0
    service_rate = 0

    for data in data_list:
        for i in xrange(len(data[2])):
            total_requests += len(data[2][i])

    # calculate overall arrival rates
    # the length of data[0][0] is the number of sampling time

    avg_arrival_rate = []  # list that stores the average arrival rate
                           # of each server
    for data in data_list:
        avg_arrival_rates_list = []  # list that stores the average arrival
                                     # rate of each sampling interval for
                                     # a single server

        for i in xrange(len(data[0][0])):
            one_sampling_interval = 0
            for j in xrange(len(data[2])):
                one_sampling_interval += data[7][j][i]

            # store overall arrival rate of each sampling interval
            # in order to estimate service rate with CPU utilisation
            # which is also collected during each sampling interval
            avg_arrival_rates_list.append(one_sampling_interval)

        # collect average arrival rate of each sever
        # for overall arrival rate calculation
        avg_arrival_rate.append(numpy.mean(avg_arrival_rates_list))

        # estimate service rate regression
        cpu_utils = data[1][len(data[1])-1]

        slope, intercept, r_value, p_value, std_err = \
            stats.linregress(avg_arrival_rates_list, cpu_utils)

        # The overall service rate of the service station is the
        # sum of server rate of each server, since both servers are
        # serving requests simultaneously
        service_rate += slope

    # For the similar reason, the arrival rate is the sum of arrival rate of
    # all servers in the service station.
    arrival_rate = sum(avg_arrival_rate)

    return total_requests, arrival_rate, service_rate


def process_monitor_log(base_dir, observer_addr, line_counter, queue):
    """Parse the monitor log and calculate various metric for all servers in
    the service station monitored by the observer

    :param base_dir:
    :param observer_addr:
    :param line_counter:
    :param queue:
    :return: tuple of metrics needed for optimisation
    """

    monitor_log_path = base_dir + 'observer_log.txt'

    station_name, observer_ip = observer_addr.split('=')

    sync_files(host_ip=observer_ip, username='ubuntu',
               host_file_path=':~/results.txt',
               pk_path='logs/ec2_private_key', dst_loc=monitor_log_path)

    parsed_log_dir, line_counter = parse_monitor_log(monitor_log_path,
                                                     line_counter)

    result_queue = generate_data(parsed_log_dir, 2)

    data_list = []
    while not result_queue.empty():
        server_data = result_queue.get()
        data_list.append(server_data)

    metrics_tuple = calculate_metrics(data_list)

    queue.put('%s,%s,%s' % (station_name, metrics_tuple, line_counter))


# if __name__ == '__main__':
#     # parse_monitor_log('2014_0701_1034')
#     # for i in xrange(len(sys.argv)):
#     # print sys.argv[i]
#     process_monitor_log(sys.argv[1], 0)