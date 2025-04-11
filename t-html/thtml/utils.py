from .parser import instrument, prefix
from .dom import Node, Text, Fragment, parse as domify


def as_attribute(attributes, listeners, key, name):
  def aria(value):
    del attributes[key]
    values = []
    for k, v in value.items():
      attributes[k if k == 'role' else f'aria-{k.lower()}'] = v

  def attribute(value):
    del attributes[key]
    attributes[name] = value

  def dataset(value):
    del attributes[key]
    values = []
    for k, v in value.items():
      attributes[f'data-{k.replace("_", "-")}'] = v

  def listener(value):
    del attributes[key]
    if value in listeners:
      i = listeners.index(value)
    else:
      i = len(listeners)
      listeners.append(value)
    attributes[name] = f'self.python_listeners?.[{i}].call(this,event)'

  if name[0] == '@':
    name = 'on' + name[1:].lower()
    return listener
  if name == 'aria':
    return aria
  elif name == 'data':
    return dataset
  else:
    return attribute


def as_comment(node):
  parent = node.parent
  nodes = parent.nodes
  index = nodes.index(node)
  def comment(value):
    nodes[index] = as_node(value)

  return comment


def as_component(updates, node):
  parent = node.parent
  nodes = parent.nodes
  index = nodes.index(node)
  def component(value):
    def later():
      nodes[index] = value(node.attributes, node.nodes)
    updates.append(later)

  return component


def as_node(value):
  if isinstance(value, Node):
    return value
  if isinstance(value, (list, tuple)):
    node = Fragment()
    for item in value:
      node.append(as_node(item))
    return node
  if callable(value):
    return as_node(value())
  return Text(value)


def set_updates(node, listeners, updates):
  if node.type == node.ELEMENT:
    if node.name == prefix:
      updates.append(as_component(updates, node))

    attributes = node.attributes
    for key, name in attributes.items():
      if key.startswith(prefix):
        updates.append(as_attribute(attributes, listeners, key, name))
    for child in node.nodes:
      set_updates(child, listeners, updates)

  elif node.type == node.COMMENT and node.data == prefix:
    updates.append(as_comment(node))


def parse(listeners, template, length, svg):
  updates = []
  content = instrument(template, prefix, svg)
  fragment = domify(content, svg)
  for node in fragment.nodes:
    set_updates(node, listeners, updates)
  if len(updates) != length:
    raise ValueError(f'{len(updates)} updates found, expected {length}')

  return [node, updates]
