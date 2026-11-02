# Implementation Plan: Standalone package

**Branch**: `claude/adoring-cannon-e140c6` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-standalone-package/spec.md`

## Summary

Three modules and two test files exist. Everything that makes them a package
does not: no `pyproject.toml`, no `__init__.py`, no `conftest.py`, no docs, no
lint gate, no CI. This plan adds exactly those, adjusts the three tests the
extraction from `unxt` left behind, and pins the three behaviours that became
cross-distribution contract.

The engine itself is not changed. Research (R3, R4) found that two of the three
"behaviours to pin" are already implemented and already correct — what is
missing is the tests, and in one case the constitution is wrong about where the
behaviour lives. So the shape of this work is: packaging and documentation are
new; the engine's code is untouched; one constitution principle is amended with
its evidence stated.

## Technical Context

**Language/Version**: Python, floor 3.10, CI through 3.15. The floor is a
constitutional constraint, not a default — `>=3.10` is deliberately looser than
`unxt`'s `>=3.12`.

**Primary Dependencies**: exactly two at runtime — `wadler-lindig>=0.1.8` and
`plum-dispatch>=2.7.0`. A test enforces this (principle I). Dev-only:
`pytest`, `sybil`, `pre-commit`/`prek`, `ruff`, `pyright`, `zensical`,
`mkdocstrings[python]`, `pymdown-extensions`.

**Storage**: N/A. The only persistent state is three process-wide registries
(`_AXES`, `_ALIASES`, `_MARKUPS`) populated at import.

**Testing**: `pytest` for the unit suite; `sybil` makes every docstring example
and every Markdown fence a collected test item (principle III).

**Target Platform**: any platform the two dependencies support. CI on Linux.

**Project Type**: library, src layout, hatchling backend.

**Performance Goals**: N/A — this feature adds no code paths that run at
import or render time. The one performance-relevant decision is removing a
subprocess from the test suite (R2), which makes it faster, not slower.

**Constraints**:

- The public surface is the union of two `__all__` tuples plus one submodule.
  No private-but-documented tier.
- Every example must execute. An example may not import a consumer — that
  would be circular, since `unxt` depends on this package.
- `uv lock` must resolve across the whole `>=3.10` range, which forces a marker
  on the docs group (R5).
- Nothing is published; no tag is created.

**Scale/Scope**: 3 source modules (1584 lines), 2 test files (990 lines), 4
documentation pages, 3 workflows. 32 public names.

## Constitution Check

*GATE: passed before Phase 0; re-checked after Phase 1 design below.*

| Principle | Gate | Verdict |
|---|---|---|
| **I. Two dependencies, enforced by a test** | Does this add a runtime dependency? Does the enforcing test exist and actually enforce? | **PASS with a repair.** No runtime dependency added. But the test principle I claims exists is only half there: the current test checks *relative* imports, and the one that was supposed to check the rest was `unxt`-shaped and is vacuous here. T-014 replaces it with the parse-every-module form the principle describes. |
| **II. No domain knowledge** | Does anything added know about units, quantities, arrays or `jax`? | **PASS.** The docs rewrite is driven by this: both converted guides currently argue through quantities and must be re-grounded on `Term`/`Version`/`Point` (R9). That is the principle being enforced on prose, which is where it is easiest to violate. |
| **III. Examples are tests, and owe nothing to a consumer** | Is every example collected and run? Does any example import a consumer? | **PASS.** `conftest.py` (T-009) is what makes this true; before it, no example anywhere runs. No example imports a consumer — the converted guides' quantity examples are replaced, not ported. |
| **IV. One registry, collisions are loud** | Are the three rules contract, and do they hold? | **PASS after amendment.** Bullet 3 holds and is pinned by T-016. Bullets 1 and 2 misdescribe the code: the refusal is at parse, not at registration, and neither claimant "wins" (R3). T-017 amends them, stating the evidence, as governance requires. |
| **V. A rendering claim is pinned by a test that was watched fail** | Was each new test observed failing before the behaviour it asserts was relied on? | **PASS by construction.** T-015, T-016 and T-018 are each written and run *before* their subject is touched or relied upon, and the failure output is recorded in the task. For T-015 and T-016 the behaviour already exists, so "watched fail" means watched fail against a deliberately broken copy — the task says exactly how. |

**Additional Constraints check**: floor 3.10 ✓ (and CI proves it, T-021);
version `0.x` ✓ (`0.1.0`); public surface = `engine.__all__` + `generic.__all__`
+ `examples` ✓ (T-003); docs in Markdown built by zensical, configured in
`zensical.toml` ✓ (T-010), with every plugin's effect verified in the built
site, never inferred ✓ (T-013).

**Development Workflow check**: test first ✓ (T-014 through T-018 each write
and run the test before the change); `uv run pytest` green ✓ (T-019);
`pre-commit run --all-files` as the gate, not `ruff check` alone ✓ (T-008,
T-020); CI 3.10–3.15 ✓ (T-021); pull request on a branch, never `main` ✓
(already on `claude/adoring-cannon-e140c6`, and the `no-commit-to-branch` hook
enforces it).

### Post-Phase-1 re-check

Design added no violations. One thing worth naming: the constitution says the
docs are "Markdown built by `zensical`", and `mkdocstrings` is a MkDocs plugin.
Principle-adjacent risk, handled explicitly — R6/R11 and T-013 require reading
the built HTML to confirm the API page renders members, with a hand-written
fallback if it does not. The constitution's own warning about silent plugin
failure is the reason this is a task rather than an assumption.

## Project Structure

### Documentation (this feature)

```text
specs/001-standalone-package/
├── plan.md              # This file
├── research.md          # Phase 0 — 11 findings, all measured
├── data-model.md        # Phase 1 — the registry entities and their rules
├── quickstart.md        # Phase 1 — the five verification commands
├── contracts/
│   └── public-surface.md  # Phase 1 — the 32 names and the 4 contracts
├── checklists/
│   └── requirements.md    # spec quality checklist
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

