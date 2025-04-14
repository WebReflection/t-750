from html.parser import HTMLParser
from html import escape, unescape
import re

# TODO: style,script,textarea,title,xmp are nodes which content is not escaped
#       and it cannot contain interpolations right now but these need to be handled

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

  def __init__(self, nodeType):
    self.nodeType = nodeType
    self.parentNode = None

  def replaceWith(self, node):
    parentNode = self.parentNode
    index = parentNode.childNodes.index(self)
    parentNode.childNodes[index] = node
    node.parentNode = parentNode
    self.parentNode = None


class Comment(Node):
  def __init__(self, data):
    super().__init__(Node.COMMENT)
    self.data = data

  def __str__(self):
    return f"<!--{escape(str(self.data))}-->"

  def cloneNode(self, deep=False):
    return Comment(self.data)


class DocumentType(Node):
  def __init__(self, data):
    super().__init__(Node.DOCUMENT_TYPE)
    self.data = data

  def __str__(self):
    return f"<!{self.data}>"

  def cloneNode(self, deep=False):
    return DocumentType(self.data)


class Text(Node):
  def __init__(self, data):
    super().__init__(Node.TEXT)
    self.data = data

  def __str__(self):
    return escape(str(self.data))

  def cloneNode(self, deep=False):
    return Text(self.data)


class Parent(Node):
  def __init__(self, nodeType):
    super().__init__(nodeType)
    self.childNodes = []

  def appendChild(self, node):
    self.childNodes.append(node)
    node.parentNode = self
    return node

  def replaceChildren(self, *nodes):
    for node in nodes:
      self.childNodes.append(node)
      node.parentNode = self


class Element(Parent):
  def __init__(self, name, xml=False):
    super().__init__(Node.ELEMENT)
    self.attributes = {}
    self.name = name
    self.xml = xml

  def __str__(self):
    html = f"<{self.name}"
    for key, value in self.attributes.items():
      if value != None:
        if isinstance(value, bool):
          if value:
            html += f" {key}"
        else:
          html += f" {key}=\"{escape(str(value))}\""
    if len(self.childNodes) > 0:
      html += ">"
      for child in self.childNodes:
        # TODO: handle <title> and others that don't need/want escaping
        html += str(child)
      html += f"</{self.name}>"
    elif self.xml:
      html += " />"
    else:
      html += ">"
      if not VOID_ELEMENTS.match(self.name):
        html += "</" + self.name + ">"
    return html

  def cloneNode(self, deep=False):
    element = Element(self.name, self.xml)
    element.attributes = self.attributes.copy()
    if deep:
      element.replaceChildren(*[child.cloneNode(deep) for child in self.childNodes])
    return element


class Fragment(Parent):
  def __init__(self):
    super().__init__(Node.FRAGMENT)

  def __str__(self):
    return "".join(str(node) for node in self.childNodes)

  def cloneNode(self, deep=False):
    fragment = Fragment()
    if deep:
      fragment.replaceChildren(*[child.cloneNode(deep) for child in self.childNodes])
    return fragment


class DOMParser(HTMLParser):
  def __init__(self, xml=False):
    super().__init__()
    self.xml = xml
    self.node = Fragment()

  def handle_starttag(self, tag, attrs):
    element = Element(tag, self.xml)
    self.node.appendChild(element)
    self.node = element
    for name, value in attrs:
      element.attributes[name] = value

  def handle_endtag(self, tag):
    parentNode = self.node.parentNode
    if parentNode:
      self.node = parentNode

  def handle_data(self, data):
    self.node.appendChild(Text(data))

  def handle_comment(self, data):
    if data == '/':
      self.handle_endtag(self.node.name)
    else:
      self.node.appendChild(Comment(data))

  def handle_decl(self, data):
    self.node.appendChild(DocumentType(data))

  def unknown_decl(self, data):
    raise Exception(f"Unknown declaration: {data}")


def parse(content, xml=False):
  parser = DOMParser(xml)
  parser.feed(content)
  return parser.node
