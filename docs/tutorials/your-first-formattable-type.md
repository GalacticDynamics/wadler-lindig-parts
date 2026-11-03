---
title: Make your first formattable type
description: Build a Duration type that prints itself as text, HTML and LaTeX — writing the rendering code only once.
---

# Make your first formattable type

In this tutorial we will build a `Duration` type that prints as `3:07`, and
then watch it print itself as HTML and as LaTeX without our writing either.

We will write one method. Everything else arrives on its own.

You need Python 3.10 or newer and the package:

```
pip install wadler-lindig-parts
```

Everything below runs in a Python session. Nothing needs a network, an
account or a key.

## Step 1: a type that cannot print itself yet

Let's start with a plain dataclass holding minutes and seconds:

```python
>>> import dataclasses
>>> from wadler_lindig_parts import PPart, ReprMixin, pparts

>>> @dataclasses.dataclass(repr=False)
... class Duration(ReprMixin):
...     minutes: int
...     seconds: int
...     __repr_spec__ = "bare"

```

Two things in there are doing work. `ReprMixin` is what will route `repr`,
`str` and `format` through the engine. `repr=False` stops the dataclass
decorator writing its own `__repr__` over the one the mixin gives us.

Nothing prints nicely yet, because we have not said what a duration is *made
of*. That is the next step, and it is the only code we write.

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

Now ask for a duration:

```python
>>> Duration(3, 7)
3:07

```

There it is. `str` gives the same thing:

```python
>>> print(Duration(3, 7))
3:07

```

## Step 3: the part we did not write

We described the pieces. We never said anything about HTML. Ask for it
anyway:

```python
>>> f"{Duration(3, 7):html}"
'<span>3</span>:<span>07</span>'

```

Notice that each piece came back wrapped in its own `<span>` — and the colon
did not. Our roles survived into the output.

LaTeX works too, and we did not write that either:

```python
>>> f"{Duration(3, 7):latex}"
'$3:07$'

```

This is the thing to take away from this tutorial: we described the value
once, and every output route laid that same description out its own way.

## Step 4: why the colon was marked

Let's check what `"sep"` bought us. The `mul` keyword asks for a
multiplication separator between a value and its label:

```python
>>> f"{Duration(3, 7):mul}"
'3:07'

```

It left our colon alone. Because we marked that fragment as a separator, the
engine knows it is ours and does not overwrite it. Had we marked it as
content, a request for `mul` would have pushed a `*` into the middle of the
time.

## Step 5: look at what the engine sees

The fragments themselves are plain data, and we can look at them:

```python
>>> pparts(Duration(3, 7))
(PPart(role='minutes', text='3', kind='content', doc=None),
 PPart(role='colon', text=':', kind='sep', doc=None),
 PPart(role='seconds', text='07', kind='content', doc=None))

```

Three fragments, each with the role we gave it, and the middle one carrying
`kind='sep'`. Every markup we asked for above was built from exactly this
tuple.

## What we built

A `Duration` type that renders as text, HTML and LaTeX, from one method. If
you re-run the session from the top you will get the same output every time.

The next tutorial teaches the other half of the system: adding a word to the
format-spec vocabulary, so `Duration` can answer to a spec that did not exist
when we wrote it.

- Next: [Teach the grammar a new word](teach-the-grammar-a-new-word.md)
- The tasks in this tutorial, written for someone who already knows they want
  them: [How to make a type formattable](../how-to/make-a-type-formattable.md)
- Why the roles matter and why there is one engine rather than four:
  [Why formatting is one engine](../explanation/why-formatting-is-one-engine.md)
