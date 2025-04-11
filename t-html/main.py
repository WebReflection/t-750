from thtml import render, html, svg
from js import document
from random import random

def passthrough(value, listeners):
  print(str(value))
  output = str(value)
  if len(listeners) > 0:
    from base64 import b64encode
    import dill
    code = b64encode(dill.dumps(listeners)).decode('utf-8')
    listeners.clear()
    output += f'''<script type="py">
from base64 import b64decode
import dill
import js
js.python_listeners = dill.loads(b64decode('{code}'))
</script>'''

  return output


data = {"a": 1, "b": 2}
aria = {"role": "button", "label": "Click me"}
names = ["John", "Jane", "Jim", "Jill"]


# listener example
def on_click(event):
  import js
  js.alert(event.type)


# Component example
def Component(props, children):
  return html(t'''
    <div a={props['a']} b={props['b']}>
      {children}
    </div>
  ''')


# SSR example
document.body.innerHTML = render(passthrough, html(t'''
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
    <!-- ignored void elements -->
    <hr />
    <svg>
      <!-- preseved XML/SVG self closing nature -->
      {svg(t'<rect width="200" height="100" rx="20" ry="20" fill="blue" />')}
    </svg>
    <!-- components -->
    <{Component} a="1" b={2}>
      <p>Hello Components!</p>
    <//>
    <ul>
      <!-- lists within parts of the layout -->
      {[html(t"<li>{name}</li>") for name in names]}
    </ul>
  </div>
'''))
