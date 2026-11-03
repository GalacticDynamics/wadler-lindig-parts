---
title: How to render your own payload type
description: Register a pvalue method so the value axis and format specs mean something for your own numeric types.
---

# How to render your own payload type

A fragment's payload — the array, quantity or vector it carries — is rendered
by `pvalue`. The default sends it through `repr`, or through `format` when the
spec carries one, which suits a scalar and suits nothing with structure.

`pvalue` is a dispatch point, so you can register a method for your own type
and decide there what a value format spec means for it.

## Register a method

Dispatch on your type and return a `wadler_lindig` document:

```python
>>> import dataclasses
>>> import wadler_lindig as wl
>>> from wadler_lindig_parts import markup_table, pspec, pvalue
>>> from wadler_lindig_parts.examples import Term

>>> @dataclasses.dataclass
... class Vec3:
...     x: float
...     y: float
...     z: float
...     def __iter__(self):
...         yield from (self.x, self.y, self.z)

>>> @pvalue.dispatch
... def _(obj: Vec3, /, *, markup="text", short_arrays="compact",
...        value_spec=None, **kw):
...     fmt = (lambda c: format(c, value_spec)) if value_spec else repr
...     text = "<" + ", ".join(fmt(c) for c in obj) + ">"
...     escape = markup_table(markup)["escape"]
...     return wl.TextDoc(escape(text) if escape else text)

>>> t = Term(Vec3(1.0, 2.0, 3.0), "m")
>>> pspec(t, "mul")
'<1.0, 2.0, 3.0> * m'

```

Without the method the payload would have fallen back to its `repr`,
`Vec3(x=1.0, y=2.0, z=3.0)`, which is a constructor call rather than a value.

## Honour `value_spec`

Here the spec is applied to each component. The default could not do that:
it calls `format()` on the payload as a whole, and `format()` on a container
raises.

```python
>>> pspec(t, "mul-.2f")
'<1.00, 2.00, 3.00> * m'

```

## Escape for the markup

A payload's text reaches the output inside whatever markup was asked for, so
apply that markup's `escape` before returning. Skip it and a `<` in your
output becomes a tag:

```python
>>> pspec(t, "html-mul")
'<span>&lt;1.0, 2.0, 3.0&gt;</span> * <span>m</span>'

```

The angle brackets came through as `&lt;` and `&gt;` because the method asked
`markup_table` for the escape function rather than assuming plain text. The
`<span>` wrappers are the engine's, added after.

## If you want `short_arrays` to mean something

The `value` axis's three keywords arrive as `short_arrays`, mapped through
`SHORT_ARRAYS` — `array` → `False`, `values` → `"compact"`, `type` → `True`.
Branch on it if your type has a verbose and a terse form; ignore it if it does
not.

## Accept and forward `**kw`

Axes your method does not consume are passed through it on their way to
anything nested inside. Drop `**kw` and those values stop seeing the spec,
with nothing raised to tell you.

## See also

- [The `value` axis](../reference/axes.md#value) — the keywords and what they map to.
- [How to nest formattable values](nest-formattable-values.md) — the same forwarding rule one level up.
- [API](../reference/api.md) — `pvalue`, `markup_table`, `SHORT_ARRAYS`.
