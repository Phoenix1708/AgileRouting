from EaseXML import *
from models.xml_classes.xml_class import XMLClass

"""
sample structure
<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <Name>
        xueshi-ireland-elb-logs
    </Name>
    <Prefix>
        AWSLogs/305933725014/elasticloadbalancing/eu-west-1/2014/07/21/
        305933725014_elasticloadbalancing_eu-west-1_xueshi-ofbench-servers
        _20140721T2115Z_54.228.193.7
    </Prefix>
    <Marker/>
    <MaxKeys>
        1000
    </MaxKeys>
    <Delimiter>
        .log
    </Delimiter>
    <IsTruncated>
        false
    </IsTruncated>
    <CommonPrefixes>
        <Prefix>
            AWSLogs/305933725014/elasticloadbalancing/eu-west-1/2014/07/21/
            305933725014_elasticloadbalancing_eu-west-1_xueshi-ofbench-servers
            _20140721T2115Z_54.228.193.7_5nrglkcr.log
        </Prefix>
    </CommonPrefixes>
</ListBucketResult>
"""


class ListBucketResult(XMLClass):

    class_name = 'ListBucketResult'

    _nodesOrder = [u'Name', u'Prefix', u'Marker', u'MaxKeys', u'Delimiter',
                   u'IsTruncated', u'CommonPrefixes']

    name = TextNode(name='Name')
    prefix = TextNode(name='Prefix')
    marker = TextNode(name='Marker')
    maxKeys = TextNode(name='MaxKeys')
    delimiter = TextNode(name='Delimiter')
    is_truncated = TextNode(name='IsTruncated')
    common_prefixes = ListNode(u'CommonPrefixes')


class CommonPrefixes(XMLObject):
    prefix = TextNode(name='Prefix')