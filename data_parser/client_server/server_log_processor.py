from __future__ import division
import os
import time
import math

from datetime import datetime

from data_parser import client_server
from data_parser.client_server.monitor_log_parser import process_monitor_log
from data_parser.client_server.service_rate import calculate_service_rate
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_station_csparql, print_message, \
    get_expected_num_logs, get_next_nth_elb_log_time


class ServiceStationMetric:
    """
    Class that encapsulate metrics of service stations
    """

    def __init__(self, name, requests, arr_rate, service_rate_para_list,
                 service_rate):
        self.station_name = name
        self.total_requests = requests
        self.arrival_rate = arr_rate
        # TODO: separate elements from the list into individual parameter
        self.service_rate_para_list = service_rate_para_list
        self.service_rate = service_rate


def calculate_waiting_time():
    # record the start time to calculate time elapsed
    start_time = time.time()
    # get expected ELB access logs based on measurement interval
    expected_logs_to_obtain = get_expected_num_logs()

    # calculate the time for which the last expected access log is
    day, hour, month, next_expected_logging_minute, year \
        = get_next_nth_elb_log_time(expected_logs_to_obtain)

    # from UTC to GMT hour + 1
    time_str = ''.join([str(year), str(month), str(day), str(hour+1),
                        str(int(next_expected_logging_minute))])
    date = datetime.strptime("".join(time_str), '%Y%m%d%H%M')
    date_milli = time.mktime(date.timetuple()) + date.microsecond
    # calculate waiting time
    waiting_time = (date_milli - start_time)
    return waiting_time


def process_server_logs(base_dir, line_counters, total_users, queue):
    """

    :param base_dir:        Base directory of monitor log
    :param line_counters:   Counter for continuously reading the single log file
    :param total_users:     The total number of users simulated
    :param queue:           Queue to store results when using in thread
    :return:
    """

    # First we need to calculate how much time to wait before retrieving
    # csparql logs. i.e how long the actual measurement time is. Since S3
    # only omit log at 5, 10, 15 etc. minute of the hour, we can only measure
    #  the time that measurement start until the last expected log omission time
    # which is not the actual time that log being obtained since there is delay
    waiting_time = calculate_waiting_time()

    print_message('')
    print_message('Waiting for the next batch of service station monitoring '
                  'logs (%s seconds)...\n' % waiting_time)
    time.sleep(waiting_time)

    module_path = os.path.dirname(client_server.__file__)
    base_dir = module_path + '/logs/' + base_dir + '/'

    # retrieve service station and observer mapping
    station_observers = get_station_csparql()
    # retrieve and process the log of each service station with a new threads
    csparql_reader = ThreadingManager()

    # python strptime thread safety bug. Has to call strptime once before
    # creating thread. Details can be found on:
    # http://bugs.python.org/issue11108
    time.strptime("30 Nov 00", "%d %b %y")

    for station_name, observer_ip in station_observers.iteritems():
        observer_addr = '%s=%s' % (station_name, observer_ip)

        csparql_reader.start_tasks(target_func=process_monitor_log,
                                   name='csparql_reader',
                                   para=[base_dir, observer_addr,
                                         line_counters[station_name]])

    # wait for all threads to finish and collect their results
    result_queue = csparql_reader.collect_results()

    total_requests = 0

    # Now collect metric data from all service station and then calculate the
    # necessary metric for the optimisation since these metrics are calculated
    # for the entire online services
    service_station_metric_list = []

    while not result_queue.empty():
        # get metrics returned
        result_dict = result_queue.get()

        station_name = result_dict['station_name']
        station_total_requests = result_dict['total_requests']
        arrival_rate = result_dict['arrival_rate']
        service_rate_para_list = result_dict['service_rate_para_list']
        line_counter = result_dict['line_counter']

        total_requests += station_total_requests

        service_station_metric = ServiceStationMetric(station_name,
                                                      station_total_requests,
                                                      arrival_rate / 60,
                                                      service_rate_para_list,
                                                      service_rate=0)

        service_station_metric_list.append(service_station_metric)

        # update the current line counter
        line_counters[station_name] = line_counter

    # now calculate service rate for each station
    for station_metric in service_station_metric_list:

        # parameter needed for calculating service rate for servers from
        # one service station
        mu_para_list = station_metric.service_rate_para_list

        # Calculating service rate of each server in one station
        service_time_list = []  # list to store service time of each server

        # for service rate calculation parameters for each server ...
        for s_para in mu_para_list:
            # number of users for this vm
            num_of_requests = s_para['num_of_requests']
            num_of_user = int(math.ceil(
                total_users * (num_of_requests / total_requests)))
            num_of_cores = s_para['cpu_cores']
            data = s_para['data']

            mean_service_time = calculate_service_rate(num_of_user,
                                                       num_of_cores, data)
            service_time_list.append(mean_service_time)

            print_message('Mean service time of VM \'%s\' at station \'%s\': %s'
                          % (s_para['vm_name'], station_metric.station_name,
                             str(mean_service_time)))

        # The overall service rate is calculated by the number of requests
        # completed by all servers within the time that the slowest server
        # takes to complete a single request
        max_time = max(service_time_list)

        comp_reg_sum = 0
        for service_time in service_time_list:
            comp_reg_sum += max_time / service_time

        overall_service_rate = comp_reg_sum / max_time

        station_metric.service_rate = overall_service_rate

    # store result of this thread in result the queue
    queue.put((service_station_metric_list, total_requests))
    queue.put(line_counters)

    # return service_station_metric_list, line_counters