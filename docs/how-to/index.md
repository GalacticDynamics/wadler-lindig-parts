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
  case: one `pparts` method and two short dunders, with the `ReprMixin`
  shortcut at the end.
- [How to nest formattable values](nest-formattable-values.md) — when your
  type holds other formattable values and must forward axes to them.

- [How to write a constructor-form repr](write-a-constructor-repr.md) — when
  `call` layout should print a constructor call and your type is not a
  dataclass.

## Extending the grammar

- [How to add an axis](add-an-axis.md) — when a spec needs to ask for
  something the engine has no word for, including sharing a word safely with
  another library.
- [How to add a markup](add-a-markup.md) — when you need an output format
  beside text, HTML and LaTeX.
- [How to render your own payload type](render-your-own-payload-type.md) —
  when you own the array or quantity inside a fragment and want to decide
  what a value format spec means for it.
