---
title: How to nest formattable values
description: Forward **kw from your pparts so axes reach the values inside your type.
---

# How to nest formattable values

This guide shows you how to make a type whose fields are themselves
formattable honour specs it has never heard of.

## Accept `**kw` and forward it

The engine passes every axis your type does not itself consume. Forward that
dictionary to each nested `pparts` call, and wrap each nested result in a
`PGroup` so its fragments stay grouped:

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PGroup, PPart, pparts, pspec
>>> from wadler_lindig_parts.examples import Term

>>> @dataclasses.dataclass
... class Interval:
...     lo: Term
...     hi: Term

>>> @pparts.dispatch
... def _(obj: Interval, /, *, markup="text", **kw):
...     return (
...         PPart("open", "[", "sep"),
...         PGroup("lo", pparts(obj.lo, markup=markup, **kw)),
...         PPart("comma", ", ", "sep"),
...         PGroup("hi", pparts(obj.hi, markup=markup, **kw)),
...         PPart("close", ")", "sep"),
...     )

>>> iv = Interval(Term(0.0, "x"), Term(1.0, "x"))
>>> pspec(iv, "mul")
'[0.0 * x, 1.0 * x)'

```

`Interval` has never heard of the `value` axis, but a format spec still
reaches the coefficients inside both `Term`s, because `**kw` was forwarded:

```python
>>> pspec(iv, ".2f")
'[0.00 x, 1.00 x)'

```

Markup reaches them the same way:

```python
>>> pspec(iv, "html")
'[<span>0.0</span> <span>x</span>, <span>1.0</span> <span>x</span>)'

```

## If you drop `**kw`

The nested values fall back to defaults and silently stop honouring the spec.
Nothing raises — the fragments are still valid — so this is worth a test in
your own suite rather than a review comment.

## If a nested field is not formattable

It degrades to `str(obj)` like any unregistered type. Wrap it in `PPart` with
a role of its own if you want a markup to be able to style it.

## See also

- [How to make a type formattable](make-a-type-formattable.md) — the single-level case.
- [Axes, layouts and markups](../reference/axes.md) — what is being forwarded.
- [API](../reference/api.md) — `PGroup`, `pparts`.
