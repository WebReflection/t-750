"""
Port the code from viewdom.examples.static_string.
"""

import pytest

from thtml import html
from thtml.dom import Element


def test_string_literal():
    """Simplest form of templating: just a string, no tags, no attributes"""
    fragment = html(t"Hello World")
    assert str(fragment) == "Hello World"


def test_simple_render():
    """Same thing, but in a `<div> with attributes`."""
    fragment = html(t'<div title="Greeting">Hello World</div>')
    div: Element = fragment.nodes[0]
    assert div.name == "div"
    assert div.attributes == {"title": "Greeting"}
    assert str(fragment) == '<div title="Greeting">Hello World</div>'


def test_simple_interpolation():
    """Simplest rendering of a value in the scope."""
    name = "World"
    fragment = html(t"<div>Hello {name}</div>")
    assert str(fragment) == "<div>Hello World</div>"


def test_attribute_value_expression():
    """Pass in a Python symbol as part of the template, inside curly braces."""
    klass = "container1"
    fragment = html(t"<div class={klass}>Hello World</div>")
    div = fragment.nodes[0]
    assert div.attributes == {"class": "container1"}


@pytest.mark.xfail(raises=ValueError)
def test_expressions_in_attribute_value():
    """Simple Python expression inside an attribute value."""
    fragment = html(t'<div class="container{1}">Hello World</div>')
    div = fragment.nodes[0]
    assert div.attributes == {"class": "container1"}


def test_child_nodes():
    """Nested markup shows up as nodes."""
    fragment = html(t"<div>Hello <span>World<em>!</em></span></div>")
    div: Element = fragment.nodes[0]
    span: Element = div.nodes[1]
    assert span.name == "span"
    assert str(span) == "<span>World<em>!</em></span>"
    em = span.nodes[1]
    assert em.name == "em"
    assert str(em) == "<em>!</em>"
