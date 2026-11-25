---
title: How to nest formattable values
description: Forward **kw from your pparts so axes reach the values inside your type.
---

# How to nest formattable values

When your type holds other formattable values, a spec aimed at those values
has to reach them. It does that only if you forward `**kw`.

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

The nested values fall back to their defaults. Nothing raises, because the
fragments are still well formed — `pspec(iv, ".2f")` would simply print
`[0.0 x, 1.0 x)` and nobody would see a problem. Assert on a nested spec in
your own tests; a reviewer will not catch it.

## If a nested field is not formattable

It degrades to `str(obj)` like any unregistered type. Wrap it in `PPart` with
a role of its own if you want a markup to be able to style it.

A dataclass field is the exception: it gets the field layout, so the spec
reaches its values too. A string has its own method and prints quoted, as in a
`repr`; to show a string as bare text, emit it as `PPart(role, s)` instead of
passing it to `pparts`.

## Pass context from a parent to its children

A container sometimes knows something its children should use, such as a unit
they share and can leave out. Put it in `**kw`: every child's `pparts` and
`pfields` receive it. For a dataclass, `fields_to_parts` and `fields_to_pdoc`
build the default layouts, so a container can add one keyword and keep them:

```python
>>> from wadler_lindig_parts import (
...     ReprMixin, fields_to_parts, fields_to_pdoc, pfields,
... )

>>> @dataclasses.dataclass(repr=False)
... class Leaf(ReprMixin):
...     __repr_spec__ = "call"
...     unit: str

>>> @pfields.dispatch
... def _(obj: Leaf, /, **kw):
...     return () if kw.get("parent_unit") == obj.unit else (("unit", obj.unit),)

>>> @dataclasses.dataclass(repr=False)
... class Tree(ReprMixin):
...     __repr_spec__ = "call"
...     unit: str
...     leaf: Leaf
...
...     def __pdoc__(self, **kw):
...         kw = {**kw, "parent_unit": self.unit}
...         return fields_to_pdoc(self, pfields(self, **kw), **kw)

>>> @pparts.dispatch
... def _(obj: Tree, /, *, markup="text", **kw):
...     kw = {**kw, "parent_unit": obj.unit}
...     return fields_to_parts(obj, pfields(obj, **kw), markup=markup, **kw)

>>> Tree("m", Leaf("m"))
Tree(unit='m', leaf=Leaf())
>>> f"{Tree('m', Leaf('s')):product}"
"Tree(unit='m', leaf=Leaf(unit='s'))"

```

Merge the keyword into `kw` as shown, rather than passing it beside `**kw`. A
container nested inside another then replaces its parent's value instead of
raising a duplicate-keyword error.

## See also

- [How to make a type formattable](make-a-type-formattable.md) — the single-level case.
- [Axes, layouts and markups](../reference/axes.md) — what is being forwarded.
- [API](../reference/api.md) — `PGroup`, `pparts`, `pfields`, `fields_to_parts`, `fields_to_pdoc`.
