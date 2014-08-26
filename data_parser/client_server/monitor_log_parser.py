import os
import time

import numpy

import Resources
from data_parser.client_server.data_generation import generate_data
from etc.configuration import cfg
from utilities.utils import sync_files, print_message


def parse_monitor_log(input_files_dir, line_counter):
    if not input_files_dir:
        print 'Please supply the directory that contains observer results'
        return

    original_file_dir = input_files_dir
    parsed_file_dir = original_file_dir + "parsed_results/"

    if not os.path.exists(parsed_file_dir):
        os.makedirs(parsed_file_dir)

    # get time to store current reading
    current_time = time.strftime("%Y_%m%d_%H%M")

    files = [f for f in os.listdir(original_file_dir)
             if f.startswith('observer_log')]

    # for i in xrange(len(files)):
    file_name = files[0]
    sub_folder_name = '%s/%s/' % (file_name[0: file_name.rfind('.')],
                                  current_time)

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
    # need_to_skip_to_the_next = False

    # debug
    file_path = os.path.abspath(original_file_dir + '/' + file_name)

    with open(file_path) as test_f:
        print_message('File length: %s' % (len(test_f.readlines())))
        print_message('Line counter %s\n' % line_counter)

    # counter for number of skip due to incorrect format of some
    # csparql log entries
    skip_counter = 0

    # counter to skip to the last
    with open(file_path) as f:

        # count = 0  # counter for skip to the line left over last time
        # while count < line_counter:
        # try:
        # f.next()
        # except StopIteration as e:
        # # print 'StopIteration\n' + str(e.message)
        # count += 1
        #     count += 1

        # current_line = 1  # default to 1 to enable the while loop

        count = 0  # counter for skip to the line left over last time
        if line_counter != 0:
            for current_line in f:
                if count == int(line_counter):
                    break
                count += 1

        # Skip to the line after ObserverReceivedTimestamp
        for current_line in f:
            line_counter += 1
            line_segments = current_line.split("\t")
            if len(line_segments) < 3:
                continue
            if 'ObserverReceivedTimesampt' in line_segments[1]:
                break

        # The csparql log sometimes contain entries with "MonitorDatum"
        # entries mixed up, hence we explicitly set the program to expect
        # metrics in the expected order and skip those mixed entries
        # since it is way to difficult to parse it for external program
        # like this one and it is actually the job of the csparql
        # observer to print metrics in a consistent format which on the
        # other hand is the efficient fix of this issue
        expected_properties = ['isAbout', 'isProducedBy',
                               'hasMonitoredMetric', 'hasValue',
                               'hasTimeStamp']
        expected_prop_counter = 0  # counter to keep track of order of
        # expected properties encountered

        for current_line in f:
            line_counter += 1

            # parse current line of the file
            # current_line = f.readline()
            # line_counter += 1

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

            # Check the metric property is currently expected and the
            # metric id is the same one as the one that we'd been
            # reading other expected properties for

            # If the property is not expected skip to next bundle of metric
            # i.e next 'isAbout'. OR if it is expected but the metric ID
            # is not the same as other metric property we've been reading
            #  for the current metric ID we skip as well. Except
            # that when expecting 'isAbout' i.e the first property,
            # we don't check for metric ID, since it could be a new metric
            if metric_prop != expected_properties[expected_prop_counter] or \
               (expected_prop_counter != 0 and metric_id != last_metric_id):
                # Skip to the next 'isAbout' line
                expected_prop_counter = 0  # expecting the 'isAbout'
                skip_counter += 1
                continue

            # if the metric property is expected then expect the next one
            if expected_prop_counter == len(expected_properties) - 1:
                expected_prop_counter = 0
            else:
                expected_prop_counter += 1

            # save reading of last metric since following reading
            # will be of a new metric id
            if last_metric_id != metric_id:
                # check whether any of the 4 properties :
                # vm_id, metric name, metric value, timestamp
                # is none, which means that the very end of the file
                # has one record that is only partially written, hence
                # ignore this record

                # if vm_id and metric_name and metric_value and timestamps:

                result_dir_path = parsed_file_dir + sub_folder_name + vm_id

                if not os.path.exists(result_dir_path):
                    os.makedirs(result_dir_path)

                result_file_path = result_dir_path + '/' + metric_name + '.txt'

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

                # record the position left over
                # line_counter = f.tell()

    print_message('[Debug] Skipped: %s' % skip_counter)

    return parsed_file_dir + sub_folder_name, line_counter


def calculate_total_requests(data):
    requests = 0
    for i in xrange(len(data[2])):
        requests += len(data[2][i])
    return requests


