from __future__ import division
from cvxopt import matrix, solvers
import math

from utilities.utils import print_message


def calculate_cost_coef(total_requests, avg_data_in, avg_data_out, elb_price,
                        prices_ranges, cost_mode):
    cost_coef = 0
    data_out = total_requests * avg_data_out

    # in order for each cost calculation method to be valid we need to
    # add constrain that specify the amount of data for each method and
    # eventually pick the one that is solvable and the result is the largest

    data_constrain_coef = 0

    # x <= 1 GB
    if cost_mode == 0:
        cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
                    + data_out * prices_ranges['First_1_GB']

    # 1GB < x <= 10240 GB
    elif cost_mode == 1:
        cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
                    + data_out * prices_ranges['UP_to_10_TB']

    # 10240 GB < x <= 51200 GB
    elif cost_mode == 2:
        cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
                    + (data_out - 10240) * prices_ranges['Next_40_TB'] \
                    + 10240 * prices_ranges['UP_to_10_TB']

    # 52100 < x <= 153600 GB
    elif cost_mode == 3:
        cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
                    + (data_out - 51200) * prices_ranges['Next_100_TB'] \
                    + 40960 * prices_ranges['Next_40_TB'] \
                    + 10240 * prices_ranges['UP_to_10_TB']

    # 153600 GB < x <= 512000 GB
    elif cost_mode == 4:
        cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
                    + (data_out - 153600) * prices_ranges['Next_350_TB'] \
                    + 102400 * prices_ranges['Next_100_TB'] \
                    + 40960 * prices_ranges['Next_40_TB'] \
                    + 10240 * prices_ranges['UP_to_10_TB']

    return cost_coef


# def add_data_constrain(coefficients_for_p_i, amount_data, cost_mode,
# num_of_stations, idx):
#
# # | #data  0    0    0   ... | < 1 GB
#
# # | #data  0    0    0   ... | > 1 GB
# # | #data  0    0    0   ... | < 10240 GB
#
# # |   0  #data  0    0   ... | > 1 GB
# # |   0  #data  0    0   ... | < 10240 GB
# # ......
#
#     # | #data  0    0    0   ... | > 10240 GB
#     # | #data  0    0    0   ... | < 51200 GB
#     # ......
#
#     # | #data  0    0    0   ... | > 52100 GB
#     # | #data  0    0    0   ... | < 153600 GB
#     # ......
#
#     # | #data  0    0    0   ... | > 153600 GB
#     # | #data  0    0    0   ... | < 512000 GB
#
#     data_amount_coef = [0 for i in xrange(num_of_stations)]
#
#     # x <= 1 GB
#     if cost_mode == 0:
#         data_amount_coef[idx] = amount_data
#         """ Order Matters (same applied to all other mode)
#             Add coefficient for '>' first
#         """
#         coefficients_for_p_i.extend(data_amount_coef * -1)
#         coefficients_for_p_i.extend(data_amount_coef)
#
#     # 1GB < x <= 10240 GB
#     elif cost_mode == 1:
#         cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
#                     + data_out * prices_ranges['UP_to_10_TB']
#
#     # 10240 GB < x <= 51200 GB
#     elif cost_mode == 2:
#         cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
#                     + (data_out - 10240) * prices_ranges['Next_40_TB'] \
#                     + 10240 * prices_ranges['UP_to_10_TB']
#
#     # 52100 < x <= 153600 GB
#     elif cost_mode == 3:
#         cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
#                     + (data_out - 51200) * prices_ranges['Next_100_TB'] \
#                     + 40960 * prices_ranges['Next_40_TB'] \
#                     + 10240 * prices_ranges['UP_to_10_TB']
#
#     # 153600 GB < x <= 512000 GB
#     elif cost_mode == 4:
#         cost_coef = total_requests * (avg_data_in + avg_data_out) * elb_price \
#                     + (data_out - 153600) * prices_ranges['Next_350_TB'] \
#                     + 102400 * prices_ranges['Next_100_TB'] \
#                     + 40960 * prices_ranges['Next_40_TB'] \
#                     + 10240 * prices_ranges['UP_to_10_TB']


