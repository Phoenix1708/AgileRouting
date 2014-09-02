from __future__ import division
import math
import scipy
from utilities.utils import print_message


def remove_data(data, category_list, delete):
    if not delete:
        return data, category_list, delete

    # data(:,delete) = [];
    # category_list(:,delete) = [];
    for i in xrange(len(data)):
        # for j in delete:
        #
        # # fill in the gap between length of data and the target index
        # if len(data[i]) < j+1 or len(data[i]) == 0:
        #         for k in range(j+1 - (len(data[i]))):
        #             data[i].append([])

        # if len(data[i]) < j+1 or len(data[i]) == 0:
        #     continue

        # remove the data
        data[i] = [v[1] for v in enumerate(data[i]) if v[0] not in delete]
        # data[i].remove(data[i][j])

    category_list = [v[1] for v in enumerate(category_list)
                     if v[0] not in delete]

    # reset delete index list
    delete = []
    return data, category_list, delete


def format_data(data, period, category_list, cpu_file):
    metric_list = ['addtocartbulk', 'checkLogin', 'checkoutoptions', 'login',
                   'logout', 'main', 'orderhistory', 'quickadd']
    delete = []

    for i in xrange(len(data[2]) - 1):
        if not data[2][i]:
            delete.append(i)

    # delete data
    data, category_list, delete = remove_data(data, category_list, delete)

    # find out those metrics that are not in the metric_list
    for i in xrange(len(data[2]) - 1):
        flag = 0
        for j in range(8):
            if category_list[i] == metric_list[j]:
                flag = 1

        if flag == 0:
            delete.append(i)

    # delete data
    data, category_list, delete = remove_data(data, category_list, delete)

    start_time = min(data[2][0])
    max_time = max(data[2][0])

    for i in xrange(1, len(data[2]) - 1):
        if data[2][i] and start_time > min(data[2][i]):
            start_time = min(data[2][i])
        if data[2][i] and max_time > max(data[2][i]):
            max_time = max(data[2][i])

    samples = int(math.floor(((max_time - start_time) / period)))

    print_message('Number of samples (interval:%s) : %s' % (period, samples))

    for i in xrange(len(data[2]) - 1):
        end_time = start_time
        # last_index = -1

        # index for calculating arrival rate
        # arr_last_index = -1

        departure = [a + r * 1000 for a, r in zip(data[2][i], data[3][i])]

        # departure = []
        # for j in xrange(len(data[2][i])):
        # departure.append(data[2][i][j] + data[3][i][j] * 1000)

        for k in xrange(samples):

            index = [v[0] for v in enumerate(departure)
                     if end_time <= v[1] < (end_time + period)]

            arr_index = [v[0] for v in enumerate(data[2][i])
                         if end_time <= v[1] < (end_time + period)]

            response_times = [0]
            if index:
                response_times = [data[3][i][idx] for idx in index]
            data[4][i].append(scipy.mean(response_times))
            data[5][i].append(len(index) / period * 1000)
            data[6][i].append(len(index))
            data[7][i].append(len(arr_index))

            data[0][i].append(end_time + period)
            end_time += period

            # if no departure time beyond the end
            # time of current sampling interval
            # if len(index) < 1:
            #     # if len(data[5][i]):
            #     data[4][i].append(0)
            #     data[5][i].append(0)
            #     data[6][i].append(0)
            #     data[7][i].append(0)
            #     # break
            #
            # else:
            #     if arr_index[0] - arr_last_index - 1 == 0:
            #         data[7][i].append(0)
            #
            #     if index[0] - last_index - 1 == 0:
            #         data[4][i].append(0)
            #         data[5][i].append(0)
            #         data[6][i].append(0)
            #     else:
            #         data[4][i].append(
            #             scipy.mean(data[3][i][last_index+1:index[0]:1]))
            #         data[5][i].append((index[0] - 1 - last_index)/period*1000)
            #         data[6][i].append(index[0] - 1 - last_index)
            #         data[7][i].append(arr_index[0] - 1 - arr_last_index)
            #         last_index = index[0] - 1
            #         arr_last_index = arr_index[0] - 1
            #
            #     data[0][i].append(end_time + period)
            #     end_time += period

    # Number of samples for each request might not be equal
    max_num_requests = 0
    max_requests_idx = 0
    for i in xrange(len(data[2]) - 1):
        if max_num_requests < len(data[2][i]):
            max_num_requests = len(data[2][i])
            max_requests_idx = i

    for i in xrange(len(data[2]) - 1):
        data[0][i] = data[0][max_requests_idx]
        if len(data[4][i]) < len(data[0][i]):
            data[4][i].append([0] * (len(data[0][i]) - len(data[4][i])))
            data[5][i].append([0] * (len(data[0][i]) - len(data[5][i])))
            data[6][i].append([0] * (len(data[0][i]) - len(data[6][i])))

    data[0][len(data[0]) - 1] = data[0][0]

    with open(cpu_file) as f:
        count = 0
        cpu = []
        cpu_time = []
        flag = 0
        line = f.readline()
        while line:
            cpu_num = float(line)

            if count % 2 == 0:
                if cpu_num > 1 or math.isnan(cpu_num):
                    flag = 1
                else:
                    cpu.append(cpu_num)
            else:
                if flag:
                    flag = 0
                else:
                    cpu_time.append(cpu_num)

            count += 1
            line = f.readline()

    cpu_time = [e - 3600 * 1000 for e in cpu_time]
    indices = [i[0] for i in sorted(enumerate(cpu_time), key=lambda x: x[1])]
    cpu_time = [cpu_time[i] for i in indices]
    cpu = [cpu[i] for i in indices]

    for i in xrange(len(data[0][0])):
        indices_found = [v[0] for v in enumerate(cpu_time)
                         if data[0][0][i] <= v[1] < data[0][0][i] + period]

        if indices_found:
            mean = scipy.mean([cpu[i] for i in indices_found])
            data[1][len(data[1]) - 1].append(mean)

    return [data, category_list]
