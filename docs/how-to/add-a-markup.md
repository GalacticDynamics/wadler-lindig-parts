---
title: How to add a markup
description: Register a new output format so every registered type can render in it.
---

# How to add a markup

A markup is an output format: `text`, `html` and `latex` ship, and you can add
more. Every type that has registered `pparts` can render in yours as soon as
it exists, including types from libraries that know nothing about you.

## Register a markup row

A row is four required keys. The name becomes a keyword on the `markup` axis.

```python
>>> from wadler_lindig_parts import register_markup, unregister_markup
>>> from wadler_lindig_parts.examples import Term

>>> register_markup(
...     "brackets",
...     {"_content": "[{}]", "wrap": "{}", "vsep": ", ", "escape": None},
... )
>>> f"{Term(2.0, 'x'):brackets-mul}"
'[2.0] * [x]'
>>> unregister_markup("brackets")

```

Those four keys are the required ones. [Markups](../reference/axes.md#markups)
lists them with their meanings, and the optional keys as well.

## If you want your own separator text

Add a key named after each `sep` keyword. Without one, the markup falls back
to the engine's default for that keyword.

```python
>>> register_markup(
...     "arrows",
...     {"_content": "{}", "wrap": "{}", "vsep": ", ", "escape": None,
...      "mul": " -> ", "bare": " "},
... )
>>> f"{Term(2.0, 'x'):arrows-mul}"
'2.0 -> x'
>>> unregister_markup("arrows")

```

## If your format needs escaping

Pass a callable as `escape` and it is applied to fragment text before
wrapping. For anything angle-bracket-based, `html.escape` is the one you
want:

```python
>>> import html as html_module

>>> register_markup(
...     "safe",
...     {"_content": "{}", "wrap": "{}", "vsep": ", ",
...      "escape": html_module.escape, "bare": " "},
... )
>>> f"{Term(2.0, '<b>'):safe}"
'2.0 &lt;b&gt;'
>>> unregister_markup("safe")

```

## A row missing a key is refused

All four required keys are checked at registration, not when something is
first rendered:

```python
>>> try:
...     register_markup("broken", {"_content": "[{}]", "wrap": "{}"})
... except ValueError as e:
...     print(e)
markup row is missing required keys ['vsep', 'escape']

```

## See also

- [Axes, layouts and markups](../reference/axes.md#markups) — the three rows that ship.
- [Registration rules](../reference/registration-rules.md#markup-rows) — every constraint.
- [API](../reference/api.md) — `register_markup`, `markup_table`, `REQUIRED_MARKUP_KEYS`.
