import os
import time

from data_parser.client_server.parse_monitor_log import process_monitor_log
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


def process_logs(line_counters):
    # create directory to store logs
    base_dir = 'logs/' + time.strftime("%Y_%m%d_%H%M") + '/'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # retrieve service station and observer mapping
    station_observers = get_station_csparql()
    # retrieve and process the log of each service station with a new threads
    csparql_reader = ThreadingManager()
    for station_name, observer_ip in station_observers:
        observer_addr = '%s=%s' % (station_name, observer_ip)

        csparql_reader.start_tasks(target_func=process_monitor_log,
                                   name='csparql_reader',
                                   para=[base_dir, observer_addr,
                                         line_counters[station_name]])

    result_queue = csparql_reader.collect_results()

    service_station_metric_list = []
    while not result_queue.empty():
        station_name, metrics_tuple, line_counter = \
            result_queue.get().split(',')

        # update the current line counter
        line_counters[station_name] = line_counter
        # get metrics
        total_requests, arrival_rate, service_rate = metrics_tuple

        service_metric = ServiceStationMetric(station_name, total_requests,
                                              arrival_rate, service_rate)
        service_station_metric_list.append(service_metric)

    return service_station_metric_list, line_counters