# Implementation Plan: Tag-derived version

**Branch**: `002-tag-derived-version` | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-tag-derived-version/spec.md`

## Summary

Stop declaring the version and start deriving it from the repository's `v*`
tags, so that a release is a tag push. `pyproject.toml` declares the version
dynamic and names `hatch-vcs` as a build requirement; `uv.lock` loses the one
line that repeated the number; `ci.yml`'s `lint` job gains the full history
every other job already fetches; and `cd.yml`'s header comment records that
the tag is now the version. Nothing else moves. The release path, its
filename, its two environment names and its test-index-first ordering are
already what they need to be.

The mechanism is `quax`'s, measured against it rather than recalled — see
[research.md](./research.md) R1. The three places this repository differs from
`quax` are in Complexity Tracking below.

## Technical Context

**Language/Version**: Python, floor `>=3.10`, CI through 3.15

**Primary Dependencies**: unchanged at runtime — `wadler-lindig` and
`plum-dispatch`. New at *build* time only: `hatch-vcs` (R11)

**Storage**: N/A

**Testing**: `pytest` with Sybil collecting every Markdown fence under `docs/`
and `README.md` and every docstring under `src/`; 438 tests today

**Target Platform**: a published Python package, built on `ubuntu-latest`

**Project Type**: single library, `src/` layout

**Performance Goals**: N/A

**Constraints**:

- `.github/workflows/cd.yml` keeps its filename, and the `testpypi` and
  `pypi` environment names stay exactly as they are. Each trusted publisher is
  registered against the filename plus one environment name. No setting on
  either index is touched.
- The source-distribution allowlist stays an allowlist and its contents stay
  as they are (R7).
- `src/wadler_lindig_parts/engine.py` may import only `wadler_lindig`, `plum`
  and the standard library, and a test enforces it. A build-time requirement
  is outside what that test sees (R11).
- The public surface does not grow. No `__version__` (R4).
- The `docs` and `lint` dependency groups stay 3.11+ by marker.

**Scale/Scope**: four files changed, one of them by a single deleted line and
one by a single added line.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design — see the second column.*

| Principle | Before design | After design |
|---|---|---|
| I. Two dependencies, enforced by a test | At risk only if a build requirement counted. It does not: the test parses modules under `src/`, and nothing there changes. | Pass. `hatch-vcs` sits in `[build-system] requires`, is absent from the installed package's dependency set, and is invisible to the import test (R11). |
| II. No domain knowledge | Not engaged. | Pass. No module changes. |
| III. Examples are tests, and owe nothing to a consumer | At risk if the version appeared in a page or a docstring, since every fence is executed. | Pass. Measured: the version string appears in no tracked file other than `pyproject.toml` and `uv.lock`, so no example has to change and none becomes wrong. |
| IV. One registry, collisions are loud | Not engaged. | Pass. |
| V. A rendering claim is pinned by a test that was watched fail | Not engaged — this feature makes no rendering claim. Its claims are about build outputs, and they are pinned by builds whose output is read, in [quickstart.md](./quickstart.md). | Pass. |
| Additional: Python `>=3.10` | Unchanged, and the 3.10 job still proves it. | Pass. |
| Additional: Versioning, `0.x` until the override and composer work settles | This feature chooses no version. It chooses where the version is read from. | Pass. |
| Additional: Public surface | At risk from a generated version file backing a `__version__`. | Pass by omission (R4). |
| Workflow: test first | A build is not a unit test, but the ordering still applies: every claim in quickstart.md was run against a throwaway clone *before* the change was written here, including the one that could have failed (R6). | Pass. |
| Workflow: changes arrive by pull request | Branch `002-tag-derived-version`, pull request to `main`, merged by the owner. | Pass. |

No violations. Complexity Tracking below records deviations from the model
project, not from the constitution.

## Project Structure

### Documentation (this feature)

```text
specs/002-tag-derived-version/
├── spec.md
├── plan.md               # this file
├── research.md           # R1-R11, all measured
├── quickstart.md         # the commands that prove it, and their expected output
├── contracts/
│   └── release.md        # what a tag promises, and what is fixed from outside
├── checklists/
│   └── requirements.md
└── tasks.md              # /speckit-tasks output
```

There is no `data-model.md`. This feature introduces no entity, no field and
no state machine; the one thing it has that resembles data is the release
contract, which is in `contracts/release.md` because it is a contract with
parties outside this repository.

### Source Code (repository root)

```text
pyproject.toml                  # version declared dynamic; hatch-vcs added to the build; version config added
uv.lock                         # one line removed, by re-locking
.github/workflows/ci.yml        # fetch-depth: 0 on the lint job
.github/workflows/cd.yml        # header comment only
```

No file under `src/`, `tests/` or `docs/` is touched. There is nothing to add
to `.gitignore`, because no file is generated (R4).

**Structure Decision**: the four files above and nothing else. The version
configuration goes next to the other `[tool.hatch.*]` tables rather than at
the top of the file, so that everything the build backend reads sits in one
place.

## Phases

Two, and the boundary between them is a working state.

**P1 - the version comes from the tag.** `pyproject.toml` and `uv.lock`. At
the end of it the repository builds, the suite passes, and a build at a tagged
commit is named for the tag. This is the whole of User Story 1 and User Story
2.

**P2 - the automation and its record agree with that.** `ci.yml`'s `lint`
job and `cd.yml`'s header comment. Neither changes what is built; both change
what happens when somebody else runs or reads it. This is User Story 3's
second scenario and FR-007 and FR-011.

## Risks

| Risk | Likelihood | Handling |
|---|---|---|
| A wheel cannot be built from the published source distribution, because there is no git history there | Plausible, and the only way this feature fails quietly | Measured before writing the plan: it works, and the version comes from the source distribution's `PKG-INFO` (R6). This is the path the release workflow itself takes. |
| `uv.lock` ends up inconsistent, so `--locked` or `--frozen` fails in CI | Low | Re-lock rather than hand-edit, then run both gates that use those flags. Measured: the diff is one deleted line (R5). |
| The `lint` job starts emitting a shallow-checkout warning | **Certain without the fix - measured** | `fetch-depth: 0` on that job (R8). |
| A build on a pull request produces an unuploadable version and somebody reads that as a failure | Plausible | `no-local-version` keeps development versions well-formed (R2), and the publish jobs' `refs/tags/v` guard is what actually prevents a publish. Recorded in contracts/release.md so the next reader does not have to work it out. |
| A future reader changes the release path without knowing the tag is the version | Plausible - it is the comment's whole job | FR-011: the comment that already explains the fixed filename and environments also records the tag-is-the-version rule. |
| A moved tag leaves a red CD run that looks like a defect in this change | Already happened once, against `v0.2.0` | Written down in the spec's Edge Cases and in R9, with why the refusal is kept rather than worked around. |

## Complexity Tracking

No constitution violations requiring justification. Three deviations from the
model project, recorded for the reviewer:

| Deviation from `quax@main` | Why | Alternative rejected because |
|---|---|---|
| No `build.hooks.vcs.version-file`, and so no `_version.py` and no `__version__` | The constitution fixes the public surface and says there is no private-but-documented tier; a generated version module exists to back a public attribute this package does not have. `importlib.metadata` already answers the question, which is the reason `galax` gives for the same omission | Writing the file to match `quax` exactly would add a generated module, a `.gitignore` entry and a linter exclusion in service of a name nobody asked for |
| The source-distribution allowlist is kept, which `quax` has no equivalent of | It exists because of a measured 202 KB regression, and its comment says anything added later is excluded by default | Dropping it to match the model project would re-open a fault this repository has already had |
| The release path has a test-index stage before the real one, which `quax` does not | It predates this feature, and it is what makes a moved tag or a re-run fail before the index where a version cannot be reused (R9) | Removing it to match the model project would move that failure to the index that matters |

One further difference, recorded because it looks like a deviation and is not:
`figpress` and the other date-versioned libraries carry a workflow step that
checks the written version against the tag, and this repository gains no such
step. That step keeps two copies of a number in agreement; this feature
removes the second copy (R10).
