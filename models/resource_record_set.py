from models.resource_record import Record
from models.xml_classes.change_resource_record_sets_request import \
    ChangeResourceRecordSetsRequest, Change, ChangeBatch, Changes


class ResourceRecordSets(object):
    """
    Represent Route53 Resource Record Sets
    """

    xml_namespace = 'https://route53.amazonaws.com/doc/2013-04-01/'

    def __init__(self, connection=None, hosted_zone_id=None, comment=None):
        self.connection = connection
        self.hosted_zone_id = hosted_zone_id
        self.comment = comment
        self.changes = []
        self.next_record_name = None
        self.next_record_type = None

    def __repr__(self):
        if self.changes:
            record_list = ','.join([c.__repr__() for c in self.changes])
        else:
            record_list = ','.join([record.__repr__() for record in self])
        return '<ResourceRecordSets:%s [%s]' % (self.hosted_zone_id,
                                                record_list)

    def add_change(self, action, name, record_type, ttl=600,
                   alias_hosted_zone_id=None, alias_dns_name=None,
                   identifier=None,
                   weight=None, region=None, alias_evaluate_target_health=None,
                   health_check=None):
        """
        store record set changes together and commit together.

        :param action: Change action ('CREATE', 'DELETE', 'UPSERT')

        :param name: The domain name whose record that will be changed

        :param record_type: The record type

        :param ttl: The record Time To Live (TTL) value

        :param alias_dns_name: dns name of the alias target

        :param alias_hosted_zone_id: hosted zone id of the alias target

        :param identifier: identifier of Weighted and latency based record

        :param weight: Weighted resource record sets weight

        :param region: Latency based resource record sets region

        :param alias_evaluate_target_health: whether to do health check.

        """
        change = Record(
            name, record_type, ttl,
            alias_hosted_zone_id=alias_hosted_zone_id,
            alias_dns_name=alias_dns_name, identifier=identifier,
            weight=weight, region=region,
            alias_evaluate_target_health=alias_evaluate_target_health,
            health_check=health_check)
        self.changes.append([action, change])
        return change

    def to_xml(self):
        """Building the XML serialization class, which will then be
        serialised to ChangeResourceRecordSetsRequest"""

        # preparing values for the inner most tags
        changes_xml = Changes()

        for change in self.changes:
            action = change[0]
            resource_record_set = change[1].to_xml()
            change_xml = Change(Action=action,
                                ResourceRecordSet=resource_record_set)
            changes_xml.changes.append(change_xml)

        change_batch = ChangeBatch(Comment=self.comment, Changes=changes_xml)

        change_request = ChangeResourceRecordSetsRequest(
            xmlns=self.xml_namespace, change_batch=change_batch)

        return change_request.toXml(prettyPrint=False)

    def commit(self):
        """ Commit current change to Route 53"""
        return self.connection.change_resource_record_sets(self.hosted_zone_id,
                                                           self.to_xml())