def optimise(num_of_stations, total_requests, elb_prices,
             avg_data_in_per_reqs, avg_data_out_per_reqs,
             in_bandwidths, out_bandwidths, budget,
             service_rates, sla_response_t, measurement_interval, k,
             ec2_prices_ranges=None, cost_mode=None):
    """
    :param num_of_stations: total number of receipts of client requests
    :param total_requests:  total number of requests generated by client
    :param elb_prices:      list of pricing of every ELB involved

    :param avg_data_in_per_reqs:    the average amount of data transferred in
                                    pre request for requests received at
                                    *each service station*

    :param avg_data_out_per_reqs:   the average amount of data transferred out
                                    pre request for requests received at
                                    *each service station*

    :param in_bandwidths:   The capacity of the link used by each service
                            station to receive request
    :param out_bandwidths:  The capacity of the link used by each service
                            station to send response

    :param service_rates:   Overall service rate of each service station
    :param sla_response_t:  Service Level Agreement of the response time
                            for each service station

    :param budget:          Budget of the OSP

    :param k:               coefficient to reflect on how much additional
                            cost to pay for one unit of throughput improvement

    :param measurement_interval: The length of measurement time (in seconds)

    :param ec2_prices_ranges:   The price charged by EC2 based on different
                                amount of data sent out of EC2 (Dict of dict)
    :param cost_mode:           Mode for selecting different EC2 data trans

    :return:                The current best weight for each requests receipt


    # Objective: (e.g number of service station = 2)
    # maximise  Cost + K * throughput
    #
    # total_requests *
    # (avg_data_in_per_req[0] + avg_data_out_per_req[0]) *
    # elb_price[0] *
    # P[0]
    # +
    #         total_requests * avg_data_out_per_req[0] * P[0] * ec2_price_range
    #         +
    #         K * total_requests *
    #         P[0]

    #         +

    #         total_requests *
    #         (avg_data_in_per_req[1] + avg_data_out_per_req[1]) *
    #         elb_price[1] *
    #         P[1]
    #         +
    #         total_requests * avg_data_out_per_req[0] * P[0] * ec2_price_range
    #         +
    #         K * total_requests *
    #         P[1]

    #         "Actually formulation":

    #         (total_requests *
    #         (avg_data_in_per_req[0] + avg_data_out_per_req[0]) *
    #         elb_price[0]
    #         +
    #         K * total_requests
    #         +
    #         total_requests * avg_data_out_per_req[0] * ec2_price_range) * P[0]
    #
    #         +
    #
    #         (total_requests *
    #         (avg_data_in_per_req[1] + avg_data_out_per_req[1]) *
    #         elb_price[1]
    #         +
    #         K * total_requests
    #         +
    #         total_requests * avg_data_out_per_req[1] * ec2_price_range) * P[1]

    #
    # Subject to:

    #   "data_in/second < bandwidth of the in_link"

    #   (total_requests * avg_data_in_per_req[0] * P[0]))
    #   / measurement_interval < in_bandwidth[0]

    #   (total_requests * avg_data_in_per_req[1] * P[1]))
    #   / measurement_interval < in_bandwidth[1]

    #   "data_out/second < bandwidth of the out_link"

    #   (total_requests * avg_data_out_per_req[0] * P[0]))
    #   / measurement_interval < out_bandwidth[0]

    #   (total_requests * avg_data_out_per_req[1] * P[1]))
    #   / measurement_interval < out_bandwidth[1]

    #   "Actually formulation":
    #
    #   total_requests * avg_data_in_per_req[0] / measurement_interval * P[0] +
    #                    0                                             * P[1]
    #                                                      <= in_bandwidth[0]

    #                    0                                             * P[0] +
    #   total_requests * avg_data_in_per_req[1] / measurement_interval * P[1]
    #                                                      <= in_bandwidth[1]

    #   total_requests * avg_data_out_per_req[0] / measurement_interval * P[0] +
    #                    0                                              * P[1]
    #                                                      <= out_bandwidth[0]

    #                    0                                              * P[0] +
    #   total_requests * avg_data_out_per_req[1] / measurement_interval * P[1]
    #                                                      <= out_bandwidth[1]



    #   "Response time constrain"

    #   D_sla[0] * service_rates[0]^-1 * total_requests * P[0]
    #           <= measurement_interval * (D_sla[0] - service_rates[0]^-1)

    #   D_sla[1] * service_rates[1]^-1 * total_requests * P[1]
    #           <= measurement_interval * (D_sla[1] - service_rates[1]^-1)

    #   "Actually formulation":

    #   D_sla[0] * service_rates[0]^-1 * total_requests * P[0] +
    #                    0                              * P[1]
    #           <= measurement_interval * (D_sla[0] - service_rates[0]^-1)

    #                    0                              * P[0] +
    #   D_sla[1] * service_rates[1]^-1 * total_requests * P[1]
    #           <= measurement_interval * (D_sla[1] - service_rates[1]^-1)


    #   "Budget of OSP" (EC2 cost is calculated differently)
    #   total_requests * (avg_data_in_per_reqs[0] +
    #                     avg_data_out_per_reqs[0]) * elb_prices[0] * P[0]
    #   +
    #
    #   total_requests * (avg_data_in_per_reqs[1] +
    #                     avg_data_out_per_reqs[1]) * elb_prices[1] * P[1]
    #           <= budget


    #   "Sum of weights is 1"
    #   P[0] + P[1] + ... P[num Of Servers - 1] = 1

    #   "P are all positive"
    #   1 * P[0] + 0 * P[1] + 0 * P[2] .... > 0
    #   0 * P[0] + 1 * P[1] + 0 * P[2] .... > 0
    #   0 * P[0] + 0 * P[1] + 1 * P[2] .... > 0
    #   ... ...
    #
    # Variable: P[i]
    """

    coefficients = []
    # right hand side of constrains
    right_hand_side = []
    # coefficients in objective function
    obj_func_coef = []

    for i in xrange(num_of_stations):
        # Building coefficients for constrains inequations.

        # Collecting coefficients of each variable of each constrains inequation

        """ In bandwidth constrains """
        # | t*a/m  0    0    0   ... | < in_bandwidth[0]
        # |   0  t*a/m  0    0   ... | < in_bandwidth[1]
        # |   0    0  t*a/m  0   ... | < in_bandwidth[2]
        # |   0    0    0  t*a/m ... | ... ...
        in_bandwidth_coef = [0 for i1 in xrange(num_of_stations)]
        in_bandwidth_coef[i] = \
            total_requests * avg_data_in_per_reqs[i] / measurement_interval

        """ Out bandwidth constrains """
        out_bandwidth_coef = [0 for i2 in xrange(num_of_stations)]
        out_bandwidth_coef[i] = \
            total_requests * avg_data_out_per_reqs[i] / measurement_interval

        """ Response time constrain """
        response_t_coef = [0 for i3 in xrange(num_of_stations)]
        response_t_coef[i] = \
            sla_response_t[i] * math.pow(service_rates[i], -1) * total_requests

        """ All variable (weights) are positive """
        all_pos_coef = [0 for i4 in xrange(num_of_stations)]
        all_pos_coef[i] = -1  # convert to standard form

        """ coefficient for the "sum of weights is 1" constrain (i.e all 1) """
        sum_p_coef = 1

        """ Cost less then or equal to budget """
        # EC2_cost = 0.9312 * total_data_out * P + 196.6
        # (for data less than 40TB)
        # cost_coef = \
        #     total_requests * (avg_data_in_per_reqs[i] +
        #                       avg_data_out_per_reqs[i]) * elb_prices[i] + \
        #     0.9312 * total_requests * avg_data_out_per_reqs[i]
        #
        # #### test ####
        # print_message('Total cost : %s $' % (cost_coef + 192.6))
        # #### test ####

        #TODO: plus previous value ?
        cost_coef = \
            total_requests * (avg_data_in_per_reqs[i] +
                              avg_data_out_per_reqs[i]) * elb_prices[i] + \
            0.120 * total_requests * avg_data_out_per_reqs[i]

        #### test ####
        print_message('Total cost : $%s' % cost_coef)
        #### test ####

        # Store all coefficients for this variable in the above order
        """ Order matters """
        coefficients_for_p_i = []
        coefficients_for_p_i.extend(in_bandwidth_coef)
        coefficients_for_p_i.extend(out_bandwidth_coef)
        coefficients_for_p_i.extend(response_t_coef)
        coefficients_for_p_i.extend(all_pos_coef)
        # in order to turn the "sum of weights is 1" equability constrain to
        # inequality constrain, replace the original equality constrain with
        # 2 new inequality that represent a very tiny range around the original
        # right hand side of the equability constrain
        # P1 + P2 + P3 + .... > 1 - 0.0000000001
        # P1 + P2 + P3 + .... < 1 + 0.0000000001
        coefficients_for_p_i.append(sum_p_coef * -1)
        coefficients_for_p_i.append(sum_p_coef)
        coefficients_for_p_i.append(cost_coef)

        # """ Cost less then or equal to budget """
        # # Cost needs to be calculated differently
        # cost_coef = calcualte_cost_coef(total_requests,
        #                                 avg_data_in_per_reqs[i],
        #                                 avg_data_out_per_reqs[i],
        #                                 elb_prices[i], ec2_prices_ranges[i],
        #                                 cost_mode)
        # #### test ####
        # print_message('Total cost in mode %s : %s' % (cost_mode, cost_coef))
        # #### test ####
        #
        # # coefficient for total cost less than budget
        # coefficients_for_p_i.append(cost_coef)
        #
        # # constrain of the amount of data sent
        # total_requests * avg_data_out_per_reqs[i]
        # coefficients_for_p_i.append()

        # add this list in the coefficient collection as the coefficient of
        # current variable i.e weight
        coefficients.append(coefficients_for_p_i)

        # Building objective function coefficient for this variable
        obj_p_i_coef = \
            total_requests * (avg_data_in_per_reqs[i] +
                              avg_data_out_per_reqs[i]) * elb_prices[i] + \
            k * total_requests + \
            0.120 * total_requests * avg_data_out_per_reqs[i]

        # maximise = minimise the negative form
        obj_func_coef.append(obj_p_i_coef * -1)

    """ Order Matters """
    # Now adding right hand side.
    # Right hands side has to be added in the order that coefficients was added
    # e.g in_bandwidths -> out_bandwidths -> Response time constrains -> ...
    right_hand_side.extend([in_bandwidths[n] for n in xrange(num_of_stations)])
    right_hand_side.extend([out_bandwidths[m] for m in xrange(num_of_stations)])
    right_hand_side.extend(
        [measurement_interval *
         (sla_response_t[k] - math.pow(service_rates[k], -1))
         for k in xrange(num_of_stations)]
    )
    right_hand_side.extend([0 for j in xrange(num_of_stations)])
    right_hand_side.append(0.0000000001 - 1)
    right_hand_side.append(1 + 0.0000000001)
    right_hand_side.append(budget)

    print 'coefficients: %s' % coefficients
    print 'right_hand_side: %s' % right_hand_side
    print 'obj_func_coef: %s' % obj_func_coef

    a = matrix(coefficients)
    b = matrix(right_hand_side)
    c = matrix(obj_func_coef)

    sol = solvers.lp(c, a, b)

    # solvers.qp()

    return sol['x']


