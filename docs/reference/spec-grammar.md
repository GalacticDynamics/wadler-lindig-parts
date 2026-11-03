---
title: Format spec grammar
description: The shape of a format spec, the scan rule, qualified keywords, and the trailing value spec.
---

# Format spec grammar

A format spec is a `-`-joined run of **keywords**, optionally ending in a
**value spec** — an ordinary Python format spec applied to the values inside.

```
[keyword[-keyword...]][-]value-spec
```

Specs are read by [`parse_spec`](api.md#wadler_lindig_parts.parse_spec), which
returns a [`Spec`](api.md#wadler_lindig_parts.Spec) mapping every axis to a
value. The same string is accepted by `format`, `f"{...:spec}"`,
[`pspec`](api.md#wadler_lindig_parts.pspec) and `__repr_spec__`.

```python
>>> from wadler_lindig_parts import parse_spec

>>> parse_spec("html-mul")["markup"]
'html'
>>> parse_spec("html-mul")["sep"]
'mul'

```

## The scan rule

The parse is total and strictly left to right:

1. Split the spec on `-`.
2. Consume tokens while they are keywords, expanding an alias in place.
3. **Stop at the first token that is not a keyword.** Everything from that
   token onward — rejoined with `-` — is the value spec.

The consequence is a single rule for writers: **the value spec goes last.**

| Spec | `markup` | `sep` | `value` |
|---|---|---|---|
| `""` | `text` | `bare` | `values` |
| `"html"` | `html` | `bare` | `values` |
| `"html-mul"` | `html` | `mul` | `values` |
| `".3g"` | `text` | `bare` | `.3g` |
| `"mul-.3g"` | `text` | `mul` | `.3g` |
| `"-.2f"` | `text` | `bare` | `-.2f` |
| `"mul-->10.2f"` | `text` | `mul` | `->10.2f` |

```python
>>> parse_spec("mul-.3g")["value"]
'.3g'

```

### Separators inside the value spec

A Python format spec may itself contain `-`, as a sign flag or a fill
character. The scan stops rather than continuing to split, so those survive
intact ([why](../explanation/why-formatting-is-one-engine.md)):

```python
>>> parse_spec("-.2f")["value"]
'-.2f'
>>> parse_spec("mul-->10.2f")["value"]
'->10.2f'

```

A token that is not a keyword is therefore never an error on its own — it
becomes the value spec, and a type whose fragments do not format values
ignores it silently.

```python
>>> parse_spec("nonsense")["value"]
'nonsense'

```

## Keyword order

Keywords do not say which axis they belong to, so any order means the same
thing:

```python
>>> parse_spec("html-mul") == parse_spec("mul-html")
True

```

Setting one axis twice is an error:

```python
>>> try:
...     parse_spec("html-latex")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'html-latex': 'markup' is set twice

```

## Qualified keywords

`axis=word` names the axis explicitly. This is the primitive form; a bare
keyword is shorthand for it.

```python
>>> parse_spec("markup=html")["markup"]
'html'
>>> parse_spec("markup=html-sep=mul")["sep"]
'mul'

```

Two axes may claim the same keyword. Both registrations succeed; the bare word
then raises and names both claimants, while each qualified form keeps working.
See [Registration rules](registration-rules.md#keyword-collisions).

`width` and `indent` have **no bare keywords at all** and are always written
qualified:

```python
>>> parse_spec("width=20")["width"]
20
>>> parse_spec("indent=4")["indent"]
4

```

## Reserved characters

| Character | Meaning | Constraint |
|---|---|---|
| `-` | joins components | may not appear in any registered name |
| `=` | qualifies a keyword with its axis | may appear in a value spec |

Because the scan splits on `-` before any lookup, a registered name containing
one could never be resolved — so registration refuses it. See
[Registration rules](registration-rules.md#reserved-characters).

Both characters are safe inside a value spec, which is taken verbatim:

```python
>>> parse_spec("markup=html-=10.2f")["value"]
'=10.2f'

```

## Layout scoping

An axis declares which layouts it applies to. Naming one under a layout it
does not apply to is an error rather than a silent no-op:

```python
>>> try:
...     parse_spec("call-mul")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'call-mul': 'sep' does not apply to 'call' layout

```

A value spec is likewise only accepted under layouts whose free-text axis
allows it:

```python
>>> try:
...     parse_spec("call-.2f")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'call-.2f': free text does not apply to 'call' layout

```

For which axis applies where, see [Axes, layouts and markups](axes.md).

## See also

- [Axes, layouts and markups](axes.md) — the vocabulary this grammar reads.
- [Registration rules](registration-rules.md) — what may be added to it.
- [`parse_spec`](api.md#wadler_lindig_parts.parse_spec) — the function itself.
