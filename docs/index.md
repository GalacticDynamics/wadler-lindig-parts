---
title: wadler-lindig-parts
description: One engine behind repr, str, __format__ and the representations Jupyter asks for.
---

# wadler-lindig-parts

One engine behind `repr`, `str`, `__format__` and the representations Jupyter
asks for. A type says what it is **made of** — a tree of roled fragments — and
every output route lays that same tree out its own way.

Add a markup and every registered type gets it. Register a type and it gets
every markup, including ones added later by somebody else.

```python
>>> from wadler_lindig_parts.examples import Version

>>> v = Version(2, 1)
>>> v
2.1
>>> f"{v:html}"
'<span>2</span>.<span>1</span>'
>>> f"{v:latex}"
'$2.1$'

```

Three routes, one `pparts` method, and they cannot disagree.

```
pip install wadler-lindig-parts
```

Exactly two runtime dependencies — `wadler-lindig` and `plum-dispatch` —
on Python 3.10 through 3.15.

## Where to go

<div class="grid cards" markdown>

- **[Tutorials](tutorials/index.md)**

    Start here if the package is new to you. Two lessons that build a type
    from nothing and then extend the grammar it speaks.

- **[How-to guides](how-to/index.md)**

    Task-sized answers for people already building something: register a
    type, nest values, add an axis, add a markup.

- **[Reference](reference/index.md)**

    The spec grammar, the six axes, the registration rules, and every public
    name.

- **[Explanation](explanation/index.md)**

    Why there is one engine rather than four, and what the design cost.

</div>

## What a spec looks like

A format spec is a `-`-joined run of keywords, optionally ending in an
ordinary Python format spec:

```python
>>> from wadler_lindig_parts.examples import Term

>>> t = Term(2.0, "x")
>>> f"{t:mul}"
'2.0 * x'
>>> f"{t:html-mul}"
'<span>2.0</span> * <span>x</span>'
>>> f"{t:mul-.3f}"
'2.000 * x'

```

The full rules are in [Format spec grammar](reference/spec-grammar.md).
