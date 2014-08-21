from __future__ import division
import time
import math
from data_parser.client_server.server_log_processor import process_server_logs
from data_parser.optimization import optimise
from data_parser.s3.process_access_log import process_elb_access_log
from etc.configuration import setup_logging, cfg
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_station_region, get_stations, \
    calculate_waiting_time, get_stations_bandwidth, get_elb_buckets_map, \
    print_message


def main():
    setup_logging()

    # line counter for reading csparql logs of each service station
    line_counters = dict()

    # bucket and ELB info for getting access log from S3
    elb_buckets_dict = dict()
    elb_regions = get_station_region()
    elb_buckets = get_elb_buckets_map()
    for station, region in elb_regions.iteritems():
        elb_region_str = '%s:%s' % (station, region)
        elb_buckets_dict.update({elb_region_str: unicode(elb_buckets[station])})

    # collecting access log for each elb with different threads
    elb_data_manager = ThreadingManager()

    stations = get_stations()
    for station in stations:
        line_counters.update({station: 0})

    log_base_dir = time.strftime("%Y_%m%d_%H%M")
    total_num_users = cfg.get_int('Default', 'total_num_users')

    # counter = 0  # For testing
    while True:

        # Processing csparql log and ELB access log simultaneously by 2 threads

        # Start csparql log paring first since ELB access log has delay
        # omitting the log file

        # First we need to calculate how much time to wait before retrieving
        # csparql logs. i.e how long the actual measurement time is. Since S3
        # only omit log at 5, 10, 15 etc. minute of the hour, we can only
        # measure the time that measurement start until the last expected log
        # omission time which is not the actual time that log being obtained
        # since there is delay
        measurement_interval = calculate_waiting_time()

        csparql_log_parser = ThreadingManager()
        csparql_log_parser.start_task(
            target_func=process_server_logs,
            name="server_log_processor",
            para=[log_base_dir, line_counters, total_num_users,
                  measurement_interval]
        )

        # Begin gathering info of the amount of data
        # transferred through each service station
        data_counting_task = ThreadingManager()
        data_counting_task.start_task(
            target_func=process_elb_access_log,
            name="elb_access_log_processor",
            para=[elb_buckets_dict, elb_data_manager]
        )

        # collecting csparql log first since its processing will complete first
        # while elb data might has delay
        csparql_log_queue = csparql_log_parser.collect_results()
        (service_station_metric_list, total_request) = csparql_log_queue.get()
        line_counters = csparql_log_queue.get()

        print_message('')
        print_message('Service station logs processing finished\n')

        # collecting elb data now
        elb_data_queue = data_counting_task.collect_results()
        data_in, data_out = elb_data_queue.get()

        # Begin reading logs from OFBench client.
        # The line_counters is maintained here for continuous log reading
        # total_requests, line_counters = process_client_logs(line_counters)

        """Preparing optimisation parameters"""
        # Calculate The "average amount of data involved in each request" for
        # each service station and the "total number of requests"

        # These 2 dictionary stores the average data send and received per
        # request sent and received by *each service station*. Hence the
        # length of the dictionary should be equals to the number of service
        # stations
        avg_data_in_per_reqs = dict()
        avg_data_out_per_reqs = dict()
        # requests arrival rate and service rate of each service station
        arrival_rates = dict()
        service_rates = dict()

        for service_station_metric in service_station_metric_list:
            # getting metric
            station_name = service_station_metric.station_name
            arrival_rate = service_station_metric.arrival_rate
            service_rate = service_station_metric.service_rate

            requests = service_station_metric.total_requests

            print '\nTotal requests for station %s: %s' \
                  % (station_name, requests)

            # arrival_rate and service_rate
            arrival_rates.update({station_name: arrival_rate})
            service_rates.update({station_name: service_rate})

            response_time = \
                math.pow(service_rate, -1) / (1 - math.pow(service_rate, -1) *
                                              arrival_rate)
            print '[Debug] predicted response time of service station ' \
                  '\'%s\': %s' % (station_name, response_time)

            # calculate average data sent and receive
            d_in = data_in.get(station_name)
            d_out = data_out.get(station_name)

            # convert the amount of data to GB
            d_in = float(d_in / math.pow(1024, 3))
            d_out = float(d_out / math.pow(1024, 3))

            avg_data_in_per_req = d_in / requests
            avg_data_out_per_req = d_out / requests

            avg_data_in_per_reqs.update({station_name: avg_data_in_per_req})
            avg_data_out_per_reqs.update({station_name: avg_data_out_per_req})

        # For testing purpose
        print '\n[Debug] total_request: %s' % total_request
        print '[Debug] avg_data_in_per_reqs: %s' % avg_data_in_per_reqs
        print '[Debug] avg_data_out_per_reqs: %s' % avg_data_out_per_reqs
        print '[Debug] arrival_rates: %s' % arrival_rates
        print '[Debug] service_rates: %s\n' % service_rates

        # counter += 1
        # time.sleep(20)

        # TODO: Delay service level agreement, cost budget
        # TODO: print out delay

        # ELB pricing
        elb_prices = [0.008, 0.008]
        # bandwidths for each client
        in_bandwidths = []
        out_bandwidths = []
        # average data per requests
        avg_in_data = []
        avg_out_data = []
        service_rates_list = []
        # Service Level Agreement of response time for each station
        sla_response_t = [1.5, 1.5]

        in_band_dict, out_band_dict = get_stations_bandwidth()
        # convert to GB/s

        for station in stations:
            # convert from Mb/s to GB/s
            in_band = in_band_dict[station] / 8 / 1024
            out_band = out_band_dict[station] / 8 / 1024
            in_bandwidths.append(in_band)
            out_bandwidths.append(out_band)

            avg_in_data.append(avg_data_in_per_reqs[station])
            avg_out_data.append(avg_data_out_per_reqs[station])
            service_rates_list.append(service_rates[station])

        weights = optimise(num_of_stations=2, total_requests=total_request,
                           elb_prices=elb_prices,
                           avg_data_in_per_reqs=avg_in_data,
                           avg_data_out_per_reqs=avg_out_data,
                           in_bandwidths=in_bandwidths,
                           out_bandwidths=out_bandwidths,
                           budget=1000000, service_rates=service_rates_list,
                           sla_response_t=sla_response_t,
                           measurement_interval=measurement_interval, k=-10)
        print weights

        # base_domain = 'agilerouting.net'
        #
        # conn = Route53Connection()
        # zone = conn.get_zone(base_domain)
        #
        # print zone
        #
        # Ireland_ELB = \
        # 'dualstack.xueshi-ofbench-servers-1324038295
        # .eu-west-1.elb.amazonaws.com.'
        #
        # base_record = dict(name="www.%s" % base_domain,
        # type="A", weight=weight_a,
        # identifier="Ireland")
        #
        # rrs = ResourceRecordSets(conn, zone.id)
        # new = rrs.add_change(action="UPSERT", **base_record)
        # new.set_alias('Z32O12XQLNTSW2', Ireland_ELB, False)
        # change_result = rrs.commit()


if __name__ == "__main__":
    main()
    print 'done'