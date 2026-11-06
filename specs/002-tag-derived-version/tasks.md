---

description: "Task list for deriving wadler-lindig-parts' version from its git tags"
---

# Tasks: Tag-derived version

**Input**: Design documents from `/specs/002-tag-derived-version/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md),
[research.md](./research.md), [contracts/release.md](./contracts/release.md),
[quickstart.md](./quickstart.md)

**Tests**: no new test file. Nothing under `src/` changes, so there is no
behaviour for a unit test to pin, and principle V is about rendering claims.
The claims this feature makes are about build outputs, and the constitution's
"test first" ordering is honoured the only way it can be here: every check
below was run against a throwaway clone before the change was written into
this repository, including the one that could have failed quietly (R6). Each
check task says what output counts as a pass, so a reviewer can re-run it
rather than take it on trust.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel — different files, no dependency on an
  incomplete task
- **[Story]**: which user story the task serves (US1–US3)
- Every task names its exact file path, or the exact command and the output
  that counts as a pass

## Path Conventions

Single project, src layout. Paths are relative to the repository root. Any task
that creates a tag runs in a throwaway clone under `/tmp`, never in the
repository: this feature creates no tag here.

---

## Phase 1: Baseline

**Purpose**: the feature's success criteria are comparisons, so the "before"
side has to be recorded before anything changes. Both outputs go in the pull
request body.

- [X] T001 Record which tracked files *declare* the released version: `git grep -n '0\.2\.0' -- ':!specs'` at the tip of `main`. Expected two hits and both of them declarations — `pyproject.toml:29` and `uv.lock:817`. This is the "two" in SC-003
- [X] T002 [P] Record the source distribution's top-level manifest before the change: `uv build --sdist` then `tar tzf dist/wadler_lindig_parts-0.2.0.tar.gz | sed 's|^wadler_lindig_parts-0.2.0/||' | awk -F/ '{print $1}' | sort -u`. Expected nine entries — the seven allowlisted ones plus `.gitignore` and `PKG-INFO`, which the build backend adds itself. This is the baseline FR-009 is checked against (R7)

---

## Phase 2: User Story 1 — A release is a tag push and nothing else (P1)

**Goal**: the built version comes from the `v*` tag and from nowhere else.

**Independent test**: at a clean commit carrying `vX.Y.Z`, both artefact
filenames carry `X.Y.Z`.

- [X] T003 [US1] In `pyproject.toml`, remove `version = "0.2.0"` from `[project]` and add `dynamic = ["version"]` in its place
- [X] T004 [US1] In `pyproject.toml`, change `[build-system]` `requires` from `["hatchling"]` to `["hatch-vcs", "hatchling"]`. This is a build-time requirement and not a runtime dependency, so constitution principle I is untouched and the import test in `tests/test_engine.py` does not see it (R11)
- [X] T005 [US1] In `pyproject.toml`, add the version configuration immediately above `[tool.hatch.build.targets.sdist]`, so everything the build backend reads sits together: `[tool.hatch.version]` with `source = "vcs"`; `[tool.hatch.version.raw-options]` with `local_scheme = "no-local-version"`; and `[tool.hatch.version.raw-options.scm.git]` with `describe_command = ["git", "describe", "--dirty", "--tags", "--long", "--match", "v*"]`. Write a comment above it recording the two load-bearing parts: `no-local-version` because both indexes reject a local segment outright (measured: `0.2.1.dev1+gc1ffc7a.d20261106` without it, `0.2.1.dev1` with it), and `--match v*` because that is the same glob `cd.yml` is triggered by, so the tag that releases and the tag that sets the version are one set (measured: `--match zzz*` instead yields `0.1.dev37`)
- [X] T006 [US1] Run `uv lock`. Expected `Updated wadler-lindig-parts v0.2.0 -> (dynamic)` and a one-deletion diff in `uv.lock`. Do not hand-edit the lockfile
- [X] T007 [US1] Prove the tag is the version, in a throwaway clone: `git clone . /tmp/wlp-check`, `git remote remove origin`, `git tag v0.9.9`, `uv build`. Pass is `wadler_lindig_parts-0.9.9.tar.gz` and `wadler_lindig_parts-0.9.9-py3-none-any.whl`, with `Building wheel from source distribution` in the output — the same path `hynek/build-and-inspect-python-package` takes. This is FR-002 and SC-004
- [X] T008 [US1] Prove a wheel builds from the published source distribution with no repository history: unpack the `0.9.9` source distribution, confirm `git rev-parse --is-inside-work-tree` fails there, confirm its `PKG-INFO` reads `Version: 0.9.9`, then `uv build --wheel` in that directory. Pass is a `0.9.9` wheel. This is FR-006, and it is the one claim that could have failed silently (R6)
- [X] T009 [US1] Confirm the source distribution still carries exactly the baseline from T002, nine entries and no more. This is FR-009

---

## Phase 3: User Story 2 — The version cannot disagree with the tag (P2)

**Goal**: there is no second place for the number to live, so there is nothing
to keep in step.

**Independent test**: no tracked file names the version.

- [X] T010 [US2] Confirm `uv.lock`'s own `[[package]] name = "wadler-lindig-parts"` entry has a `source` and `dependencies` and no `version` field. This is FR-005
- [X] T011 [US2] Confirm no tracked file declares the version any more: `git grep -nE '^version' -- pyproject.toml` returns nothing, and with T010 that is both declarations gone. `git grep -n '0\.2\.0' -- ':!specs'` still returns one hit, inside the new comment that explains where the version comes from; SC-003 counts declarations rather than occurrences for exactly this reason. Together with T010 this is why no check comparing a written version against the tag is added (R9, R10)
- [X] T012 [US2] Confirm the lockfile is still consistent under both flags CI uses, by running the gates in T017 — `--locked` in the floor job and `--frozen` in the others. A dynamic version that left the lockfile stale would fail there first

---

## Phase 4: User Story 3 — A build that is not a release says so (P3)

**Goal**: every build that is not a tagged release gets a version that says
so, and cannot be published.

**Independent test**: a clean commit one past a tag builds a development
version with no local segment.

- [X] T013 [US3] In the throwaway clone, at a clean commit one past the tag, run `uv build --sdist`. Pass is a name of the form `wadler_lindig_parts-0.2.1.dev1.tar.gz`: a development version ahead of the last tag, with no `+` segment. This is FR-003
- [X] T014 [P] [US3] In `.github/workflows/ci.yml`, add `fetch-depth: 0` to the `lint` job's checkout, which is the only job in the file without it. That job runs `uv sync`, which builds this package's metadata, so without the full history it emits `UserWarning: "…" is shallow and may cause errors` and derives `0.1.dev1` (measured, R8). This is FR-007
- [X] T015 [US3] Confirm, by reading `.github/workflows/cd.yml`, that both publish jobs keep their `if: startsWith(github.ref, 'refs/tags/v')` guard and that the `build` job keeps `fetch-depth: 0`. Nothing is edited here; this is the check that a hand-started run on a branch builds but does not publish

---

## Phase 4b: User Story 1, fourth scenario — a release that would publish nothing fails

**Goal**: a tagged run for a version the real index already holds stops before
anything is built.

**Independent test**: run the step with `GITHUB_REF_NAME` set to a released tag
and to an unreleased one, and read the exit codes.

**Why this phase exists at all**: an earlier draft of these artefacts asserted
that a moved tag produced a red run. It does not. `v0.2.0` was force-updated on
2026-11-06 and run `42186814040` went green on all three jobs while PyPI's
upload timestamps stayed those of the first run — a release that reported
success and published nothing (R9).

- [X] T019 [US1] Add a first step to `.github/workflows/cd.yml`'s `build` job, after the checkout and before `hynek/build-and-inspect-python-package`, named "Refuse to rebuild a version PyPI already has" and guarded by `if: startsWith(github.ref, 'refs/tags/v')`. It strips the leading `v` from `GITHUB_REF_NAME`, reads `https://pypi.org/pypi/wadler-lindig-parts/json`, and exits non-zero with a `::error::` naming the version if that version is in `releases`. `python3` and the standard library only — no new dependency, and nothing added to the package. Read PyPI and **not** TestPyPI: a run that died between the two publish jobs has already filled TestPyPI and that retry has to be let through. Write the reasoning above the step, including that a network failure there fails the release and a re-run is the fix (FR-013)
- [X] T020 [US1] Verify the step as a step, not as a snippet: parse `cd.yml`, confirm the `build` job's steps are checkout, the new step, then the build action; extract the step's `run` block from the parsed YAML and execute it under `bash` with `GITHUB_REF_NAME=v0.2.0` (expect exit 1 and the error naming `0.2.0`) and with `GITHUB_REF_NAME=v0.2.1` (expect exit 0). Check `0.1.0` too, so the result is not a special case for the latest release. This is SC-006

