# 003 — A field layout for every dataclass

**Date**: 2026-11-24 | **Branch**: `003-dataclass-field-layout` | **Milestone**: `v0.4.0`

## What changes

A dataclass with no `pparts` of its own used to render as its `str` text in the
parts layout. Now it renders as `Name(field=value, ...)`, and each value renders
through its own `pparts`. A markup or a value format spec given to the dataclass
therefore reaches the values inside it.

Which fields print is decided in one place, `pfields`. Both routes use it: the
parts layout of any dataclass, and the constructor form (`call`) of a `ReprMixin`
dataclass. A type that registers `pfields` changes its `repr` and its formatted
output together.

The two layouts are public as `fields_to_parts` and `fields_to_pdoc`, so a type
can keep the default layout and add a context keyword for its children. galax
uses this for a composite potential, which leaves out a component's unit system
when it matches the composite's.

`ReprMixin` gains `__notebook_parts__`. When it is true, a `call` type shows its
parts layout in a notebook (HTML and LaTeX) instead of its constructor text. It is
false by default, so nothing changes for existing types.

## Why every dataclass

galax asked for this layout so that its own types could adopt the engine by
registering only their exceptions. It could have applied to `ReprMixin` types
only. The maintainer chose every dataclass, so a dataclass from another library
inside a galax object (a coordinax vector, for one) also renders field by field,
with its quantities formatted by unxt, before that library adopts the engine.

## What "default" means

A field is left out when it has `repr=False`, or when its value *is* its default
object and `hide_defaults` is on. This is wadler-lindig's own rule, so the parts
layout and `wl.pformat` cannot disagree. Equality is not used: it is ambiguous for
arrays. A field built by `default_factory` therefore always prints. A type that
wants it hidden uses one shared default object instead. A field that has no
value yet (`init=False`, not set) prints as `<uninitialised>`, as wadler-lindig
prints it.

## Where a value spec goes

A value spec reaches a field's value when the value has its own `pparts`, is a
dataclass, or is a non-integer number that `format(value, spec)` accepts. A
number that rejects a spec a float accepts (a `Fraction` under `.3`) falls back
to its `repr`; a spec no float accepts raises, so a typo is not swallowed. A
value whose own `pparts` refuses a value spec with a `TypeError` (unxt's unit
systems do) is rendered again without it, so `f"{pot:.2e}"` works on a galax
potential that holds one. Any other value prints as
its `repr`: `format` would print `True` as `1.00`, cut a string to the spec's
precision, or read the spec as a date's strftime pattern. So `.2f` formats the
floats in a dataclass and leaves the rest alone, instead of failing on them or
changing them.

A value with no parts of its own prints as wadler-lindig lays it out: its
`repr`, with line breaks under the parent's width, escaped for the markup, and
arrays summarised as `wl.pformat` does under the same `value` setting. So a
string prints in quotes and `"a, b=c"` cannot read as two fields. A `call` mixin
type that is not a dataclass nests as its own `__pdoc__`, unless it registers
`pparts`. Each field goes through ordinary `pparts` dispatch, so a registration
on a parametric type such as `list[X]` is found. At the top level, a
non-dataclass with no `pparts` still raises on a value spec, as before.

## Boundaries

- A `ReprMixin` type with a parts spec and no `pparts` still raises. That guard
  caught a real missing registration in unxt, and the field layout would have
  hidden it. Only a `call`-spec mixin dataclass falls back to its fields.
- A plain dataclass whose hand-written `__repr__` routes through the engine now
  renders its fields instead of raising the recursion error. The recursion guard
  still covers every other type.
- A dataclass that contains itself raises a `TypeError` that says so.
- No new runtime dependency.
