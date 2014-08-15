import os
import time
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_env, sync_files


def _parse_client_log(input_files_dir, line_counter):
    """
    Function to read client log. Currently counting the number of requests
    More functions can be added in the future

    :param input_files_dir: Client log file directory
    :param line_counter:    The line number to start reading
    :return:
    """
    if not input_files_dir:
        print 'Please supply the directory that contains client logs'
        return
    elif not os.path.exists(input_files_dir):
        print 'Directory \''+input_files_dir+'\' does not exist'
        return

    client_log_file_path = input_files_dir + '/responses.csv'

    with open(client_log_file_path, 'r') as f:
        # seg = client_log_file_path.split('/')
        # file_name = seg[len(seg) - 1]
        current_num_lines = len(f.readlines())
        # current total number of lines minus the total number of lines
        # recorded last time to get the number of request sent during current
        # measurement period
        num_lines = current_num_lines - line_counter
        # set line counter to new value
        line_counter = current_num_lines

        return [num_lines, line_counter]

    # response_files = [os.path.join(dir_path, f)
    #                   for dir_path, dir_names, file_names
    #                   in os.walk(input_files_dir)
    #                   for f in file_names
    #                   if os.path.splitext(f)[1] == '.csv']

    # Read client log files with different threads
    # Note: Currently the threads only reads the line number hence the
    # overhead of starting threads might be greater than the parallel
    # processing benefit brought by multi-threading.

    # client_log_reader = ThreadingManager()
    #
    # for i in xrange(len(response_files)):
    #     file_name = response_files[i]
    #
    #     client_log_reader.start_threads(read_file_lines, 'client_log_reader',
    #                                     (file_name, line_counter))
    #
    # # collect result for each file reader
    # result_queue = client_log_reader.collect_results()
    #
    # total_request = 0
    # while not result_queue.empty():
    #     f_name, num_lines, line_counter = result_queue.get().split('=')
    #     total_request += num_lines

    # return [total_request, line_counter]


def process_client_log(client_host_ip, base_dir, client_name, line_counter,
                       queue):
    """
    Function to process logs of client. e.g counting how many requests has
    been sent. The client IP environment variable has to follow the
    "OFBIZ_CLIENT_<client_name>_IP" convention

    :param base_dir:        Location to stored the log file
    :param line_counter:    The counter for continuously reading a file from
                            last time

    :return:                "Total number of requests" (for now, more data
                            can be returned in the future)
    """

    # set up local log directory
    client_log_dir = base_dir + "/client_%s_logs/" % client_name
    if os.path.exists(client_log_dir):
        os.makedirs(client_log_dir)

    # using rsync to get the update from client logs
    # (only download response at the moment. More can be added in future
    sync_files(host_ip=client_host_ip, username='ubuntu',
               host_file_path='~/ofbench-client/results/test/responses.csv',
               pk_path='logs/ec2_private_key', dst_loc=client_log_dir)

    print 'Updated client log stored in directory: ' + client_log_dir

    total_requests, line_counter = _parse_client_log(client_log_dir,
                                                     line_counter)

    queue.put('%s,%s' % (total_requests, line_counter))
    # return total_requests, line_counter


# def read_file_lines(client_log_file_path, line_counter, queue):
#     """
#     Counting the number of requests sent by the client
#
#     :param client_log_file_path: Path to the response record file of client
#     :param queue:                Queue to log reading store results
#     :return:
#     """
#     if not client_log_file_path:
#         print 'Please supply the directory that contains client logs'
#         return
#
#     with open(client_log_file_path, 'r') as f:
#         seg = client_log_file_path.split('/')
#         file_name = seg[len(seg) - 1]
#         current_num_lines = len(f.readlines())
#         # current total number of lines minus the total number of lines
#         # recorded last time to get the number of request sent during current
#         # measurement period
#         num_lines = current_num_lines - line_counter
#         # set line counter to new value
#         line_counter = current_num_lines
#
#         queue.put('%s=%s:%s' % (file_name, num_lines, line_counter))


def process_client_logs(line_counters):
    """
    Retrieve logs from all clients. Counting the number of requests sent

    :param line_counters: collection of log reading counters for each client
    :return: Total number of requests sent by all client
    """

    total_requests = 0
    # create directory to store logs
    dir_name = time.strftime("%Y_%m%d_%H%M")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # observer_ip = get_env('CSPARQL_OBSERVER_IP')
    # TODO: When client number increases the below can be made to a function
    ofbench_client_1_ip = get_env('OFBIZ_CLIENT_1_IP')
    ofbench_client_2_ip = get_env('OFBIZ_CLIENT_2_IP')

    clients = [ofbench_client_1_ip, ofbench_client_2_ip]

    # Read client log files with different threads
    # Note: Currently the threads only reads the line number hence the
    # overhead of starting threads might be greater than the parallel
    # processing benefit brought by multi-threading.
    client_log_reader = ThreadingManager()

    for i in xrange(len(clients)):
        client_log_reader.start_tasks(process_client_log, 'client_log_reader',
                                        (clients[i], dir_name,
                                        line_counters[i], str(i)))

# num_request_c1, line_counters[0] = process_client_log(ofbench_client_1_ip,
#                                                       dir_name,
#                                                       line_counters[0], '1')
#
# num_request_c2, line_counters[1] = process_client_log(ofbench_client_2_ip,
#                                                       dir_name,
#                                                       line_counters[1], '2')
# total_requests = num_request_c1 + num_request_c1

    result_queue = client_log_reader.collect_results()
    l = 0
    while not result_queue.empty():
        req_sum, l_counter = result_queue.get().split(',')
        total_requests += req_sum
        line_counters[l] = l_counter
        l += 1

    return total_requests, line_counters