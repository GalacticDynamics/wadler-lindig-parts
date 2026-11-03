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
>>> from wadler_lindig_parts import PPart, ReprMixin, pparts

>>> @dataclasses.dataclass(repr=False)
... class Duration(ReprMixin):
...     minutes: int
...     seconds: int
...     __repr_spec__ = "bare"

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

It did not recognise `total` as a keyword, so it took it as a *format spec for
the values inside* — which our fragments ignore. That is what an unregistered
word is: not an error, just text that lands somewhere harmless.

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

Here is the payoff. We taught the grammar one word. We said nothing about
HTML, and nothing about LaTeX:

```python
>>> f"{d:html-total}"
'<span>187</span>s'
>>> f"{d:latex-total}"
'$187s$'

```

Both work. Our new word composed with markups that already existed, and it
will compose with any markup added later by anyone.

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

One last thing. The registry is process-wide — our word is visible to every
piece of code in this session, which is the point of a shared grammar, and
also why a tutorial should tidy up after itself:

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

A word that did not exist, which now composes with every markup in the
grammar — and which we removed again in one line.

In a real library you would register your axes at import, once, rather than
unregistering them; the tidy-up above is because we are sharing a session.

- The same task without the narration:
  [How to add an axis](../how-to/add-an-axis.md)
- Every axis the engine ships, and what each one controls:
  [Axes, layouts and markups](../reference/axes.md)
- What registration accepts and refuses:
  [Registration rules](../reference/registration-rules.md)
- Why one flat namespace, and what happens when two libraries want one word:
  [Why formatting is one engine](../explanation/why-formatting-is-one-engine.md)
