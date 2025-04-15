from thtml import render, html, svg
from random import random
from json import dumps

from t import t

def passthrough(value, listeners):
  try:
    import js
    js.console.log(js.JSON.parse(dumps(value)))
  except Exception as e:
    pass

  output = str(value)
  print(output)

  return output


data = {"a": 1, "b": 2}
aria = {"role": "button", "label": "Click me"}
names = ["John", "Jane", "Jim", "Jill"]

globals()["data"] = data
globals()["aria"] = aria
globals()["names"] = names

# listener example
def on_click(event):
  import js
  js.alert(event.type)

globals()["on_click"] = on_click

# Component example
def Component(props, children):
  globals()["props"] = props
  globals()["children"] = children
  return html(t('''
    <div a={props['a']} b={props['b']}>
      {children}
    </div>
  '''))

globals()["Component"] = Component


def li(name):
  globals()["name"] = name
  return html(t("<li>{name}</li>"))

globals()["li"] = li

# SSR example
content = render(passthrough, html(t('''
  <div>
    <!-- boolean attributes hints: try with True -->
    <h1 hidden={False}>Hello, PEP750 SSR!</h1>
    <!-- automatic quotes with safe escapes -->
    <p class={'test & "test"'}>
      <!-- sanitized content out of the box -->
      Some random number: {random()}
    </p>
    <!-- autofix for self closing non void tags -->
    <textarea placeholder={random()} />
    <!-- special attributes cases + @click special handler -->
    <div data={data} aria={aria} @click={on_click} />
    <!-- sanitized void elements -->
    <hr />
    <svg>
      <!-- preseved XML/SVG self closing nature -->
      {svg(t('<rect width="200" height="100" rx="20" ry="20" fill="blue" />'))}
    </svg>
    <!-- components -->
    <{Component} a="1" b={2}>
      <p>Hello Components!</p>
    <//>
    <ul>
      <!-- lists within parts of the layout -->
      {[li(name) for name in names]}
    </ul>
  </div>
''')))

try:
  from js import document
  document.body.innerHTML = content
except Exception as e:
  pass
