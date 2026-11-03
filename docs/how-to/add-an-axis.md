---
title: How to add an axis
description: Register a new word in the format-spec grammar, scope it to layouts, and share it safely with other libraries.
---

# How to add an axis

Registering an axis adds a word to the format-spec vocabulary, so a spec can
ask your library for something the package has no concept of.

[Teach the grammar a new word](../tutorials/teach-the-grammar-a-new-word.md)
walks through one end to end if you would rather see it built up.

## Register the axis

An `Axis` is a name, the keywords that set it, a default, and — per layout —
how its value becomes a renderer argument.

```python
>>> from wadler_lindig_parts import (
...     Axis, parse_spec, register_axis, unregister_axis,
... )

>>> _ = register_axis(Axis(
...     name="vector_form",
...     keywords={"vecform": True},
...     default=False,
...     layouts={"call": lambda v: {"vector_form": v}},
... ))

>>> parse_spec("call-vecform")["vector_form"]
True

```

The `layouts` mapping is what scopes the axis. An axis is only legal under the
layouts it declares, and naming it elsewhere is an error rather than a silent
no-op:

```python
>>> try:
...     parse_spec("product-vecform")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'product-vecform': 'vector_form' does not apply to 'product' layout

```

## Register it at import, once

The registry is process-wide. Register your axes when your package is
imported, not lazily — a `__repr_spec__` naming your axis is parsed at class
creation, so the axis must exist before those classes are defined.

Unregister only in tests:

```python
>>> unregister_axis("vector_form")

```

## If you want shorthand for a combination

Register an alias. Its name is a single token; its expansion is a whole spec.

```python
>>> from wadler_lindig_parts import register_alias, unregister_alias

>>> register_alias("terse", "call-type")
>>> parse_spec("terse") == parse_spec("call-type")
True
>>> unregister_alias("terse")

```

The engine ships no aliases at all, so every alias in a running process came
from a consumer.

## If another library might want your keyword

Keywords share one flat namespace. Two axes may claim one word — both
registrations succeed, and the bare word then raises while `axis=word` keeps
working for each claimant.

If you expect to share vocabulary, **write the qualified form from the start**
and a collision can never affect you:

```python
>>> _ = register_axis(Axis(
...     name="vector_form", keywords={"vecform": True}, default=False,
...     layouts={"call": lambda v: {"vector_form": v}},
... ))
>>> parse_spec("call-vector_form=vecform")["vector_form"]
True
>>> unregister_axis("vector_form")

```

Names may not contain `-`; use `_` for a two-word name. For the full set of
constraints see [Registration rules](../reference/registration-rules.md).

## See also

- [How to add a markup](add-a-markup.md) — add an output format instead.
- [Axes, layouts and markups](../reference/axes.md) — the six that ship.
- [API](../reference/api.md) — `Axis`, `register_axis`, `register_alias`.
