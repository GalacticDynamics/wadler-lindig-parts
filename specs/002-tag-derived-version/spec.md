# Feature Specification: Tag-derived version

**Feature Branch**: `002-tag-derived-version`

**Created**: 2026-11-06

**Status**: Draft

**Input**: User description: "Derive the package version from the git tag instead of a static string in pyproject.toml, so that pushing a v* tag is the whole release action."

## Context

Feature 001 chose a static `version` in `pyproject.toml` and wrote down why:
`plan.md` recorded the deviation as "Static `version = "0.1.0"` rather than
`hatch-vcs` — there are no tags, and the request forbids creating one", and
`research.md` repeated it. FR-023 of that feature required a release path that
existed but was never exercised.

Both halves of that reason have expired. `v0.1.0` was tagged and published on
2026-11-03, `v0.2.0` was tagged and published on 2026-11-06, and PyPI serves
both. This feature lifts a decision whose reason is gone. It is not a claim
that the earlier decision was wrong: with no tags in the repository there was
nothing for a tag-derived version to read, and the model project's mechanism
could not have worked.

What is left behind is the duplication the static version creates. The number
appears in `pyproject.toml` and again in `uv.lock`'s own
`wadler-lindig-parts` entry, so a release is three steps — edit the version,
re-lock, tag — and the first two can be done wrongly or forgotten. Release
0.2.0 was prepared that way by hand.

## User Scenarios & Testing *(mandatory)*

The "users" here are two parties:

- **The releaser** — whoever cuts a release. Today that is the repository
  owner, who is also the only person who can merge to `main` and push a tag.
- **The consumer** — a library author or a reader who installs the package and
  wants to know which version they have.

### User Story 1 - A release is a tag push and nothing else (Priority: P1)

The releaser decides the next release is 0.2.1. They push the tag `v0.2.1` at
the commit they want released. No file in the repository names that number
before, during or after. The automation builds the package, which reports its
version as `0.2.1`, publishes it to the test index and then to the real one,
and the releaser's whole contribution was the tag.

**Why this priority**: This is the feature. Everything else below is a
consequence of it or a boundary around it.

**Independent Test**: At a commit that carries a `v*` tag and a clean working
tree, build the package and read the version out of the two artefact
filenames. It must equal the tag with the leading `v` removed.

**Acceptance Scenarios**:

1. **Given** a clean checkout whose `HEAD` carries the tag `vX.Y.Z`,
   **When** the package is built, **Then** both the source distribution and
   the wheel are named for version `X.Y.Z`.
2. **Given** that same checkout, **When** the repository is searched for the
   string `X.Y.Z`, **Then** no tracked file contains it as a declared version.
3. **Given** a `v*` tag pushed to the remote, **When** the release automation
   runs, **Then** it publishes to the test index first and to the real index
   only after that succeeds, exactly as it does today.
4. **Given** a `v*` tag naming a version the real index already holds,
   **When** the release automation runs, **Then** it stops in the first step
   of the build job, naming the version, and nothing is built or uploaded.

---

### User Story 2 - The version cannot disagree with the tag (Priority: P2)

The releaser can no longer tag `v0.3.0` and publish a package that calls
itself something else, because there is no second place for the number to
live. The mismatch is not caught by a check; it has no way to occur.

**Why this priority**: It is the reason to prefer this over keeping the static
version and adding a check that the two agree. A check can be skipped,
mis-scoped, or made to pass by editing the wrong file. Removing the second
copy of the number removes the class of error.

**Independent Test**: Confirm that `uv lock` no longer records a version for
this package's own entry, and that `pyproject.toml` declares the version as
dynamic rather than literal. The two files that had to be edited in step with
each other now have nothing to keep in step.

**Acceptance Scenarios**:

1. **Given** the change is in place, **When** `uv lock` runs, **Then** the
   `wadler-lindig-parts` entry in `uv.lock` carries no version field.
2. **Given** the change is in place, **When** a release is prepared,
   **Then** no commit is needed between the last substantive change and the
   tag.

---

### User Story 3 - A build that is not a release says so (Priority: P3)

