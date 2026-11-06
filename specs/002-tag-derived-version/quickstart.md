# Quickstart: proving the version comes from the tag

Every command below was run. The build checks need a clean working tree,
because a dirty tree deliberately produces a development version even at a
tag, and they create a tag, so they run in a throwaway clone and never in the
repository.

## The existing gates, unchanged

```sh
uv run --frozen pytest                                                  # 438 passed
uv run --python 3.10 --no-default-groups --group tests --locked pytest   # 438 passed
uv run --frozen --group docs zensical build --clean --strict            # No issues found
uv run --frozen pre-commit run --all-files                              # all nine hooks pass
```

The second is the interpreter floor under the locked resolution, and it is the
gate that would fail if the lockfile and `pyproject.toml` disagreed. The fourth
includes `taplo`, which reformats `pyproject.toml` if the new tables are laid
out differently from the rest of the file.

## The version is gone from the files

```sh
git grep -nE '^version' -- pyproject.toml   # no output
```

`uv.lock`'s `[[package]] name = "wadler-lindig-parts"` entry has a `source` and
`dependencies` and no `version`.

`git grep -n '0\.2\.0' -- ':!specs'` is *not* empty, and should not be: it
returns one hit, inside the comment above the new tables that names the two
tags whose existence made this change possible. What falls to zero is
declarations of the version, not mentions of the number.

## Re-locking is a one-line diff

```sh
uv lock   # Updated wadler-lindig-parts v0.2.0 -> (dynamic)
```

`git diff --stat uv.lock` shows one file, one deletion.

## A build at a tagged commit is named for the tag

```sh
git clone . /tmp/wlp-check && cd /tmp/wlp-check && git remote remove origin
git tag v0.9.9
uv build
```

Expected `wadler_lindig_parts-0.9.9.tar.gz` and
`wadler_lindig_parts-0.9.9-py3-none-any.whl`, with `Building wheel from source
distribution` in the output — the same path
`hynek/build-and-inspect-python-package` takes.

## A build off a tag says so, with no local segment

In that clone, one commit past the tag and clean:

```sh
uv build --sdist   # wadler_lindig_parts-0.2.1.dev1.tar.gz
```

A development version ahead of the last tag, and no `+` in it. A local segment
would make the artefact unuploadable to either index.

## A wheel builds from the source distribution with no git history

```sh
tar xzf dist/wadler_lindig_parts-0.9.9.tar.gz -C /tmp/unpack
cd /tmp/unpack/wadler_lindig_parts-0.9.9
git rev-parse --is-inside-work-tree   # fatal: not a git repository
grep -m1 '^Version:' PKG-INFO         # Version: 0.9.9
uv build --wheel                      # wadler_lindig_parts-0.9.9-py3-none-any.whl
```

This is the one claim in the feature that could have failed silently, so it is
checked directly rather than inferred from the sibling projects.

## The source distribution still carries only what it carried before

```sh
tar tzf dist/wadler_lindig_parts-0.9.9.tar.gz \
  | sed 's|^wadler_lindig_parts-0.9.9/||' | awk -F/ '{print $1}' | sort -u
```

Expected, and identical to the same listing taken before the change: the seven
allowlisted entries — `LICENSE`, `README.md`, `conftest.py`, `docs`,
`pyproject.toml`, `src`, `tests` — plus `.gitignore` and `PKG-INFO`, which the
build backend adds on its own.

## The release path refuses a version PyPI already holds

The `build` job's first step, run as a step would run it — extracted from the
parsed workflow rather than retyped:

```sh
GITHUB_REF_NAME=v0.2.0 bash step.sh   # exit 1, ::error::0.2.0 is on PyPI already
GITHUB_REF_NAME=v0.1.0 bash step.sh   # exit 1, so it reads the index rather than
                                      # special-casing the latest release
GITHUB_REF_NAME=v0.2.1 bash step.sh   # exit 0
```

It reads PyPI only, never TestPyPI: a run that died between the two publish
stages has already filled TestPyPI and has to be allowed through.
