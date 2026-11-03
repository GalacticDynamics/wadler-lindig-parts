---
title: How-to guides
description: Task-sized answers for people already building with wadler-lindig-parts.
---

# How-to guides

Solutions to specific problems, for people already using the package.

If you have never used it before, start with
[Make your first formattable type](../tutorials/your-first-formattable-type.md)
— these guides assume you know what `pparts` is. If you want the full list of
axes, keywords or constraints rather than steps, that is in the
[reference](../reference/index.md).

## Making your types renderable

- [How to make a type formattable](make-a-type-formattable.md) — the base
  case: one `pparts` method and `ReprMixin`.
- [How to nest formattable values](nest-formattable-values.md) — when your
  type holds other formattable values and must forward axes to them.

## Extending the grammar

- [How to add an axis](add-an-axis.md) — when a spec needs to ask for
  something the engine has no word for, including sharing a word safely with
  another library.
- [How to add a markup](add-a-markup.md) — when you need an output format
  beside text, HTML and LaTeX.

## Not yet written

- **How to write `__pdoc__` for a constructor-form repr** — currently covered
  only as a pointer in
  [How to make a type formattable](make-a-type-formattable.md#if-your-types-repr-is-a-constructor-expression).
  A dataclass gets a usable `__pdoc__` for free, so the guide is needed only
  for types that are not dataclasses, and it has to document
  `wadler_lindig`'s protocol rather than this package's.
- **How to register `pvalue` for your own payload type** — `pvalue` is a
  dispatch point, which is how a library with array types decides what a
  value format spec means for them. The extension point is real and public;
  no worked example has been written for it yet.
