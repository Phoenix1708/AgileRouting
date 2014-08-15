from etc.configuration import Config


class HostedZone(object):

    def __init__(self, id=None, name=None, owner=None, version=None,
                 caller_reference=None, config=None):
        self.id = id
        self.name = name
        self.owner = owner
        self.version = version
        self.caller_reference = caller_reference
        self.config = config

    def startElement(self, name, attrs, connection):
        if name == 'Config':
            self.config = Config()
            return self.config
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'Id':
            self.id = value
        elif name == 'Name':
            self.name = value
        elif name == 'Owner':
            self.owner = value
        elif name == 'Version':
            self.version = value
        elif name == 'CallerReference':
            self.caller_reference = value
        else:
            setattr(self, name, value)