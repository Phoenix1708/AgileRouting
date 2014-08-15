from connection.s3_connection import S3Connection
from data_parser.client_server.process_logs import process_logs
from data_parser.optimization import optimise
from data_parser.s3.process_access_log import process_access_log
from etc.configuration import setup_logging
from utilities.multi_threading import ThreadingManager
from utilities.utils import get_station_region, get_stations


def counting_elb_data(bucket, elb, queue):
    """ S3 log processing thread content.

    :param bucket:      The bucket that stores access log
    :param elb          String representation of Elastic load balancer name
                        and region (elb_name:elb_region)
    :param queue:       A queue to store result for each buckets
    :return:            String representation of the total amount of data
                        processed by elb
    """

    elb_name, elb_region = elb.split(':')
    results = process_access_log(bucket, elb_region, elb_name)

    total_receive, total_sent = results.split(',')

    # convert bucket name and total amount of data in to string
    # so that the element in queue can have bucket name info
    data_str = '%s=%s,%s' % (elb_name, total_receive, total_sent)
    queue.put(data_str)


def main():
    setup_logging()

    # bucket and ELB info for getting access log from S3
    elb_buckets_dict = dict()
    elb_regions = get_station_region()
    for station, region in elb_regions:
        elb_region_str = '%s:%s' % (station, region)
        elb_buckets_dict.update({elb_region_str: u'xueshi-ireland-elb-logs'})

    # collecting access log for each elb with different threads
    elb_data_manager = ThreadingManager()

    # line counter for reading csparql logs of each service station
    line_counters = dict()
    stations = get_stations()
    for station in stations:
        line_counters.update({station: 0})

    counter = 0  # For testing
    while counter < 5:  # True:
        # begin gathering info of the amount of data
        # transferred stored in S3 bucket
        for elb, bucket in elb_buckets_dict.iteritems():
            c = S3Connection()
            bucket = c.get_bucket(bucket)

            elb_data_manager.start_tasks(
                target_func=counting_elb_data,
                name="elb_data_collector",
                para=[bucket, elb]
            )

        # waiting for all threads to finish parsing S3 log
        # by which time it will be the end of measurement interval
        result_queue = elb_data_manager.collect_results()

        # collect the total data processed by each ELB
        # '%s=%s,%s' % (station name, total_receive, total_sent)
        data_in = dict()
        data_out = dict()
        while not result_queue.empty():
            station, data_str = result_queue.get().split('=')
            data_received, data_sent = data_str.split(',')
            data_in.update({station: data_received})
            data_out.update({station: data_sent})

        # Begin reading logs from OFBench client.
        # The line_counters is maintained here for continuous log reading
        # total_requests, line_counters = process_client_logs(line_counters)

        # Begin reading csparql logs
        # The line_counters is maintained here for continuous log reading
        service_station_metric_list, line_counters = process_logs(line_counters)

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
            service_rate = service_station_metric.service_rates
            requests = service_station_metric.total_requests

            # total requests from clients
            total_request += requests
            # arrival_rate and service_rate
            arrival_rates.update({station_name: arrival_rate})
            service_rates.update({station_name: service_rate})

            # calculate average data sent and receive
            d_in = data_in.get(station_name)
            d_out = data_out.get(station_name)
            # convert the amount of data to KB in order to calculate
            # cost using the ELB pricing
            d_in = float(d_in / 1024)
            d_out = float(d_out / 1024)

            avg_data_in_per_req = d_in / requests
            avg_data_out_per_req = d_out / requests

            avg_data_in_per_reqs.update({station_name: avg_data_in_per_req})
            avg_data_out_per_reqs.update({station_name: avg_data_out_per_req})

        # For testing purpose
        print 'total_request: %s' % total_request
        print 'avg_data_in_per_reqs: %s' % avg_data_in_per_reqs
        print 'avg_data_out_per_reqs: %s' % avg_data_out_per_reqs
        print 'arrival_rates: %s' % arrival_rates
        print 'service_rates: %s' % service_rates

        counter += 1

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