def calculate_metrics(data_list):
    """
    Function to calculate metrics needed for optimisation.

    What needs to be calculated:
    1. The total number of requests
    2. Requests arrival rate of the station (lambda)
    3. Service Rate of the station (mu)

    :param data_list:   list of data for each server in current service station
    :param total_users: Total number of users served by this station
    :return:            tuple of metric (total_request, lambda, mu)
    """
    # total_requests = 0
    # overall_service_rate = 0
    #
    # for data in data_list:
    # for i in xrange(len(data[2])):
    # total_requests += len(data[2][i])

    # calculate overall arrival rates
    # the length of data[0][0] is the number of sampling time

    # avg_arrival_rate = []  # list that stores the average arrival rate
    # # of each server
    # for data in data_list:
    # arrival_rates_list = []  # list that stores the average arrival
    # # rate of each sampling interval for
    #                              # a single server
    #
    #     # sum the arrival rate for each request at the same sampling interval
    #     for i in xrange(len(data[0][0])):
    #         one_sampling_interval = 0
    #         for j in xrange(len(data[2]) - 1):
    #             one_sampling_interval += data[7][j][i]
    #
    #         # store overall arrival rate of each sampling interval
    #         # in order to estimate service rate with CPU utilisation
    #         # which is also collected during each sampling interval
    #         arrival_rates_list.append(one_sampling_interval)
    #
    #     # estimate service rate regression
    #     cpu_utils = data[1][len(data[1])-1]
    #
    #     print_message('Arrival rates: %s' % arrival_rates_list)
    #     print_message('CPU utils: %s' % cpu_utils)
    #
    #     # FIXME: hard to estimate when the amount of data is small
    #
    #     slope, intercept, r_value, p_value, std_err = \
    #         stats.linregress(arrival_rates_list, cpu_utils)
    #
    #     service_rate = math.pow(slope, -1)
    #     print_message('Service_rate: %s' % service_rate)
    #
    #     # collect average arrival rate of each sever
    #     # for overall arrival rate calculation
    #     avg_arrival_rate.append(numpy.mean(arrival_rates_list))
    #
    #     # The overall service rate of the service station is the
    #     # sum of server rate of each server, since both servers are
    #     # serving requests simultaneously
    #     overall_service_rate += service_rate
    #
    # # For the similar reason, the arrival rate is the sum of arrival rate of
    # # all servers in the service station.
    # arrival_rate = sum(avg_arrival_rate)

    # "vm, number of requests, cpu_core, data" dict list
    service_rate_para_list = []
    # list that stores the average arrival rate of each server
    avg_server_arrival_rate = []

    # collecting relative parameters
    for vm_data in data_list:
        vm_name = vm_data[0]
        data = vm_data[1]

        arrivals_list = []  # list that stores the average arrival
        # rate of "each sampling interval" for
        # a single server

        # sum the arrival rate for each request at the same sampling interval
        for i in xrange(len(data[0][0])):
            sampling_interval_arrivals = 0
            for j in xrange(len(data[2]) - 1):
                sampling_interval_arrivals += data[7][j][i]

            # store overall arrival rate of each sampling interval
            # in order to estimate service rate with CPU utilisation
            # which is also collected during each sampling interval
            arrivals_list.append(sampling_interval_arrivals)

        # Mean of arrivals of all sampling intervals is the arrival rate
        # the unit time of which is the sampling interval (in this case it is
        #  1 minutes
        avg_server_arrival_rate.append(numpy.mean(arrivals_list))

        # calculate service rate
        num_of_requests = calculate_total_requests(data)
        para_tuple = {'vm_name': vm_name, 'num_of_requests': num_of_requests,
                      'data': data}

        vm_cpu_spec = dict(cfg.items('VMSpec'))
        cpu_core = [vm_cpu_spec[spec] for spec in vm_cpu_spec.keys()
                    if spec in vm_name]

        # cpu_core = cfg.get('VMSpec', vm_name)
        if not cpu_core:
            print 'No specification configured for VM \'%s\'' % vm_name
            return

        print_message('Number of CPUs of \'%s\': %s' % (vm_name, cpu_core))

        para_tuple.update({'cpu_cores': cpu_core})

        service_rate_para_list.append(para_tuple)

    # calculate total number of requests
    total_requests = sum([p['num_of_requests'] for p in service_rate_para_list])

    station_arrival_rate = sum(avg_server_arrival_rate)

    return total_requests, station_arrival_rate, service_rate_para_list
    # , overall_service_rate


def process_monitor_log(base_dir, observer_addr, line_counter, queue):
    """Parse the monitor log and calculate various metric for all servers in
    the service station monitored by the observer

    :param base_dir:        Base directory of monitor log
    :param observer_addr:   Service station name and observer ips pair
    :param line_counter:    Counter for continuously reading the single log file

    :param queue:           Queue that store metrics needed for optimisation
                            generated by current thread
    """

    station_name, observer_ip = observer_addr.split('=')

    # every thread store data in separate folder
    base_dir = base_dir + station_name + '/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    monitor_log_path = base_dir + 'observer_log.txt'

    # Flag indicates whether the logs of all servers contain useful data or not
    all_has_info = False

    while not all_has_info:

        print_message('')
        print_message('Synchronising log from observer at: %s' % observer_ip)

        module_path = os.path.dirname(Resources.__file__)
        private_key_file_path = module_path + '/ec2_private_key'

        sync_files(host_ip=observer_ip, username='ubuntu',
                   host_file_path='~/results.txt',
                   pk_path=private_key_file_path, dst_loc=monitor_log_path)

        parsed_log_dir, line_counter = parse_monitor_log(base_dir,
                                                         int(line_counter))
        result_queue = generate_data(parsed_log_dir)

        # observer log has contain ResponseInfo if the queue if not empty

        # check all server has response info
        # TODO: the number of server can be read from config
        if result_queue.qsize() > 1:
            all_has_info = True
        else:
            time.sleep(5)

    data_list = []
    while not result_queue.empty():
        server_data = result_queue.get()
        data_list.append(server_data)

    total_requests, arrival_rate, service_rate_para_list \
        = calculate_metrics(data_list)

    result_dict = {'station_name': station_name,
                   'total_requests': total_requests,
                   'arrival_rate': arrival_rate,
                   'service_rate_para_list': service_rate_para_list,
                   'line_counter': line_counter}

    queue.put(result_dict)


    # if __name__ == '__main__':
    # parse_monitor_log('logs/2014_0817_1556', 0)
    # # for i in xrange(len(sys.argv)):
    # # print sys.argv[i]
    # # process_monitor_log(sys.argv[1], 0)
    #     print 'done'