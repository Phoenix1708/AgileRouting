from __future__ import division
import math
import numpy


# def zeros(row, col=None):
# if not col:
# return [0] * row
#
#     zeros_matrix = []
#     for r in xrange(row):
#         zeros_matrix.append([])
#         for c in xrange(col):
#             zeros_matrix[r].append(0)
#             # zeros_matrix[r][c] = 0
#
#     return zeros_matrix
#
#
# def ones(row, col=None):
#     if not col:
#         return [1] * row
#
#     ones_matrix = []
#     for r in xrange(row):
#         ones_matrix.append([])
#         for c in xrange(col):
#             ones_matrix[r].append([])
#             ones_matrix[r][c] = 1
#
#     return ones_matrix


def cell(row, col=None):
    if not col:
        return [[] for i in xrange(row)]

    the_cell = []
    for c in xrange(col):
        the_cell.append([])
        for r in xrange(row):
            the_cell[c].append([])

    return the_cell


def _calculate_service_rate(times, num_exp, sample_size, warm_up, num_of_jobs,
                            num_of_cores):
    k = len(times)

    # calculate departure times
    for k1 in xrange(k):
        departure = [a + r for a, r in zip(times[k1][0], times[k1][1])]
        times[k1].append(departure)

    # Build array with all events
    # first column: time
    # second column: 0-arrival, 1-departure
    # third column: class
    # fourth column: arrival time (only for departures)
    times_order = cell(4)
    for kk in xrange(k):
        if len(times[kk]) > 2:
            zero_list = numpy.zeros(shape=(len(times[kk][0])))
            one_list = numpy.ones(shape=(len(times[kk][0])))

            # arrivals
            times_order[0].extend(times[kk][0])
            times_order[1].extend(zero_list)
            times_order[2].extend([one * kk for one in one_list])
            times_order[3].extend(zero_list)

            # departure
            times_order[0].extend(times[kk][2])
            times_order[1].extend(one_list)
            times_order[2].extend([one1 * kk for one1 in one_list])
            times_order[3].extend(times[kk][0])

    # order events based on arrival time
    indices = [t[0] for t in
               sorted(enumerate(times_order[0]), key=lambda x: x[1])]
    times_order[0] = [times_order[0][idx] for idx in indices]
    times_order[1] = [times_order[1][idx] for idx in indices]
    times_order[2] = [times_order[2][idx] for idx in indices]
    times_order[3] = [times_order[3][idx] for idx in indices]

    t = 0
    # STATE
    # each row corresponds to a current job
    # first column:  the class of the job
    # second column: the arrival time
    # third column: the elapsed service time
    state = numpy.zeros(shape=(0, 3))

    told = t

    # ACUM
    # number of service completions observed for each class (row)
    # and total service time per class (second column)
    acum = numpy.zeros(shape=(k, 2))
    observed = cell(k)  # holds all the service times observed

    # advance until observe warmUp entities minimum of each class
    i = 0
    while min(acum[:, 0]) < warm_up:
        t = times_order[0][i]
        telapsed = t - told
        n = state.shape[0]

        # add to each job in process the service time elapsed (divided
        # by the portion of the server actually dedicated to it in a PS server

        r = min(n, num_of_jobs)
        for j in xrange(r):
            state[j][2] += telapsed / r

        if times_order[1][i] == 0:
            next_row = [times_order[2][i], t, 0]
            state = numpy.vstack((state, next_row))
            # state[0].extend(times_order[2][i])
            # state[1].append(t)
            # state[2].append(0)
        else:
            # find job in progress that must leave
            k = 0
            while state[k][1] != times_order[3][i]:
                k += 1
            # update stats
            acum[int(state[k][0])][0] += 1
            acum[int(state[k][0])][1] += state[k][2]

            # update state
            # state = [state(1:k-1,:); state(k+1:end,:)];
            state = numpy.delete(state, k, axis=0)
            # [s.remove(s[k]) for s in state]

        i += 1
        told = t

    mean_service_time = numpy.zeros(shape=(k, num_exp))

    for e in xrange(num_exp):
        # actually sampled data
        acum = numpy.zeros(shape=(k, 2))
        seperate = cell(k)
        observed = cell(k)

        while sum(acum[:, 0]) < sample_size:
            t = times_order[0][i]
            telapsed = t - told
            n = state.shape[0]

            # add to each job in process the service time elapsed (divided
            # by the portion of the server actually dedicated to it in
            # a PS server
            r = min(n, num_of_jobs)
            for j in xrange(r):
                if r <= num_of_cores:
                    state[j][2] += telapsed / r
                else:
                    state[j][2] += telapsed * num_of_cores / r

            if times_order[1][i] == 0:
                next_row = [times_order[2][i], t, 0]
                state = numpy.vstack((state, next_row))
                # state[0].extend(times_order[2][i])
                # state[1].append(t)
                # state[2].append(0)
            else:
                # find job in progress that must leave
                k = 0
                while state[k][1] != times_order[3][i]:
                    k += 1
                # update stats
                if acum[int(state[k][0])][1] == 0:
                    acum[int(state[k][0])][1] = math.pow(2, -52)  # EPS
                else:
                    acum[int(state[k][0])][0] += 1
                    acum[int(state[k][0])][1] += state[k][2]
                    seperate[int(state[k][0])].append(state[k][2])
                    observed[int(state[k][0])].append(state[k][2])

                acum[int(state[k][0])][0] += 1
                acum[int(state[k][0])][1] += state[k][2]

                # update state
                # state = [state(1:k-1,:); state(k+1:end,:)];
                state = numpy.delete(state, k, axis=0)
                # [s.remove(s[k]) for s in state]

            i += 1
            told = t

        mean_service_time[:, e] = \
            [a2 / a1 for a2, a1 in zip(acum[:, 1], acum[:, 0])]

    return mean_service_time, observed


