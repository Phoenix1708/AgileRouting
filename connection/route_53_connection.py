import urllib
import uuid
import xml.sax

from action.route53.zone import Zone
from connection.AWSConnection import AWSConnection
from etc.configuration import log
from models import xml_response
from models.resource_record_set import ResourceRecordSets
from utilities import exception
from utilities import xml_handler as handler


class Route53Connection(AWSConnection):
    DefaultHost = 'route53.amazonaws.com'
    """The default Route53 API endpoint to connect to."""

    Version = '2013-04-01'
    """Route53 API version."""

    XMLNameSpace = 'https://route53.amazonaws.com/doc/2013-04-01/'
    """XML schema for this Route53 API version."""

    def __init__(self, port=None, proxy=None, proxy_port=None,
                 host=DefaultHost):

        super(Route53Connection, self).__init__(host, True, port, proxy,
                                                proxy_port)

    def _required_auth_capability(self):
        return ['route53']

    def send_request(self, action, path, response_class=None, headers=None,
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
            retry_handler=self._retry_handler)

    def get_all_hosted_zones(self, start_marker=None):
        """
        Returns a Python data structure with information about all
        Hosted Zones defined for the AWS account.

        :param int start_marker: start marker to pass when fetching additional
            results after a truncated list
        """
        params = {}
        if start_marker:
            params = {'marker': start_marker}

        list_hosted_zones_response = self.send_request(
            'GET', '/%s/hostedzone' % self.Version,
            'ListHostedZonesResponse', params=params)

        return list_hosted_zones_response.hostedZones

    def get_hosted_zone(self, hosted_zone_id):
        """
        Get detailed information about a particular Hosted Zone.

        :type hosted_zone_id: str
        :param hosted_zone_id: The unique identifier for the Hosted Zone

        """
        uri = '/%s/hostedzone/%s' % (self.Version, hosted_zone_id)
        response = self.send_request('GET', uri)
        body = response.read()
        log.debug(body)

        if response.status >= 300:
            raise exception.UnsuccessfulRequestError(response.status,
                                           response.reason,
                                           body)
        e = xml_response.Element(list_marker='NameServers',
                                 item_marker=('NameServer',))
        h = xml_response.XmlHandler(e, None)
        h.parse(body)
        return e

    def get_hosted_zone_by_name(self, hosted_zone_name):
        """
        Get detailed information about a particular Hosted Zone.

        :type hosted_zone_name: str
        :param hosted_zone_name: The fully qualified domain name for the Hosted
            Zone

        """
        if hosted_zone_name[-1] != '.':
            hosted_zone_name += '.'
        all_hosted_zones = self.get_all_hosted_zones()
        for zone in all_hosted_zones['ListHostedZonesResponse']['HostedZones']:
            # check that they gave us the FQDN for their zone
            if zone['Name'] == hosted_zone_name:
                return self.get_hosted_zone(zone['Id'].split('/')[-1])

    # def create_hosted_zone(self, domain_name, caller_ref=None, comment=''):
    #     """
    #     Create a new Hosted Zone.  Returns a Python data structure with
    #     information about the newly created Hosted Zone.
    #
    #     :type domain_name: str
    #     :param domain_name: The name of the domain. This should be a
    #         fully-specified domain, and should end with a final period
    #         as the last label indication.
    #
    #     :type caller_ref: str
    #     :param caller_ref: A unique string that identifies the request
    #         and that allows failed CreateHostedZone requests to be retried
    #         without the risk of executing the operation twice.
    #
    #     :type comment: str
    #     :param comment: Any comments you want to include about the hosted
    #         zone.
    #
    #     """
    #     if caller_ref is None:
    #         caller_ref = str(uuid.uuid4())
    #     params = {'name': domain_name,
    #               'caller_ref': caller_ref,
    #               'comment': comment,
    #               'xmlns': self.XMLNameSpace}
    #     xml_body = HZXML % params
    #     uri = '/%s/hostedzone' % self.Version
    #     response = self.send_request('POST', uri,
    #                                  {'Content-Type': 'text/xml'}, xml_body)
    #     body = response.read()
    #     log.debug(body)
    #
    #     if response.status == 201:
    #         e = xml_response.Element(list_marker='NameServers',
    #                                  item_marker=('NameServer',))
    #         h = xml_response.XmlHandler(e, None)
    #         h.parse(body)
    #         return e
    #     else:
    #         raise exception.UnsuccessfulRequestError(response.status,
    #                                        response.reason,
    #                                        body)

    # def delete_hosted_zone(self, hosted_zone_id):
    #     """
    #     Delete the hosted zone specified by the given id.
    #
    #     :type hosted_zone_id: str
    #     :param hosted_zone_id: The hosted zone's id
    #
    #     """
    #     uri = '/%s/hostedzone/%s' % (self.Version, hosted_zone_id)
    #     response = self.send_request('DELETE', uri)
    #     body = response.read()
    #     log.debug(body)
    #
    #     if response.status not in (200, 204):
    #         raise exception.UnsuccessfulRequestError(response.status,
    #                                        response.reason,
    #                                        body)
    #     e = xml_response.Element()
    #     h = xml_response.XmlHandler(e, None)
    #     h.parse(body)
    #     return e

    def get_all_rrsets(self, hosted_zone_id, type=None,
                       name=None, identifier=None, maxitems=None):
        """
        Retrieve the Resource Record Sets defined for this Hosted Zone.
        Returns the raw XML data returned by the Route53 call.

        :type hosted_zone_id: str
        :param hosted_zone_id: The unique identifier for the Hosted Zone

        :type type: str
        :param type: The type of resource record set to begin the record
            listing from.  Valid choices are:

                * A
                * AAAA
                * CNAME
                * MX
                * NS
                * PTR
                * SOA
                * SPF
                * SRV
                * TXT

            Valid values for weighted resource record sets:

                * A
                * AAAA
                * CNAME
                * TXT

            Valid values for Zone Apex Aliases:

                * A
                * AAAA

        :type name: str
        :param name: The first name in the lexicographic ordering of domain
                     names to be retrieved

        :type identifier: str
        :param identifier: In a hosted zone that includes weighted resource
            record sets (multiple resource record sets with the same DNS
            name and type that are differentiated only by SetIdentifier),
            if results were truncated for a given DNS name and type,
            the value of SetIdentifier for the next resource record
            set that has the current DNS name and type

        :type maxitems: int
        :param maxitems: The maximum number of records

        """
        params = {'type': type, 'name': name,
                  'Identifier': identifier, 'maxitems': maxitems}
        uri = '/%s/hostedzone/%s/rrset' % (self.Version, hosted_zone_id)
        response = self.send_request('GET', uri, params=params)
        body = response.read()
        log.debug(body)
        if response.status >= 300:
            raise exception.UnsuccessfulRequestError(response.status,
                                           response.reason,
                                           body)
        rs = ResourceRecordSets(connection=self, hosted_zone_id=hosted_zone_id)
        h = handler.XmlHandler(rs, self)
        xml.sax.parseString(body, h)
        return rs

    def change_rrsets(self, hosted_zone_id, xml_body):
        """
        Create or change the resource record set.
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
        response = self.send_request('POST', uri, response_class,
                                     header, xml_body)

        return response

        # body = response.read()
        # log.debug(body)
        #
        # if response.status >= 300:
        #     raise exception.DNSServerError(response.status,
        #                                    response.reason,
        #                                    body)
        #
        #
        #
        # e = xml_response.Element()
        # h = xml_response.XmlHandler(e, None)
        # h.parse(body)
        # return e

    def get_change(self, change_id):
        """
        Get information about a proposed set of changes, as submitted
        by the change_rrsets method.
        Returns a Python data structure with status information about the
        changes.

        :type change_id: str
        :param change_id: The unique identifier for the set of changes.
            This ID is returned in the response to the change_rrsets method.

        """
        uri = '/%s/change/%s' % (self.Version, change_id)
        response = self.send_request('GET', uri)
        body = response.read()
        log.debug(body)

        if response.status >= 300:
            raise exception.UnsuccessfulRequestError(response.status,
                                           response.reason,
                                           body)
        e = xml_response.Element()
        h = xml_response.XmlHandler(e, None)
        h.parse(body)
        return e

    def create_zone(self, name):
        """
        Create a new Hosted Zone.  Returns a Zone object for the newly
        created Hosted Zone.

        :type name: str
        :param name: The name of the domain. This should be a
            fully-specified domain, and should end with a final period
            as the last label indication.  If you omit the final period,
            Amazon Route 53 assumes the domain is relative to the root.
            This is the name you have registered with your DNS registrar.
            It is also the name you will delegate from your registrar to
            the Amazon Route 53 delegation servers returned in
            response to this request.
        """
        zone = self.create_hosted_zone(name)
        return Zone(self, zone['CreateHostedZoneResponse']['HostedZone'])

    def get_zone(self, name):
        """
        Returns a Zone object for the specified Hosted Zone.

        :param name: The name of the domain. This should be a
            fully-specified domain, and should end with a final period
            as the last label indication.
        """
        name = self._make_qualified(name)
        for zone in self.get_zones():
            if name == zone.name:
                return zone

    def get_zones(self):
        """
        Returns a list of Zone objects accessible via the AWS account.

        :rtype: list
        :returns: A list of Zone objects.

        """
        response = self.get_all_hosted_zones()
        return [Zone(self, zone) for zone in response.hostedZones.data]

    def _make_qualified(self, value):
        """
        Ensure passed domain names end in a period (.) character.
        This will usually make a domain fully qualified.
        """
        if type(value) in [list, tuple, set]:
            new_list = []
            for record in value:
                if record and not record[-1] == '.':
                    new_list.append("%s." % record)
                else:
                    new_list.append(record)
            return new_list
        else:
            value = value.strip()
            if value and not value[-1] == '.':
                value = "%s." % value
            return value

    def _retry_handler(self, response, retry_counter):
        """
        Mainly handle HTTP 400. HTTP 400 error it can be ignored since
        Route53 API has certain limitations, which might cause 400 error
        """

        # if no 400 detected return none
        status = None
        log.debug("HTTP response status: %s" % response.status)

        if response.status == 400:
            code = response.getheader('Code')

            if code and 'PriorRequestNotComplete' in code:
                msg = "'PriorRequestNotComplete' received, " \
                      "retry attempt %s" % retry_counter

                # wait_time = min(random.random() * (2 ** retry_counter),
                # cfg.get('HTTPConnection',
                #                          'max_retry_delay', 60))

                retry_counter += 1
                status = (msg, retry_counter)

        return status
