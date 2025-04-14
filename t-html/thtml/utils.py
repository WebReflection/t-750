from .parser import instrument, prefix
from .dom import Node, Text, Fragment, parse as domify


def as_attribute(attributes, listeners, name):
  def aria(value):
    for k, v in value.items():
      attributes[k if k == 'role' else f'aria-{k.lower()}'] = v

  def attribute(value):
    attributes[name] = value

  def dataset(value):
    values = []
    for k, v in value.items():
      attributes[f'data-{k.replace("_", "-")}'] = v

  def listener(value):
    if value in listeners:
      i = listeners.index(value)
    else:
      i = len(listeners)
      listeners.append(value)
    attributes[name] = f'self.python_listeners?.[{i}](event)'

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
  return lambda value: node.replaceWith(as_node(value))


def as_component(node, components):
  return lambda value: components.append(lambda: node.replaceWith(value(node.attributes, node.childNodes)))


def as_node(value):
  if isinstance(value, Node):
    return value
  if isinstance(value, (list, tuple)):
    node = Fragment()
    node.replaceChildren(*value)
    value.clear()
    return node
  if callable(value):
    # TODO: this could be a hook pleace for asyncio
    #       and run to completion before continuing
    return as_node(value())
  return Text(value)


def set_updates(node, listeners, updates, path):
  if node.nodeType == node.ELEMENT:
    if node.name == prefix:
      updates.append(Update(path, Component()))

    remove = []
    for key, name in node.attributes.items():
      if key.startswith(prefix):
        remove.append(key)
        updates.append(Update(path, Attribute(name)))
    
    for key in remove:
      del node.attributes[key]

    i = 0
    for child in node.childNodes:
      set_updates(child, listeners, updates, path + [i])
      i += 1

  elif node.nodeType == node.COMMENT and node.data == prefix:
    updates.append(Update(path, Comment()))


class Attribute:
  def __init__(self, name):
    self.name = name

  def __call__(self, node, listeners):
    return as_attribute(node.attributes, listeners, self.name)


class Comment:
  def __call__(self, node):
    return as_comment(node)


class Component:
  def __call__(self, node, updates):
    return as_component(node, updates)


class Update:
  def __init__(self, path, update):
    self.path = path
    self.value = update


def parse(listeners, template, length, svg):
  updates = []
  content = instrument(template, prefix, svg)
  fragment = domify(content, svg)

  i = 0
  for node in fragment.childNodes:
    set_updates(node, listeners, updates, [i])
    i += 1

  if len(updates) != length:
    raise ValueError(f'{len(updates)} updates found, expected {length}')

  return [fragment, updates]
