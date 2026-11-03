---
title: Axes, layouts and markups
description: The six axes the engine ships, the two layouts, the three markups, and the registries holding them.
---

# Axes, layouts and markups

An **axis** is one independent choice a format spec can make. Every axis
arrives through
[`register_axis`](api.md#wadler_lindig_parts.register_axis), including the six
below — there is no privileged set, and an axis a consumer adds is read out of
a spec exactly like a built-in one.

```python
>>> from wadler_lindig_parts import AXES, ALIASES, MARKUPS

>>> sorted(AXES)
['indent', 'layout', 'markup', 'sep', 'value', 'width']
>>> sorted(MARKUPS)
['html', 'latex', 'text']

```

## Summary

| Axis | Default | Keywords | Applies to | Controls |
|---|---|---|---|---|
| `layout` | `product` | `call`, `product` | both | whether to show what the value **is** or how to **rebuild** it |
| `markup` | `text` | `text`, `html`, `latex` | `product` | which output format |
| `sep` | `bare` | `mul`, `bare` | `product` | the separator between a value and its label |
| `value` | `values` | `array`, `values`, `type`, or a format spec | both | how verbose an array-like payload is, and how a payload is formatted |
| `width` | `None` | *(none — `width=<n>` only)* | both | the column at which layout breaks lines |
| `indent` | `None` | *(none — `indent=<n>` only)* | both | the indent for a broken line |

`markup` and `sep` apply under `product` only. Naming either under `call` is
an error — see [Layout scoping](spec-grammar.md#layout-scoping).

## `layout`

**Default:** `product`. **Keywords:** `call`, `product`. **Applies to:** both.

`product` renders what a value *is*, from its `pparts` fragments. `call`
renders how to *rebuild* it, by handing off to the object's own `__pdoc__`.

```python
>>> from wadler_lindig_parts import pspec
>>> from wadler_lindig_parts.examples import Point, Term

>>> pspec(Term(2.0, "x"), "mul")
'2.0 * x'
>>> pspec(Point(1.0, 2.0), "call")
'Point(x=1.0, y=2.0)'

```

`Point` registers no `pparts` and still renders under `call`: a dataclass gets
a usable `__pdoc__` from `wadler_lindig` for free.

## `markup`

**Default:** `text`. **Keywords:** one per registered markup. **Applies to:** `product`.

Selects the markup row used to wrap fragments. Adding a markup adds its name
as a keyword.

```python
>>> from wadler_lindig_parts.examples import Version

>>> f"{Version(2, 1):text}"
'2.1'
>>> f"{Version(2, 1):html}"
'<span>2</span>.<span>1</span>'
>>> f"{Version(2, 1):latex}"
'$2.1$'

```

## `sep`

**Default:** `bare`. **Keywords:** `mul`, `bare`. **Applies to:** `product`.

Chooses the separator a markup places between a payload and its label.
Fragments a type marks `kind="sep"` are its own and are left alone.

```python
>>> pspec(Term(2.0, "x"), "bare")
'2.0 x'
>>> pspec(Term(2.0, "x"), "mul")
'2.0 * x'

```

## `value`

**Default:** `values`. **Keywords:** `array`, `values`, `type`, or any Python
format spec. **Applies to:** both; free text under `product` only.

The axis reaches the renderer as two arguments to
[`pvalue`](api.md#wadler_lindig_parts.pvalue): the three keywords select
`short_arrays`, and a format spec becomes `value_spec`.

A format spec is applied to the payload as a whole, via `format()`:

```python
>>> pspec(Term(2.0, "x"), ".3f")
'2.000 x'
>>> pspec(Term(2.0, "x"), ".1e")
'2.0e+00 x'

```

It is therefore only meaningful for a payload `format()` accepts. The default
`pvalue` passes a list straight to `format()`, which refuses it:

```python
>>> try:
...     pspec(Term([1.0, 2.0, 3.0], "x"), ".3f")
... except TypeError as e:
...     print(e)
unsupported format string passed to list.__format__

```

`pvalue` is itself a dispatch point, so a library holding array types
registers its own method and decides what a spec means for them.

The three keywords map to `wadler_lindig`'s `short_arrays` argument. They
affect array-like payloads; a plain Python list renders the same under all
three.

```python
>>> from wadler_lindig_parts import SHORT_ARRAYS
>>> SHORT_ARRAYS
{'array': False, 'values': 'compact', 'type': True}

>>> pspec(Term([1.0, 2.0, 3.0], "x"), "values")
'[1.0, 2.0, 3.0] x'

```

## `width`

**Default:** `None`. **Keywords:** none; written `width=<n>`. **Applies to:** both.

The column at which the document breaks lines. Layout is `wadler_lindig`'s, so
breaking and indentation come from the document rather than from this package.

```python
>>> from wadler_lindig_parts import doc_to_str, parts_to_doc, pparts

>>> parts = pparts(Term([1.0, 2.0, 3.0], "metres"))
>>> print(doc_to_str(parts_to_doc(parts), 60))
[1.0, 2.0, 3.0] * metres
>>> print(doc_to_str(parts_to_doc(parts), 20))
[1.0, 2.0, 3.0] *
  metres

```

A payload is atomic: a width narrower than the payload cannot break it
further.

```python
>>> doc_to_str(parts_to_doc(parts), 12) == doc_to_str(parts_to_doc(parts), 20)
True

```

`FLAT` is the sentinel width meaning "never break".

```python
>>> from wadler_lindig_parts import FLAT
>>> FLAT
1000000000

```

## `indent`

**Default:** `None`. **Keywords:** none; written `indent=<n>`. **Applies to:** both.

The indent applied to a continuation line after a break.

```python
>>> from wadler_lindig_parts import parse_spec
>>> parse_spec("indent=4")["indent"]
4

```

## Markups

A markup is a row of strings describing how to wrap fragments. Three ship.

| Key | Required | Meaning |
|---|---|---|
| `_content` | yes | wraps a `content` fragment |
| `wrap` | yes | wraps the whole rendered value |
| `vsep` | yes | separator between stacked values |
| `escape` | yes | callable applied to text, or `None` |
| `bare`, `mul`, … | no | the separator for each `sep` keyword |

```python
>>> from wadler_lindig_parts import REQUIRED_MARKUP_KEYS, markup_table

>>> REQUIRED_MARKUP_KEYS
('_content', 'wrap', 'vsep', 'escape')

>>> markup_table("html")["_content"]
'<span>{}</span>'
>>> markup_table("latex")["wrap"]
'${}$'

```

A row missing a required key is refused at registration — see
[Registration rules](registration-rules.md#markup-rows).

## Registries

Three mappings hold the grammar. All are read-only views; they change only
through the register/unregister functions.

| Registry | Holds | Ships with |
|---|---|---|
| `AXES` | axis name → `Axis` | the six above |
| `MARKUPS` | markup name → row | `text`, `html`, `latex` |
| `ALIASES` | alias name → spec string | **nothing** |

`ALIASES` is empty by design: the engine ships no shorthand at all, so every
alias in existence was registered by a consumer.

```python
>>> len(ALIASES)
0

```

## See also

- [Format spec grammar](spec-grammar.md) — how these words are written in a spec.
- [Registration rules](registration-rules.md) — how to add to these registries.
- [How to add an axis](../how-to/add-an-axis.md) · [How to add a markup](../how-to/add-a-markup.md)
