# How to make your own type formattable

A type joins the formatting grammar by saying what it is **made of**, not how
it renders. Register `pparts` and the type gets every markup, every value form
and the per-element format spec — including axes added later by someone else.

This guide is for library authors. For the vocabulary itself, see
[the grammar](../index.md); for why it is built this way, see
[Why formatting is one engine](../explanation/why-formatting-is-one-engine.md).

## Register `pparts`, inherit `ReprMixin`

Register `pparts` to say what the type is made of, and inherit `ReprMixin` to
get `repr`, `str`, `format`, the Jupyter representations and `__pdoc__` from
one spec string.

Use `@dataclass(repr=False)` — the default `repr=True` would overwrite the
mixin's `__repr__`, and the shadowing is silent.

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

>>> Version(1, 2)
1.2
>>> f"{Version(1, 2):html}"
'<span>1</span>.<span>2</span>'

```

The separator is its own fragment with the `sep` kind, so a markup can style
it differently from the numbers — and so the `sep` axis leaves it alone, which
is why `mul` renders `1.2` rather than `1 * 2`:

```python
>>> f"{Version(1, 2):mul}"
'1.2'

```

`__repr_spec__` is parsed when the class is created, so a bad spec fails at
definition rather than on first print. Reassigning it later has no effect.

That timing matters across packages: an axis your spec names must be
registered **before** the `class` statement runs. Since you and the engine are
separate distributions, that is load order between them — register your axes
at import of your own package, before importing the classes whose specs use
them.

If your type's `repr` is a constructor expression, write `__pdoc__` yourself
instead — see
[the explanation](../explanation/why-formatting-is-one-engine.md) for why that
one route is not built from fragments.

## Pass the axes down to nested values

Accept `**kw` in your `pparts` and forward it. The engine sends every axis
your type does not itself handle, so nested values honour specs your type has
never heard of:

```python
>>> from wadler_lindig_parts import PGroup, pspec
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
>>> pspec(iv, ".2f")           # reaches the nested terms
'[0.00 x, 1.00 x)'

```

`Interval` has never heard of the `value` axis. The format spec still reaches
the coefficients inside both `Term`s, because `**kw` was forwarded.

A type that registers no `pparts` still renders — it degrades to `str(obj)` —
but asking it for a value format spec raises, since it has declared no
elements to format.

## Add a keyword of your own

To add an axis, register it with the layouts it applies to and how its value
becomes a renderer argument. To add shorthand for a combination of existing
keywords, register an alias.

Unregister both when you are done, or they stay in the process-wide registry:

```python
>>> from wadler_lindig_parts import (
...     Axis, register_axis, register_alias,
...     unregister_axis, unregister_alias,
... )

>>> _ = register_axis(Axis(
...     name="vector_form",
...     keywords={"vecform": True},
...     default=False,
...     layouts={"call": lambda v: {"vector_form": v}},
... ))
>>> register_alias("terse", "call-type")

>>> from wadler_lindig_parts import parse_spec
>>> parse_spec("terse") == parse_spec("call-type")
True
>>> parse_spec("call-vecform")["vector_form"]
True

>>> unregister_alias("terse")
>>> unregister_axis("vector_form")

```

An axis is scoped to the layouts it declares. Asking for it under another one
is an error rather than a silent no-op:

```python
>>> _ = register_axis(Axis(
...     name="vector_form",
...     keywords={"vecform": True},
...     default=False,
...     layouts={"call": lambda v: {"vector_form": v}},
... ))
>>> try:
...     parse_spec("product-vecform")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'product-vecform': 'vector_form' does not apply to 'product' layout
>>> unregister_axis("vector_form")

```

To add a markup beside `text`, `html` and `latex`, register a row with
`_content`, `wrap`, `vsep` and `escape`:

```python
>>> from wadler_lindig_parts import register_markup, unregister_markup

>>> register_markup(
...     "brackets",
...     {"_content": "[{}]", "wrap": "{}", "vsep": ", ", "escape": None},
... )
>>> f"{Term(2.0, 'x'):brackets-mul}"
'[2.0] * [x]'
>>> unregister_markup("brackets")

```

All four keys are required, and a row missing one is refused when it is
registered rather than when something is first rendered:

```python
>>> try:
...     register_markup("broken", {"_content": "[{}]", "wrap": "{}"})
... except ValueError as e:
...     print(e)
markup row is missing required keys ['vsep', 'escape']

```

## What registration refuses

Registration raises rather than overwriting, so a spec cannot change meaning
without someone editing it. That holds for a duplicate **axis name**, a
duplicate **alias**, a duplicate **markup name**, a keyword that is already an
alias, and a second axis claiming the spec's trailing free-text run:

```python
>>> register_alias("mine", "call-type")
>>> try:
...     register_alias("mine", "product-html")
... except ValueError as e:
...     print(e)
alias 'mine' is already registered as 'call-type'
>>> unregister_alias("mine")

```

It also refuses any registered name containing a `-`. The separator joins a
spec's components and `parse_spec` splits on it before looking anything up, so
such a name could never be resolved — and `axis=word` would not rescue it,
because the qualified form is split first too. Use `_` inside a name if you
need two words:

```python
>>> try:
...     register_alias("two-words", "call-type")
... except ValueError as e:
...     print(e)
alias 'two-words' may not contain '-': it joins the components of a spec, so a
name holding one can never be resolved, with or without a qualifying 'axis='
prefix

```

An alias's *expansion* is a whole spec, so it is full of separators — that is
what an alias is for. The restriction is on the name alone.

A **keyword** claimed by a second axis is the one case that does *not* raise at
registration. Both registrations succeed and the word becomes ambiguous; the
refusal lands when a spec uses it bare, and `axis=word` keeps working for each
claimant. That is deliberate — refusing the second registration would leave
nothing for `axis=word` to resolve to, and a word two libraries both want
would become a defeat rather than an inconvenience.

```python
>>> def claim(name):
...     return Axis(
...         name=name, keywords={"dim": name}, default=None,
...         layouts={"product": lambda v: {name: v}},
...     )
>>> _ = register_axis(claim("units_dim"))
>>> _ = register_axis(claim("vector_dim"))   # succeeds

>>> try:
...     parse_spec("dim")
... except ValueError as e:
...     print(str(e).split(". Expected")[0])
invalid format spec 'dim': ambiguous keyword 'dim'; claimed by 'units_dim', 'vector_dim'. Write it as one of: units_dim=dim, vector_dim=dim

>>> parse_spec("vector_dim=dim")["vector_dim"]
'vector_dim'

>>> unregister_axis("vector_dim")
>>> unregister_axis("units_dim")

```

If you expect to share vocabulary with another library, write the qualified
form from the start and you will never be affected.

## See also

- [The grammar](../index.md) — the scan rule, the six axes, the two layouts.
- [API reference](../api.md) — `Axis` fields, registration constraints, markup rows.
- [Why formatting is one engine](../explanation/why-formatting-is-one-engine.md) — the design, and what it traded away.
