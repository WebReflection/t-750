from .utils import Attribute, Comment, Component, parse

parsed = {}
listeners = []

def _util(svg):
  def fn(t):
    template = t.args[0::2]

    values = []
    for entry in t.args[1::2]:
      values.append(entry.value)

    length = len(values)

    if not template in parsed:
      parsed[template] = parse(listeners, template, length, svg)

    content, updates = parsed[template]

    node = content.cloneNode(True)
    changes = []
    path = None
    child = None
    i = 0

    for update in updates:
      if path != update.path:
        path = update.path
        child = node
        for index in path:
          child = child.childNodes[index]

      if isinstance(update.value, Attribute):
        changes.append(update.value(child, listeners))
      elif isinstance(update.value, Comment):
        changes.append(update.value(child))
      else:
        changes.append(update.value(child, changes))

    for i in range(length):
      changes[i](values[i])

    for i in range(len(changes) - 1, length - 1, -1):
      changes[i]()

    return node

  return fn

def render(where, what):
  return where(what() if callable(what) else what, listeners)

html = _util(False)
svg = _util(True)

__all__ = ["render", "html", "svg"]
