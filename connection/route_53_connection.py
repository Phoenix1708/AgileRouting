import urllib

from action.route53.hostedzone import HostedZone
from connection.aws_http_connection import AWSHTTPConnection
from utilities.utils import make_qualified


class Route53Connection(AWSHTTPConnection):
    DefaultHost = 'route53.amazonaws.com'

    Version = '2013-04-01'  # Required by the HTTP request URL

    def __init__(self, port=None, host=DefaultHost):
        super(Route53Connection, self).__init__(host, True, port)

    def _target_aws_service(self):
        return ['route53']

    def make_request(self, action, path, response_class=None, headers=None,
                     data='', params=None):
        """Build Route53 specific HTTP URL with query parameters
        """
        if params:
            pairs = []
            for key, val in params.iteritems():
                if val is None:
                    continue
                pairs.append(key + '=' + urllib.quote(str(val)))

            path += '?' + '&'.join(pairs)

        return super(Route53Connection, self).send_request(
            action, path, response_class, headers, data,
            retry_handler=self.retry_handler)

    def list_all_hosted_zones(self):
        """
        Returns a Python data structure with information about all
        Hosted Zones defined for the AWS account.

        """
        params = {}

        list_hosted_zones_response = self.make_request(
            'GET', '/%s/hostedzone' % self.Version,
            'ListHostedZonesResponse', params=params)

        return list_hosted_zones_response.hostedZones

    def list_all_resource_record_sets(self, hosted_zone_id, response_class,
                                      r_type=None, name=None, identifier=None,
                                      max_items=None):
        """
        Get the Resource Record Sets in this Hosted Zone.

        Syntax:

        GET /2013-04-01/hostedzone/Amazon Route 53 hosted zone ID/rrset?
           name=DNS domain name at which to start listing resource record sets
           type=resource record set type&
           identifier=value of SetIdentifier&
           maxitems=maximum number of resource record sets in the response

        :type hosted_zone_id: str
        :param hosted_zone_id: The unique identifier for the Hosted Zone

        :param r_type: The type of resource record set

        :param name: DNS domain name at which to start listing
                     resource record sets

        :param identifier: Weighted, latency, geolocation, and latency
                           resource record identifier

        :param max_items: The maximum number of records

        """
        params = {'type': r_type, 'name': name,
                  'Identifier': identifier, 'maxitems': max_items}
        uri = '/%s/hostedzone/%s/rrset' % (self.Version, hosted_zone_id)
        response = self.make_request('GET', uri, response_class, params=params)

        return response

    def change_resource_record_sets(self, hosted_zone_id, xml_body):
        """
        Sent change resource record sets request

        Returns a Python object with information about the set of
        changes, including the Change ID.

        :type hosted_zone_id: str
        :param hosted_zone_id: The unique identifier for the Hosted Zone

        :type xml_body: str
        :param xml_body: change requests XML message body

        """

        uri = '/%s/hostedzone/%s/rrset' % (self.Version, hosted_zone_id)
        response_class = 'ChangeResourceRecordSetsResponse'
        header = {'Content-Type': 'text/xml'}
        response = self.make_request('POST', uri, response_class,
                                     header, xml_body)
        return response

    def get_zone(self, name):
        """
        Returns a Zone object for the specified Hosted Zone.

        :param name: The fully-specified domain of the domain.
        """
        name = make_qualified(name)
        for zone in self.get_zones():
            if name == zone.name:
                return zone

    def get_zones(self):
        """
        Returns a list of HostedZone objects accessible by the AWS account used.

        :returns: A list of HostedZone objects.

        """
        response = self.list_all_hosted_zones()
        return [HostedZone(self, zone) for zone in response.hostedZones.data]

    @staticmethod
    def retry_handler(response, retry_counter):
        """
        Mainly handle HTTP 400. HTTP 400 error it can be ignored since
        Route53 API has certain limitations, which might cause 400 error

        http://docs.aws.amazon.com/Route53/latest/
        DeveloperGuide/DNSLimitations.html
        """

        # if no 400 detected return none
        status = None

        if response.status == 400:
            code = response.getheader('Code')

            if code and 'PriorRequestNotComplete' in code:
                msg = "'PriorRequestNotComplete' received, " \
                      "retry attempt %s" % retry_counter

                retry_counter += 1
                status = (msg, retry_counter)

        return status
