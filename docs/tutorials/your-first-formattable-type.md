---
title: Make your first formattable type
description: Build a Duration type that prints itself as text, HTML and LaTeX — writing the rendering code only once.
---

# Make your first formattable type

In this tutorial we will build a `Duration` type that prints as `3:07`, and
then watch it print itself as HTML and as LaTeX without our writing either.

We will write one method, `pparts`. The HTML and the LaTeX come from the
package.

You need Python 3.10 or newer and the package:

```
pip install wadler-lindig-parts
```

Everything below runs in a Python session. Nothing needs a network, an
account or a key.

## Step 1: a type that cannot print itself yet

Let's start with a plain dataclass holding minutes and seconds, and two short
methods that hand its printing to the engine:

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, pparts, pspec

>>> @dataclasses.dataclass
... class Duration:
...     minutes: int
...     seconds: int
...
...     def __repr__(self) -> str:
...         return pspec(self, "bare")
...
...     def __format__(self, spec: str, /) -> str:
...         return pspec(self, spec)

```

`__repr__` asks the engine for one particular spec, `bare`. `__format__`
passes on whatever spec the caller wrote, which is how `f"{d:html}"` will
reach the engine later. No `repr=False` is needed: a `__repr__` written in
the class body survives the dataclass decorator.

Both methods route through the engine, and the engine does not yet know what
a `Duration` is made of, so do not print one until step 2 — an unregistered
type renders through `str`, and `str` on this class is `__repr__` again.
Telling the package what a duration is made of is the next step, and the only
real code we write.

## Step 2: say what it is made of

Register a `pparts` method. It returns the pieces of the value, each with a
**role** — a name for what that piece is:

```python
>>> @pparts.dispatch
... def _(obj: Duration, /, *, markup="text", **kw):
...     return (
...         PPart("minutes", str(obj.minutes)),
...         PPart("colon", ":", "sep"),
...         PPart("seconds", f"{obj.seconds:02d}"),
...     )

```

Notice the third argument on the middle fragment. `"sep"` marks the colon as a
*separator* rather than content — we will see that pay off in step 4.

Now make one and look at it:

```python
>>> d = Duration(3, 7)
>>> d
3:07

```

There it is. `str` gives the same thing:

```python
>>> print(d)
3:07

```

## Step 3: the part we did not write

We described the pieces. We never said anything about HTML. Ask for it
anyway:

```python
>>> f"{d:html}"
'<span>3</span>:<span>07</span>'

```

Notice that each piece came back wrapped in its own `<span>` — and the colon
did not. Our roles survived into the output.

LaTeX works too, and we did not write that either:

```python
>>> f"{d:latex}"
'$3:07$'

```

We described the value once. Each output format read that same description
and wrapped it its own way: `<span>` tags for HTML, `$…$` for LaTeX.

## Step 4: why the colon was marked

Now for the colon. The `mul` keyword asks for a multiplication sign between a
value and its label:

```python
>>> f"{d:mul}"
'3:07'

```

It left the colon alone. A fragment marked `"sep"` is the type's own
separator, so `mul` does not replace it. Marked as content instead, the same
request would have printed `3 * 07`.

## Step 5: look at what the engine sees

The fragments themselves are plain data, and we can look at them:

```python
>>> pparts(d)
(PPart(role='minutes', text='3', kind='content', doc=None),
 PPart(role='colon', text=':', kind='sep', doc=None),
 PPart(role='seconds', text='07', kind='content', doc=None))

```

Three fragments, each with the role we gave it, and the middle one carrying
`kind='sep'`. Every markup we asked for above was built from exactly this
tuple.

## What we built

A `Duration` type that renders as text, HTML and LaTeX, from one `pparts`
method and two lines of plumbing. If you re-run the session from the top you
will get the same output every time.

If you would rather not write those two methods, `ReprMixin` supplies them,
along with `__str__`, the Jupyter hooks and a `__pdoc__`, in exchange for a
base class and a `__repr_spec__`:
[How to make a type formattable](../how-to/make-a-type-formattable.md) shows
both routes.

The next tutorial adds a word to the format-spec vocabulary itself, so
`Duration` can answer to `f"{d:total}"` — a spec that does not exist yet.

- Next: [Teach the grammar a new word](teach-the-grammar-a-new-word.md)
- The tasks in this tutorial, written for someone who already knows they want
  them: [How to make a type formattable](../how-to/make-a-type-formattable.md)
- Why the roles matter and why there is one engine rather than four:
  [Why formatting is one engine](../explanation/why-formatting-is-one-engine.md)
