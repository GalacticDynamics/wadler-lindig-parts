# 002 — The version comes from the git tag

**Date**: 2026-11-06 | **Branch**: `002-tag-derived-version` | **Milestone**: `v0.2.1`

A record, not a Spec Kit feature. The change is nine lines of configuration,
and this file is the part of it worth keeping: what was lifted, what was
measured, and the one thing the measurements contradicted.

## What changed, and why it could not have been done before

`pyproject.toml` declares `dynamic = ["version"]` and derives the version from
the repository's `v*` tags; `uv.lock` loses the line that repeated the number;
`ci.yml`'s `lint` job gets the full history every other job already fetched;
and `cd.yml` gains one step, below.

Feature 001 chose a static version and recorded why in three places — there
were no tags, and its FR-023 forbade creating one. Both halves expired when
`v0.1.0` and `v0.2.0` were tagged and published. This lifts a decision whose
reason is gone; it does not claim the decision was wrong. None of 001's three
records is edited.

What the static version left behind was the number written twice, here and in
`uv.lock`, so preparing 0.2.0 meant two edits, a re-lock and a tag. It now
means a tag.

## Mechanism, and where it came from

`nstarman/quax@main` — the project 001 was modelled on, and whose workflow set
this repository already has. `unxt` and `coordinax` carry the same settings.
The mechanism, not the scheme: `figpress` and its siblings version by date,
keep the number in a source file, and need a workflow step to check it against
the tag — a mechanism for keeping two copies of a number in agreement, which
is the problem this removes rather than manages.

Four deliberate differences from `quax`:

- **No `build.hooks.vcs.version-file`**, so no `_version.py` and no
  `__version__`. The constitution fixes the public surface at
  `engine.__all__` + `generic.__all__` + `examples`, with no
  private-but-documented tier, and `importlib.metadata.version(...)` already
  answers the question. `galax` omits the same hook for the same reason.
- **The sdist allowlist stays**, which `quax` has no equivalent of. It exists
  because of a measured 202 KB regression.
- **A TestPyPI stage before PyPI**, which `quax` does not have. It predates
  this change, and it is why the new refusal reads PyPI only.
- **The `build` job refuses a version PyPI already holds.** See below.


## Measured

| Claim | Result |
|---|---|
| Clean tree at a tag | `v0.9.9` → `wadler_lindig_parts-0.9.9.tar.gz` and `-0.9.9-py3-none-any.whl` |
| Clean tree one commit past a tag | `0.2.1.dev1`, no local segment |
| Without `local_scheme = "no-local-version"` | `0.2.1.dev1+gc1ffc7a.d20261106`, which neither index accepts |
| `--match zzz*` instead of `v*` | `0.1.dev37`, so the glob is honoured rather than decorative |
| Wheel from the unpacked sdist, no `.git` | `0.9.9`, read from the sdist's own `PKG-INFO` |
| sdist top-level entries, before and after | identical: the seven allowlisted ones plus `.gitignore` and `PKG-INFO` |
| `uv lock` | `Updated wadler-lindig-parts v0.2.0 -> (dynamic)`, one deleted line |
| Shallow checkout, no tags | warns it is shallow, derives `0.1.dev1` — hence `fetch-depth: 0` on `lint` |
| A dirty tree at a tag | a development version, so the build never claims to be the release |

The sdist-to-wheel row is the one that could have failed silently: it is the
path `hynek/build-and-inspect-python-package` takes, and the version survives
only because it is written into the sdist's metadata and read back from there.

## A moved tag, and the claim this document first got wrong

The first draft of this record said a moved tag produces a failed release run,
because the index refuses a version it already holds, and that keeping that
refusal was the whole design. Then run `42186814040` was read — the one queued
when `v0.2.0` was force-updated to correct a word in its annotated message.
It went green on all three jobs.

The uploads, though, belong to the first run: PyPI reports `08:18:45` and
`08:18:46`, and the second run's publish step did not start until `08:20:06`.
Its log shows `skip-existing: false`, the two uploads, a response from
`upload.pypi.org/legacy/` with no error anywhere in the run, and the step
finishing in 10.7s. The attestation digests it generated are exactly those of
the files already served, because both runs built the same commit `2858847` —
so the rebuild was byte-identical and the index took it as a no-op.

A release that reports success and published nothing is worse than one that
fails, because only the second kind gets looked at.

That evidence does not cover the case that matters: a tag moved to a
*different* commit builds different files under a version the index already
holds. This document does not guess what the upload would do with that,
because the refusal does not depend on the answer — whatever it does, the
repository would say a version is one commit while the index serves an
artefact built from another, and nothing in the release path compares the two.

So `cd.yml`'s `build` job now refuses, before anything is built, a version
PyPI already holds. Standard library only. It reads PyPI and not TestPyPI
deliberately: a run that died between the two publish jobs has already filled
TestPyPI, and that retry has to get through. Verified by extracting the step
from the parsed workflow and running it under `bash` — `v0.2.0` and `v0.1.0`
exit 1, `v0.2.1` exits 0. A network failure there fails a release; a re-run is
the fix.

Rejected: doing nothing, which was the first draft's answer and rested on the
mistake above; `skip-existing: true`, which makes the no-op explicit rather
than loud and would have to sit on the TestPyPI step to help at all; and a
step comparing the tag against the built version, which is a tautology once
the version comes from the tag.

Better than all of these, and not a file: a ruleset forbidding update and
deletion of `v*` tags removes the cause. Only the repository owner can set it.

## Out of scope

No tag is created and nothing is published. The workflow filename and the two
environment names do not move, and no setting on either index is touched —
`cd.yml`'s header says why. No name is added to the public surface. No GitHub
Release is created from a tag: neither `quax` nor the date-versioned libraries
do, and `v0.2.0` has none, so that would be its own change.
