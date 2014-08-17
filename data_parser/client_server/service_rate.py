def zeros(row, col=None):
    if not col:
        return [0] * row

    zeros_matrix = []
    for r in xrange(row):
        zeros_matrix.append([])
        for c in xrange(col):
            zeros_matrix[r].append([])
            zeros_matrix[r][c] = 0

    return zeros_matrix


def ones(row, col=None):
    if not col:
        return [1] * row

    ones_matrix = []
    for r in xrange(row):
        ones_matrix.append([])
        for c in xrange(col):
            ones_matrix[r].append([])
            ones_matrix[r][c] = 1

    return ones_matrix


def _calculate_service_rate(times, num_exp, sample_size, warm_up, num_of_jobs,
                            num_of_cores):
    k = len(times)

    # calculate departure times
    for i in xrange(k):
        for j in xrange(len(times[i][0])):
            departure = [a + r for a, r in zip(times[i][0], times[i][1])]
            times[i].append(departure)

    # Build array with all events
    # first column: time
    # second column: 0-arrival, 1-departure
    # third column: class
    # fourth column: arrival time (only for departures)
    times_order = [[] for i in xrange(4)]
    for kk in xrange(k):
        if len(times[kk]) > 2:
            zero_list = zeros(len(times[kk][0]))
            one_list = ones(len(times[kk][0]))

            times_order[0].extend(times[kk][0])
            times_order[1].extend(zero_list)
            times_order[2].extend([i * kk for i in one_list])
            times_order[3].extend(zero_list)

            times_order[0].extend(times[kk][2])
            times_order[1].extend(one_list)
            times_order[2].extend([i * kk for i in one_list])
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
    state = []

    told = t

    # ACUM
    # number of service completions observed for each class (row)
    # and total service time per class (second column)
    acum = zeros(k, 2)
    observed = [[] for i in xrange(k)]  # holds all the service times observed

    # advance until observe warmUp entities minimum of each class
    i = 1
    while min([acum[i][0] for i in len(acum)]) < warm_up:
        t = times_order[i][0]
        telapsed = t - told
        n = len(state)

        # add to each job in process the service time elapsed (divided
        # by the portion of the server actually dedicated to it in a PS server

        r = min(n, num_of_jobs)
        for j in xrange(r):
            state[j][2] += telapsed / r

        if times_order[i][1] == 0:
            state[0].extend(times_order[i][2])
            state[1].append(t)
            state[2].append(0)




    mean_service_time = None
    obs = None

    return mean_service_time, obs


def calculate_service_rate(num_of_jobs, num_of_cores, data):
    num_exp = 1
    sample_size = 0
    for i in xrange(len(data[2]) - 1):
        sample_size = sample_size + len(data[2][i]) - 1

    warm_up = 0

    k = len(data[2]) - 1
    sample_number = [0] * k

    times = [[] for i in xrange(k)]
    for j in xrange(k):
        times[j].append([d / 1000 for d in data[2][j]])
        times[j].append([data[3][j]])

        sample_number[j] = len(data[2][j])

    mean_service_time, obs = _calculate_service_rate(times, num_exp,
                                                     sample_size, warm_up,
                                                     num_of_jobs, num_of_cores)


# if __name__ == '__main__':
#     print init_matrix(2, [])