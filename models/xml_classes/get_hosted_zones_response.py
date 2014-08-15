from EaseXML import *
from models.xml_classes.xml_class import XMLClass

"""
Xml message structure
<GetHostedZoneResponse xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
   <HostedZone>
      <Id>/hostedzone/Amazon Route 53 hosted zone ID</Id>
      <Name>DNS domain name</Name>
      <CallerReference>unique identifier that you specified
         when you created the hosted zone</CallerReference>
      <Config>
         <Comment>comment that you specified when you
            created the hosted zone</Comment>
      </Config>
      <ResourceRecordSetCount>number of resource record sets
         in the hosted zone</ResourceRecordSetCount>
   </HostedZone>
   <DelegationSet>
      <NameServers>
         <NameServer>DNS name for Amazon Route 53 name server</NameServer>
         <NameServer>DNS name for Amazon Route 53 name server</NameServer>
         <NameServer>DNS name for Amazon Route 53 name server</NameServer>
         <NameServer>DNS name for Amazon Route 53 name server</NameServer>
      </NameServers>
   </DelegationSet>
</GetHostedZoneResponse>
"""


class GetHostedZoneResponse(XMLClass):

    class_name = 'GetHostedZoneResponse'

    _nodesOrder = [u'HostedZone', u'DelegationSet']
    hostedZone = ItemNode(u'HostedZone')
    DelegationSet = ItemNode(u'DelegationSet')


class HostedZone(XMLObject):
    _nodesOrder = [u'Id', u'Name', u'CallerReference',
                   u'Config', u'ResourceRecordSetCount']
    Id = TextNode(u'Id')
    Name = TextNode(u'Name')
    CallerReference = TextNode(u'CallerReference')
    Config = ItemNode(u'Config'''', optional=True''')
    ResourceRecordSetCount = TextNode(u'Config')


class Config(XMLObject):
    _nodesOrder = [u'Comment']
    Comment = TextNode(u'Comment', optional=True)


class DelegationSet(XMLObject):
    _nodesOrder = [u'NameServers']
    Comment = ItemNode(u'NameServers')


class NameServers(XMLObject):
    nameServers = ListNode(u'NameServer')
