from .parser import instrument, prefix
from .dom import Fragment, Node, Text
from .dom import COMMENT, ELEMENT, FRAGMENT
from .dom import _appendChildren, _replaceWith, parse as domify



def as_comment(node):
  return lambda value: _replaceWith(node, as_node(value))


def as_component(node, components):
  return lambda value: components.append(lambda: _replaceWith(node, value(node['props'], node['children'])))


def as_node(value):
  if isinstance(value, Node):
    return value
  if isinstance(value, (list, tuple)):
    node = Fragment()
    _appendChildren(node, value)
    return node
  if callable(value):
    # TODO: this could be a hook pleace for asyncio
    #       and run to completion before continuing
    return as_node(value())
  return Text(value)


def as_prop(props, listeners, name):
  def aria(value):
    for k, v in value.items():
      props[k if k == 'role' else f'aria-{k.lower()}'] = v

  def attribute(value):
    props[name] = value

  def dataset(value):
    for k, v in value.items():
      props[f'data-{k.replace("_", "-")}'] = v

  def listener(value):
    if value in listeners:
      i = listeners.index(value)
    else:
      i = len(listeners)
      listeners.append(value)
    props[name] = f'self.python_listeners?.[{i}](event)'

  if name[0] == '@':
    name = 'on' + name[1:].lower()
    return listener
  if name == 'aria':
    return aria
  elif name == 'data':
    return dataset
  else:
    return attribute


def set_updates(node, listeners, updates, path):
  type = node['type']
  if type == ELEMENT:
    if node['name'] == prefix:
      updates.append(Update(path, Component()))

    remove = []
    props = node['props']
    for key, name in props.items():
      if key.startswith(prefix):
        remove.append(key)
        updates.append(Update(path, Attribute(name)))

    for key in remove:
      del props[key]

  if type == ELEMENT or type == FRAGMENT:
    i = 0
    for child in node['children']:
      set_updates(child, listeners, updates, path + [i])
      i += 1

  elif type == COMMENT and node['data'] == prefix:
    updates.append(Update(path, Comment()))



class Attribute:
  def __init__(self, name):
    self.name = name

  def __call__(self, node, listeners):
    return as_prop(node['props'], listeners, self.name)


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

  if len(fragment['children']) == 1:
    fragment = fragment['children'][0]

  set_updates(fragment, listeners, updates, [])

  if len(updates) != length:
    raise ValueError(f'{len(updates)} updates found, expected {length}')

  return [fragment, updates]
