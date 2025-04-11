from html.parser import HTMLParser
from html import escape
import re

VOID_ELEMENTS = re.compile(
  r'^(?:area|base|br|col|embed|hr|img|input|keygen|link|menuitem|meta|param|source|track|wbr)$',
  re.IGNORECASE
)

class Node:
  ELEMENT = 1
  ATTRIBUTE = 2
  TEXT = 3
  CDATA = 4
  # ENTITY_REFERENCE = 5
  # ENTITY = 6
  # PROCESSING_INSTRUCTION = 7
  COMMENT = 8
  # DOCUMENT = 9
  DOCUMENT_TYPE = 10
  FRAGMENT = 11
  # NOTATION = 12

  def __init__(self, type, xml=False):
    self.type = type
    self.xml = xml


class Text(Node):
  def __init__(self, data):
    super().__init__(Node.TEXT)
    self.data = data

  def __str__(self):
    return escape(self.data)


class Comment(Node):
  def __init__(self, data):
    super().__init__(Node.COMMENT)
    self.data = data

  def __str__(self):
    return f"<!--{escape(self.data)}-->"


class Parent(Node):
  def __init__(self, type, xml=False):
    super().__init__(type, xml)
    self.nodes = []
    self.parent = None

  def append(self, *nodes):
    for node in nodes:
      node.parent = self
      self.nodes.append(node)

  def replace(self, old_node, new_node):
    self.nodes[self.nodes.index(old_node)] = new_node
    old_node.parent = None
    new_node.parent = self


class Element(Parent):
  def __init__(self, name, xml=False):
    super().__init__(Node.ELEMENT, xml)
    self.attributes = {}
    self.nodes = []
    self.name = name

  def __str__(self):
    html = f"<{self.name}"
    for key, value in self.attributes.items():
      html += f" {key}=\"{escape(value)}\""
    if len(self.nodes) > 0:
      html += ">"
      for child in self.nodes:
        html += str(child)
      html += f"</{self.name}>"
    elif self.xml:
      html += " />"
    else:
      html += ">"
      if not VOID_ELEMENTS.match(self.name):
        html += "</" + self.name + ">"
    return html


class Fragment(Parent):
  def __init__(self, xml=False):
    super().__init__(Node.FRAGMENT, xml)

  def __str__(self):
    return "".join(str(node) for node in self.nodes)


class DocumentType(Node):
  def __init__(self, data, xml=False):
    super().__init__(Node.DOCUMENT_TYPE, xml)
    self.data = data

  def __str__(self):
    return f"<!{self.data}>"


class DOMParser(HTMLParser):
  def __init__(self, xml=False):
    super().__init__()
    self.xml = xml
    self.node = Fragment(xml)

  def handle_starttag(self, tag, attrs):
    element = Element(tag, self.xml)
    self.node.append(element)
    self.node = element
    for attr in attrs:
      element.attributes[attr[0]] = attr[1]

  def handle_endtag(self, tag):
    if self.node.parent:
      self.node = self.node.parent

  def handle_data(self, data):
    self.node.append(Text(data))

  def handle_comment(self, data):
    if data == '/':
      self.handle_endtag(self.node.name)
    else:
      self.node.append(Comment(data))

  def handle_decl(self, data):
    self.node.append(DocumentType(data))

  def unknown_decl(self, data):
    raise Exception(f"Unknown declaration: {data}")


def parse(content, xml=False):
  parser = DOMParser(xml)
  parser.feed(content)
  return parser.node
