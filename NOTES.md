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

Having this structure would also allow middleware of tooling for result processing.

## Structured example

First: I've obsessed about this for 5 years. On the beach in France, notepad, drawing diagrams, etc. Even before I was
on the beach reading everything you ever wrote 3 years ago.

Let's say I have a huge pre-rendered site: Python docs in Sphinx, Wikipedia in Markdown, a Gatsby-like generation of a
GraphQL source. I make one change in a "resource" and I want to re-render the site. That's an incremental build, which
we all understand. The system can easily check that this one resource is out-of-date, grab its view, and re-render it.

Let's say, though, that I change the `title` `of a document and that title appears in many places: in listings,
portlets, or like Sphinx, in anchor text. I don't want to re-render the entire site. I want to know what used that data
and re-render just the views for those "pages." In front-ends, this is "change detection."

I could re-render the entire view for all of those. But if the `title` is in a component, we could have fine-grained
change detection:

- The *component instance* watches the change in *that* title
- Re-renders
- Stores the updated structure and its stringified rendering
- Then tells all the usages of that component *instance* that "I'm out of date."

Let's say that component *instance* was used in seven view *instances*. Those view instances could re-render. But they
don't really have to. It's already been rendered, for that input. We just need the view *instance* to store a data
structure, not a string. And in that view instance's data structure, there's a reference to the component *instance*.
Getting a new string to write to disk is thus a fast, string-only operation.

This is why my ViewDOM
renderer [returned a data structure](https://viewdom.readthedocs.io/en/latest/examples/components.html#component-in-vdom)
that could be turned to a string. For example, a view instance in JSON:

```json
{
  "tag": "html",
  "props": {
    "lang": "en"
  },
  "children": [
    "This is a ",
    {
      "tag": "Link",
      "props": {},
      "children": [],
      "refs": {
        "to": 1032382383
      }
    }
  ]
}
```

Somewhere else the system would store `1032382383` and its last rendering and stringifying. JSON is used to allow
storing between program execution, aka "incremental builds."

But this would slow down turning a "rendered" view into a string. Each component instance in a view would have to *pull*
the component's last string, even if it wasn't the one that changed. Instead, we would do a *push*, and store the last
computed string on all the usages:

```json
{
  "tag": "html",
  "props": {
    "lang": "en"
  },
  "children": [
    "This is a ",
    {
      "tag": "Link",
      "props": {},
      "children": [],
      "refs": {
        "to": 1032382383,
        "lastHash": "X38H98",
        "lasstRendered": "<a href='/foo'>My latest foo</a>"
      }
    }
  ]
}
```

The `1032382383` component instance knows this view instance is watching. It grabs this JSON, walks the tree, finds
`refs.to=1032382383`, and patches the `lastHash` and `rendered` in place. It then marks that view instance as dirty. At
the end of the transaction, all dirty views are rendered to a string and written to disk.

Transaction—that sounds like a database! One of the great flaws of Gatsby was that you couldn't trust the cache. You
want something everybody trusts. Something like SQLite, which has interesting JSON properties:

- Fast storage/retrieval
- Indexes on paths into JSON columns
- JSON patch
- And of course, database-y things (transactions, cache, etc.)

With this, the component instance `1032382383` could query everything in the system, at any part of the tree, with
`refs.to==1032382383`. *That's* the callback storage. *That's* the reference system: just a query. Then, for each query
result, do a JSON patch in place. All in SQL, no Python.

And voila, you have Redux/MobX, but for all the documents in your site. Actions which update computeds which update
watchers which dump strings to disk.

There's an extra-credit version of this. In the above, the change was to the title of a resource. Simple scalar values
for that are usually used in templates just as an insertion. No logic. Let's say I wrote my component this way:

```python
def Link(href: string, title: Scalar[string]) -> VDOM:
    return html(t
    '<a href="{href}>{title}</a>')
```

That is, I tell
the [dependency injector](https://viewdom.readthedocs.io/en/latest/examples/hopscotch.html#simple-injection) that this
argument is just passed through into the output. This leads to extra information getting stored in the JSON
representation, in SQLite, which I can query.

Then, if a title comes in and the only usage/watcher is a `Scalar`, then no Python rendering is needed. The entire
operation could take place in a SQL query as a JSON Patch.

The frontend world has experience
with [fine-grained reactivity](https://dev.to/ryansolid/a-hands-on-introduction-to-fine-grained-reactivity-3ndf). But
this model is in the context of a single browser "document" and a non-persistent "store." I'm generalizing the model to
the entire site:

- Instead of a single DOM/VDOM, the structure of every page is represented
- Not just represented, but *stored transactionally*
- Instead of storing references to subscribers...
- ...the reactivity system can *find* them anywhere in any tree with an indexed query

At this point, the amount of work to update a state machine based on a single change is tiny. Multiple orders of
magnitude less, in fact. And a good part of the work is done in SQLite, outside Python:

- Controlled memory usage
- C-speed operation
- Across multiple cores
- Transactionally

Imagine a demo where a meaningful change to a Wikipedia dump could be completed in a second.

Finally, in my fairy tale scenario, components are treated as side effects executed *inside the database* as part of the
transaction. SQLite has extension functions in Go, Rust, etc. If MicroPython could be an extension language, then a
change causes a trigger which calls the rendering function. Templating is just a side effect. 