import os
import time
import numpy
import Resources
from etc.configuration import cfg
from utilities.multi_threading import ThreadingManager
from utilities.utils import execute_remote_command, print_message, \
    station_metadata_map


resources_location = os.path.dirname(Resources.__file__)


def measure_round_trip_delay(from_host, to_host, from_host_pk,
                             measurement_interval, queue):
    start_time = time.time()
    current_time = start_time
    time_elapsed = current_time - start_time

    measurements = []   # list to store series of measurement

    while time_elapsed < measurement_interval:   # in the unit of seconds

        cmd = ' '.join(["ping", "-c 5", to_host])
        out, err = execute_remote_command(from_host, cmd, 'ubuntu', '',
                                          from_host_pk)

        rt_str = [text for text in out.split('\n')
                  if 'min/avg/max/' in text]

        # print rt_str

        stat_str = rt_str[0].split('=')
        metric_name = stat_str[0]
        values = stat_str[1].split('/')
        avg_idx = metric_name.split('/').index('avg')

        avg_round_trip_delay = values[avg_idx]
        print_message('Average round trip delay between %s and %s: %s'
                      % (from_host, to_host, avg_round_trip_delay))

        # record current measurement
        measurements.append(float(avg_round_trip_delay))

        time.sleep(30)  # sleep for half a min

        current_time = time.time()
        time_elapsed = current_time - start_time

    average_round_trip_delay = numpy.mean(measurements)

    queue.put('%s,%s,%s' % (from_host, to_host, average_round_trip_delay))

    # return avg_round_trip_delay


def _measure_latency(src_hosts, dst_hosts, measurement_interval):
    """
    Measuring round trip delay between each pair of hosts

    :param src_hosts:           A Dictionary stores ip, name, private key of
                                the hosts that we measure delay from i.e clients
                                <(src_host_ip, src_host_name): src_host_pk>

    :param dst_hosts:               A Dictionary stores ip and name of the
                                    hosts that we want to measure the delay from
                                    the each source hosts

    :param measurement_interval:    period of measurement

    :return:                        Average round trip delay between each
                                    pair of hosts
    """

    station_delay_dict = dict()

    delay_manager = ThreadingManager()
    ip_f_host_dict = {}

    for s_host, s_host_pk in src_hosts.iteritems():
        for d_hosts_ip, d_hosts_name in dst_hosts.iteritems():

            s_host_ip, s_host_name = s_host

            # <ip: host_name>
            ip_f_host_dict.update({s_host_ip: s_host_name})

            delay_manager.start_task(
                target_func=measure_round_trip_delay,
                name="delay_measurer",
                para=[s_host_ip, d_hosts_ip, s_host_pk, measurement_interval]
            )

    delay_results = delay_manager.collect_results()
    while not delay_results.empty():
        # get metrics returned
        from_host, to_host, average_round_trip_delay \
            = delay_results.get().split(',')

        src_host_name = ip_f_host_dict[from_host]
        to_host_name = dst_hosts[to_host]

        measurement_key = '%s,%s' % (src_host_name, to_host_name)

        station_delay_dict.update({measurement_key: average_round_trip_delay})

    return station_delay_dict


def measure_latency(available_clients, available_stations, m_interval, queue):

    src_host = dict()
    to_host = dict()
    for client_name in available_clients:

        src_ip = cfg.get('IPs', client_name)
        ip_name_pair = (src_ip, client_name)

        pk_name = cfg.get('PrivateKeys', client_name)
        private_key_file_path = resources_location + '/' + pk_name

        src_host.update({ip_name_pair: private_key_file_path})

    for station_name in available_stations:
        ip_key_str = '%s_server_1' % station_name
        to_host.update({station_metadata_map['ip'][ip_key_str]: station_name})

    result_dict = _measure_latency(src_host, to_host, m_interval)
    queue.put(result_dict)

    # return result_dict


if __name__ == '__main__':

    ip_host_name = ('54.255.65.145', 'ap_south_1_client_1')
    module_path = os.path.dirname(Resources.__file__)
    private_key_file_path = module_path + '/xueshisingapore.pem'

    src_host = {ip_host_name: private_key_file_path}
    to_host = {'176.34.66.152': 'xueshi-station-1'}
    m_interval = 60

    result_dict = _measure_latency(src_host, to_host, m_interval)
    print result_dict
