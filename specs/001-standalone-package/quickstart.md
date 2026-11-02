# Phase 1 quickstart: how this feature is verified

Five commands. All five must pass before the pull request is opened, and the
pull request reports each one's actual output — not a claim that it passed.

## Prerequisites

- `uv` on `PATH` (measured here: 0.13.0)
- Python 3.10 available to `uv` (`uv python install 3.10` if not)
- A clean checkout of this branch

## Setup

```bash
uv sync
```

This resolves and installs the project plus the default `dev` group. It fails
before this feature lands, because there is no `pyproject.toml`.

**Expected**: resolves. If it reports `No solution found when resolving
dependencies for split (markers: python_full_version == '3.10.*')`, the docs
group is missing its `python_version >= "3.11"` marker — see R5.

## V1 — The suite, including every example

```bash
uv run pytest
```

**Expected**: all pass, zero errors. The run must include collected items from
`src/wadler_lindig_parts/*.py` (docstring examples) and from `docs/*.md`
(Markdown fences) — not only `tests/`. Confirm with:

```bash
uv run pytest --collect-only -q | tail -5
```

**Expected**: the summary counts items from all three roots. If `src/` and
`docs/` contribute nothing, `conftest.py` is not wired up and V1 passed
vacuously — which is the exact failure principle III forbids.

## V2 — The floor interpreter, with no consumer installed

```bash
uv run --python 3.10 --no-default-groups --group tests pytest
```

**Expected**: all pass. This is what turns `requires-python = ">=3.10"` into a
fact rather than a claim about syntax.

Then prove the environment really has no consumer in it:

```bash
uv run --no-default-groups --group tests python -c "import unxt"
```

**Expected**: `ModuleNotFoundError: No module named 'unxt'`. A **zero** exit
status here invalidates V1 and V2 — the suite would have been passing with a
consumer's axes already registered, which is the condition the whole extraction
was meant to escape.

## V3 — The documentation site

```bash
uv run zensical build --clean --strict
```

**Expected**: build succeeds, no warnings. `--strict` aborts on warnings;
`--clean` prevents a stale cache from hiding one.

Then verify the API page actually rendered, rather than trusting that naming a
plugin did something:

```bash
grep -c 'register_axis' site/api/index.html
```

**Expected**: a non-zero count. Zero means `mkdocstrings` is inert under
zensical — which the constitution warns is silent — and the API page must be
hand-written instead. Do not infer a plugin's effect from its presence in
`zensical.toml`.

## V4 — The lint gate

```bash
uv run pre-commit run --all-files
```

**Expected**: every hook passes. `ruff check` alone is **not** this gate — the
formatter and the other hooks catch what it does not.

The `no-commit-to-branch` hook fails by design when run outside a commit on a
non-`main` branch; CI skips it via `SKIP=no-commit-to-branch`, and so should a
local full-file run if it objects.

## V5 — What must *not* have happened

```bash
git tag --list 'v*'
```

**Expected**: empty. No release tag is created by this work.

Nothing is published to any package index. `.github/workflows/cd.yml` exists,
is gated on `refs/tags/v*`, and has never run. Configuring trusted publishing
on PyPI's side is the repository owner's separate step.

## The contracts

Each of the four contracts in
[contracts/public-surface.md](./contracts/public-surface.md) is pinned by a
test in `tests/test_engine.py`, so V1 covers them. Per constitution principle
V, each new test is **watched failing** before its behaviour is relied upon —
for C1 and C2, whose behaviour already exists, that means watched failing
against a deliberately broken copy of the function, with the failure output
recorded in the task.

Surface rule S1 is checkable directly:

```bash
uv run python -c "
import wadler_lindig_parts as p
from wadler_lindig_parts import engine, generic
want = set(engine.__all__) | set(generic.__all__)
missing = sorted(n for n in want if not hasattr(p, n))
print(len(want), 'names;', 'missing:', missing or 'none')
print('examples reachable:', hasattr(p, 'examples'))
print('__all__ matches:', set(p.__all__) == want | {'examples'})
"
```

**Expected**: `32 names; missing: none`, `examples reachable: True`,
`__all__ matches: True`.

## The one thing to watch for

This package's documentation is almost entirely examples over registered types.
A fault seen in the consumer's repository, never root-caused, makes `pparts`
return **one** fragment where three are expected — and it was seen under Sybil
while passing in a fresh interpreter.

Its signature, any one of which is the unregistered-type fallback path showing
through:

- `pparts(Term(...))` returns one fragment, not three;
- under `html`, the whole string in a single `<span>` rather than per-role
  wrappers;
- a separator the `sep` axis cannot override — `2 * 1` where `2.1` is expected,
  or the reverse.

If any appears: investigate and report what was found. Do **not** work around
it by passing literal `PPart`s, which is how it was handled in the consumer's
repository — that option is not available here, because examples over
registered types are the ones that make this package's argument. The pull
request states whether the signature appeared, either way.
