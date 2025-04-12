# Things Paul Came Across

## General Python housekeeping

- *Proper package*. Make imports more normal by changing `t-html` to something legally importable.
- *pyproject.toml*. Put dependencies in there, then put everything under `src/thtml`. This would mean moving the
  PyScript demo code up to root.
- *Type hints*. Spread more of these around, for those that use IDEs that can autocomplete and squiggle.
- *More comments*. To help people walking through the code.

## Things I did

- *Setup CPython built from the branch*. It's a more productive way to work than the Pyodide build. Let me know if you
  want help doing this.
- *Development in tests*. I find this more productive, especially running tests under the debugger.
- *Failed tests*. I have some test cases that don't yet work. I marked them with the pytest marker.
