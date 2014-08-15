from models.xml_classes.xml_class import XMLClass

from models.xml_classes.change_resource_record_sets_request import \
    ChangeResourceRecordSetsRequest
from models.xml_classes.change_resource_record_sets_response import \
    ChangeResourceRecordSetsResponse
from models.xml_classes.get_hosted_zones_response import GetHostedZoneResponse
from models.xml_classes.list_hosted_zones_response import \
    ListHostedZonesResponse
from models.xml_classes.list_bucket_result import ListBucketResult


def get_xml_class(response_class):
    """
    Since subclass and superclass are in different module
    In order for __subclasses__() to list all subclasses this module
    has to import all subclasses. Otherwise, it won't return anything
    """
    for xml_cls in XMLClass.__subclasses__():
        xml_cls_obj = xml_cls()
        if xml_cls_obj.match(response_class):
            return xml_cls_obj