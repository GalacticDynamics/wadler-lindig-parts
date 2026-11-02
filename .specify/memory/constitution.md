# wadler-lindig-parts Constitution

Every principle below is already true of this code and checkable by a command
named beside it. Nothing here is an aspiration: the package was extracted from
`unxt` precisely because these properties already held, and the extraction is
what makes them worth stating.

## Core Principles

### I. Two dependencies, enforced by a test (NON-NEGOTIABLE)

The runtime dependencies are `wadler-lindig` and `plum-dispatch`. Nothing else,
ever. Anything a module needs beyond those two and the standard library is a
design error in that module, not a reason to add a dependency.

This is not a convention to remember. `tests/test_engine.py` parses every
module in `src/wadler_lindig_parts/` and fails on any import outside the
allowed set. A new dependency cannot be added without deleting that test, which
a reviewer will see.

### II. No domain knowledge

The package knows about fragments, roles, axes, markups and documents. It does
not know about units, quantities, arrays, `jax`, or any other domain. A library
that wants its own vocabulary registers an axis; it does not get a special case
here.

The same import test enforces the mechanical half. The judgement half belongs
to review: a role named for one library's concept, or an axis whose keywords
only make sense to one caller, is domain knowledge wearing a generic name.

### III. Examples are tests, and owe nothing to a consumer

Every example in a docstring or a Markdown page is executed by Sybil. An
example that cannot run is a broken test, not stale prose.

This has a sharp consequence the package was built around: an example may not
import a consumer. `unxt` depends on this package, so a doctest importing
`unxt.Quantity` would be circular. `examples.py` exists for this reason and
provides the types the documentation demonstrates on — `Version`, `Term` and
`Point` — each chosen for a property the others lack.

### IV. One registry, shared between libraries; collisions are loud

Axis keywords live in one flat namespace shared by every library that registers
into it. Three rules follow, and they are contract rather than implementation
detail now that the registrants are separate distributions:

- Two axes may claim one word. Both registrations succeed, and neither wins:
  `_KEYWORDS` holds a list of claimants.
- Using the word *bare* in a spec raises, and the error names both claimants
  and both qualified forms.
- `axis=word` always resolves explicitly, so two libraries wanting one word is
  an inconvenience rather than a defeat.

Keyword resolution enforces the first two, at parse time. `register_axis`
refuses a duplicate axis *name*, a second claim on free text, and a keyword
already taken by an *alias* — but deliberately not a keyword another axis
claims. `tests/test_engine.py` pins all three rules.

**Amended 2026-11-02.** The first two bullets previously read "The first
registration of a word wins" and "A second claim on the same word raises, and
the error names both claimants", attributed to `register_axis`. The evidence
that changed: `register_axis` was read, and it appends to a claimant list
rather than refusing — the refusal is in keyword resolution, and no claimant
wins, because the bare word becomes unusable while both qualified forms keep
working. The third bullet is what decided which side was the bug: refusing the
second registration would leave nothing for `axis=word` to resolve to, turning
a shared word into a defeat. The code was right and the principle was wrong.

### V. A rendering claim is pinned by a test that was watched fail

Rendering is full of behaviour that looks obvious and is not: `mul` leaves an
object's own separator alone, a markup wrapper must cost zero layout columns, a
LaTeX control sequence is billed at its visible width. Every such claim in this
package is asserted by a test, and the test was observed failing before the
code existed.

Measured values, not plausible ones. A docstring example showing output nobody
ran is the failure mode this principle exists to prevent.

## Additional Constraints

- **Python `>=3.10`.** Both dependencies allow it. The package is deliberately
  looser than `unxt`, which requires `>=3.12`: a general-purpose renderer
  should not inherit a consumer's floor.
- **Versioning.** `0.x` while the axis and markup APIs are still moving. `1.0`
  when the type-scoped override and markup-composer work has settled.
- **Public surface.** `engine.__all__` + `generic.__all__`, plus `examples`.
  There is no private-but-documented tier: a name downstream needs is public,
  and a name that is public is tested.
- **Docs.** Markdown built by `zensical`, configured in `zensical.toml`.
  Note that zensical silently ignores MkDocs plugins — a plugin named in the
  config neither works nor complains — so a plugin's effect is verified in the
  built site, never inferred from its presence.

## Development Workflow

- Test first. Write the failing test, run it, watch it fail, then implement.
- `uv run pytest` must pass, including the doctests in `src/` and `docs/`.
- `uv run pre-commit run --all-files` is the lint gate. `ruff check` alone is
  not: the formatter and the hooks catch what it does not.
- CI runs the suite on 3.10 through 3.15. The 3.10 job is what makes the floor
  a fact rather than a claim about syntax; the newest job is also where the
  `newest-supported` resolution runs, so the top of the range claims both that
  the suite passes there and that it passes with every dependency upgraded.

  **Amended 2026-11-02**, from `3.10 through 3.14`. The evidence is that 3.15.0
  final had been released and the suite was run on it: 287 passed on 3.15.0
  under the locked resolution, and 287 passed again after
  `uv sync --group tests --upgrade` (plum-dispatch 2.10.1, sybil 10.1.0,
  wadler-lindig 0.1.8), with `import unxt` still failing. The range is a record
  of where the suite is observed to pass, so an interpreter is added once it
  has been run, not when it is announced.
- Changes arrive by pull request on a branch, never by committing to `main`.

## Governance

This constitution describes what is already enforced. When a principle and the
code disagree, that is a bug in one of them — say which, in the pull request,
rather than quietly changing both.

Amending a principle requires saying what evidence changed. Principle I in
particular cannot be amended by adding a dependency; it is amended by arguing
that the package's purpose has changed, and the reviewer who agrees deletes the
test knowingly.

**Version**: 1.2.0 | **Ratified**: 2026-11-02 | **Last Amended**: 2026-11-02
