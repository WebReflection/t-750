"""
Port the code from viewdom.examples.variables.
"""

import pytest

from thtml import html
from thtml.dom import Element, DocumentType

@pytest.fixture(scope='module')
def fixture_name():
    return "Fixture Name"

def test_insert_variable():
    """Template is in a function, and `name` comes from that scope."""
    name = "World"
    fragment = html(t"<div>Hello {name}</div>")
    assert str(fragment) == "<div>Hello World</div>"

def test_from_import():
    """A symbol is imported from another module."""
    name = Element.__name__
    fragment = html(t"<div>Hello {name}</div>")
    assert str(fragment) == "<div>Hello Element</div>"

def test_from_function_arg(fixture_name):
    """A symbol is passed into a function."""
    fragment = html(t"<div>Hello {fixture_name}</div>")
    assert str(fragment) == "<div>Hello Fixture Name</div>"

