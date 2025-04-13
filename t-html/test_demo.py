"""Cover the examples in Andrea's demo."""

from thtml import html, svg
from thtml.dom import Element, DocumentType


def test_automatic_quotes():
    """Automatic quotes with safe escapes."""
    fragment = html(t"""<p class={'test & "test"'}>Hello</p>""")
    assert str(fragment) == '<p class="test &amp; &quot;test&quot;">Hello</p>'


def test_sanitized_content():
    """Sanitized content out of the box"""
    from random import random

    fragment = html(t"Some random number: {random()}")
    # QUESTION: Not sure what to test here
    assert str(fragment).startswith("Some random number")


def test_self_closing_tags():
    """Sanitized content out of the box"""
    value = "Hello"
    fragment = html(t"<textarea placeholder={value} />")
    assert str(fragment) == '<textarea placeholder="Hello"></textarea>'


def test_special_attributes():
    """Data and ARIA"""
    data = {"a": 1, "b": 2}
    aria = {"role": "button", "label": "Click me"}
    fragment = html(t"<div data={data} aria={aria} />")
    div: Element = fragment.nodes[0]
    assert div.attributes == {
        "aria-label": "Click me",
        "data-a": 1,
        "data-b": 2,
        "role": "button",
    }
    assert (
        str(fragment)
        == '<div data-a="1" data-b="2" role="button" aria-label="Click me"></div>'
    )


def test_click_handler():
    """Bind a Python function to an element event handler."""

    def on_click(event):
        import js

        js.alert(event.type)

    fragment = html(t"<div @click={on_click} />")
    div: Element = fragment.nodes[0]
    assert div.attributes == {
        "onclick": "self.python_listeners?.[0].call(this,event)",
    }
    assert (
        str(fragment)
        == '<div onclick="self.python_listeners?.[0].call(this,event)"></div>'
    )


def test_ignore_voided():
    """Voided elements."""
    fragment = html(t"<hr />")
    assert str(fragment) == "<hr>"


def test_svg():
    """preseved XML/SVG self closing nature."""
    fragment = html(
        t"""
    <svg>
      {svg(t'<rect width="200" height="100" rx="20" ry="20" fill="blue" />')}
    </svg>
    """
    )
    assert str(fragment) == (
        "<svg>\n"
        '      <rect width="200" height="100" rx="20" ry="20" fill="blue" />\n'
        "    </svg>"
    )


def test_component():
    """Render a t-string that references a component."""

    def Component(props, children):
        return html(t"""
                    <div a={props['a']} b={props['b']}>
                      {children}
                    </div>
                  """)

    fragment = html(t'''
<{Component} a="1" b={2}>
  <p>Hello Components!</p>
<//>    
    ''')

    component = fragment.nodes[0]
    assert "<p>Hello Components!</p" in str(component)

def test_lists_within_layout():
    """A template in a template."""

    names = ["John", "Jane", "Jill"]
    fragment = html(t'''
    <ul>
      {[html(t"<li>{name}</li>") for name in names]}
    </ul>
    ''')

    assert "<li>John</li>" in str(fragment)
    assert "<li>Jane</li>" in str(fragment)
    assert "<li>Jill</li>" in str(fragment)