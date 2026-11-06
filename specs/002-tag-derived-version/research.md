# Research: Tag-derived version

Every decision below was measured, not inferred. The measurements were taken
in a throwaway clone of this repository at `2858847` (`main`, carrying the
`v0.2.0` tag), with the change applied and with throwaway local tags where a
tagged state was needed. Nothing was pushed and no tag was created in the
repository itself.

## R1 — Where the mechanism comes from

**Decision**: take it from `nstarman/quax` at `main`.

**Measured**: `quax`'s `pyproject.toml` declares `dynamic = ["version"]`,
`requires = ["hatch-vcs", "hatchling"]`, `version.source = "vcs"`,
`local_scheme = "no-local-version"`, and a `describe_command` of
`["git", "describe", "--dirty", "--tags", "--long", "--match", "v*"]`. Its
`cd.yml` is the same workflow this repository already has, minus the
test-index stage. `unxt` and `coordinax` carry the same five settings.

**Rationale**: feature 001 was modelled on that project — this repository's
`cd.yml`, `ci.yml` and `build_docs.yml` are its workflow set, and `research.md`
for 001 cites it by name throughout. Taking the version mechanism from
anywhere else would leave this repository half-modelled on one project and
half on another.

**Alternatives considered**: the owner's date-versioned libraries. See R10.

## R2 — `local_scheme = "no-local-version"` is load-bearing

**Decision**: set it.

**Measured**, one commit past `v0.2.0`:

| configuration | built version |
|---|---|
| with `no-local-version` | `0.2.1.dev1` |
| without it | `0.2.1.dev1+gc1ffc7a.d20261106` |

**Rationale**: PyPI and TestPyPI both reject a version carrying a local
segment. Without this setting, every build that is not exactly at a clean tag
produces a version that cannot be uploaded at all. That is harmless for the
release path, which only ever builds at a tag — but the release workflow also
runs on `workflow_dispatch`, where the build job runs on a branch, and a build
whose artefact is structurally unuploadable is a worse diagnostic than one that
is merely refused for being a development version.

## R3 — `describe_command` with `--match v*` is honoured, and matters

**Decision**: keep the explicit `describe_command`.

**Measured**: with `--match "zzz*"` substituted for `--match "v*"`, the built
version became `0.1.dev37` — no tag matched, so the derivation fell back to a
counted distance from the root. The option therefore reaches the underlying
tool rather than being inert.

**Rationale**: `cd.yml` is triggered by `push: tags: ["v*"]`. Pinning the
derivation to the same glob makes the set of tags that releases and the set of
tags that sets the version one set, which is FR-004. The default glob is
`*[0-9]*`, which would also match a tag like `2026-audit` that releases
nothing. `galax` records the same reasoning for a sharper case: per-package
tags such as `galax-interop-astropy-v0.1.0` match the default glob and "would
otherwise become the root's version". It uses `v[0-9]*` where `quax` uses
`v*`; this repository takes `v*`, because that is the glob its `cd.yml` is
already triggered by and matching the two is the point.

## R4 — No generated version file, and no `__version__`

**Decision**: configure `version.source = "vcs"` only. Do not add
`build.hooks.vcs.version-file`.

**Measured**: `src/wadler_lindig_parts/` contains `__init__.py`, `engine.py`,
`examples.py` and `generic.py`. No module defines `__version__`, and a search
of the whole repository for that name finds nothing at all outside this
feature's own specification. `quax`, `unxt` and `coordinax` all write a
`_version.py` through that
hook; `unxt` and `coordinax` then have to exclude the generated file from
their linters' paths, and `galax` records in a comment that it has no such
hook because its namespace layout gives it nowhere to put one.

**Rationale**: the constitution fixes the public surface at
`engine.__all__` + `generic.__all__` + `examples`, and says there is no
private-but-documented tier. A generated `_version.py` exists to back a
`__version__` attribute, which would be a new public name; adding one is a
different decision from changing where the version comes from, and FR-010 puts
it out of scope. `importlib.metadata.version("wadler-lindig-parts")` already
answers the question for an installed package. Omitting the hook also keeps
`.gitignore` unchanged.

## R5 — What happens to `uv.lock`

**Decision**: re-lock and commit the result.

**Measured**: `uv lock` reported
`Updated wadler-lindig-parts v0.2.0 -> (dynamic)` and the diff was a single
deleted line — `version = "0.2.0"` from the package's own entry. `quax`'s and
`unxt`'s own entries in their lockfiles carry no version line either, which is
what a dynamic version looks like in a lockfile.

**Rationale**: this is the duplication the feature exists to remove. One line
in one file is the entire mechanical change to the lockfile; nothing about the
resolution moves.

## R6 — A wheel built from the published source distribution

**Decision**: nothing extra is needed.

**Measured**: at a clean throwaway tag `v0.9.9`, `uv build` produced
`wadler_lindig_parts-0.9.9.tar.gz` and
`wadler_lindig_parts-0.9.9-py3-none-any.whl`, reporting
`Building wheel from source distribution`. The source distribution was then
unpacked into a directory where `git rev-parse --is-inside-work-tree` fails
with `not a git repository`, its `PKG-INFO` read `Version: 0.9.9`, and
`uv build --wheel` in that directory produced
`wadler_lindig_parts-0.9.9-py3-none-any.whl`.

