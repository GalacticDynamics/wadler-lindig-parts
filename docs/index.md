# wadler-lindig-parts

One engine behind `repr`, `str`, `__format__` and the representations Jupyter
asks for. A type says what it is **made of** — a tree of roled fragments — and
every output route lays that same tree out its own way.

Add a markup and every registered type gets it. Register a type and it gets
every markup, including ones added later by somebody else.

```python
>>> from wadler_lindig_parts.examples import Version

>>> Version(2, 1)
2.1
>>> f"{Version(2, 1):html}"
'<span>2</span>.<span>1</span>'
>>> f"{Version(2, 1):latex}"
'$2.1$'

```

Three routes, one `pparts` method, and they cannot disagree.

- To make your own type formattable, see
  [How to make your own type formattable](how-to/make-a-type-formattable.md).
- For why it is built this way, see
  [Why formatting is one engine](explanation/why-formatting-is-one-engine.md).
- For every public name, see the [API reference](api.md).

## The spec grammar

A format spec is a `-`-joined run of **keywords**, optionally ending in a
Python format spec:

```python
>>> from wadler_lindig_parts import parse_spec

>>> parse_spec("html-mul")["markup"]
'html'
>>> parse_spec("html-mul")["sep"]
'mul'

```

### The scan goes left to right, and stops

The scan stops at the first token that is not a keyword. Everything from there
on is the format spec — `-` and all.

That is load-bearing rather than stylistic. A Python format spec may itself
contain `-`, as a sign flag in `-.2f` or a fill character in `->10.2f`. Split
on `-` and sort the pieces into keywords and leftovers, and `->10.2f` becomes
two tokens, neither of which means anything.

```python
>>> parse_spec("-.2f")["value"]
'-.2f'
>>> parse_spec("mul-->10.2f")["value"]
'->10.2f'

```

The price is one rule to carry: **the format spec goes last.**

### Keywords share one flat namespace

A keyword does not say which axis it belongs to, so a run can be written in
any order — these are the same request:

```python
>>> parse_spec("html-mul") == parse_spec("mul-html")
True

```

The cost arrives when two libraries want one word. Both registrations succeed;
the bare word then raises and names both claimants, while `axis=word` keeps
working for each. A collision costs one word in one spec, not a rewrite.

```python
>>> from wadler_lindig_parts import Axis, register_axis, unregister_axis

>>> def claim(name):
...     return Axis(
...         name=name,
...         keywords={"dim": name},
...         default=None,
...         layouts={"product": lambda v: {name: v}},
...     )

>>> _ = register_axis(claim("units_dim"))
>>> _ = register_axis(claim("vector_dim"))

>>> try:
...     parse_spec("dim")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'dim': ambiguous keyword 'dim'; claimed by 'units_dim', 'vector_dim'. Write it as one of: units_dim=dim, vector_dim=dim

>>> parse_spec("units_dim=dim")["units_dim"]
'units_dim'
>>> parse_spec("vector_dim=dim")["vector_dim"]
'vector_dim'

>>> unregister_axis("vector_dim")
>>> unregister_axis("units_dim")

```

`axis=word` is in fact the real form — a keyword *sets an axis to a value* —
and the bare word is shorthand for it.

## The six axes

Every axis arrives through `register_axis`, including these. There is no
privileged set: an axis a consumer adds is read out of a spec exactly like a
built-in one.

| Axis | Keywords | What it controls |
|---|---|---|
| `layout` | `call`, `product` | whether to show what the value **is** or how to **rebuild** it |
| `markup` | `text`, `html`, `latex` | which output format |
| `sep` | `mul`, `bare` | the separator between a value and its label |
| `value` | `array`, `values`, `type`, or a format spec | how verbose a payload is, and how each element is formatted |
| `width` | `width=<n>` | the column at which layout breaks lines |
| `indent` | `indent=<n>` | the indent for a broken line |

```python
>>> from wadler_lindig_parts import AXES, ALIASES, MARKUPS

>>> sorted(AXES)
['indent', 'layout', 'markup', 'sep', 'value', 'width']
>>> sorted(MARKUPS)
['html', 'latex', 'text']

```

`ALIASES` is empty, and that is the point: the engine ships no shorthand at
all. Every alias in existence is registered by a consumer.

```python
>>> len(ALIASES)
0

```

## The two layouts

`product` shows what a value **is**. `call` shows how to **rebuild** it, by
handing off to the type's own `__pdoc__`.

```python
>>> from wadler_lindig_parts import pspec
>>> from wadler_lindig_parts.examples import Point, Term

>>> pspec(Term(2.0, "x"), "mul")
'2.0 * x'
>>> pspec(Point(1.0, 2.0), "call")
'Point(x=1.0, y=2.0)'

```

`Point` registers no `pparts` at all and still renders in `call` layout — a
dataclass gets a usable `__pdoc__` from `wadler_lindig` for free. That is why
the constructor form delegates rather than being built from fragments; see
[the explanation](explanation/why-formatting-is-one-engine.md).

## Layout is wadler-lindig's, not ours

`parts_to_doc` builds a `wadler_lindig` document, so every markup gets line
breaking and nesting for free, and composes inside a larger document. A
markup's wrapper text is emitted zero-width, so it reaches the output without
being billed as visible columns.

```python
>>> from wadler_lindig_parts import doc_to_str, parts_to_doc, pparts

>>> parts = pparts(Term([1.0, 2.0, 3.0], "metres"))
>>> print(doc_to_str(parts_to_doc(parts), 60))
[1.0, 2.0, 3.0] * metres
>>> print(doc_to_str(parts_to_doc(parts), 20))
[1.0, 2.0, 3.0] *
  metres

```

The break lands at the separator and the continuation is indented, because
that is what the document says to do — none of it is this package's code.
The payload itself stays atomic, so a width narrower than the list cannot
make it any narrower:

```python
>>> doc_to_str(parts_to_doc(parts), 12) == doc_to_str(parts_to_doc(parts), 20)
True

```
