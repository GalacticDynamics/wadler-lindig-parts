---
title: Is it right for me?
description: What you have, what you want, and whether this package applies.
---

# Is wadler-lindig-parts right for my type?

This package fits when one thing holds: **your type has parts**, and you want
more than one way of showing them. A number with a unit. A coefficient and a
symbol. A version with a major and a minor. A vector with components and a
frame.

If your type prints one way and always will, `__repr__` is enough and this
package is overhead. If it prints two ways that keep drifting apart, or you
have been asked for a notebook rendering and are dreading writing a fourth
spelling, this is what it is for.

## What you have

| You have | Use | Read |
|---|---|---|
| a type whose repr is fixed text with no parts | nothing here — plain `__repr__` | — |
| a type with parts, wanting repr, str and markups from one declaration | register `pparts`, route `repr` and `format` | [Quickstart](quickstart.md), [make a type formattable](../how-to/make-a-type-formattable.md) |
| a container holding other formattable values | forward `**kw` to the children's `pparts` | [nest formattable values](../how-to/nest-formattable-values.md) |
| a type whose repr should rebuild it — `eval(repr(x)) == x` | `__pdoc__`, reached by the `call` layout | [write a constructor-form repr](../how-to/write-a-constructor-repr.md) |
| a payload the engine does not know how to render | register `pvalue` for it | [render your own payload type](../how-to/render-your-own-payload-type.md) |

## What you want

| You want | Use | Read |
|---|---|---|
| HTML in a notebook and LaTeX in a paper, from one declaration | the `markup` axis — `text`, `html`, `latex` | [What it does](what-it-does.md), [axes](../reference/axes.md) |
| an output format the package has never heard of | register a markup row | [add a markup](../how-to/add-a-markup.md) |
| a spec keyword your library's users will type | register an axis | [add an axis](../how-to/add-an-axis.md) |
| long values to break across lines sensibly | nothing — layout is what the engine does | [What it does](what-it-does.md) |
| to know what a spec string may contain | — | [format spec grammar](../reference/spec-grammar.md) |

## What it does not do

- **It does not know your domain.** No units, no arrays, no plotting. It
  knows fragments, roles, axes and markups. Domain vocabulary arrives as an
  axis your library registers.
- **It is not a pretty-printer you call.** It is a protocol your type
  implements. The output comes from `repr`, `str` and `format` as usual.
- **It does not render HTML tables or rich widgets.** A markup wraps
  fragments; it does not lay out a page.

## What it costs

Two runtime dependencies, `wadler-lindig` and `plum-dispatch`, and one
registered function per type. The registry is process-global and shared with
every other library using the package, so keyword collisions are possible —
the first registration of a word wins, a second raises, and `axis=word`
always resolves explicitly. See
[registration rules](../reference/registration-rules.md).
