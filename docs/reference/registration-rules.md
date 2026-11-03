---
title: Registration rules
description: What register_axis, register_alias and register_markup accept and refuse, and the one collision that is allowed.
---

# Registration rules

Registration raises rather than overwriting, so a spec cannot change meaning
without someone editing it. Each function takes `replace=True` to overwrite
deliberately.

All three registries are process-wide and shared by every package in the
interpreter.

## Summary

| Condition | `register_axis` | `register_alias` | `register_markup` |
|---|---|---|---|
| Name already registered | raises | raises | raises |
| Name is already a keyword | — | raises | raises |
| Name is already an alias | raises (keyword) | raises | raises |
| Name contains `-` | raises | raises | raises |
| Second claim on free text | raises | — | — |
| Row missing a required key | — | — | raises |
| Keyword already claimed by another axis | **accepted** | — | — |

Every refusal is a `ValueError`, raised before any registry is touched — a
rejected registration leaves the grammar exactly as it was.

## Axes

A duplicate axis name is refused:

```python
>>> from wadler_lindig_parts import Axis, register_axis, unregister_axis

>>> def probe(name, word):
...     return Axis(name=name, keywords={word: True}, default=None,
...                 layouts={"product": lambda v: {name: v}})

>>> _ = register_axis(probe("probe_a", "wa"))
>>> try:
...     register_axis(probe("probe_a", "wb"))
... except ValueError as e:
...     print(e)
axis 'probe_a' is already registered

```

A keyword that is already an alias is refused, because an alias is a whole
spec and so has no qualified form to fall back on:

```python
>>> from wadler_lindig_parts import register_alias, unregister_alias

>>> register_alias("al", "html-mul")
>>> try:
...     register_axis(probe("probe_b", "al"))
... except ValueError as e:
...     print(e)
keyword 'al' is already an alias

```

Only one axis may claim the spec's trailing free-text run. `value` already
does:

```python
>>> try:
...     register_axis(Axis(name="probe_c", keywords={"wc": True}, default=None,
...                        layouts={"product": lambda v: {}}, free_text=("product",)))
... except ValueError as e:
...     print(e)
axis 'probe_c' claims free text, but 'value' already does; a spec has only one trailing run to give

```

## Aliases

An alias maps a name to a whole spec string. The name is refused if it is
taken, in either direction:

```python
>>> try:
...     register_alias("al", "text")
... except ValueError as e:
...     print(e)
alias 'al' is already registered as 'html-mul'

>>> try:
...     register_alias("wa", "text")
... except ValueError as e:
...     print(e)
alias 'wa' is already a keyword of axis 'probe_a'

```

The restriction is on the name only. An alias's **expansion** is a whole spec
and therefore contains separators — that is what an alias is for.

## Markup rows

A markup name also becomes a keyword on the `markup` axis, so it is subject to
the keyword rules:

```python
>>> from wadler_lindig_parts import MARKUPS, register_markup, unregister_markup

>>> try:
...     register_markup("html", MARKUPS["text"])
... except ValueError as e:
...     print(e)
markup 'html' is already registered

>>> try:
...     register_markup("wa", MARKUPS["text"])
... except ValueError as e:
...     print(e)
'wa' is already a keyword or alias

```

All four keys in
[`REQUIRED_MARKUP_KEYS`](axes.md#markups) must be present. A row missing one is
refused at registration, not when something is first rendered:

```python
>>> try:
...     register_markup("broken", {"_content": "{}", "wrap": "{}"})
... except ValueError as e:
...     print(e)
markup row is missing required keys ['vsep', 'escape']

```

## Reserved characters

No registered name may contain `-`. `parse_spec` splits on it before any
lookup, so such a name could never be resolved — and the qualified
`axis=word` form does not rescue it, because that is split first too.

The rule applies to axis names, keywords, alias names and markup names alike:

```python
>>> try:
...     register_alias("a-b", "text")
... except ValueError as e:
...     print(str(e).split(":")[0])
alias 'a-b' may not contain '-'

```

Use `_` inside a name that needs two words.

## Keyword collisions

Two axes claiming one keyword is the single case that does **not** raise at
registration. Both succeed, and the registry records both claimants:

```python
>>> _ = register_axis(probe("probe_e", "shared"))
>>> _ = register_axis(probe("probe_f", "shared"))

```

The refusal lands when a spec uses the word bare, and names both claimants and
both escapes:

```python
>>> from wadler_lindig_parts import parse_spec

>>> try:
...     parse_spec("shared")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'shared': ambiguous keyword 'shared'; claimed by 'probe_e', 'probe_f'. Write it as one of: probe_e=shared, probe_f=shared

```

Each qualified form keeps working:

```python
>>> parse_spec("probe_e=shared")["probe_e"]
True
>>> parse_spec("probe_f=shared")["probe_f"]
True

```

For why this case is permitted rather than refused, see
[Why keywords share one namespace](../explanation/why-formatting-is-one-engine.md).

```python
>>> for name in ["probe_f", "probe_e", "probe_a"]:
...     unregister_axis(name)
>>> unregister_alias("al")

```

## See also

- [Axes, layouts and markups](axes.md) — what is in the registries.
- [Format spec grammar](spec-grammar.md) — how registered names are written in a spec.
- [How to add an axis](../how-to/add-an-axis.md) · [How to add a markup](../how-to/add-a-markup.md)
