from typing import Callable

from .dom import Fragment
from .utils import parse

parsed = {}
listeners = []

def _util(svg) -> Callable[[object], Fragment]:
  def fn(t):
    template = t.args[0::2]

    values = []
    for entry in t.args[1::2]:
      values.append(entry.value)

    length = len(values)

    # TODO: this is broken right now
    if False and template in parsed:
      node, updates = parsed[template]
    else:
      node, updates = parse(listeners, template, length, svg)
      parsed[template] = [node, updates]

    for i in range(length):
      updates[i](values[i])

    for i in range(len(updates) - 1, length - 1, -1):
      updates[i]()

    return node

  return fn

def render(where, what):
  return where(what() if callable(what) else what, listeners)

html = _util(False)
svg = _util(True)

__all__ = ["render", "html", "svg"]
