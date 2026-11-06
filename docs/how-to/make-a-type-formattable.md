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

Register `pparts` in the same breath as the two methods. A `repr` that routes
through the engine before the engine knows what the type is made of falls back
to rendering with `str`, which calls `repr` again.

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

## If your type registers no `pparts` at all

It still renders — it degrades to `str(obj)`. Asking it for a value format
spec raises, since it has declared no value a spec could format.

## See also

- [How to nest formattable values](nest-formattable-values.md) — forward axes to values inside your type.
- [How to write a constructor-form repr](write-a-constructor-repr.md) — the `call` side.
- [How to add an axis](add-an-axis.md) — add a word to the grammar.
- [API](../reference/api.md) — `PPart`, `PGroup`, `ReprMixin`, `pparts`.
