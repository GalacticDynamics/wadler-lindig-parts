---
title: How to make a type formattable
description: Register pparts and inherit ReprMixin so your type renders in every markup.
---

# How to make a type formattable

This guide shows you how to give your own type `repr`, `str`, `__format__`,
the Jupyter representations and `__pdoc__` from a single `pparts` method.

New to the package? Start with
[Make your first formattable type](../tutorials/your-first-formattable-type.md)
instead — it covers the same ground at a slower pace.

## Register `pparts` and inherit `ReprMixin`

Return the pieces of the value, each with a role. Mark any piece that is a
separator rather than content with `kind="sep"`, so the `sep` axis leaves it
alone.

Use `@dataclass(repr=False)`: the default `repr=True` silently overwrites the
mixin's `__repr__`.

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, ReprMixin, pparts

>>> @dataclasses.dataclass(repr=False)
... class Version(ReprMixin):
...     major: int
...     minor: int
...     __repr_spec__ = "bare"

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

`__repr_spec__` sets the spec used for `repr`. For what you may put in it, see
[Format spec grammar](../reference/spec-grammar.md).

## Register your axes before the class statement

`__repr_spec__` is parsed when the class is created, so a bad spec fails at
definition rather than on first print, and reassigning it later has no effect.

If your spec names an axis your own package registers, register it **before**
the `class` statement runs — at import of your package, ahead of the modules
defining those classes. Across two distributions that is load order between
them.

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

## If your type registers no `pparts` at all

It still renders — it degrades to `str(obj)`. Asking it for a value format
spec raises, since it has declared no elements to format.

## See also

- [How to nest formattable values](nest-formattable-values.md) — forward axes to values inside your type.
- [How to write a constructor-form repr](write-a-constructor-repr.md) — the `call` side.
- [How to add an axis](add-an-axis.md) — add a word to the grammar.
- [API](../reference/api.md) — `PPart`, `PGroup`, `ReprMixin`, `pparts`.
