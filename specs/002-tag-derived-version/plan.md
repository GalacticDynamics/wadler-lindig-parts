# Implementation Plan: Tag-derived version

**Branch**: `002-tag-derived-version` | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-tag-derived-version/spec.md`

## Summary

Stop declaring the version and start deriving it from the repository's `v*`
tags, so that a release is a tag push. `pyproject.toml` declares the version
dynamic and names `hatch-vcs` as a build requirement; `uv.lock` loses the one
line that repeated the number; `ci.yml`'s `lint` job gains the full history
every other job already fetches; and `cd.yml` gains one step that refuses to
rebuild a version PyPI already holds, plus the header comment that says why.
The release path's filename, its two environment names and its
test-index-first ordering do not move.

That one new step is the answer to the only hazard the measurements turned up:
a moved tag re-runs the whole publish path and reports success while
publishing nothing (R9). An earlier draft of these artefacts claimed such a
run went red. It does not, and that is the worse outcome.

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

**Scale/Scope**: four files changed, one of them by a single deleted line.

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
├── quickstart.md         # the commands that prove it, and what they print
├── checklists/
│   └── requirements.md
└── tasks.md              # /speckit-tasks output
```

There is no `data-model.md` and no `contracts/`. This feature introduces no
entity, no field and no state machine, and what a tag promises is stated where
it is enforced: in `cd.yml`'s own comments and in FR-002 to FR-004, FR-008 and
FR-013. A separate contract document said the same things a third time.

### Source Code (repository root)

```text
pyproject.toml                  # version declared dynamic; hatch-vcs added to the build; version config added
uv.lock                         # one line removed, by re-locking
.github/workflows/ci.yml        # fetch-depth: 0 on the lint job
.github/workflows/cd.yml        # one step in the build job, plus the header comment that explains it
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

**P2 - the automation agrees with that, and says so.** `ci.yml`'s `lint` job
gets the history it now needs; `cd.yml` gets the refusal and the comment that
explains it. Neither changes what a release builds. This is User Story 3's
second scenario, User Story 1's fourth, and FR-007, FR-011 and FR-013.

## Risks

| Risk | Likelihood | Handling |
|---|---|---|
| A wheel cannot be built from the published source distribution, because there is no git history there | Plausible, and the only way this feature fails quietly | Measured before writing the plan: it works, and the version comes from the source distribution's `PKG-INFO` (R6). This is the path the release workflow itself takes. |
| `uv.lock` ends up inconsistent, so `--locked` or `--frozen` fails in CI | Low | Re-lock rather than hand-edit, then run both gates that use those flags. Measured: the diff is one deleted line (R5). |
| The `lint` job starts emitting a shallow-checkout warning | **Certain without the fix - measured** | `fetch-depth: 0` on that job (R8). |
| A build on a pull request produces an unuploadable version and somebody reads that as a failure | Plausible | `no-local-version` keeps development versions well-formed (R2), and the publish jobs' `refs/tags/v` guard is what actually prevents a publish. |
| A future reader changes the release path without knowing the tag is the version | Plausible - it is the comment's whole job | FR-011: the comment that already explains the fixed filename and environments also records the tag-is-the-version rule. |
| A moved tag re-runs the publish path and reports success while publishing nothing | **Already happened — measured.** `v0.2.0` was force-updated on 2026-11-06 and run `42186814040` went green on all three jobs while PyPI's upload timestamps stayed those of the first run | One step at the top of the `build` job refuses a version PyPI already holds, so the second attempt fails instead of reporting success (FR-013, R9). An earlier draft of these artefacts asserted the opposite — that such a run went red — and that error is what the step exists to correct. |
| A moved tag points a published version at a different commit, which nothing compares | Plausible, and not covered by the evidence above — that run never reached it | The same step. It refuses before the build, so it does not depend on what the upload would have done with differing files. Preventing the tag from moving at all is better and is a repository setting rather than a file; raised in the pull request. |
| The new step fails a release because of a network blip | Plausible | A re-run is the fix, and it is stated in the step's own comment. The step uses `python3` and the standard library only. |

## Complexity Tracking

No constitution violations requiring justification. Four deviations from the
model project, recorded for the reviewer:

| Deviation from `quax@main` | Why | Alternative rejected because |
|---|---|---|
| No `build.hooks.vcs.version-file`, and so no `_version.py` and no `__version__` | The constitution fixes the public surface and says there is no private-but-documented tier; a generated version module exists to back a public attribute this package does not have. `importlib.metadata` already answers the question, which is the reason `galax` gives for the same omission | Writing the file to match `quax` exactly would add a generated module, a `.gitignore` entry and a linter exclusion in service of a name nobody asked for |
| The source-distribution allowlist is kept, which `quax` has no equivalent of | It exists because of a measured 202 KB regression, and its comment says anything added later is excluded by default | Dropping it to match the model project would re-open a fault this repository has already had |
| The release path has a test-index stage before the real one, which `quax` does not | It predates this feature. It is also why the new refusal reads PyPI and not TestPyPI: a run that died between the two stages has already filled TestPyPI and has to be let through (R9) | Removing it to match the model project would lose the stage that catches a package which cannot be uploaded at all |
| The `build` job refuses a version PyPI already holds, which no project in the family does | The measured behaviour of a moved tag is a green run that publishes nothing (R9). With the version derived from the tag, the tag is the only statement of which commit a version is, so the release path is where the missing check belongs | Doing nothing was the earlier draft's answer and rested on a mistake about what the index does; `skip-existing: true` makes the no-op explicit rather than loud |

One further difference, recorded because it looks like a deviation and is not:
`figpress` and the other date-versioned libraries carry a workflow step that
checks the written version against the tag, and this repository gains no such
step. That step keeps two copies of a number in agreement; this feature
removes the second copy (R10).