---

## Phase 5: Polish

- [X] T016 In `.github/workflows/cd.yml`, extend the header comment: it already explains that the filename and the two environment names are fixed by the trusted publishers registered against them, and it must now also record that the tag *is* the version, so a reader who is about to change the release path knows that renaming or re-globbing the trigger changes what gets published. Keep every existing sentence; this is an addition, not a rewrite. It must also point at the `build` job's first step rather than restate it, and it must correct the claim an earlier draft of it made, that a moved tag produces a red run (FR-011)
- [X] T017 Run every gate and keep the output for the pull request: `uv run --frozen pytest` (438 tests), `uv run --python 3.10 --no-default-groups --group tests --locked pytest`, `uv run --frozen --group docs zensical build --clean --strict`, and `uv run --frozen pre-commit run --all-files`. The last one includes `taplo-format`, which will reformat `pyproject.toml` if the new tables are laid out differently from the rest of the file — let it, and commit the result. This is SC-005
- [X] T018 Open the pull request to `main` on the `v0.2.1` milestone (GalacticDynamics/wadler-lindig-parts#25), quoting the output of T001, T007, T008, T011, T013, T017 and T020 in the body. Do not create a tag, do not publish, do not merge: the first tag on the new path is the owner's to push, and `main` requires an approving review the author cannot give

---

## Dependencies

```text
Phase 1 (T001, T002)      baseline, must be taken before T003
   └─> Phase 2 (T003 … T009)   pyproject.toml, then the lockfile, then the proofs
         └─> Phase 3 (T010 … T012)  reads the result of Phase 2
               └─> Phase 5 (T017, T018)
Phase 4 (T014) is independent of all of the above — a different file, no
dependency either way. T013 and T015 read Phase 2's result.
Phase 4b (T019, T020) and Phase 5 (T016) all touch `cd.yml`, so they run in
order: T019, then T020 to verify it, then T016 for the header comment.
```

T003, T004 and T005 all edit `pyproject.toml` and are therefore strictly
sequential despite being three separate edits. T006 must follow all three,
because `uv lock` reads the finished file.

## Parallel opportunities

- T002 alongside T001.
- T014 alongside any of Phase 2 or Phase 3: a different file, and it does not
  change what is built.
- Nothing in Phase 4b runs alongside T016: both edit `cd.yml`.

## Implementation strategy

Phase 2 alone is a complete, shippable change: after it the version comes from
the tag and a release is a tag push. Phase 3 adds no edit at all — it is the
check that the duplication is gone. Phase 4's one edit and Phase 5's comment
keep the automation and its written record honest about the new arrangement,
and neither alters a build.

Phase 4b is the one part that was not in the original plan. It was added after
the measurement in R9 contradicted what these artefacts first claimed about a
moved tag, and it is the only phase that changes what a release *does* rather
than what it is named.

## Notes

- Feature 001 recorded the static version as a deliberate deviation in three
  places: its `plan.md` Complexity Tracking, its `research.md`, and its T001.
  None of them is edited. They are the record of a decision made under a
  constraint that has since expired, and `spec.md` here is where the lifting is
  written down (FR-012).
- No task touches a setting on PyPI or TestPyPI, and no task renames the
  workflow file or either environment (FR-008).