**Rationale**: this is the exact path the release workflow takes —
`hynek/build-and-inspect-python-package` builds the source distribution and
then the wheel from it — and it is the path a consumer takes with
`--no-binary`. The version survives because it is written into the source
distribution's metadata at build time and read back from there. This was the
one part of the mechanism that could have failed silently, which is why it was
measured rather than assumed from the sibling projects.

## R7 — The source distribution's contents do not move

**Decision**: leave `[tool.hatch.build.targets.sdist]` exactly as it is.

**Measured**, top-level entries of the built source distribution:

| | before | after |
|---|---|---|
| allowlisted | `LICENSE`, `README.md`, `conftest.py`, `docs`, `pyproject.toml`, `src`, `tests` | identical |
| added by the backend | `.gitignore`, `PKG-INFO` | identical |

**Rationale**: the allowlist comment records a 202 KB regression against a
25 KB wheel and says that anything added to the repository later is excluded by
default. This feature adds no file to the package, so the allowlist needs no
entry — and the two entries the backend adds on its own were already there
before the change, so the comparison is against a real baseline rather than
against the comment's list alone.

## R8 — Which automation jobs need the tag history

**Decision**: add `fetch-depth: 0` to `ci.yml`'s `lint` job. Every other job
already has it.

**Measured**: the `build` job in `cd.yml`, all three build jobs in
`build_docs.yml`, and `tests`, `oldest-supported` and `newest-supported` in
`ci.yml` already check out with `fetch-depth: 0`. `lint` does not. In a
`--depth 1 --no-tags` clone, `git describe` fails with
`No names found, cannot describe anything`, and the build emits
`UserWarning: "…" is shallow and may cause errors` and produces `0.1.dev1`.

**Rationale**: the `lint` job runs `uv sync`, which builds this package's
metadata, so it is a job that reads the version even though it never asserts
anything about it. The result today would be a warning and a meaningless
version rather than a failure, which is exactly the kind of thing that is
cheap to fix now and confusing to diagnose later. One line, and it makes the
file internally consistent.

## R9 — A tag that is moved after its release was published

**Decision**: change nothing. The refusal is the mechanism.

**Measured**: `v0.2.0` was force-updated once on 2026-11-06 to correct a word
in its annotated message. That queued a second `CD` run against the same tag,
which failed at the upload step because the version already exists on the
index.

**Rationale**: with the version derived from the tag, a moved tag cannot
produce a new version — it produces a second attempt at a version an index
already holds, and the index refuses to overwrite it. That refusal is the
property worth keeping, so the design's answer is to keep it and to say where
it lands: `publish-pypi` needs `publish-testpypi`, so the refusal happens at
the test index and the real index is never reached.

**Alternatives considered and rejected**:

- `skip-existing: true` on the publish steps, which the owner's `figpress`
  uses. On the test-index step it would turn the refusal into a pass and let a
  moved tag reach the real index, where the same refusal would then be the
  failure. The protection would be the same and the failure would be one job
  later, so it buys nothing and costs the early stop.
- A step that compares the tag against the version before building. With the
  version derived from the tag they agree by construction; the step would be
  asserting a tautology. This is the step `figpress` needs and this repository
  does not — see R10.
- A step that refuses to build when the version is already on the index. It
  duplicates the index's own check, needs a network call in the build job, and
  adds a way for a release to fail that has nothing to do with the release.

## R10 — Why not the date-versioned libraries' mechanism

**Decision**: take the mechanism from `quax`, not from `figpress`.

**Measured**: `figpress`, `figpress-plotly`, `figpress-apps` and `syw-site`
all declare `dynamic = ["version"]` with `[tool.hatch.version] path = …`,
which reads a literal string out of a source file. `figpress`'s `release.yml`
therefore carries a step named "The versions match the tag" running
`python3 scripts/version.py check "$GITHUB_REF_NAME"`, and publishes with
`skip-existing: true`.

**Rationale**: those projects version by date and keep the number written down,
so they need a workflow step to check the written number against the tag. That
is a mechanism for keeping two copies of a number in agreement, which is the
problem this feature removes rather than manages. The `hatch-vcs` mechanism
has one copy and no step.

**Note on scheme versus mechanism**: the date scheme is not adopted. The
constitution fixes this package at `0.x` until the type-scoped override and
markup-composer work settles, and `v0.1.0` and `v0.2.0` are already published
under semantic versioning.

## R11 — Dependency added to the build, not to the package

**Decision**: `requires = ["hatch-vcs", "hatchling"]` in `[build-system]`.

**Measured**: `hatch-vcs` 0.5.0 requires `hatchling>=1.1.0` and
`setuptools-scm>=8.2.0`; `setuptools-scm` 10.3.4 in turn requires
`vcs-versioning`, `packaging`, `setuptools`, and `tomli` and
`typing_extensions` below 3.11. None of these is a runtime dependency: they
are present only while the package is being built.

**Rationale**: constitution principle I is about what the package imports at
runtime, and `tests/test_engine.py` enforces it by parsing the modules in
`src/`. A build backend requirement is invisible to that test and to an
installed package's dependency set, so principle I is untouched. This is
stated rather than assumed, because "adding a dependency" is the one thing the
constitution says principle I cannot be amended by.
