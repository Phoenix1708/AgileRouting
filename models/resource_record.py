from models.xml_classes.change_resource_record_sets_request import \
    AliasTarget, WeightedAlisaRecordSet, LatencyAlisaRecordSet, \
    WeightedRecordSet, ResourceRecords, ResourceRecord


class Record(object):
    """Represent Route53 DNS Record"""

    def __init__(self, name=None, r_type=None, ttl=600, resource_records=None,
                 alias_hosted_zone_id=None, alias_dns_name=None,
                 identifier=None, weight=None, region=None,
                 alias_evaluate_target_health='false', health_check=None):

        self.name = name
        self.type = r_type
        self.ttl = ttl
        # basic record properties
        if resource_records is None:
            resource_records = []
        self.resource_records = resource_records

        # alias record properties
        self.alias_hosted_zone_id = alias_hosted_zone_id
        self.alias_dns_name = alias_dns_name

        # weighted record properties
        self.identifier = identifier
        self.weight = str(weight)
        self.alias_evaluate_target_health = alias_evaluate_target_health

        # latency record properties
        self.region = region
        self.health_check = health_check

    def set_alias(self, alias_hosted_zone_id, alias_dns_name,
                  alias_evaluate_target_health=False):
        """ Make details for alias resource record set """
        self.alias_hosted_zone_id = alias_hosted_zone_id
        self.alias_dns_name = alias_dns_name
        self.alias_evaluate_target_health = alias_evaluate_target_health

    def to_xml(self):
        """ Convert the record business object to resource record xml object
        for xml serialization """

        # building record properties
        record_properties = dict(Name=self.name+'.',
                                 Type=self.type,
                                 HealthCheckId=self.health_check,
                                 AliasTarget=None,
                                 ResourceRecords=None,
                                 TTL=self.ttl,
                                 SetIdentifier=None,
                                 Weight=None,
                                 Region=None)
        alias_target = None
        resource_records = None

        # preparing alias record
        if self.alias_hosted_zone_id is not None and \
           self.alias_dns_name is not None:

            alias_target = AliasTarget(
                HostedZoneId=self.alias_hosted_zone_id,
                DNSName=self.alias_dns_name,
                EvaluateTargetHealth=
                str(self.alias_evaluate_target_health).lower())
        else:
            # or just normal resource record(s)
            resource_records = ResourceRecords()

            for r in self.resource_records:
                resource_records.ResourceRecords.append(ResourceRecord(Value=r))

        resource_record = None

        # Alias record
        if alias_target:

            record_properties['AliasTarget'] = alias_target

            if self.identifier is not None and self.weight is not None:
                # it is a weighted alias record
                record_properties['SetIdentifier'] = self.identifier
                record_properties['Weight'] = self.weight

                resource_record = WeightedAlisaRecordSet(**record_properties)

            elif self.identifier is not None and self.region is not None:
                # it is a latency alias record now
                record_properties['SetIdentifier'] = self.identifier
                record_properties['Region'] = self.region

                resource_record = LatencyAlisaRecordSet(**record_properties)

        # normal (non-alias) record
        else:

            record_properties['ResourceRecords'] = resource_records

            # the record is an alias record
            if self.identifier is not None and self.weight is not None:
                # it is an weighted alias record
                record_properties['SetIdentifier'] = self.identifier
                record_properties['Weight'] = self.weight

                resource_record = WeightedRecordSet(**record_properties)

            elif self.identifier is not None and self.region is not None:
                # it is an latency record now
                record_properties['SetIdentifier'] = self.identifier
                record_properties['Region'] = self.region

                resource_record = LatencyAlisaRecordSet(**record_properties)

        return resource_record
