"""
Port the code from viewdom.examples.static_string.
"""

import pytest

from thtml import html


def test_string_literal():
    """Simplest form of templating: just a string, no tags, no attributes"""
    fragment = html(t"Hello World")
    assert str(fragment) == "Hello World"


def test_simple_render():
    """Same thing, but in a `<div> with attributes`."""
    fragment = html(t'<div title="Greeting">Hello World</div>')
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
    assert str(fragment) == '<div class="container1">Hello World</div>'


@pytest.mark.xfail(raises=ValueError)
def test_expressions_in_attribute_value():
    """Simple Python expression inside an attribute value."""
    fragment = html(t'<div class="container{1}">Hello World</div>')
    assert str(fragment) == {"class": "container1"}


def test_child_nodes():
    """Nested markup shows up as nodes."""
    fragment = html(t"<div>Hello <span>World<em>!</em></span></div>")
    assert str(fragment) == "<div>Hello <span>World<em>!</em></span></div>"


def test_doctype():
    """Sometimes it is hard to get a DOCTYPE in to the resulting output."""
    fragment = html(t"<!DOCTYPE html>\n<div>Hello World</div>")
    assert str(fragment) == "<!DOCTYPE html>\n<div>Hello World</div>"


def test_reducing_boolean():
    """collapse truthy-y values into simplified HTML attributes."""
    fragment = html(t"<div editable={True}>Hello World</div>")
    assert str(fragment) == "<div editable>Hello World</div>"
