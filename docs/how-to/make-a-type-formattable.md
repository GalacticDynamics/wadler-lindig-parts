---
title: How to make a type formattable
description: Register pparts, route repr and format through the engine, and your type renders in every markup.
---

# How to make a type formattable

One `pparts` method plus two short dunders give your type `repr`, `str`,
`__format__` and every markup. A base class is available if you would rather
not write the dunders, and it is the last section here.

New to the package?
[Make your first formattable type](../tutorials/your-first-formattable-type.md)
builds one from scratch instead of assuming you know the pieces.

## Register `pparts`, then route `repr` and `format`

Return the pieces of the value, each with a role. Mark any piece that is a
separator rather than content with `kind="sep"`, so the `sep` axis leaves it
alone.

`__repr__` names the spec `repr` should use; `__format__` passes the caller's
spec through. A hand-written `__repr__` in the class body survives
`@dataclass`, so no `repr=False` is needed here.

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, pparts, pspec

>>> @dataclasses.dataclass
... class Version:
...     major: int
...     minor: int
...
...     def __repr__(self) -> str:
...         return pspec(self, "bare")
...
...     def __format__(self, spec: str, /) -> str:
...         return pspec(self, spec)

>>> @pparts.dispatch
... def _(obj: Version, /, *, markup="text", **kw):
...     return (
...         PPart("major", str(obj.major)),
...         PPart("dot", ".", "sep"),
...         PPart("minor", str(obj.minor)),
...     )

>>> v = Version(1, 2)
>>> v
1.2
>>> f"{v:html}"
'<span>1</span>.<span>2</span>'

```

The separator is its own fragment, which is why `mul` renders `1.2` rather
than `1 * 2`:

```python
>>> f"{v:mul}"
'1.2'

```

For what you may put in a spec, see
[Format spec grammar](../reference/spec-grammar.md).

Until `pparts` is registered, a dataclass like `Version` prints its fields.
A type that is not a dataclass raises a `TypeError` naming the omission,
rather than looping through the `str` fallback and back into `__repr__`.

## If your type's repr is a constructor expression

Write `__pdoc__` yourself rather than registering `pparts`; `call` layout
renders through it. A plain dataclass already gets a usable `__pdoc__` from
`wadler_lindig`, so it may need nothing at all:

```python
>>> from wadler_lindig_parts import pspec
>>> from wadler_lindig_parts.examples import Point

>>> pspec(Point(1.0, 2.0), "call")
'Point(x=1.0, y=2.0)'

```

For the full recipe, see
[How to write a constructor-form repr](write-a-constructor-repr.md); for why
that one route is not built from fragments, see
[Why formatting is one engine](../explanation/why-formatting-is-one-engine.md).

## If you would rather not write the two methods

`ReprMixin` supplies them, and adds `__str__`, `_repr_html_`, `_repr_latex_`
and a `__pdoc__`. The spec moves to a `__repr_spec__` class attribute, and
`@dataclass(repr=False)` becomes necessary, because a generated `__repr__`
would silently shadow the inherited one:

```python
>>> from wadler_lindig_parts import ReprMixin

>>> @dataclasses.dataclass(repr=False)
... class Release(ReprMixin):
...     major: int
...     minor: int
...     __repr_spec__ = "bare"

>>> @pparts.dispatch
... def _(obj: Release, /, *, markup="text", **kw):
...     return (
...         PPart("major", str(obj.major)),
...         PPart("dot", ".", "sep"),
...         PPart("minor", str(obj.minor)),
...     )

>>> Release(1, 2)
1.2

```

Two things change beyond the base class. `__repr_spec__` is parsed when the
*class* is created, so a bad spec fails at definition rather than on first
print, and reassigning it later has no effect. That also means an axis your
own package registers has to be registered **before** the `class` statement
runs — at import of your package, ahead of the modules defining those
classes, and across two distributions that is load order between them. A spec
inside `__repr__` is parsed on each call, so it has no such ordering
requirement.

## If your type is a dataclass

You may not need `pparts` at all. A dataclass with no registration is laid out
by its fields, and each value renders as its own type does, so a markup or a
value format spec reaches the values inside. A plain dataclass has no
`__format__` that calls the engine, so these examples use `pspec`:

```python
>>> from wadler_lindig_parts.examples import Point, Term

>>> @dataclasses.dataclass
... class Segment:
...     start: Point
...     slope: Term

>>> s = Segment(Point(0.0, 1.0), Term(2.0, "x"))
>>> pspec(s, "product")
'Segment(start=Point(x=0.0, y=1.0), slope=2.0 x)'
>>> pspec(s, ".2f")
'Segment(start=Point(x=0.00, y=1.00), slope=2.00 x)'

```

The fields that print come from `pfields`. Its default follows
wadler-lindig: a field with `repr=False` is left out, and so is a field whose
value is its default object. To change that for one type, register a `pfields`
method; [How to write a constructor-form repr](write-a-constructor-repr.md)
shows one.

The layout is an ordinary `pparts` registration on `Dataclass`, a dispatch
type every dataclass that is not a `ReprMixin` matches. A `pparts` method of
your own for a dataclass therefore replaces the layout by ordinary dispatch.
The values inside are rendered the same way: strings and non-integer numbers
have registrations of their own (a string prints in quotes, a number takes the
value spec), and anything unregistered degrades to its `str`. Those methods are
specific, so a broader registration of yours (a `Union` with `str`, or
`numbers.Number`) does not handle a plain string or float; register the exact
type for that.

## If your type registers no `pparts` at all

A dataclass gets the field layout above. Anything else still renders: it
degrades to `str(obj)`. A value spec it cannot take is ignored, as it is by any
such value, but a spec that is not a valid Python format spec raises before
anything renders. Rendering a type whose own `str` or `repr` routes back into
the engine raises too, since it would otherwise loop.

## See also

- [How to nest formattable values](nest-formattable-values.md) — forward axes to values inside your type.
- [How to write a constructor-form repr](write-a-constructor-repr.md) — the `call` side.
- [How to add an axis](add-an-axis.md) — add a word to the grammar.
- [API](../reference/api.md) — `PPart`, `PGroup`, `ReprMixin`, `pparts`, `pfields`.
