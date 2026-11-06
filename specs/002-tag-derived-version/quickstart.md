# Quickstart: proving the version comes from the tag

Every command below was run. The expected output is what it produced, quoted
rather than paraphrased. The build checks need a clean working tree, because a
dirty tree deliberately produces a development version even at a tag.

## The existing gates, unchanged

```sh
uv run --frozen pytest
uv run --python 3.10 --no-default-groups --group tests --locked pytest
uv run --frozen --group docs zensical build --clean --strict
uv run --frozen pre-commit run --all-files
```

The first collects 438 tests, the Sybil fences under `docs/` and `README.md`
among them. The second is the interpreter floor under the locked resolution,
and it is the gate that would fail if the lockfile and `pyproject.toml`
disagreed. The third is the strict documentation build. The fourth is the lint
hook set, including the formatter and `taplo`, which reformats
`pyproject.toml` if the new tables are laid out differently from the rest of
the file.

## The version is gone from the files

```sh
git grep -nE '^version' -- pyproject.toml   # no output
```

`uv.lock`'s `[[package]] name = "wadler-lindig-parts"` entry has a `source`
and `dependencies` and no `version`.

`git grep -n '0\.2\.0' -- ':!specs'` is *not* empty, and should not be: it
returns one hit, inside the comment above the new tables that names the two
tags whose existence made this change possible. The thing that falls to zero
is declarations of the version, not mentions of the number.

## Re-locking is a one-line diff

```sh
uv lock
```

Expected: `Updated wadler-lindig-parts v0.2.0 -> (dynamic)`, and
`git diff --stat uv.lock` showing one changed file, one deletion.

## A build at a tagged commit is named for the tag

Run in a throwaway clone, never in the repository, because it creates a tag:

```sh
git clone . /tmp/wlp-check && cd /tmp/wlp-check && git remote remove origin
git tag v0.9.9
uv build
```

Expected:

```text
Building source distribution...
Building wheel from source distribution...
Successfully built dist/wadler_lindig_parts-0.9.9.tar.gz
Successfully built dist/wadler_lindig_parts-0.9.9-py3-none-any.whl
```

The tag's number appears in both filenames, and `Building wheel from source
distribution` is the same path the release workflow takes.

## A build off a tag says so, with no local segment

In that same clone, one commit past the tag and clean:

```sh
uv build --sdist
```

Expected a name of the form `wadler_lindig_parts-0.2.1.dev1.tar.gz` — a
development version ahead of the last tag, and no `+` in it. A `+` segment
would make the artefact unuploadable to either index.

## A wheel builds from the source distribution with no git history

```sh
tar xzf dist/wadler_lindig_parts-0.9.9.tar.gz -C /tmp/unpack
cd /tmp/unpack/wadler_lindig_parts-0.9.9
git rev-parse --is-inside-work-tree   # fatal: not a git repository
grep -m1 '^Version:' PKG-INFO         # Version: 0.9.9
uv build --wheel
```

Expected: `Successfully built dist/wadler_lindig_parts-0.9.9-py3-none-any.whl`.
This is the one claim in the feature that could have failed silently, so it is
checked directly rather than inferred from the sibling projects.

## The source distribution still carries only what it carried before

```sh
tar tzf dist/wadler_lindig_parts-0.9.9.tar.gz \
  | sed 's|^wadler_lindig_parts-0.9.9/||' | awk -F/ '{print $1}' | sort -u
```

Expected, and identical to the same listing taken before the change:

```text
.gitignore
LICENSE
PKG-INFO
README.md
conftest.py
docs
pyproject.toml
src
tests
```

The seven allowlisted entries, plus the two the build backend adds on its own.

## The release path refuses a version PyPI already holds

The new first step of `cd.yml`'s `build` job, run exactly as a step would run
it — extracted from the parsed workflow rather than retyped — with
`GITHUB_REF_NAME` set both ways:

```sh
GITHUB_REF_NAME=v0.2.0 bash step.sh    # exit 1
GITHUB_REF_NAME=v0.2.1 bash step.sh    # exit 0
```

Expected:

```text
::error::0.2.0 is already on PyPI. The tag is the version, so this run would
republish a released version instead of making a new one. If the tag was
moved, move it back; to release again, tag a new version.
exit=1

0.2.1 is not on PyPI yet
exit=0
```

`0.1.0` also exits 1, so the check is reading the index rather than special-
casing the latest release. The step reads PyPI only, never TestPyPI: a run that
died between the two publish stages has already filled TestPyPI and has to be
allowed through.
