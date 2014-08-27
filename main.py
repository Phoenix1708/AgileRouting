from __future__ import division
import time
import math
from connection.route_53_connection import Route53Connection
from data_parser.client_server.server_log_processor import process_server_logs
from data_parser.optimization import optimise, optimisation
from data_parser.s3.process_access_log import process_elb_access_log
from etc.configuration import setup_logging, cfg
from models.resource_record_set import ResourceRecordSets
from utilities.exception import UnsuccessfulRequestError
from utilities.heart_beater import measure_latency
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_station_region, get_available_stations, \
    calculate_waiting_time, get_stations_bandwidth, get_elb_buckets_map, \
    print_message, log_info, get_available_clients, station_metadata_map


base_domain = 'agilerouting.net'

# name of the file that record metrics
metric_record_file = 'metrics.txt'


def clients_optimisation(avg_data_in_per_reqs, avg_data_out_per_reqs, client,
                         elb_prices, latency_results_dict, measurement_interval,
                         service_rates, stations, total_request_per_client,
                         queue):
    # bandwidths for each client
    in_bandwidths = []
    out_bandwidths = []
    # average data per requests
    avg_in_data = []
    avg_out_data = []
    service_rates_list = []
    station_latency = []
    # TODO: start new threads for each client
    in_band_dict, out_band_dict = get_stations_bandwidth(client)
    # Budget 100,000 / 30 / 24 / 60 / interval
    # Not total budget. Budget for the interval
    budget = 1000
    client_avg_data_in_per_reqs = avg_data_in_per_reqs[client]
    client_avg_data_out_per_reqs = avg_data_out_per_reqs[client]
    request_sum = total_request_per_client[client]
    # get latency for each from this client to each station
    station_latency_dict = dict()
    for key_str, latency_val in latency_results_dict.iteritems():
        src_host, dst_host = key_str.split(',')
        if client == src_host:
            station_latency_dict.update({dst_host: latency_val})
    for station in stations:
        # convert from Mb/s to GB/s
        in_band = float(in_band_dict[station]) / 8 / 1024
        out_band = float(out_band_dict[station]) / 8 / 1024
        in_bandwidths.append(in_band)
        out_bandwidths.append(out_band)

        avg_in_data.append(client_avg_data_in_per_reqs[station])
        avg_out_data.append(client_avg_data_out_per_reqs[station])
        service_rates_list.append(service_rates[station])
        station_latency.append(station_latency_dict[station])

    # weights = optimise(num_of_stations=2, total_requests=request_sum,
    # elb_prices=elb_prices,
    # avg_data_in_per_reqs=avg_in_data,
    # avg_data_out_per_reqs=avg_out_data,
    # in_bandwidths=in_bandwidths,
    # out_bandwidths=out_bandwidths,
    # budget=budget, service_rates=service_rates_list,
    # measurement_interval=measurement_interval, k=1)
    weights = optimisation(num_of_stations=2,
                           total_requests=request_sum,
                           elb_prices=elb_prices,
                           avg_data_in_per_reqs=avg_in_data,
                           avg_data_out_per_reqs=avg_out_data,
                           in_bandwidths=in_bandwidths,
                           out_bandwidths=out_bandwidths,
                           budget=budget,
                           service_rates=service_rates_list,
                           measurement_interval=measurement_interval,
                           station_latency=station_latency)

    print_message('Weights calculated for client %s: %s' % (client, weights))

    # weights are fraction initially but Route53 only accept integer and
    # must be an integer between 0 and 255
    # so we convert the ratio of weights to ratio of integers
    # this scaling should match the searching step of in optimisation
    # Weight
    weights = [int(val * 255) for val in weights]

    route53_conn = Route53Connection()
    zone = route53_conn.get_zone(base_domain)
    elb_records = station_metadata_map['StationELBDNS']
    alias_zone_id = {'xueshi-station-1': 'Z32O12XQLNTSW2',
                     'xueshi-station-2': 'Z35SXDOTRQ7X7K'}

    # TODO: This is actually which region of the server user most closet to
    # need to be mapped to IPs
    clients_regions = {'ap_south_1_client_1': 'ireland',
                       'us_east_1_client_1': 'nvirginia',
                       'us_west_1_client_1': 'nvirginia'}

    identifiers = dict(cfg.items('StationWRRAliasIdentifiers'))

    stations = get_available_stations()
    # Since we put optimisation parameter by the order available
    # stations the output weights should be in the same order
    station_weights = {}
    for idx in xrange(len(stations)):
        station_weights.update({stations[idx]: int(round(weights[idx]))})

    rrs = ResourceRecordSets(route53_conn, zone.id)

    for s_name, weights_val in station_weights.iteritems():
        alias_dns_name = elb_records[s_name]
        host_zone_id = alias_zone_id[s_name]

        # Client region not station region
        region_name = clients_regions[client]

        dns_record_name = '%s.%s' % (region_name, base_domain)
        identifier = identifiers[s_name]
        base_record = dict(name=dns_record_name,
                           record_type="A", weight=weights_val,
                           identifier=identifier)

        print_message('[Debug]: weight before sending change request %s'
                      % weights_val)

        new = rrs.add_change(action="UPSERT", **base_record)
        new.set_alias(host_zone_id, unicode(alias_dns_name), False)

    # with retry in case request rejected due to proc
    succeed = False
    while not succeed:
        try:
            rrs.commit()
            succeed = True
        except UnsuccessfulRequestError as e:

            retriable_err = 'The request was rejected because Route 53 ' \
                            'was still processing a prior request'
            if retriable_err in e.body:
                # pause for a while before send another request
                time.sleep(2.5)
                print_message('Previous request to Route 53 in progress.\n '
                              'Re-sending request...')

    print_message('Weights set for client %s: %s' % (client, weights))
    log_info(metric_record_file,
             'Weights set for client %s: %s' % (client, weights))

    queue.put((client, weights))


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

    stations = get_available_stations()
    for station in stations:
        line_counters.update({station: 0})

    log_base_dir = time.strftime("%Y_%m%d_%H%M")
    total_num_users = cfg.get_int('Default', 'total_num_users')

    # Get all available client region
    available_clients = get_available_clients()

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

        # Measuring latency between each client region and service station
        latency_manager = ThreadingManager()
        latency_manager.start_task(
            target_func=measure_latency,
            name="latency_manager",
            para=[available_clients, stations, measurement_interval]
        )

        server_log_processor = ThreadingManager()
        server_log_processor.start_task(
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
            para=[elb_buckets_dict]
        )

        latency_results_dict = latency_manager.collect_results().get()

        # collecting csparql log first since its processing will complete first
        # while elb data might has delay
        server_metrics_queue = server_log_processor.collect_results()
        (station_metric_list, total_request) = server_metrics_queue.get()
        line_counters = server_metrics_queue.get()

        print_message('')
        print_message('Service station logs processing finished\n')

        # collecting elb data now
        elb_data_queue = data_counting_task.collect_results()
        data_in, data_out = elb_data_queue.get()
        # TODO: work out total requests sent by client from each region

        """ Preparing optimisation parameters """
        # Calculate The "average amount of data involved in each request" for
        # each service station and the "total number of requests"

        # These 2 dictionary stores the average data send and received per
        # request sent and received by *each service station* from *each
        # client*. The length of the dictionary should be equals to the
        # number of clients (regions)

        # <Client_name: <Station: data_in_per_req>>
        avg_data_in_per_reqs = dict()
        # <Client_name: <Station: data_out_per_req>>
        avg_data_out_per_reqs = dict()

        # initialise
        for cli_name in available_clients:
            avg_data_in_per_reqs.update({cli_name: {}})
            avg_data_out_per_reqs.update({cli_name: {}})

        # requests arrival rate and service rate of each service station
        arrival_rates = dict()
        service_rates = dict()

        for station_metric in station_metric_list:
            # getting metric
            station_name = station_metric.station_name
            arrival_rate = station_metric.arrival_rate
            service_rate = station_metric.service_rate

            requests = station_metric.total_requests

            print '\nTotal requests for station %s: %s' \
                  % (station_name, requests)

            log_info(metric_record_file,
                     '\nTotal requests for station %s: %s'
                     % (station_name, requests))

            # arrival_rate and service_rate
            arrival_rates.update({station_name: arrival_rate})
            service_rates.update({station_name: service_rate})

            response_time = \
                math.pow(service_rate, -1) / (1 - math.pow(service_rate, -1) *
                                              arrival_rate)
            print '[Debug] predicted current response time of service station '\
                  '\'%s\': %s' % (station_name, response_time)

            log_info(metric_record_file,
                     '[Debug] predicted currentresponse time of service '
                     'station \'%s\': %s' % (station_name, response_time))

        # TODO: needs to be calculated per client
        # TODO: if c-sparql could record the source of each requests
        # TODO: things would be much more easier
        total_request_per_client = dict()
        data_in_sum = 0
        client_data_in_sum = dict()

        for a_client in available_clients:
            client_data_in_sum.update({a_client: 0})

        for station_name in stations:
            d_in = data_in.get(station_name)
            for c, sent_data in d_in.iteritems():
                # calculate total data sent by each client
                # and the total data sent by all client
                client_data_in_sum[c] += sent_data
                data_in_sum += sent_data

        # calculate total amount of requests sent by each client
        for ac in available_clients:
            t_request = math.ceil(
                total_request * (client_data_in_sum[ac] / data_in_sum))
            t_request = int(t_request)

            # build this so that it could be used by calculating out data
            total_request_per_client.update({ac: t_request})

        for station_name in stations:
            d_in = data_in.get(station_name)

            for c, sent_data in d_in.iteritems():
                t_request = total_request_per_client[c]
                # convert the amount of data to GB
                sent_data = float(sent_data / math.pow(1024, 3))
                avg_data_in_per_req = sent_data / t_request
                avg_data_in_per_reqs[c].update(
                    {station_name: avg_data_in_per_req})

        for station_name in stations:
            d_out = data_out.get(station_name)

            for c1, received_data in d_out.iteritems():
                t_request = total_request_per_client[c1]
                received_data = float(received_data / math.pow(1024, 3))
                avg_data_out_per_req = received_data / t_request
                avg_data_out_per_reqs[c1].update(
                    {station_name: avg_data_out_per_req})

                # # convert the amount of data to GB
                # d_in = float(d_in / math.pow(1024, 3))
                # d_out = float(d_out / math.pow(1024, 3))
                #
                # avg_data_in_per_req = d_in / requests
                # avg_data_out_per_req = d_out / requests
                #
                # avg_data_in_per_reqs.update({station_name: avg_data_in_per_req})
                # avg_data_out_per_reqs.update({station_name: avg_data_out_per_req})

        # For testing purpose
        info_str = \
            '\n[Debug] total_request: %s\n' \
            '[Debug] avg_data_in_per_reqs: %s\n' \
            '[Debug] avg_data_out_per_reqs: %s\n' \
            '[Debug] arrival_rates: %s\n' \
            '[Debug] service_rates: %s\n' \
            % (total_request,
               avg_data_in_per_reqs,
               avg_data_out_per_reqs,
               arrival_rates, service_rates)

        print info_str
        # print '\n[Debug] total_request: %s' % total_request
        # print '[Debug] avg_data_in_per_reqs: %s' % avg_data_in_per_reqs
        # print '[Debug] avg_data_out_per_reqs: %s' % avg_data_out_per_reqs
        # print '[Debug] arrival_rates: %s' % arrival_rates
        # print '[Debug] service_rates: %s\n' % service_rates

        log_info(metric_record_file, info_str)

        # counter += 1
        # time.sleep(20)

        # TODO: Get elb price and SLA from config

        # ELB pricing
        elb_prices = [0.008, 0.008]

        # Service Level Agreement of response time for each station
        # sla_response_t = [1.5, 1.5]

        # optimise for each client...
        # do optimisation for each client in a new threads
        optimiser = ThreadingManager()
        for client in available_clients:
            optimiser.start_tasks(
                target_func=clients_optimisation,
                name="optimiser",
                para=[avg_data_in_per_reqs,
                      avg_data_out_per_reqs, client,
                      elb_prices, latency_results_dict,
                      measurement_interval, service_rates,
                      stations, total_request_per_client]
            )

        # synchronising threads
        optimiser.collect_results()

        # it takes up to 60 mins for Route 53 record changes to take effect
        time.sleep(60)

        # clients_optimisation(avg_data_in_per_reqs,
        # avg_data_out_per_reqs, client,
        # elb_prices, latency_results_dict,
        # measurement_interval, service_rates,
        #                      stations, total_request_per_client)


