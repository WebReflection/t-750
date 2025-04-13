# Things Paul Came Across

## General Python housekeeping I could do later

- *Proper package*. Make imports more normal by changing `t-html` to something legally importable.
- *pyproject.toml*. Put dependencies in there, then put everything under `src/thtml`. This would mean moving the
  PyScript demo code up to root.
- *Type hints*. Spread more of these around, for those that use IDEs that can autocomplete and squiggle.
- *More comments*. To help people walking through the code.
- *Assert by "DOM" not strings*. I usually use `BeautifulSoup` to parse the results into a queryable structure, then
  make asserts that way.

## Things I did

- *Setup CPython built from the branch*. It's a more productive way to work than the Pyodide build. Let me know if you
  want help doing this.
- *Development in tests*. I find this more productive, especially running tests under the debugger.
- *Failed tests*. I have some test cases that don't yet work. I marked them with the pytest marker.

## Structured rendering

The `html` function returns a `Fragment` with a list of `nodes`. But these nodes seem mostly-rendered.

I want fast incremental rebuilds. Let's say a view has a component. There's a change, but the change is only in the
component. I don't want to re-render the entire view. I especially don't want to re-render all the views in the entire
site where that component appears. My ViewDOM system was going in a direction where I could track dependencies and push
updates.

If the `html` function returned a data structure (in ViewDOM, a VDOM), then the view's usage of the component would be a
reference. When doing an `__str__` to make a string, the view doesn't need re-rendering. I can then store all the
rendered view data and rendered component data in a cache and not re-calculate on the next run. Hence: incremental
build. (Longer term: the cache is SQLite, the tree is JSON, and I can index all the nodes in the site, to quickly find
and patch them with updates.)

