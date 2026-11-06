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

Inherit `ReprMixin`, and register a `pparts` method returning the fragments
your type is made of. `repr=False` on the dataclass decorator matters: a
generated `__repr__` would shadow the one `ReprMixin` provides, and the
shadowing is silent.

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, ReprMixin, pparts

>>> @dataclasses.dataclass(repr=False)
... class Duration(ReprMixin):
...     amount: float
...     unit: str
...     __repr_spec__ = "bare"

>>> @pparts.dispatch
... def _(obj: Duration, /, *, markup: str = "text", **kw: object) -> tuple:
...     return (
...         PPart("amount", f"{obj.amount:g}"),
...         PPart("gap", " ", "sep"),
...         PPart("unit", obj.unit),
...     )

```

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

That is `repr`, `str` and `__format__`, none of which you wrote.

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

## What `__repr_spec__` did

It chose the spec `repr` uses. `bare` means product layout with no operator
between the parts. Change it and `repr` changes with it, while every other
route keeps working:

```python
>>> @dataclasses.dataclass(repr=False)
... class Loud(ReprMixin):
...     amount: float
...     unit: str
...     __repr_spec__ = "mul"

>>> @pparts.dispatch
... def _(obj: Loud, /, *, markup: str = "text", **kw: object) -> tuple:
...     return (
...         PPart("amount", f"{obj.amount:g}"),
...         PPart("mul", " * ", "sep"),
...         PPart("unit", obj.unit),
...     )

>>> Loud(1.5, "hours")
1.5 * hours

```

## Next

- [Your first formattable type](../tutorials/your-first-formattable-type.md)
  — the same ground at a walking pace, with the reasoning.
- [How to make a type formattable](../how-to/make-a-type-formattable.md) —
  the reference version of what you just did.
- [Is it right for me?](is-it-right.md) — if you are still deciding.