def calculate_service_rate(num_of_jobs, num_of_cores, data):
    num_exp = 1
    sample_size = 0
    for i in xrange(len(data[2]) - 1):
        sample_size = sample_size + len(data[2][i]) - 1

    warm_up = 0

    k = len(data[2]) - 1
    sample_number = numpy.zeros(shape=k)

    times = cell(k)
    for kk in xrange(k):
        times[kk].extend(cell(2))
        times[kk][0].extend([d / 1000 for d in data[2][kk]])
        times[kk][1].extend(data[3][kk])

        sample_number[kk] = len(data[2][kk])

    mean_service_time, observed = _calculate_service_rate(times, num_exp,
                                                          sample_size, warm_up,
                                                          num_of_jobs,
                                                          num_of_cores)

    d = mean_service_time.mean(axis=0)

    return d


if __name__ == '__main__':
    #     # a = numpy.array([1, 2, 3])
    #     # b = numpy.array([4, 5, 6])
    #     # test = numpy.hstack((a, b))
    #     # test[1][0] = 10
    one_list = numpy.ones(shape=10)
    print one_list
    print [one * 3 for one in one_list]

    # np_test = numpy.array([[1.22636426]
    #                        [0.06122791]
    #                        [0.50653574]
    #                        [0.10256183]
    #                        [0.34213803]
    #                        [2.02279895]])
    # np_test.mean(axis=0)
    # test = numpy.ones(shape=(0, 3))
    #
    # print test
    # print test.shape[0]
    #
    # # test[0][1] += 3
    # # print test
    #
    # test = numpy.vstack((test, [2, 3, 4]))
    # test = numpy.vstack((test, [2, 3, 4]))
    # print test
    #     test[1][0] = 2
    #     print test
    #
    #     print test.mean(axis=1)
    #
    # temp = [a+r for a, r in zip(test[:, 0], test[:, 1])]
    # print temp
    #
    # test1 = numpy.ones(shape=(3, 2))
    # print test1
    #
    # test1[:, 0] = temp
    # print test1

    # test[0][1] = 5
    # print test
    # print max(test[:, 1])
    # print test.shape[1]

    # print test2

    # k = 5
    # times = cell(k)
    # for kk in xrange(k):
    #     times[kk].extend(cell(2))
    #     times[kk][0].extend([1,2,3,4,5])
    #     times[kk][1].extend([5,4,3,2,1])
    # for i in xrange(len(times)):
    #     departure = [a + r for a, r in zip(times[i][0], times[i][1])]
    #     times[i].append(departure)
    #
    # print times


    # # times.remove(times[0])
    # [s.remove(s[2]) for s in times]
    # print times