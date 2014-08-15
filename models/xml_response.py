import xml.sax
from utilities import utils


class XmlHandler(xml.sax.ContentHandler):

    def __init__(self, root_node, connection):
        self.connection = connection
        self.nodes = [('root', root_node)]
        self.current_text = ''

    def startElement(self, name, attrs):
        self.current_text = ''
        t = self.nodes[-1][1].startElement(name, attrs, self.connection)
        if t is not None:
            if isinstance(t, tuple):
                self.nodes.append(t)
            else:
                self.nodes.append((name, t))

    def endElement(self, name):
        self.nodes[-1][1].endElement(name, self.current_text, self.connection)
        if self.nodes[-1][0] == name:
            self.nodes.pop()
        self.current_text = ''

    def characters(self, content):
        self.current_text += content

    def parse(self, s):
        xml.sax.parseString(s, self)
        
class Element(dict):

    def __init__(self, connection=None, element_name=None,
                 stack=None, parent=None, list_marker=('Set',),
                 item_marker=('member', 'item'),
                 pythonize_name=False):
        dict.__init__(self)
        self.connection = connection
        self.element_name = element_name
        self.list_marker = utils.mklist(list_marker)
        self.item_marker = utils.mklist(item_marker)
        if stack is None:
            self.stack = []
        else:
            self.stack = stack
        self.pythonize_name = pythonize_name
        self.parent = parent

    def __getattr__(self, key):
        if key in self:
            return self[key]
        for k in self:
            e = self[k]
            if isinstance(e, Element):
                try:
                    return getattr(e, key)
                except AttributeError:
                    pass
        raise AttributeError

    def get_name(self, name):
        if self.pythonize_name:
            name = utils.pythonize_name(name)
        return name

    def startElement(self, name, attrs, connection):
        self.stack.append(name)
        for lm in self.list_marker:
            if name.endswith(lm):
                l = ListElement(self.connection, name, self.list_marker,
                                self.item_marker, self.pythonize_name)
                self[self.get_name(name)] = l
                return l
        if len(self.stack) > 0:
            element_name = self.stack[-1]
            e = Element(self.connection, element_name, self.stack, self,
                        self.list_marker, self.item_marker,
                        self.pythonize_name)
            self[self.get_name(element_name)] = e
            return element_name, e
        else:
            return None

    def endElement(self, name, value, connection):
        if len(self.stack) > 0:
            self.stack.pop()
        value = value.strip()
        if value:
            if isinstance(self.parent, Element):
                self.parent[self.get_name(name)] = value
            elif isinstance(self.parent, ListElement):
                self.parent.append(value)

class ListElement(list):

    def __init__(self, connection=None, element_name=None, list_marker=None,
                 item_marker=('member', 'item'), pythonize_name=False):
        if not list_marker:
            list_marker = ['Set']

        list.__init__(self)
        self.connection = connection
        self.element_name = element_name
        self.list_marker = list_marker
        self.item_marker = item_marker
        self.pythonize_name = pythonize_name

    def get_name(self, name):
        if self.pythonize_name:
            name = utils.pythonize_name(name)
        return name

    def startElement(self, name, attrs, connection):
        for lm in self.list_marker:
            if name.endswith(lm):
                l = ListElement(self.connection, name,
                                self.list_marker, self.item_marker,
                                self.pythonize_name)
                setattr(self, self.get_name(name), l)
                return l
        if name in self.item_marker:
            e = Element(self.connection, name, parent=self,
                        list_marker=self.list_marker,
                        item_marker=self.item_marker,
                        pythonize_name=self.pythonize_name)
            self.append(e)
            return e
        else:
            return None

    def endElement(self, name, value, connection):
        if name == self.element_name:
            if len(self) > 0:
                empty = []
                for e in self:
                    if isinstance(e, Element):
                        if len(e) == 0:
                            empty.append(e)
                for e in empty:
                    self.remove(e)
        else:
            setattr(self, self.get_name(name), value)
