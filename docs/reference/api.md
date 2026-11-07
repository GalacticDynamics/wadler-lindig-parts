---
title: API
description: Every public name in wadler_lindig_parts, generated from its docstrings.
---

# API

The public surface is the top-level `wadler_lindig_parts` module: every name
below is reachable as `wadler_lindig_parts.<name>`. There is no
private-but-documented tier — a name a consumer needs is public, and a name
that is public is tested.

For the grammar these functions read, see
[Format spec grammar](spec-grammar.md); for the vocabulary, see
[Axes, layouts and markups](axes.md).

## The extension point

::: wadler_lindig_parts.pparts

::: wadler_lindig_parts.render_options

::: wadler_lindig_parts.PPart

::: wadler_lindig_parts.PGroup

::: wadler_lindig_parts.doc_part

::: wadler_lindig_parts.ReprMixin

## Registration

::: wadler_lindig_parts.Axis

::: wadler_lindig_parts.register_axis

::: wadler_lindig_parts.unregister_axis

::: wadler_lindig_parts.register_alias

::: wadler_lindig_parts.unregister_alias

::: wadler_lindig_parts.register_markup

::: wadler_lindig_parts.unregister_markup

## The registries

::: wadler_lindig_parts.AXES

::: wadler_lindig_parts.ALIASES

::: wadler_lindig_parts.MARKUPS

::: wadler_lindig_parts.REQUIRED_MARKUP_KEYS

::: wadler_lindig_parts.markup_table

## Specs

::: wadler_lindig_parts.Spec

::: wadler_lindig_parts.parse_spec

::: wadler_lindig_parts.pspec

::: wadler_lindig_parts.render

::: wadler_lindig_parts.bad_spec

::: wadler_lindig_parts.inert_axes

## Rendering

::: wadler_lindig_parts.parts_to_doc

::: wadler_lindig_parts.parts_to_markup

::: wadler_lindig_parts.pparts_to_pdoc

::: wadler_lindig_parts.doc_to_str

::: wadler_lindig_parts.math_doc

::: wadler_lindig_parts.unwrap_math

::: wadler_lindig_parts.pvalue

::: wadler_lindig_parts.FLAT

::: wadler_lindig_parts.SHORT_ARRAYS

## Example types

The types the documentation demonstrates on. They exist because an example may
not import a consumer: `unxt` depends on this package, so a doctest reaching
for `unxt.Quantity` would be circular. `Version` and `Term` register `pparts`;
`Point` deliberately does not.

::: wadler_lindig_parts.examples
