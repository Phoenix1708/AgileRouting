from EaseXML import *


class NoXMLBindingAvailableError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class XMLClass(XMLObject):
    """
    Base class of all Xml classes that used for XML Data binding
    """

    class_name = None

    def match(self, required_xml_class):
        """Check whether this xml class is the corresponding
        one for xml data binding
        """
        if required_xml_class == self.class_name:
            return True

        return False