from models.xml_classes.change_resource_record_sets_request import \
    AliasTarget, WeightedAlisaRecordSet, LatencyAlisaRecordSet, \
    WeightedRecordSet, ResourceRecords, ResourceRecord

RECORD_TYPES = ['A', 'AAAA', 'TXT', 'CNAME', 'MX', 'PTR', 'SRV', 'SPF']


class Record(object):
    """An individual ResourceRecordSet"""

    HealthCheckBody = """<HealthCheckId>%s</HealthCheckId>"""

    XMLBody = """<ResourceRecordSet>
        <Name>%(name)s</Name>
        <Type>%(type)s</Type>
        %(weight)s
        %(body)s
        %(health_check)s
    </ResourceRecordSet>"""

    WRRBody = """
        <SetIdentifier>%(identifier)s</SetIdentifier>
        <Weight>%(weight)s</Weight>
    """

    RRRBody = """
        <SetIdentifier>%(identifier)s</SetIdentifier>
        <Region>%(region)s</Region>
    """

    ResourceRecordsBody = """
        <TTL>%(ttl)s</TTL>
        <ResourceRecords>
            %(records)s
        </ResourceRecords>"""

    ResourceRecordBody = """<ResourceRecord>
        <Value>%s</Value>
    </ResourceRecord>"""

    AliasBody = """<AliasTarget>
        <HostedZoneId>%(hosted_zone_id)s</HostedZoneId>
        <DNSName>%(dns_name)s</DNSName>
        %(eval_target_health)s
    </AliasTarget>"""

    EvaluateTargetHealth = """<EvaluateTargetHealth>%s</EvaluateTargetHealth>"""

    def __init__(self, name=None, type=None, ttl=600, resource_records=None,
                 alias_hosted_zone_id=None, alias_dns_name=None,
                 identifier=None, weight=None, region=None,
                 alias_evaluate_target_health='false', health_check=None,
                 failover=None):
        self.name = name
        self.type = type
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

    def add_value(self, value):
        """Add a resource record value"""
        self.resource_records.append(value)

    def set_alias(self, alias_hosted_zone_id, alias_dns_name,
                  alias_evaluate_target_health=False):
        """Make this an alias resource record set"""
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

    def to_print(self):
        rr = ""
        if self.alias_hosted_zone_id is not None and self.alias_dns_name is not None:
            # Show alias
            rr = 'ALIAS ' + self.alias_hosted_zone_id + ' ' + self.alias_dns_name
            if self.alias_evaluate_target_health is not None:
                rr += ' (EvalTarget %s)' % self.alias_evaluate_target_health
        else:
            # Show resource record(s)
            rr = ",".join(self.resource_records)

        if self.identifier is not None and self.weight is not None:
            rr += ' (WRR id=%s, w=%s)' % (self.identifier, self.weight)
        elif self.identifier is not None and self.region is not None:
            rr += ' (LBR id=%s, region=%s)' % (self.identifier, self.region)
        elif self.identifier is not None and self.failover is not None:
            rr += ' (FAILOVER id=%s, failover=%s)' % (
                self.identifier, self.failover)

        return rr

    def endElement(self, name, value, connection):
        if name == 'Name':
            self.name = value
        elif name == 'Type':
            self.type = value
        elif name == 'TTL':
            self.ttl = value
        elif name == 'Value':
            self.resource_records.append(value)
        elif name == 'HostedZoneId':
            self.alias_hosted_zone_id = value
        elif name == 'DNSName':
            self.alias_dns_name = value
        elif name == 'SetIdentifier':
            self.identifier = value
        elif name == 'EvaluateTargetHealth':
            self.alias_evaluate_target_health = value.lower() == 'true'
        elif name == 'Weight':
            self.weight = value
        elif name == 'Region':
            self.region = value
        elif name == 'Failover':
            self.failover = value
        elif name == 'HealthCheckId':
            self.health_check = value

    def startElement(self, name, attrs, connection):
        return None
