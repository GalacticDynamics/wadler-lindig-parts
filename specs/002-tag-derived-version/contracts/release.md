# Contract: what a tag means

Three parties read this contract, and only one of them is this repository.

- **The releaser** pushes a tag and expects a published package.
- **The two indexes** accept an upload only from a workflow they were
  configured to trust, and never accept a version twice.
- **The consumer** installs the package and asks what version they have.

## The tag is the version

A tag named `vX.Y.Z` at commit C means: the package built from C is version
`X.Y.Z`, and that is the version published.

There is no second statement of `X.Y.Z` anywhere — not in `pyproject.toml`,
not in `uv.lock`, not in a module. The derivation reads the repository's `v*`
tags, and `v*` is the same glob `cd.yml` is triggered by, so a tag that
releases and a tag that sets the version are one thing.

Three consequences follow, and they are the contract rather than an
implementation detail:

- **A clean commit that is exactly at `vX.Y.Z` builds `X.Y.Z`.** Both the
  source distribution and the wheel are named for it.
- **Any other commit builds a development version** ahead of the last tag,
  with no local segment. It is well-formed and uploadable in principle, and
  the workflow will not upload it.
- **A dirty tree builds a development version even at a tag.** The tree is
  not what the tag names, so the build does not claim to be the release.

## What is fixed from outside this repository

These are not free choices and a pull request may not change them:

| Thing | Value | Why it is fixed |
|---|---|---|
| Workflow filename | `.github/workflows/cd.yml` | Each trusted publisher is registered against the filename plus one environment name. A mismatch fails the upload with no useful error. |
| Test-index environment | `testpypi` | As above, registered on test.pypi.org. |
| Real-index environment | `pypi` | As above, registered on pypi.org. |
| Ordering | test index, then real index | `publish-pypi` needs `publish-testpypi`. A package that cannot be uploaded at all fails before it reaches the index where a version cannot be reused. |

No setting on either index's side is part of this repository, and nothing in
this feature touches one.

## What is not a release

- A tag that does not begin with `v`. It triggers nothing and sets no version.
- A run started by hand on a branch. The build job runs; both publish jobs are
  skipped by their `startsWith(github.ref, 'refs/tags/v')` guard.
- A pull request. `cd.yml` is not triggered by one at all.

## What the consumer is promised

The installed distribution's metadata carries the version, reachable as
`importlib.metadata.version("wadler-lindig-parts")`.

The package exposes no `__version__` attribute. The public surface is
`engine.__all__` plus `generic.__all__` plus `examples`, and this feature adds
nothing to it.

A consumer building a wheel from the published source distribution — with no
repository history present — gets the same version as that source
distribution, read from its own metadata.

## A version is made once

A version may be published once, and the index will not tell you when you try
again. Measured on 2026-11-06: `v0.2.0` was force-updated to fix a word in its
annotated message, the whole path ran again on the same commit, uploaded
byte-identical files, and reported success on all three jobs — while the
published files' upload timestamps stayed those of the first run. The second
attempt published nothing and said it had succeeded.

So the first step of the `build` job asks PyPI whether the version the tag
names is already published, and fails if it is. Three things follow:

- **A tag that is moved** is a second attempt at a published version, and is
  refused before anything is built. That holds whether the moved tag points at
  the same commit, where the rebuild would be identical, or at a different one,
  where the repository and the index would quietly disagree about what that
  version is.
- **A re-run of a release that already succeeded** is refused the same way.
- **A run that died between the two publish stages** is *not* refused. The
  test index already holds the version but the real one does not, and the
  refusal reads the real index only, so that retry gets through to finish the
  release.

A release is retried by tagging a new version. Not by moving a tag, and not by
re-running a run.

Preventing the tag from moving in the first place would be better than
refusing the consequence, and it is a repository setting rather than anything
in these files.
