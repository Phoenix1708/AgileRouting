from EaseXML import *
from models.xml_classes.xml_class import XMLClass

"""
<?xml version="1.0" encoding="UTF-8"?>
<ChangeResourceRecordSetsResponse xmlns="https://route53.amazonaws.com/doc/2013-04-01/">
   <ChangeInfo>
      <Id>/change/unique identifier for the change batch request</Id>
      <Status>PENDING | INSYNC</Status>
      <SubmittedAt>date and time in Coordinated Universal Time 
         format</SubmittedAt>
   </ChangeInfo>
</ChangeResourceRecordSetsResponse>
"""


class ChangeResourceRecordSetsResponse(XMLClass):
    class_name = 'ChangeResourceRecordSetsResponse'
    changeInfo = ItemNode(u'ChangeInfo')


class ChangeInfo(XMLObject):
    _nodesOrder = [u'Id', u'Status', u'SubmittedAt']
    id = TextNode(name='Id')
    status = TextNode(name='Status')
    submitted_at = TextNode(name='SubmittedAt')