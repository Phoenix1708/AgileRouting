from __future__ import division
import os
from time import mktime
import time

from datetime import datetime

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

            date = datetime.strptime("".join(date_str), '%Y%m%d%H%M%S%f')

            # date = None
            # # python strptime thread safety bug
            # # http://bugs.python.org/issue11108
            # while not date:
            # try:
            # date = strptime("".join(date_str), '%Y%m%d%H%M%S%f')
            # except AttributeError as e:
            # print "[Debug]: strptime reported AttributeError\n" + \
            # "Details: %s" % e

            date_milli = mktime(date.timetuple())*1e3 + date.microsecond/1e3

            category_str = split_str[8]

            if category_str not in category_map:
                category_map[category_str] = category_index
                category_list.append(category_str)
                category_count += 1

                category = category_index

                data = update_data_array(data, 5, category, [])
                data = update_data_array(data, 6, category, [])
                data = update_data_array(data, 7, category, [])

                category_index += 1
            else:
                category = category_map[category_str]

            if split_str[9] == 'Request Begun':
                continue

            response_time = float(split_str[10])
            arrival_time = date_milli - response_time * 1000
            data = update_data_array(data, 2, category, arrival_time)
            data = update_data_array(data, 3, category, response_time)

            line = f.readline()
            count += 1

        update_data_array(data, 2, category_index, [[]])

        # fill in the gap between length of data and the target index
        for i in xrange(len(data)):
            for j in range(len(data[2])):
                if len(data[i]) < len(data[2]):
                    data[i].append([])

        raw_data = data

        data = format_data(raw_data, 60000, category_list, cpu_file)

        seg = base_path.split('/')
        vm_name = seg[len(seg) - 1]

        results = (vm_name, data)
        queue.put(results)


def generate_data(logs_folder_path):
    """ Generate metric data for each virtual machine monitored
        by the observer
    """

    # Get all "directories" that contains files
    all_dirs = [dp for dp, dn, file_names in os.walk(logs_folder_path)
                if file_names]

    data_generators_manager = ThreadingManager()

    # python strptime thread safety bug. Has to call strptime once before
    # creating thread. Details can be found on:
    # http://bugs.python.org/issue11108
    time.strptime("30 Nov 00", "%d %b %y")

    for num in xrange(len(all_dirs)):
        logs_path = all_dirs[num]

        data_generators_manager.start_tasks(
            target_func=_generate_data,
            name="monitor_data_generator",
            para=[logs_path]
        )

    result_queue = data_generators_manager.collect_results()

    return result_queue