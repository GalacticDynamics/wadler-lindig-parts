# wadler-lindig-parts

A parts layer over [`wadler-lindig`][wl]: one engine behind `repr`, `str`,
`__format__` and the representations Jupyter asks for.

A type joins in by saying what it is *made of*, not how it renders. Register
`pparts` and the type gets every markup, every value form and the per-element
format spec — including axes added later by somebody else.

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, ReprMixin, pparts

>>> @dataclasses.dataclass(repr=False)  # repr=True would shadow the mixin
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

>>> Version(2, 1)
2.1
>>> f"{Version(2, 1):html}"
'<span>2</span>.<span>1</span>'
>>> f"{Version(2, 1):latex}"
'$2.1$'

```

One `pparts` method; four output routes, and they cannot disagree.

## Install

```bash
pip install wadler-lindig-parts
```

Two runtime dependencies, `wadler-lindig` and `plum-dispatch`, and nothing
else — ever. A test parses every module and fails on any import outside that
set plus the standard library, so a third dependency cannot be added without
someone deliberately deleting that test.

## Register axes before defining classes that name them

`ReprMixin` resolves `__repr_spec__` when the **class is created**, not at
first print. So a spec naming an axis or alias that is not yet registered
fails at the `class` statement:

```python
>>> from wadler_lindig_parts import Axis, register_axis, unregister_axis

>>> try:
...     class TooEarly(ReprMixin):
...         __repr_spec__ = "call-vecform"
... except ValueError as e:
...     print("class creation failed:", str(e).split(":")[0])
class creation failed: invalid format spec 'call-vecform'

>>> _ = register_axis(Axis(
...     name="vector_form",
...     keywords={"vecform": True},
...     default=False,
...     layouts={"call": lambda v: {"vector_form": v}},
... ))
>>> class NowFine(ReprMixin):
...     __repr_spec__ = "call-vecform"
>>> NowFine._repr_spec_parsed["vector_form"]
True
>>> unregister_axis("vector_form")

```

Inside one package that was a statement about the order of lines in an
`__init__.py`. Between two installed distributions it is **load order between
them**: register your axes at import of your own package, before importing or
defining the classes whose repr specs use them. The error arrives at a `class`
statement that looks unrelated to the registration, which is why it is written
down here rather than left to the message.

## Keywords share one flat namespace

Every registering distribution writes into the same keyword index, so a run of
keywords can be written in any order — `html-bare` and `bare-html` are the
same request. Two packages may want the same word, and both registrations
succeed: the bare word then raises and names both claimants, while `axis=word`
keeps working for each.

A collision therefore costs one word in one spec, not a rewrite and not a
registration. A package expecting to share vocabulary can write the qualified
form from the start.

## Documentation

<https://galacticdynamics.github.io/wadler-lindig-parts>

New to the package? [Make your first formattable
type](https://galacticdynamics.github.io/wadler-lindig-parts/tutorials/your-first-formattable-type/)
builds one from nothing in a few minutes. Already building something? The
[how-to guides](https://galacticdynamics.github.io/wadler-lindig-parts/how-to/)
are task-sized, and the
[reference](https://galacticdynamics.github.io/wadler-lindig-parts/reference/)
has the spec grammar and every public name.

[wl]: https://github.com/patrick-kidger/wadler-lindig
