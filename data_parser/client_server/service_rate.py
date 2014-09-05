from __future__ import division
import math
import numpy


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

    # |(time), (arrival-departure-flag), (class), (arrival time)|
    # |(time), (arrival-departure-flag), (class), (arrival time)|
    # |(time), (arrival-departure-flag), (class), (arrival time)|
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

    # STATE
    # each row corresponds to a current job
    # |the class of the job, the arrival time, the elapsed service time|
    # |the class of the job, the arrival time, the elapsed service time|
    # |the class of the job, the arrival time, the elapsed service time|
    state = numpy.zeros(shape=(0, 3))

    t = 0
    t_old = t

    # ACUM
    # number of service completions observed for each class (row)
    # and total service time per class (second column)
    acum = numpy.zeros(shape=(k, 2))
    observed = cell(k)  # holds all the service times observed

    # advance until observe warmUp entities minimum of each class
    i = 0
    while min(acum[:, 0]) < warm_up:
        t = times_order[0][i]
        time_elapsed = t - t_old
        n = state.shape[0]

        r = min(n, num_of_jobs)
        for j in xrange(r):
            state[j][2] += time_elapsed / r

        if times_order[1][i] == 0:
            next_row = [times_order[2][i], t, 0]
            state = numpy.vstack((state, next_row))
        else:
            # find job in progress that must leave
            k = 0
            while state[k][1] != times_order[3][i]:
                k += 1
            # update stats
            acum[int(state[k][0])][0] += 1
            acum[int(state[k][0])][1] += state[k][2]

            state = numpy.delete(state, k, axis=0)

        i += 1
        t_old = t

    mean_service_time = numpy.zeros(shape=(k, num_exp))

    for e in xrange(num_exp):
        # actually sampled data
        acum = numpy.zeros(shape=(k, 2))
        seperate = cell(k)
        observed = cell(k)

        while sum(acum[:, 0]) < sample_size:
            t = times_order[0][i]
            time_elapsed = t - t_old
            n = state.shape[0]

            # add to each job in process the service time elapsed (divided
            # by the portion of the server actually dedicated to it
            r = min(n, num_of_jobs)
            for j in xrange(r):
                if r <= num_of_cores:
                    state[j][2] += time_elapsed / r
                else:
                    state[j][2] += time_elapsed * num_of_cores / r

            if times_order[1][i] == 0:
                next_row = [times_order[2][i], t, 0]
                state = numpy.vstack((state, next_row))
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

                state = numpy.delete(state, k, axis=0)

            i += 1
            t_old = t

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

    return d[0]