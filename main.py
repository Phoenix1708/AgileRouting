import time
from data_parser.client_server.server_log_processor import process_server_logs
from data_parser.s3.process_access_log import process_elb_access_log
from etc.configuration import setup_logging
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_station_region, get_stations


def main():
    setup_logging()

    # line counter for reading csparql logs of each service station
    line_counters = dict()

    # bucket and ELB info for getting access log from S3
    elb_buckets_dict = dict()
    elb_regions = get_station_region()
    for station, region in elb_regions.iteritems():
        elb_region_str = '%s:%s' % (station, region)
        elb_buckets_dict.update({elb_region_str: u'xueshi-ireland-elb-logs'})

    # collecting access log for each elb with different threads
    elb_data_manager = ThreadingManager()

    stations = get_stations()
    for station in stations:
        line_counters.update({station: 0})

    log_base_dir = time.strftime("%Y_%m%d_%H%M")

    counter = 0  # For testing
    while counter < 5:  # True:

        # parsing csparql log and ELB access log simultaneously by 2 threads

        # Start csparql log paring first since ELB access log has delay
        # omitting the log file
        csparql_log_parser = ThreadingManager()
        csparql_log_parser.start_task(
            target_func=process_server_logs,
            name="server_log_processor",
            para=[log_base_dir, line_counters]
        )

        # Begin gathering info of the amount of data
        # transferred through each service station
        # data_counting_task = ThreadingManager()
        # data_counting_task.start_task(
        #     target_func=process_elb_access_log,
        #     name="elb_access_log_processor",
        #     para=[elb_buckets_dict, elb_data_manager]
        # )
        #
        # # collecting elb data first since it has delay
        # elb_data_queue = data_counting_task.collect_results()
        # data_in = elb_data_queue.get()
        # data_out = elb_data_queue.get()

        csparql_log_queue = csparql_log_parser.collect_results()
        service_station_metric_list = csparql_log_queue.get()
        line_counters = csparql_log_queue.get()

        # Begin reading logs from OFBench client.
        # The line_counters is maintained here for continuous log reading
        # total_requests, line_counters = process_client_logs(line_counters)

        """Preparing optimisation parameters"""
        # Calculate The "average amount of data involved in each request" for
        # each service station and the "total number of requests"
        total_request = 0
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

            # total requests from clients
            total_request += int(requests)
            # arrival_rate and service_rate
            arrival_rates.update({station_name: arrival_rate})
            service_rates.update({station_name: service_rate})

            # calculate average data sent and receive
            # d_in = data_in.get(station_name)
            # d_out = data_out.get(station_name)

            # convert the amount of data to KB in order to calculate
            # cost using the ELB pricing
            # d_in = float(d_in / 1024)
            # d_out = float(d_out / 1024)
            #
            # avg_data_in_per_req = d_in / requests
            # avg_data_out_per_req = d_out / requests
            #
            # avg_data_in_per_reqs.update({station_name: avg_data_in_per_req})
            # avg_data_out_per_reqs.update({station_name: avg_data_out_per_req})

        # For testing purpose
        print 'total_request: %s' % total_request
        print 'avg_data_in_per_reqs: %s' % avg_data_in_per_reqs
        print 'avg_data_out_per_reqs: %s' % avg_data_out_per_reqs
        print 'arrival_rates: %s' % arrival_rates
        print 'service_rates: %s' % service_rates
        counter += 1
        # time.sleep(20)

        # TODO: Delay service level agreement, cost budget

        # ELB pricing
        # elb_prices = [0.008, 0.011]
        # maximum bandwidths for each client
        # bandwidths = []
        # service capacity of each service station
        # service_caps = []

        # optimisation
        # weights = optimisation()

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
        #                    type="A", weight=weight_a,
        #                    identifier="Ireland")
        #
        # rrs = ResourceRecordSets(conn, zone.id)
        # new = rrs.add_change(action="UPSERT", **base_record)
        # new.set_alias('Z32O12XQLNTSW2', Ireland_ELB, False)
        # change_result = rrs.commit()


if __name__ == "__main__":
    main()
    print 'done'