Somebody builds the package from a commit that is not tagged — on a pull
request, from a maintenance branch, or on their own machine. The version they
get identifies that state rather than impersonating a release, and the
automation will not publish it.

**Why this priority**: The version is now read from the repository's history
rather than written down, so every build gets a version, including builds
nobody meant as a release. The boundary has to be explicit.

**Independent Test**: Build at a clean commit one commit past a tag and read
the version. It must be recognisably a development version, and it must carry
no local version segment, because an index refuses those outright.

**Acceptance Scenarios**:

1. **Given** a clean checkout one commit past `vX.Y.Z`, **When** the package
   is built, **Then** the version is a development version ahead of `X.Y.Z`
   and contains no `+` segment.
2. **Given** the release automation triggered by hand on a branch rather than
   by a tag, **When** it runs, **Then** the build job runs and both publish
   jobs are skipped.

### Edge Cases

- **A tag is moved after its release was published.** The version is the tag,
  so a moved tag does not become a new version: it becomes a second attempt at
  a version the index already holds. Measured on 2026-11-06, nothing objects
  to that. `v0.2.0` was force-updated to correct a word in its annotated
  message; the release automation ran again on the same commit, rebuilt
  byte-identical files, uploaded them, and reported success on all three jobs,
  while the published files' upload timestamps stayed those of the first run.
  The second attempt published nothing and said it had succeeded.
  - The case that run did not reach is the one that matters: a tag moved to a
    *different* commit builds different files under a version the index
    already holds. Whatever the upload then does, the repository says that
    version is one commit while the index serves an artefact built from
    another, and nothing in the release path would notice.
  - So this feature refuses both, before anything is built: FR-013. A release
    that would publish nothing now fails instead of reporting success.
- **A re-run of a release that already succeeded** is the same case and is
  refused the same way. Re-running is not how a release is retried; a new tag
  is.
- **A run that died between the two publish stages.** The test index already
  holds the version and the real one does not, and that retry has to be let
  through so it can reach the real index. The refusal in FR-013 therefore
  reads the real index only.
- **A tag that does not begin with `v`** is neither a release nor a version:
  the automation is not triggered by it, and the version derivation does not
  consider it.
- **A shallow checkout with no tags** still produces a buildable package, with
  a development version far from any real one, and a warning that the checkout
  is shallow. No publish is possible from it. Every job that builds the
  package fetches the full history so this does not arise in automation.
- **A consumer builds a wheel from the published source distribution**, where
  there is no repository history to read. The version is recorded in the
  source distribution's own metadata when it is built, and the wheel build
  reads it from there.
- **The working tree is dirty.** The build reports a development version
  rather than the tag, even at a tagged commit. This is correct — the tree is
  not what the tag names — and it is why the verification in this feature is
  run against a clean tree.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The package version MUST be derived from the repository's `v*`
  tags. No tracked file may declare it.
- **FR-002**: At a clean commit carrying `vX.Y.Z`, the built version MUST be
  exactly `X.Y.Z`.
- **FR-003**: At any other commit, the built version MUST NOT contain a local
  version segment, because the indexes this package publishes to reject them.
- **FR-004**: The set of tags that derive the version MUST be the same set
  that triggers the release automation, so that a tag which releases and a tag
  which sets the version are never different things.
- **FR-005**: `uv.lock` MUST stop recording a version for this package's own
  entry, and the lockfile MUST remain valid under `--locked` and `--frozen`.
- **FR-006**: A wheel MUST be buildable from the published source
  distribution, with no repository history present, and MUST report the same
  version as that source distribution.
- **FR-007**: Every automation job that builds or installs this package MUST
  have the tag history available to it.
- **FR-008**: The release automation's workflow filename and its two
  environment names MUST NOT change. Each trusted publisher is registered
  against `.github/workflows/cd.yml` plus one environment name, and a mismatch
  fails the upload with no useful error. No setting on either index's side is
  touched by this feature.
- **FR-009**: The source distribution MUST keep carrying exactly what it
  carries today — `LICENSE`, `README.md`, `conftest.py`, `docs`,
  `pyproject.toml`, `src`, `tests` — and the allowlist that makes that true
  MUST stay an allowlist.
