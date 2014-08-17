import os
from time import strptime, mktime
import time
import numpy
from scipy import stats

from data_parser.client_server.data_formation import format_data
from utilities.multi_threading import ThreadingManager
from utilities.utils import print_message


def update_data_array(data, x, y, value):
    """
    :param data: the data matrix (mimic cell matrix in matlab)
    :param x: row index
    :param y: column index
    :param value: the value to store in cell matrix
    :return: the updated cell matrix
    """
    # fill up the gap in each dimension
    if len(data) < x + 1 or len(data) == 0:
        for i in range(x + 1 - len(data)):
            data.append([])
    if len(data[x]) < y + 1 or len(data[x]) == 0:
        for i in range(y + 1 - len(data[x])):
            data[x].append([])

    if not value:
        data[x][y] = value
    else:
        data[x][y].append(value)

    return data


def _generate_data(base_path, queue):
    response_file = base_path + '/ResponseInfo.txt'
    cpu_file = base_path + '/CPUUtil.txt'
    # cell(6,2);
    data = [[] for j in range(7)]
    category_map = dict()  # containers.Map;
    category_index = 0
    category_count = 0
    category_list = []
    count = 0

    # No ResponseInfo available in observer log yet
    if not os.path.exists(response_file):
        print_message('%s not exists yet\n' % response_file)
        return

    with open(response_file) as f:
        line = f.readline()
        while line:

            # skip odd line
            if count % 2 != 0:
                line = f.readline()
                count += 1
                continue

            split_str = line.split(',')

            if len(split_str) < 7:
                line = f.readline()
                count += 1
                continue

            date_str = [split_str[j] for j in xrange(7)]

            date = strptime("".join(date_str), '%Y%m%d%H%M%S%f')

            # date = None
            # # python strptime thread safety bug
            # # http://bugs.python.org/issue11108
            # while not date:
            # try:
            # date = strptime("".join(date_str), '%Y%m%d%H%M%S%f')
            #     except AttributeError as e:
            #         print "[Debug]: strptime reported AttributeError\n" + \
            #               "Details: %s" % e

            # date_milli = unix_time(datetime.fromtimestamp(mktime(date)))
            date_milli = mktime(date) * 1000
            # date_milli = calendar.timegm(date)

            # jobID = split_str[7]
            category_str = split_str[8]

            if category_str not in category_map:
                category_map[category_str] = category_index
                category_list.append(category_str)
                category_count += 1

                category = category_index

                data = update_data_array(data, 5, category, [])
                data = update_data_array(data, 6, category, [])
                # update: added the 8th row to store arrival rate
                data = update_data_array(data, 7, category, [])

                # data{6,category} = []
                # data{7,category} = []
                category_index += 1
            else:
                category = category_map[category_str]

            if split_str[9] == 'Request Begun':
                continue

            response_time = float(split_str[10])
            arrival_time = date_milli - response_time * 1000
            data = update_data_array(data, 2, category, arrival_time)
            data = update_data_array(data, 3, category, response_time)

            # data{3,category} = [data{3,
            # category};date_milli-response_time*1000];
            # data{4,category} = [data{4,category};response_time];

            line = f.readline()
            count += 1

        update_data_array(data, 2, category_index, [[]])

        # data{3, category_index} = []

        # fill in the gap between length of data and the target index
        for i in xrange(len(data)):
            for j in range(len(data[2])):
                if len(data[i]) < len(data[2]):
                    data[i].append([])

        raw_data = data

        [data, metric] = format_data(raw_data, 60000, category_list, cpu_file)

        queue.put(data)


def generate_data(logs_folder_path, num_of_vm):
    """ Generate metric data for each virtual machine monitored
        by the observer
    """

    all_dirs = [dp for dp, dn, file_names in os.walk(logs_folder_path)
                if file_names]
                # for f in file_names if os.path.splitext(f)[1] == '.txt']

    data_generators_manager = ThreadingManager()

    # python strptime thread safety bug. Has to call strptime once before
    # creating thread. Details can be found on:
    # http://bugs.python.org/issue11108
    time.strptime("30 Nov 00", "%d %b %y")

    for num in xrange(num_of_vm):
        logs_path = all_dirs[num]

        data_generators_manager.start_tasks(
            target_func=_generate_data,
            name="monitor_data_generator",
            para=[logs_path]
        )

    result_queue = data_generators_manager.collect_results()

    return result_queue


if __name__ == '__main__':
    result_queue = generate_data(
        'logs/2014_0701_1034/parsed_results/observer_results/', 2)
    data_list = []
    while not result_queue.empty():
        server_data = result_queue.get()
        data_list.append(server_data)

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

        # sum the arrival rate for each request at the same sampling interval
        for i in xrange(len(data[0][0])):
            one_sampling_interval = 0
            for j in xrange(len(data[2]) - 1):
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

    print "done"