---
title: What it does
description: A type says what it is made of, once, and every output route lays that same description out its own way.
---

# What wadler-lindig-parts does

A Python type that wants to print well ends up writing the same object out
several times. `__repr__` spells it one way. `__str__` spells it another.
`__format__` grows a little language of its own. Then a notebook asks for
`_repr_html_`, a paper wants LaTeX, and each of those is written separately
too. Five functions describe one object, and they drift, because nothing
holds them together.

This package replaces the five with one. A type declares what it is **made
of** — a sequence of labelled fragments — and every output route lays that
same declaration out in its own way.

## The declaration

A type registers `pparts`, which returns its fragments. Each fragment carries
a **role** naming what it is, and a **kind** saying whether it is content or a
separator:

```python
>>> from wadler_lindig_parts import PPart, pparts
>>> from wadler_lindig_parts.examples import Term

>>> pparts(Term(2.0, "x"))
(PPart(role='coeff', text='2.0', kind='content', doc=TextDoc(text='2.0', width=True)),
 PPart(role='mul', text=' * ', kind='sep', doc=None),
 PPart(role='symbol', text='x', kind='content', doc=None))

```

That is the whole description of a `Term`: a coefficient, a product
separator, a symbol. Nothing in it mentions HTML, or LaTeX, or line widths.

## Every route reads the same declaration

```python
>>> t = Term(2.0, "x")

>>> repr(t)
'2.0 * x'
>>> f"{t:html-mul}"
'<span>2.0</span> * <span>x</span>'
>>> f"{t:latex-mul}"
'$2.0 \\; x$'

```

The HTML wraps each content fragment in a `<span>`. The LaTeX wraps the whole
thing in `$…$` and renders the separator as a spacing command, because math
mode discards the literal space that plain text uses.

`mul` there asks to keep the operator visible. It is not decoration: the
separator style is an axis of its own, and its default is `bare`, which drops
the operator and leaves a space. Compare:

```python
>>> f"{t:html}"
'<span>2.0</span> <span>x</span>'
>>> f"{t:latex}"
'$2.0 \\, x$'

```

Two spacing commands rather than one separator string, because LaTeX math
mode needs `\,` where plain text needs a space. Neither of those
decisions is in `Term`. They belong to the markups, and a markup added later
reaches every registered type without those types changing.

## The payload is still yours

A fragment can carry a payload rather than fixed text, and then an ordinary
Python format spec reaches it:

```python
>>> f"{t:mul-.3f}"
'2.000 * x'

```

`mul` is a keyword naming the separator style; `.3f` is the format spec,
applied to the payload. The grammar is a `-`-joined run of keywords ending in
an optional format spec — see
[Format spec grammar](../reference/spec-grammar.md).

## What you get back

The engine does not return a string directly. It builds a
[Wadler-Lindig](https://github.com/patrick-kidger/wadler_lindig) document and
lays it out, which is what makes width work: the same fragments break across
lines at a narrow width, and the markup wrappers cost no columns, so a line
breaks in the same place in every markup.

```python
>>> from wadler_lindig_parts import doc_to_str, parts_to_doc

>>> long_term = Term([float(i) for i in range(8)], "x")
>>> print(doc_to_str(parts_to_doc(pparts(long_term)), 20))
[0.0, 1.0, 2.0, 3.0,
 4.0, 5.0, 6.0, 7.0] *
  x

```

## Where to go next

- [Is it right for me?](is-it-right.md) — what you have, and whether this
  applies to it.
- [Quickstart](quickstart.md) — a type of your own, printing every way, in
  about fifteen lines.
- [Why one engine rather than four](../explanation/why-formatting-is-one-engine.md)
  — the argument, and what the choice costs.
