# 003 — A field layout for every dataclass

**Date**: 2026-11-24 | **Branch**: `003-dataclass-field-layout` | **Milestone**: `v0.4.0`

## What changes

A dataclass with no `pparts` of its own used to render as its `str` text in the
parts layout. Now it renders as `Name(field=value, ...)`, and each value renders
through its own `pparts`. A markup or a value format spec given to the dataclass
therefore reaches the values inside it.

Which fields print is decided in one place, `pfields`. Both routes use it: the
parts layout of any dataclass, and the constructor form (`call`) of a `ReprMixin`
dataclass. A `ReprMixin` dataclass that registers `pfields` changes its `repr`
and its formatted output together; a plain dataclass keeps wadler-lindig's own
`repr` and changes only its formatted output.

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

## Ordinary registrations, one rule

The layout is not a special case inside the engine's fallback. It is a
`pparts` method on `Dataclass`, an ABC whose `__subclasshook__` matches every
dataclass that is not a `ReprMixin` (the mixin has its own method, and the two
must not match the same object). A type that registers its own `pparts` wins by
ordinary dispatch. Each field value goes through `pparts` like the child of any
container, so a dataclass and a hand-written container render the same value
the same way.

Two more ordinary registrations cover the values a field layout most often
holds:

- `str` prints quoted, as in a `repr`, so `"a, b=c"` cannot read as two fields.
- A non-integer number (an ABC over `numbers.Number` minus `numbers.Integral`)
  is formatted by the value spec. A number that rejects the spec (a `Fraction`
  under `.3`) prints as it would without one. An `int` or `bool` is left
  alone: `format(True, ".2f")` is `1.00`.

Anything unregistered degrades to its `str`, as in 0.3.

## Where a value spec goes

A value spec formats the values that can take it. An unregistered value, a
string, an integer, a bool and a type with no value to format ignore it,
wherever they sit. A type that formats its own payload through `pvalue` still
decides for itself: a `Term` holding a list raises under `.2f`, as in 0.3. `pspec` rejects a spec that is not a valid Python
format spec before anything renders, so a typo such as `latx` still raises. A
spec that is valid but changes nothing (on an object with no numbers) is a
silent no-op; whether that should raise is open in issue #29, because comparing
the output with and without the spec would also flag correct requests
(`.1f` on `1.5`).

This replaces 0.3's rule that an unregistered object given a value spec raises.
That rule made a container fail as soon as one field could not take the spec.

## Boundaries

- A `ReprMixin` type with a parts spec and no `pparts` still raises. That guard
  caught a real missing registration in unxt, and the field layout would have
  hidden it. Only a `call`-spec mixin dataclass falls back to its fields.
- A plain dataclass whose hand-written `__repr__` routes through the engine now
  renders its fields instead of raising the recursion error. The recursion guard
  still covers every other type.
- Changes visible to 0.3 users, all in parts-layout output: a string prints
  quoted, a non-integer number takes a value spec at the top level, an
  unregistered object ignores a value spec instead of raising, and a free-text
  spec that no float, int or str accepts (a strftime pattern) raises up front.
  `repr`, `str` and `wl.pformat` are unchanged.
- unxt's unit systems raise on a value spec today; with this release they
  should ignore it instead, so a container holding one can take `.2e`.
- A dataclass that contains itself through its fields raises a `TypeError` that
  says so. A cycle through a list or dict stops at the container's own repr
  (`[...]`, or wadler-lindig's `<recursive>` for a `ReprMixin` dataclass).
- The layout's own parts use private roles (`_field_open`, `_field_key`,
  `_field_comma`, `_field_close`), so a markup that styles a common role such as
  `name` cannot rewrite it.
- No new runtime dependency.
