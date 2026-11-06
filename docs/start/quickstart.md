---
title: Quickstart
description: A type of your own, printing every way, in about fifteen lines.
---

# Quickstart

A type that prints five ways, from one declaration. Everything below runs as
written.

```
pip install wadler-lindig-parts
```

## Declare the parts

Register a `pparts` method returning the fragments your type is made of, and
route `repr` and `format` through the engine with two short methods:

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, pparts, pspec

>>> @dataclasses.dataclass
... class Duration:
...     amount: float
...     unit: str
...
...     def __repr__(self) -> str:
...         return pspec(self, "bare")
...
...     def __format__(self, spec: str, /) -> str:
...         return pspec(self, spec)

>>> @pparts.dispatch
... def _(obj: Duration, /, *, markup: str = "text", **kw: object) -> tuple:
...     return (
...         PPart("amount", f"{obj.amount:g}"),
...         PPart("gap", " ", "sep"),
...         PPart("unit", obj.unit),
...     )

```

`bare` in `__repr__` is the spec `repr` uses: product layout with no operator
between the parts. `__format__` hands the caller's spec straight to the
engine, which is what makes the markups below work. Register `pparts` in the
same breath as those two methods — a `repr` that routes through the engine
before the engine knows what your type is made of renders through `str`,
which is `repr` again.

Three fragments: an amount, a separator, a unit. The middle one is marked
`sep` so that markups and the separator axis can treat it differently from
content.

## Use it

```python
>>> d = Duration(1.5, "hours")

>>> d
1.5 hours
>>> str(d)
'1.5 hours'
>>> f"{d}"
'1.5 hours'

```

`repr` and `format` are the two methods above. `str` came free: Python falls
back to `__repr__` when a type defines no `__str__`.

## And the markups

```python
>>> f"{d:html}"
'<span>1.5</span> <span>hours</span>'
>>> f"{d:latex}"
'$1.5\\ hours$'

```

Each content fragment is wrapped for the markup; the `gap` separator becomes
a LaTeX spacing command, because math mode discards a literal space. You
wrote neither rule — they belong to the markups, and `Duration` never
mentions them.

## The convenience base class

`ReprMixin` writes those two methods for you, and adds `__str__`, the Jupyter
hooks and a `__pdoc__`. The spec goes in a `__repr_spec__` class attribute
instead of in `__repr__`, and it needs `@dataclass(repr=False)`, because a
generated `__repr__` would silently shadow the inherited one. Most types do
not need a base class for two short methods, so the examples here write them
out; [How to make a type formattable](../how-to/make-a-type-formattable.md)
shows both routes, and [Format spec grammar](../reference/spec-grammar.md)
says what a spec may contain.

## Next

- [Your first formattable type](../tutorials/your-first-formattable-type.md)
  — the same ground at a walking pace, with the reasoning.
- [How to make a type formattable](../how-to/make-a-type-formattable.md) —
  the reference version of what you just did.
- [Is it right for me?](is-it-right.md) — if you are still deciding.
