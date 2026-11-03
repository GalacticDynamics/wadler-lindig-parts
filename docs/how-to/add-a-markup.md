---
title: How to add a markup
description: Register a new output format so every registered type can render in it.
---

# How to add a markup

This guide shows you how to add an output format beside `text`, `html` and
`latex`. Every type that has registered `pparts` gets it immediately —
including types belonging to libraries that know nothing about you.

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

| Key | Meaning |
|---|---|
| `_content` | format string wrapping each `content` fragment |
| `wrap` | format string wrapping the whole rendered value |
| `vsep` | separator between stacked values |
| `escape` | callable applied to text, or `None` for no escaping |

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

Pass a callable as `escape`; it is applied to fragment text before wrapping.
`html.escape` is the obvious choice for markup languages:

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
