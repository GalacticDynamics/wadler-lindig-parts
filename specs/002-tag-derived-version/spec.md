# 002 — The version comes from the git tag

**Date**: 2026-11-06 | **Branch**: `002-tag-derived-version` | **Milestone**: `v0.2.1`

## What the release process is

A tag named `vX.Y.Z` at a commit means that the package built from that commit
is version `X.Y.Z`, and that is the version published. No tracked file states
the number. `pyproject.toml` declares the version dynamic and derives it from
`git describe --match v*`, which is the same glob `cd.yml` is triggered by, so
the set of tags that releases and the set that sets the version are one set.

A release is therefore a tag push, where it used to be two file edits, a
re-lock and a tag. The two edits were the same number written twice, in
`pyproject.toml` and again in `uv.lock`'s own entry; the second copy is gone,
and `uv.lock` records no version for this package.

Feature 001's three records of the static-version decision stand as written.
The constraint they name — the repository had no tags, and its FR-023 forbade
creating one — stopped holding when `v0.1.0` and `v0.2.0` were tagged and
published.

## What a build is named

| Build | Version |
|---|---|
| clean tree at `vX.Y.Z` | `X.Y.Z`, in both the sdist and the wheel filename |
| clean tree past a tag | a development version ahead of it, with no local segment: `0.2.1.dev1` |
| dirty tree, even at a tag | a development version, so a build never claims to be a release it is not |
| from the published sdist, with no repository history | the sdist's own version, read back from its `PKG-INFO` |
| shallow checkout with no tags | `0.1.dev1`, with a warning that the checkout is shallow |

The last row is why every job that builds or installs this package checks out
with `fetch-depth: 0`, `ci.yml`'s `lint` job included. The row above it is the
path `hynek/build-and-inspect-python-package` takes, building the sdist and
then the wheel from it, and it works because the version is written into the
sdist's metadata at build time.

`local_scheme = "no-local-version"` is what keeps the second row uploadable:
without it the same build is named `0.2.1.dev1+gc1ffc7a.d20261106`, and both
indexes reject a local segment outright. The `--match v*` in the describe
command is live rather than decorative: substituting `--match zzz*` names the
build `0.1.dev37`, counted from the root because no tag matches.

## A moved tag

Moving a tag re-runs the whole publish path and reports success while
publishing nothing. Run `42186814040`, queued when `v0.2.0` was force-updated
to correct a word in its annotated message, went green on all three jobs; the
published files' upload timestamps are `08:18:45` and `08:18:46`, from the
first run, and that run's publish step did not start until `08:20:06`. Its log
shows `skip-existing: false`, both uploads, a response from
`upload.pypi.org/legacy/` with no error anywhere in the run, and the step
finishing in 10.7s. The attestation digests it generated match the files
already served, because both runs built the same commit `2858847`, so the
rebuild was byte-identical and the index took it as a no-op.

A release that reports success and published nothing is worse than one that
fails, because only the second kind gets looked at.

What an index does with *differing* files under a version it already holds is
not established here, and the design does not rest on it. Whatever it does, a
tag moved to another commit leaves the repository saying a version is one
commit while the index serves an artefact built from another, and nothing in
the release path compares the two.

So the first step of `cd.yml`'s `build` job refuses a version PyPI already
holds, before anything is built or uploaded. It uses `python3` and the standard
library, and it reads PyPI rather than TestPyPI, because a run that died
between the two publish jobs has already filled TestPyPI and that retry has to
get through. Run as a step, with `GITHUB_REF_NAME` set three ways, `v0.2.0`
and `v0.1.0` exit 1 and `v0.2.1` exits 0. A network failure in that step fails
the release, and a re-run is the fix.

Three alternatives are not used. Leaving the behaviour alone keeps a release
path that can report success while publishing nothing. `skip-existing: true`,
which `figpress` sets, makes the no-op explicit rather than loud, and to help
at all it would have to sit on the TestPyPI step, which is the one that stops
a package that cannot be uploaded. A step comparing the tag against the built
version asserts a tautology once the version comes from the tag; `figpress`
needs that step because it keeps the number in a source file.

A ruleset forbidding update and deletion of `v*` tags would remove the cause
rather than refuse the consequence. It is a repository setting rather than a
file, so only the repository owner can apply it, and it complements the step
rather than replacing it.

## Where the mechanism comes from

`nstarman/quax@main`, the project feature 001 was modelled on and whose
workflow set this repository already has. `unxt` and `coordinax` carry the same
settings. The scheme is not taken from anywhere: `figpress` and its siblings
version by date and keep the number in a source file, and this package stays on
semantic versioning at `0.x` per the constitution.

Four differences from `quax`:

- **No `build.hooks.vcs.version-file`**, so no `_version.py` and no
  `__version__`. The constitution fixes the public surface at
  `engine.__all__` + `generic.__all__` + `examples` with no
  private-but-documented tier, and `importlib.metadata.version(...)` answers
  the question. `galax` omits the same hook for the same reason.
- **The sdist allowlist stays**, which `quax` has no equivalent of. It exists
  because of a measured 202 KB regression, and the sdist's contents are
  unchanged by this: the seven allowlisted entries plus the `.gitignore` and
  `PKG-INFO` the build backend adds itself.
- **A TestPyPI stage before PyPI**, which `quax` does not have. It predates
  this change, and it is why the refusal above reads PyPI only.
- **The `build` job refuses a version PyPI already holds**, which no project
  in the family does.

`hatch-vcs` is a build requirement rather than a dependency: it is absent from
the installed package's dependency set and invisible to the import test in
`tests/test_engine.py`, which parses the modules under `src/`. Constitution
principle I is about what the package imports at runtime.

## Boundaries

No tag is created and nothing is published by this change. The workflow
filename and the `testpypi` and `pypi` environment names do not move, and no
setting on either index is touched, because each trusted publisher is
registered against the filename plus one environment name. No name is added to
the public surface. No GitHub Release is made from a tag: neither `quax` nor
the date-versioned libraries make them, `v0.2.0` has none, and that would be
its own change.
