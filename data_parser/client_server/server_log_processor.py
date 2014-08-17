import os
import time
from data_parser import client_server

from data_parser.client_server.monitor_log_parser import process_monitor_log
from etc.configuration import cfg
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_station_csparql


class ServiceStationMetric:
    """
    Class that encapsulate metrics of service stations
    """

    def __init__(self, name, requests, arr_rate, service_rate):
        self.station_name = name
        self.total_requests = requests
        self.arrival_rate = arr_rate
        self.service_rate = service_rate


def process_server_logs(base_dir, line_counters, queue):
    """

    :param line_counters:
    :param queue:           Queue to store results when using in thread
    :return:
    """
    # create directory to store logs

    # Wait for measurement interval before processing logs (e.g 10 mins)
    # measurement_interval = cfg.get('Default', 'measurement_interval', 10)
    measurement_interval = 5  # test
    time.sleep(measurement_interval * 60)

    module_path = os.path.dirname(client_server.__file__)
    base_dir = module_path + '/logs/' + base_dir + '/'

    # retrieve service station and observer mapping
    station_observers = get_station_csparql()
    # retrieve and process the log of each service station with a new threads
    csparql_reader = ThreadingManager()
    for station_name, observer_ip in station_observers.iteritems():
        observer_addr = '%s=%s' % (station_name, observer_ip)

        csparql_reader.start_tasks(target_func=process_monitor_log,
                                   name='csparql_reader',
                                   para=[base_dir, observer_addr,
                                         line_counters[station_name]])

    result_queue = csparql_reader.collect_results()

    service_station_metric_list = []
    while not result_queue.empty():
        station_name, total_requests, arrival_rate, service_rate, line_counter \
            = result_queue.get().split(',')

        # update the current line counter
        line_counters[station_name] = line_counter

        service_metric = ServiceStationMetric(station_name, total_requests,
                                              arrival_rate, service_rate)
        service_station_metric_list.append(service_metric)

    queue.put(service_station_metric_list)
    queue.put(line_counters)

    # return service_station_metric_list, line_counters