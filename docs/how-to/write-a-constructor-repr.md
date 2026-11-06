---
title: How to write a constructor-form repr
description: Give a non-dataclass type a call-layout repr by implementing __pdoc__.
---

# How to write a constructor-form repr

`call` layout prints how to *rebuild* a value. It does not go through
`pparts` at all — it hands off to the object's own `__pdoc__`.

A dataclass already gets a working `__pdoc__` from `wadler_lindig`, so you
need this only when your type is not a dataclass, or when the one you get for
free is not the constructor call you want.

For the `product` side — the fragments every markup is built from — see
[How to make a type formattable](make-a-type-formattable.md). The two are
independent: a type may have both.

## Implement `__pdoc__`

The protocol is `__pdoc__(self, **kwargs) -> None | AbstractDoc`. Build the
document with `wadler_lindig`'s own helpers so that nesting and line breaking
keep working:

```python
>>> import wadler_lindig as wl
>>> from wadler_lindig_parts import pspec

>>> class Interval:
...     def __init__(self, lo, hi):
...         self.lo, self.hi = lo, hi
...     def __pdoc__(self, **kwargs):
...         return wl.bracketed(
...             begin=wl.TextDoc("Interval("),
...             docs=wl.named_objs([("lo", self.lo), ("hi", self.hi)], **kwargs),
...             sep=wl.comma,
...             end=wl.TextDoc(")"),
...             indent=kwargs.get("indent", 2),
...         )

>>> iv = Interval(0.0, 1.0)
>>> pspec(iv, "call")
'Interval(lo=0.0, hi=1.0)'

```

`named_objs` renders each value with the same settings as the enclosing
document, which is why `**kwargs` is forwarded rather than dropped.

The result is a document rather than a string, so it breaks under a narrow
width without your doing anything:

```python
>>> print(pspec(iv, "call", width=16))
Interval(
  lo=0.0, hi=1.0
)

```

## If you only want to override sometimes

Return `None` and the default rendering is used instead. Anything that is not
an `AbstractDoc` is ignored, so a method that returns early is handled by the
same rule — there is no separate opt-out:

```python
>>> class Maybe:
...     def __init__(self, n):
...         self.n = n
...     def __pdoc__(self, **kwargs):
...         if self.n < 0:
...             return None
...         return wl.TextDoc(f"Maybe({self.n})")

>>> pspec(Maybe(3), "call")
'Maybe(3)'
>>> pspec(Maybe(-1), "call")
'<...Maybe object at ...>'

```

## If you want `repr` itself to use it

Write `__repr__` as `pspec(self, "call")`, or inherit `ReprMixin` and set
`__repr_spec__` to a spec whose layout is `call`. The mixin is the shorter of
the two here, because it derives `__pdoc__` from the same spec:

```python
>>> from wadler_lindig_parts import ReprMixin

>>> class Span(ReprMixin):
...     __repr_spec__ = "call"
...     def __init__(self, lo, hi):
...         self.lo, self.hi = lo, hi
...     def __pdoc__(self, **kwargs):
...         return wl.bracketed(
...             begin=wl.TextDoc("Span("),
...             docs=wl.named_objs([("lo", self.lo), ("hi", self.hi)], **kwargs),
...             sep=wl.comma,
...             end=wl.TextDoc(")"),
...             indent=kwargs.get("indent", 2),
...         )

>>> Span(0.0, 1.0)
Span(lo=0.0, hi=1.0)

```

## If the renderer needs options of its own

`wadler_lindig.pformat` takes options that are not spec words, such as a
`custom=` hook that lays out a value type its own way. Return them from
`__repr_options__`. It receives the spec, so an option can apply to some specs
and not others; here the short form is kept out of `array`:

```python
>>> import dataclasses

>>> class Samples:
...     def __repr__(self):
...         return "Samples([0.1, 0.4, 0.2])"

>>> def short_samples(obj):
...     return wl.TextDoc("Samples(3)") if isinstance(obj, Samples) else None

>>> @dataclasses.dataclass(repr=False)
... class Run(ReprMixin):
...     __repr_spec__ = "call-type"
...     data: Samples
...
...     def __repr_options__(self, spec, /):
...         return {"custom": short_samples} if spec["value"] == "type" else {}

>>> Run(Samples())
Run(data=Samples(3))
>>> f"{Run(Samples()):call-array}"
'Run(data=Samples([0.1, 0.4, 0.2]))'

```

`repr`, `str`, `format` and the Jupyter hooks all ask `__repr_options__`, so
setting it once covers every route.

## If your type is a dataclass

Do nothing. `wadler_lindig` already produces the constructor form, and a
dataclass using `ReprMixin` with a `call` spec gets the same:

```python
>>> from wadler_lindig_parts.examples import Point

>>> pspec(Point(1.0, 2.0), "call")
'Point(x=1.0, y=2.0)'

```

## Note on axes

`markup` and `sep` do not apply under `call` — they are `product`-only, and
naming one is an error rather than a silent no-op. `width` and `indent` do
apply, as above. See [Layout scoping](../reference/spec-grammar.md#layout-scoping).

## See also

- [How to make a type formattable](make-a-type-formattable.md) — the `product` side.
- [Axes, layouts and markups](../reference/axes.md#layout) — what `call` and `product` each mean.
- [Why the constructor form is not built from fragments](../explanation/why-formatting-is-one-engine.md) — why this one route delegates.
