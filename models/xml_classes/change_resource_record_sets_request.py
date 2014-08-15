from EaseXML import *
from models.xml_classes.xml_class import XMLClass

"""
<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
<ChangeBatch>
   <Comment>optional comment about the changes in this
      change batch request</Comment>
   <Changes>
      <Change>
         <Action>CREATE | DELETE | UPSERT</Action>
         <ResourceRecordSet>
            <Name>DNS domain name</Name>
            <Type>DNS record type</Type>
            <SetIdentifier>unique description for this
               resource record set</SetIdentifier>
            <Weight>value between 0 and 255</Weight>
            <AliasTarget>
               <HostedZoneId>hosted zone ID for your
                  CloudFront distribution, Amazon S3 bucket,
                  Elastic Load Balancing load balancer,
                  or Amazon Route 53 hosted zone</HostedZoneId>
               <DNSName>DNS domain name for your
                  CloudFront distribution, Amazon S3 bucket,
                  Elastic Load Balancing load balancer,
                  or another resource record set
                  in this hosted zone</DNSName>
               <EvaluateTargetHealth>true | false</EvaluateTargetHealth>
            </AliasTarget>
            <HealthCheckId>optional ID of a
               Amazon Route 53 health check</HealthCheckId>
         </ResourceRecordSet>
      </Change>
      ...
   </Changes>
</ChangeBatch>
</ChangeResourceRecordSetsRequest>
"""


class ChangeResourceRecordSetsRequest(XMLClass):
    xmlns = StringAttribute()
    change_batch = ItemNode(u'ChangeBatch')


class ChangeBatch(XMLObject):
    _nodesOrder = [u'Comment', u'Changes']
    Comment = TextNode()
    Changes = ItemNode(u'Changes')


class Changes(XMLObject):
    changes = ListNode(u'Change')


class Change(XMLObject):
    _nodesOrder = [u'Action', u'ResourceRecordSet']
    Action = TextNode()
    ResourceRecordSet = ItemNode(u'ResourceRecordSet')


class ResourceRecordSet(XMLObject):
    Name = TextNode()
    Type = TextNode()
    HealthCheckId = TextNode(optional=True)


"""
        ResourceRecordSetBase
            /           \
BasicRecordSetBase      AliasRecordSet
"""


class BasicRecordSet(ResourceRecordSet):
    """
    Request for Basic record set
    """
    TTL = TextNode()
    ResourceRecords = ItemNode(u'ResourceRecords')


class ResourceRecords(XMLObject):
    ResourceRecords = ListNode(u'ResourceRecord')


class ResourceRecord(XMLObject):
    Value = TextNode()


class AliasRecordSet(ResourceRecordSet):
    """
    Request for Alias record set
    """
    AliasTarget = ItemNode(u'AliasTarget')


class AliasTarget(XMLObject):
    _nodesOrder = [u'HostedZoneId', u'DNSName', u'EvaluateTargetHealth']
    HostedZoneId = TextNode()
    DNSName = TextNode()
    EvaluateTargetHealth = TextNode()


"""""""""""""Weighted Record Set """""""""""""""


class WeightedRecordSet(BasicRecordSet):
    """
    <SetIdentifier>unique description for this
                   resource record set</SetIdentifier>
    <Weight>value between 0 and 255</Weight>
    """
    _name = u'ResourceRecordSet'
    _nodesOrder = [u'Name', u'Type', u'SetIdentifier', u'Weight', u'TTL'
                   u'HealthCheckId']
    SetIdentifier = TextNode()
    Weight = TextNode()


class WeightedAlisaRecordSet(AliasRecordSet):
    """
    <SetIdentifier>unique description for this
                   resource record set</SetIdentifier>
    <Weight>value between 0 and 255</Weight>
    <AliasTarget>
    """
    _name = u'ResourceRecordSet'
    _nodesOrder = [u'Name', u'Type', u'SetIdentifier', u'Weight',
                   u'AliasTarget', u'HealthCheckId']
    SetIdentifier = TextNode()
    Weight = TextNode()


"""""""""""""Latency Record Set """""""""""""""


class LatencyRecordSet(BasicRecordSet):
    """
    <SetIdentifier>unique description for this
                   resource record set</SetIdentifier>
    <Region>Amazon EC2 region name</Region>
    <AliasTarget>
    """
    _name = u'ResourceRecordSet'
    _nodesOrder = [u'Name', u'Type', u'SetIdentifier', u'Region', u'TTL',
                   u'HealthCheckId']
    SetIdentifier = TextNode()
    Region = TextNode()


class LatencyAlisaRecordSet(AliasRecordSet):
    """
    <SetIdentifier>unique description for this
                   resource record set</SetIdentifier>
    <Region>Amazon EC2 region name</Region>
    <AliasTarget>
    """
    _name = u'ResourceRecordSet'
    _nodesOrder = [u'Name', u'Type', u'SetIdentifier', u'Region',
                   u'AliasTarget', u'HealthCheckId']
    SetIdentifier = TextNode()
    Region = TextNode()


# class WeightedRecordSetRequest(ChangeResourceRecordSetsRequest):
#     class_name = 'WeightedRecordSetRequest'
#     _name = u'ChangeResourceRecordSetsRequest'
#
#
# class WeightedAliasRecordSetRequest(ChangeResourceRecordSetsRequest):
#     class_name = 'WeightedAliasRecordSetRequest'
#     _name = u'ChangeResourceRecordSetsRequest'



#
# class WeightedRecordSet(ResourceRecordSetBase):
#     ResourceRecordSetBase._nodesOrder.insert(2, u'SetIdentifier')
#     ResourceRecordSetBase._nodesOrder.insert(3, u'Weight')
#     AliasTarget = ItemNode(u'AliasTarget')
#
#
# class AliasTarget(XMLObject):
#     _nodesOrder = [u'HostedZoneId', u'DNSName', u'EvaluateTargetHealth']
#     HostedZoneId = TextNode()
#     DNSName = TextNode()
#     EvaluateTargetHealth = TextNode()