---
title: Teach the grammar a new word
description: Add "total" to the format-spec vocabulary and watch it compose with HTML and LaTeX for free.
---

# Teach the grammar a new word

In the last tutorial we built a `Duration` that prints as `3:07`. In this one
we will teach the format-spec grammar a word it has never heard — `total` —
so that `f"{d:total}"` prints `187s`, and so that `f"{d:html-total}"` works
the moment `total` exists, without our writing anything for it.

Start by pasting in the type from last time:

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

## Step 1: teach the type the new behaviour

First the behaviour, then the word. Our `pparts` takes a `total` keyword and
returns different fragments when it is set:

```python
>>> @pparts.dispatch
... def _(obj: Duration, /, *, markup="text", total=False, **kw):
...     if total:
...         return (
...             PPart("total", str(obj.minutes * 60 + obj.seconds)),
...             PPart("unit", "s", "sep"),
...         )
...     return (
...         PPart("minutes", str(obj.minutes)),
...         PPart("colon", ":", "sep"),
...         PPart("seconds", f"{obj.seconds:02d}"),
...     )

>>> d = Duration(3, 7)
>>> d
3:07

```

## Step 2: watch the word do nothing

The behaviour exists, but nothing can ask for it yet. Try the spec anyway:

```python
>>> f"{d:total}"
'3:07'

```

Nothing happened — and notice that nothing complained either. Let's see what
the engine made of our word:

```python
>>> from wadler_lindig_parts import parse_spec
>>> parse_spec("total")["value"]
'total'

```

It did not recognise `total` as a keyword, so it fell through to the last
thing a spec can be: a format spec for the values inside. It landed on the
`value` axis, where our plain-text fragments ignore it. An unregistered word
is not an error; it is just a word nothing is listening for.

## Step 3: register the word

Now we make it mean something. An `Axis` is a word, a default, and how its
value reaches the renderer:

```python
>>> from wadler_lindig_parts import Axis, register_axis

>>> _ = register_axis(Axis(
...     name="total_seconds",
...     keywords={"total": True},
...     default=False,
...     layouts={"product": lambda v: {"total": v}},
... ))

```

That says: the word `total` sets this axis to `True`; when unset it is
`False`; and under `product` layout its value is handed to the renderer as
`total=...` — which is exactly the keyword our `pparts` is waiting for.

Ask again:

```python
>>> f"{d:total}"
'187s'

```

Three minutes and seven seconds is 187 seconds. The word is now part of the
grammar.

## Step 4: the part we did not write

We taught the grammar one word. We said nothing about HTML, and nothing about
LaTeX — but both now accept it:

```python
>>> f"{d:html-total}"
'<span>187</span>s'
>>> f"{d:latex-total}"
'$187s$'

```

Both work. The word we added combines with markups that already existed, and
with any markup registered after it.

Notice that `s` did not get a `<span>` in the HTML — we marked it `"sep"` in
step 1, and the markup treats separators differently from content, just as it
did with the colon.

The order of the words does not matter either:

```python
>>> parse_spec("html-total") == parse_spec("total-html")
True

```

And the plain form still behaves:

```python
>>> f"{d}"
'3:07'

```

## Step 5: put the registry back

One last thing. The registry is process-wide: `total` is now a word for every
piece of code in this session, not just for our `Duration`. A library would
want exactly that. A tutorial should hand the session back as it found it:

```python
>>> from wadler_lindig_parts import unregister_axis, AXES

>>> unregister_axis("total_seconds")
>>> sorted(AXES)
['indent', 'layout', 'markup', 'sep', 'value', 'width']

```

Back to the six the engine ships with. And `total` is just text again:

```python
>>> f"{d:total}"
'3:07'

```

## What we built

A format spec the package had never heard of, which worked with every markup
it already had — from one `Axis` and one extra branch in `pparts`.

We unregistered it only because this was a shared session. A real library
registers its axes once, when it is imported, and leaves them there.

- The same task without the narration:
  [How to add an axis](../how-to/add-an-axis.md)
- Every axis the engine ships, and what each one controls:
  [Axes, layouts and markups](../reference/axes.md)
- What registration accepts and refuses:
  [Registration rules](../reference/registration-rules.md)
- Why one flat namespace, and what happens when two libraries want one word:
  [Why formatting is one engine](../explanation/why-formatting-is-one-engine.md)