# if __name__ == '__main__':
#     A = matrix([[-1.0, -1.0, 0.0, 1.0], [1.0, -1.0, -1.0, -2.0]])
#     b = matrix([1.0, -2.0, 0.0, 4.0])
#     c = matrix([2.0, 1.0])
#     sol = solvers.lp(c, A, b)
#
#     print(sol['x'])
#     test = [sol['x'][i] for i in xrange(2)]
#     print test
#     print sol['x'][0]
#     print sol['x'][1]
#     print sol['x'][2]

    # coefficients = [[
    #      0,
    #      1.5316553365099901e-07,
    #      0,
    #      0.001320873620062156,
    #      0,
    #      871.7494370007444,
    #      0,
    #      -1,
    #      -1,
    #      1,
    #      0.0757350879782905],
    #
    #      [0, 1.5316553365099901e-07, 0, 0.001320873620062156, 0,
    #       871.7494370007444, 0, -1, -1, 1, 0.0757350879782905]]
    #
    # right_hand_side = [
    #     0.04541015625,
    #     0.04748535156,
    #     0.04541015625,
    #     0.04748535156,
    #     550.6225874560688,
    #     560.8050746057617,
    #     0,
    #     0,
    #     -0.9999999999,
    #     1.0000000001,
    #     1000000]
    #
    # obj_func_coef = [23429.924264912024, 23429.924264912024]
    #
    # a = matrix(coefficients)
    # b = matrix(right_hand_side)
    # c = matrix(obj_func_coef)
    #
    # sol = solvers.lp(c, a, b)
    #
    # print sol['x']

    # test = optimise(2, 1000, [0.008, 0.010], [29, 50], [100, 200], [50, 100],
    #                 [0.5, 0.6], 4 / 5)
    #
    # test2 = optimise(2, 1000, [0.008, 0.008], [29, 29], [100, 100],
    #                  [5000, 5000], [0.5, 0.5], 4 / 5)

    # print test
    # print test2