if __name__ == "__main__":
    main()
    # weights = [162, 40]
    #
    # route53_conn = Route53Connection()
    # zone = route53_conn.get_zone(base_domain)
    #
    # elb_records = station_metadata_map['StationELBDNS']
    #
    # alias_zone_id = {'xueshi-station-1': 'Z32O12XQLNTSW2',
    # 'xueshi-station-2': 'Z35SXDOTRQ7X7K'}
    #
    # # alias_zone_id = {'xueshi-station-1': 'Z3NF1Z3NOM5OY2',
    # #                  'xueshi-station-2': 'Z3DZXE0Q79N41H'}
    #
    # station_region = {'ap_south_1_client_1': 'ireland',
    # 'us_east_1_client_1': 'nvirginia'}
    #
    # identifiers = dict(cfg.items('StationWRRAliasIdentifiers'))
    #
    # stations = get_available_stations()
    # # Since we put optimisation parameter by the order available
    # # stations the output weights should be in the same order
    # station_weights = {}
    # for idx in xrange(len(stations)):
    # station_weights.update({stations[idx]: weights[idx]})
    #
    # rrs = ResourceRecordSets(route53_conn, zone.id)
    #
    # client = 'ap_south_1_client_1'
    #
    # for s_name, weights_val in station_weights.iteritems():
    #     alias_dns_name = elb_records[s_name]
    #     host_zone_id = alias_zone_id[s_name]
    #
    #     # client region not server region
    #     region_name = station_region[client]
    #     dns_record_name = '%s.%s' % (region_name, base_domain)
    #     identifier = identifiers[s_name]
    #     base_record = dict(name=dns_record_name,
    #                        record_type="A", weight=weights_val,
    #                        identifier=identifier)
    #
    #     new = rrs.add_change(action="UPSERT", **base_record)
    #     new.set_alias(host_zone_id, unicode(alias_dns_name), False)
    #
    # change_result = rrs.commit()

    # log_info(metric_record_file, 'Station weights: %s'
    #          % station_weights)
    print 'done'