Files marked **new** do not exist yet; this feature creates them.

```text
pyproject.toml                       # new — packaging, deps, pytest, ruff, pyright
uv.lock                              # new — generated
README.md                            # new — incl. the load-order note (FR-014)
conftest.py                          # new — Sybil wiring, src/ and docs/
.pre-commit-config.yaml              # new — ruff, ruff-format, pyright, taplo
zensical.toml                        # new — docs config (no mkdocs.yml, ever)

src/wadler_lindig_parts/
├── __init__.py                      # new — re-exports the 32 names + examples
├── engine.py                        # unchanged
├── generic.py                       # unchanged
└── examples.py                      # unchanged

tests/
├── test_engine.py                   # 2 tests adjusted, 1 deleted, 3 added
└── test_downstream.py               # unchanged

docs/
├── index.md                         # new — the grammar
├── api.md                           # new — the public surface
├── explanation/
│   └── why-formatting-is-one-engine.md   # new — converted + re-grounded
└── how-to/
    └── make-a-type-formattable.md        # new — converted + re-grounded

.github/workflows/
├── ci.yml                           # new — lint, tests 3.10–3.15, oldest/newest
├── build_docs.yml                   # new — zensical build --clean --strict
└── cd.yml                           # new — exists, gated on v*, never run

.specify/memory/constitution.md      # principle IV amended (R3)
```

**Structure Decision**: single-project src layout, matching the sibling
project and the import test's existing assumption that modules live at
`src/wadler_lindig_parts/`. No `tests/{unit,integration,contract}` split: there
are two test files and 990 lines of them, and the existing split (engine vs.
downstream-consumer-perspective) is already the meaningful one. Inventing a
three-way directory structure for that would be scaffolding.

## Phase sequencing

The five user stories are independently testable, and the task ordering follows
them, with one deliberate exception: **P1 must land before anything else can be
run at all**, because without `pyproject.toml` and `__init__.py` there is no
importable package and `pytest` cannot collect. So the order is not negotiable
between P1 and the rest, but is between the rest.

```text
P1  packaging          pyproject, __init__, uv.lock         → package installs and imports
P2  suite standalone   test adjustments, conftest           → pytest green, 3.10 and default
P3  contracts pinned   3 new tests, README note             → principle IV/V honoured
P4  docs               zensical.toml, 4 pages, conversion   → site builds strict, examples run
P5  automation         pre-commit, 3 workflows              → gates enforced on every PR
```

Each boundary is a working state. After P2 the package is installable and
tested with nothing else; after P3 it is correct about its own contracts; after
P4 it is documented; after P5 the gates run themselves.

## Risks

| Risk | Likelihood | Handling |
|---|---|---|
| The unresolved `pparts`-returns-one-fragment fault reproduces in the docs examples (R10) | Unknown — never root-caused | Watch for the three-part signature; investigate and report. The workaround used in the consumer's repo (pass literal `PPart`s) is explicitly *not* available, because this package's docs are almost entirely examples over registered types. |
| `mkdocstrings` is silently inert under zensical (constitution's own warning) | Plausible | T-013 reads the built HTML for rendered members. Fallback: hand-written API page, said so in the PR. |
| `--strict` surfaces warnings the sibling project never sees, since it builds with `--clean` only (R6) | Likely at first build | Fix the warnings; they are mostly dead `{doc}` links from the conversion (R9). |
| `uv lock` fails on the 3.10 split (R5) | **Certain without the marker — measured** | Marker on the docs group's 3.11-only entries. |
| A docstring example in `engine.py` has never been executed and is wrong | Plausible — nothing has ever run them | This is the point of T-009. Principle V names exactly this failure mode ("a docstring example showing output nobody ran"). Fix the examples, not the test runner. |

## Complexity Tracking

No constitution violations requiring justification. One deviation from the
model project, recorded for the reviewer:

| Deviation | Why | Alternative rejected because |
|---|---|---|
| Static `version = "0.1.0"` rather than `hatch-vcs` | There are no tags, and the request forbids creating one; `hatch-vcs` with no tags produces a `0.1.dev…+g<sha>` version or fails outright | Tagging to make the version scheme work would violate FR-023 |
| Docs group entries carry a `python_version >= "3.11"` marker | `uv lock` resolves the whole `>=3.10` range and fails hard without it (measured, R5) | Raising the floor to 3.11 contradicts the constitution's explicit reasoning about not inheriting a consumer's floor |
| `--strict` added to the docs build, which the model project does not use | FR-019 | — |