- **FR-010**: The package's public surface MUST NOT change. No `__version__`
  attribute is added, because the constitution's public surface is
  `engine.__all__` plus `generic.__all__` plus `examples`, and adding a name
  to it is a different decision from changing where the version comes from.
- **FR-011**: The comment in the release automation that explains why the
  filename and environments are fixed MUST be updated to also record that the
  tag is now the version, since that comment is what a future reader consults
  before changing the release path.
- **FR-013**: Before anything is built, a tagged run MUST refuse to continue
  when the version the tag names is already published on the real index. The
  refusal MUST come before the build and before either upload, and MUST name
  the version and say what to do instead. It MUST read the real index only, so
  that a run which died between the two publish stages can still be retried.
- **FR-012**: The three places in feature 001's artefacts that record the
  static version as a deliberate deviation — its plan's Complexity Tracking,
  its research notes, and the task that created `pyproject.toml` — MUST be
  left as they are. They are the record of a decision made under a constraint
  that has since expired, and this specification is where the lifting is
  written down.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The number of files a releaser edits to cut a release falls
  from two to zero.
- **SC-002**: The number of steps in a release falls from three — edit,
  re-lock, tag — to one.
- **SC-003**: The number of tracked files that *declare* the version falls
  from two to zero: no `version` key under `[project]`, and no `version` field
  on the package's own lockfile entry. The number may still be mentioned in
  prose — the comment explaining where the version now comes from names the
  two tags that made the change possible — so the measurement is of
  declarations, not of occurrences.
- **SC-004**: For a tagged commit, the built version equals the tag with its
  leading `v` removed, in both artefact filenames.
- **SC-006**: A release that would publish nothing fails instead of reporting
  success. Measured against the one case in the record — a run for a version
  the real index already holds stops at the first step of the build job, where
  today it runs all three jobs green and uploads nothing.
- **SC-005**: Every existing gate passes unchanged: the full suite, the suite
  on the interpreter floor under the locked resolution, the strict
  documentation build, and the lint hook set.

## Assumptions

- **The mechanism is taken from `nstarman/quax` at `main`.** That is the
  project feature 001 was modelled on — this repository's `cd.yml`, `ci.yml`
  and `build_docs.yml` are its workflow set — and it derives its version from
  git tags with `hatch-vcs`. The two sibling packages in the same
  organisation, `unxt` and `coordinax`, use the same configuration.
- **The version scheme is not taken from anywhere.** Several of the owner's
  other libraries version by date (`vYYYY.MM.DD`) and reach it a different
  way: `figpress` and its siblings keep the number in a source file and add a
  workflow step that checks it against the tag. This package stays on semantic
  versioning per the constitution, and takes the mechanism rather than the
  scheme. The check-the-number-against-the-tag step has no analogue here,
  because with the version derived from the tag there is no second number to
  check.
- **Four deliberate differences from `quax` are recorded in the plan**, not
  left for a reviewer to notice: this package writes no generated version file
  and exposes no `__version__`; it keeps its source-distribution allowlist,
  which `quax` does not have; its release path has a test-index stage before
  the real one, which `quax` does not; and it refuses to rebuild a version the
  index already holds, which no project in the family does.
- **No GitHub Release is created.** Neither the model project nor the owner's
  date-versioned libraries create one from a tag, and `v0.2.0` has none. A
  release here means a tag and the two index uploads. Creating GitHub Releases
  would be a separate change.
- **Nothing is tagged, published or merged by this feature.** The work ends as
  a pull request. The repository owner pushes the first tag that exercises
  the new path, and the next release is the first real evidence that it works
  end to end; everything before that is evidence from local builds and from
  the model project.
- **The milestone is `v0.2.1`.** This change alters no behaviour a consumer
  can observe, so by the constitution's versioning rule the next release is a
  patch. The version-derivation tool's own guess for the commit after `v0.2.0`
  is `0.2.1`, which is where the name comes from. If the next release is
  meant to be a minor, the milestone moves and nothing else does.
