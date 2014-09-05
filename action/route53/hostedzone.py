from utilities.utils import make_qualified


class HostedZone(object):
    """
    Route53 Hosted Zone business model which contains
    properties of the hosted zone.
    """

    def __init__(self, route53connection, zone):
        self.route53connection = route53connection

        # convert zone xml object attributes to
        # zone business object attributes
        zone_attributes = vars(zone).__getitem__('_attributes')
        for attr in zone_attributes:
            attr_value = zone_attributes[attr]
            attr = attr.replace('_XO_', '')
            if attr == 'Id':
                self.id = attr_value.replace('/hostedzone/', '')
            else:
                self.__setattr__(attr.lower(), attr_value)

    def __repr__(self):
        return '<Zone:%s>' % self.name

    def find_records(self, name, r_type, identifier=None):
        """
        Search for match records in this Zone.

        :param name: The name of the records

        :param r_type: The type of the records

        :param identifier: Identifier for Weighted, latency, geolocation,
                           and latency resource record sets
        """
        name = make_qualified(name)

        self.route53connection.list_all_resource_record_sets(
            self.id, name=name, r_type=r_type, identifier=identifier)


