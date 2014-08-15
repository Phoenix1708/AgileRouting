from EaseXML import *
from models.xml_classes.xml_class import XMLClass

"""
Xml message structure
<ListHostedZonesResponse xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
   <HostedZones>
      <HostedZone>
         <Id>/hostedzone/Amazon Route 53 hosted zone ID</Id>
         <Name>DNS domain name</Name>
         <CallerReference>unique description that you specified
            when you created the hosted zone</CallerReference>
         <Config>
            <Comment>comment that you specified when you
               created the hosted zone</Comment>
         </Config>
         <ResourceRecordSetCount>number of resource record sets
            in the hosted zone</ResourceRecordSetCount>
      </HostedZone>
      ...
   </HostedZones>
   <Marker>value of the marker parameter,
      if any, in the previous request
   </Marker>
   <IsTruncated>true | false</IsTruncated>
   <NextMarker>if IsTruncated is true,
        the hosted zone ID of the first hosted zone
        in the next group of maxitems hosted zones
   </NextMarker>
   <MaxItems>value of the maxitems parameter,
      if any, in the previous request
   </MaxItems>
</ListHostedZonesResponse>
"""


class ListHostedZonesResponse(XMLClass):

    class_name = 'ListHostedZonesResponse'

    _nodesOrder = [u'HostedZones', u'Marker', u'IsTruncated',
                   u'NextMarker', u'MaxItems']
    hostedZones = ItemNode(u'HostedZones')
    Marker = TextNode(u'Marker', optional=True)
    IsTruncated = TextNode(u'IsTruncated')
    NextMarker = TextNode(u'NextMarker', optional=True)
    MaxItems = TextNode(u'MaxItems')


class HostedZones(XMLObject):
    hostedZones = ListNode(u'HostedZone')


class HostedZone(XMLObject):
    _nodesOrder = [u'Id', u'Name', u'CallerReference',
                   u'Config', u'ResourceRecordSetCount']
    Id = TextNode(u'Id')
    Name = TextNode(u'Name')
    CallerReference = TextNode(u'CallerReference')
    Config = ItemNode(u'Config')
    ResourceRecordSetCount = TextNode(u'Config')


class Config(XMLObject):
    _nodesOrder = [u'Comment']
    Comment = TextNode(u'Comment', optional=True)