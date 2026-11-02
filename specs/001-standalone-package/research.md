# Phase 0 research: standalone package

Every finding below was measured in this session. Where the feature request or
the constitution states a figure, the measurement is given beside it and the
measurement wins.

## R1 — The public surface is 32 names, not 29

**Decision**: the top-level `__init__.py` re-exports the union of
`engine.__all__` (28 names) and `generic.__all__` (4 names), plus the
`examples` submodule. 32 names and one submodule.

**Measured**:

```text
engine  28  ALIASES AXES Axis MARKUPS PGroup PPart REQUIRED_MARKUP_KEYS
            ReprMixin Spec bad_spec FLAT doc_part doc_to_str inert_axes
            markup_table math_doc parse_spec parts_to_doc parts_to_markup
            pparts pparts_to_pdoc pspec register_alias register_axis render
            unregister_alias unregister_axis unwrap_math
generic  4  SHORT_ARRAYS pvalue register_markup unregister_markup
```

**Rationale**: the requirement is "the union of the two `__all__` tuples"
(constitution, Additional Constraints). The count is a consequence of that, not
an independent constraint, so it follows the code. The request's figure of 29
is three short; nothing in the code suggests which three were meant to be
excluded, and excluding any would be a change to a module's `__all__` rather
than to the re-export.

**Alternative rejected**: trimming the surface to 29 names. There is no
candidate set — and `SHORT_ARRAYS` and `FLAT`, the two that read least like
API, are both already referenced from the engine's own docstrings.

## R2 — Three tests need attention, not two

**Decision**: adjust two and delete one.

**Measured**, by reading `tests/test_engine.py` against this repository's tree:

| Test | Line | State here |
|---|---|---|
| `test_the_engine_alone_registers_six_axes_and_no_aliases` | 312 | Works, but by copying `engine.py`/`generic.py`/`examples.py` into a temp package and importing them in a subprocess. That existed to escape `unxt.__init__`'s eager axis registration. No consumer here, so the subprocess is pure cost. |
| `test_the_package_side_exposes_no_privates_across_the_seam` | 353 | **Raises on collection.** It reads `engine.__file__`'s sibling `axes.py`. That file belongs to `unxt`'s layer and does not exist in this repository. |
| `test_this_suite_reaches_only_for_the_package_side` | 774 | Passes vacuously. It scans this file for `unxt` imports; there are none and cannot be any. |

**Rationale and disposition**:

- **312** → assert against the live registry. Same three assertions (6 axes, 0
  aliases, 3 markups), no subprocess, no `tmp_path`.
- **353** → delete. The property it guarded — that `unxt`'s layer reaches the
  engine through public names only — is now on the far side of a distribution
  boundary and is unobservable from this repository. Leaving it as a test that
  reads some other file would be a test that passes by doing nothing, which
  principle V exists to prevent. The pull request says it was deleted and why.
- **774** → replace with its inverse: parse every module under
  `src/wadler_lindig_parts/` and assert each import resolves to the standard
  library, `wadler_lindig`, `plum`, or a sibling module. That is the test
  principle I actually claims exists ("parses every module in
  `src/wadler_lindig_parts/` and fails on any import outside the allowed set"),
  and it fails on a *new* dependency rather than on a *named* one.

**Note on the existing 384-line test**: `test_the_package_side_imports_only_the_allowed_set`
(line ~384, using `_import_offenders`) already does something close to the
inverted check for *relative* imports. The new test must cover absolute imports
too; the plan keeps them as one test rather than two overlapping ones.

## R3 — The keyword-collision contract is parse-time, and the constitution is wrong about it

**Decision**: pin the measured behaviour. `register_axis` stays permissive; the
collision is refused when a spec uses the bare word.

**Measured**, `src/wadler_lindig_parts/engine.py`:

- `register_axis` (line 668) checks: duplicate *axis name*, a second claim on
  *free text*, and a keyword colliding with an *alias*. It does **not** check a
  keyword claimed by another axis. Line 697 is
  `_KEYWORDS.setdefault(word, []).append(axis.name)` — a list, deliberately.
- `_KEYWORDS` is `dict[str, list[str]]` (line 638).
- Resolution (line ~835) raises on a multi-claimant word:
  `ambiguous keyword 'x'; claimed by 'a', 'b'. Write it as one of: a=x, b=x`.
- The qualified form `axis=word` is resolved earlier in the same function,
  before the claimant list is consulted, so both axes stay reachable.
- No test anywhere in `tests/` matches `ambiguous`.

**Constitution principle IV says**: "The first registration of a word wins"
(false — neither wins; the bare word becomes unusable and both qualified forms
work) and "`register_axis` enforces the first two" (false — resolution does).
Its third bullet, "`axis=word` always resolves explicitly, so two libraries
wanting one word is an inconvenience rather than a defeat", is true and is the
reason the other two must give way.

**Rationale**: the third bullet is the substantive design commitment. The
explanation page being converted for this package's docs spends a section
arguing for it. Refusing the second registration would make it unreachable.

**Alternatives rejected**:

- *Raise at registration.* Matches the request's wording literally, but the
  losing axis is then never registered, so `axis=word` cannot resolve it and a
  shared word becomes a defeat. Contradicts principle IV's own third bullet.
- *Opt-in sharing flag.* Buys loudness back at the price of new public API for
  a collision that has not occurred.

**Consequences for this feature**: a new test pinning both halves (bare word
raises naming both; each qualified form resolves); an amendment to principle IV
stating where the refusal lands; and a correction to the how-to page's sentence
"Registration raises on any collision rather than overwriting" — which remains
true of a duplicate axis *name*, alias or markup name, so the corrected
sentence distinguishes those from a keyword claimed twice.

Chosen by the repository owner, 2026-11-02.

## R4 — The markup-row refusal already exists and is already correct; only the test is missing

**Decision**: add the missing test. No code change.

**Measured**, `src/wadler_lindig_parts/generic.py`:

- `_check_markup_row` (line 106) opens with
  `if missing := [k for k in REQUIRED_MARKUP_KEYS if k not in row]` and raises
  `markup row is missing required keys [...]`.
- `register_markup` (line 129) calls `_check_markup_row(row)` as its **first**
  statement, before the duplicate-name and keyword-clash checks and before any
  registry is touched — so a refused row leaves no partial entry.
- `test_register_markup_rejects_a_malformed_template` parametrises six bad
  rows. Every one supplies all four keys and corrupts a *value*. None omits a
  key. The missing-key branch is unexercised.

**Rationale**: principle V wants the claim pinned, and the claim is true. The
test asserts the error names the missing key and that no registry holds a
partial entry — the second half is what makes the "at registration, not at
render" part of the claim meaningful.

## R5 — The whole docs group is Python >=3.11, and unmarked it breaks `uv lock`

**Decision**: carry every docs-group entry behind a
`python_version >= "3.11"` marker, and give `zensical` a lower bound.

**Corrected during implementation.** This finding originally named only
`mkdocstrings[python]==1.0.8` as the 3.11-only entry, because the first probe
asked `uv pip compile` whether each *unpinned* spec resolved on 3.10 and
`zensical` answered yes. It answered yes by silently resolving to a years-old
zensical, not because the current one supports 3.10. Pinning
`zensical>=0.0.74` is what surfaced it:

```text
error: No solution found when resolving dependencies for split
       (markers: python_full_version < '3.11')
  cause: Because the requested Python version (>=3.10) does not satisfy
         Python>=3.11 and zensical==0.0.74 depends on Python>=3.11, we can
         conclude that zensical==0.0.74 cannot be used.
```

So an unpinned dependency in a group whose floor exceeds the project's hides
the conflict rather than reporting it, and the group looks installable on the
floor interpreter while being nothing of the kind. The lower bound is
load-bearing, not hygiene.

**Measured**: `uv lock` with `requires-python = ">=3.10"` and an unmarked
`mkdocstrings[python]==1.0.8` in a dependency group:

```text
error: No solution found when resolving dependencies for split
       (markers: python_full_version == '3.10.*')
  cause: Because the requested Python version (>=3.10) does not satisfy
         Python>=3.11 and probe:docs depends on mkdocstrings[python]==1.0.8,
         we can conclude that probe:docs's requirements are unsatisfiable.
```

With the marker: `Resolved 30 packages`. Per-dependency floors measured
against 3.10:

| Dependency | 3.10? |
|---|---|
| `wadler-lindig>=0.1.8` | yes |
| `plum-dispatch>=2.7.0` | yes |
| `sybil` | yes |
| `pytest` | yes |
| `pre-commit` | yes |
| `pymdown-extensions==12.3` | yes, but marked anyway — the group is 3.11+ as a whole |
| `mkdocstrings[python]==1.0.8` | **no — needs >=3.11** |
| `zensical>=0.0.74` | **no — needs >=3.11** (unpinned, it hid this) |

**Rationale**: `uv lock` resolves across the whole `requires-python` range, not
just the active interpreter, so an unmarked group entry with a higher floor is
a hard lock failure — the lockfile the CI jobs depend on could not be produced
at all. The marker forks the resolution and the 3.10 split simply omits the
entry. This does not weaken anything: the documentation build job runs on the
newest interpreter, as the sibling project's does.

**Alternatives rejected**:

- *Raise this package's floor to 3.11.* Contradicts the constitution's explicit
  "Python `>=3.10`. … a general-purpose renderer should not inherit a
  consumer's floor", and the floor is a runtime property that a docs-only tool
  has no business setting.
- *Pin an older mkdocstrings that supports 3.10.* Diverges from the sibling
  project's verified-working version for no gain.

## R6 — `zensical build --strict` exists

**Decision**: the documentation gate is `uv run zensical build --strict`.

**Measured**: `zensical build --help` reports
`-s, --strict  Enable strict mode - abort the build on warnings.`

**Note**: the sibling project's own docs workflow uses `--clean`, not
`--strict`. This package is deliberately stricter. The automation runs
`--clean --strict` so the strictness is not satisfied by a stale cache.

## R7 — The sibling project's merged state, read from its default branch

**Decision**: model `pyproject.toml`, `.pre-commit-config.yaml`, the workflows,
`zensical.toml` and `conftest.py` on `nstarman/quax@main`.

**Measured**: the local checkout at `/Users/nmrs/local/quax` is on branch
`jaxtyping-to-bearshape-migration`, three commits of which predate the zensical
migration. It still contains `mkdocs.yml`, `hippogriffe==0.2.2`,
`mkdocstrings[python]==1.0.4` and `pymdown-extensions==11.0.1`, and has no
`zensical.toml` and no `conftest.py`. Everything cited here was fetched from
the default branch instead:

| | local branch | `main` |
|---|---|---|
| `mkdocs.yml` | present | **deleted** |
| `zensical.toml` | absent | **present** |
| `conftest.py` | absent | **present**, `sybil.parsers.markdown` |
| `hippogriffe` | `==0.2.2` | **removed** |
| `mkdocstrings[python]` | `==1.0.4` | `==1.0.8` |
| `pymdown-extensions` | `==11.0.1` | `==12.3` |
| `lint` group | `mypy`, `prek`, `ruff` | **`prek`, `ruff`** — mypy dropped |
| type checking | `[tool.mypy]` | pre-commit `pyright` hook |

The request's description of the merged state is confirmed in every particular.

**Carried over**: `hippogriffe` is omitted because zensical silently ignored
it. `nbconvert` is omitted because this package has no notebooks, and with it
the workflows' notebook-conversion step. The version is static `0.1.0` rather
than derived from git tags (`hatch-vcs`), because there are no tags and the
request forbids creating one.

## R8 — Sybil wiring: plain Markdown, not MyST

**Decision**: one `Sybil` for `*.md` with
`sybil.parsers.markdown.PythonCodeBlockParser`, one for `*.py` with the
doctest parser, summed and installed as `pytest_collect_file`.

**Measured**: `unxt`'s `conftest.py` imports `from sybil.parsers import myst`
and builds `myst.CodeBlockParser`, `myst.DocTestDirectiveParser`,
`myst.PythonCodeBlockParser`, `myst.SkipParser` — because its pages use
```` ```{code-block} python ```` directives. The sibling project's `conftest.py`
imports `from sybil.parsers.markdown import PythonCodeBlockParser, SkipParser`
— plain fences. This package's pages will carry plain fences (R9), so the
markdown parsers are correct and the MyST ones would match nothing.

**Note**: `unxt`'s conftest also carries a `PlainDocTestParser` shim for `>>>`
prompts in Python docstrings. This package's module docstrings use exactly that
form, so the `*.py` Sybil needs a doctest parser, not only a code-block parser.
`sybil.parsers.markdown` has no docstring equivalent; `sybil.parsers.doctest`
or `sybil.parsers.rest.DocTestParser` covers it. The plan verifies which by
collecting and counting, not by assuming.

## R9 — The two converted guides: measured conversion volume, and a rewrite on top

**Decision**: convert mechanically, then re-ground the arguments on
`examples.Term` / `Version` / `Point`.

**Measured** against `GalacticDynamics/unxt@main`:

| Source | Lines | `{doc}` lines | `code-block` directives |
|---|---|---|---|
| `docs/explanation/why-formatting-is-one-engine.md` | 89 | 1 | 3 |
| `docs/how-to/make-a-type-formattable.md` | 135 | 5 | 5 |
| **total** | 224 | **6** | **8** |

Matches the request's 6 and 8 exactly.

**The rewrite is the larger half.** Both pages argue through quantities and
unit systems, which this package does not have:

- *why-formatting-is-one-engine* — its "Why the constructor form is not built
  from fragments" section runs entirely on `unxt.unitsystem`, including a
  three-example argument about a list-valued `repr` and `eval(repr(x)) == x`.
  Re-grounding it on `Point` works: `Point` is a plain dataclass with no
  `pparts` and no `ReprMixin`, which is exactly the "the type knows how to
  rebuild itself, the renderer does not" point, and `wadler_lindig` gives a
  dataclass a usable `__pdoc__` for free. Its last section, "Why the engine is
  separate from `unxt`'s layer", is written in the future tense about an
  extraction that has now happened — it must be rewritten in the past tense,
  and the claim "intended to become a package of its own, named `pparts`"
  corrected: this package is named `wadler-lindig-parts`.
- *make-a-type-formattable* — defines `Version` inline (duplicating
  `examples.Version`), and its "pass the axes down" section builds an
  `Interval` of two `u.Q`. Re-grounding on `Term`, whose coefficient may be a
  sequence, covers the same forwarding point. Its `register_markup` example
  ends by printing a quantity under a `brackets` markup; `Term` substitutes
  directly. Its collision sentence is corrected per R3.

**Also**: both pages' `{doc}` targets include pages that do not exist here
(`../reference/formatting`, `format-quantities`). Those links are re-pointed at
this package's own pages, not translated literally into dead links — a dead
link is a strict-mode warning (R6).

## R10 — The unresolved rendering fault: what to watch for

**Decision**: no mitigation designed in advance. Watch for the signature and
report.

**Carried over from the request** (not independently reproduced here): while
re-grounding doctests in the consumer's repository, two docstring blocks using
`examples.Term` had `pparts` return **one** fragment where three were expected
under Sybil, while the identical call in a fresh interpreter — beartype
typechecking on, consumer fully imported — returned three. Ruled out there: a
duplicate module (the dispatcher reported the canonical one), a dispatch cache
warmed by an earlier fallback call, and the typechecking environment. Root
cause never found. It was designed around by having those two blocks pass
literal `PPart`s and depend on no registration.

**Why it matters here**: that workaround is not available. This package's
documentation is almost entirely examples over registered types — `Version` and
`Term` under `repr`, `html`, `latex` and the `sep` axis — so if the fault
reproduces, it lands in the pages that make the package's argument.

**Signature to watch for**:

- `pparts(Term(...))` returning one fragment instead of three;
- under `html`, the whole string wrapped in a single `<span>` rather than
  per-role wrappers;
- a separator that the `sep` axis fails to override (`2 * 1` where `2.1` is
  expected, or the reverse).

All three are the unregistered-type fallback path showing through.

**Rationale for not pre-empting it**: nothing establishes it reproduces here,
and the conditions that distinguished the failing case from the passing one were
never identified — so there is no mitigation to design, only a check to run.
The implementation runs the full suite and inspects the `Term` and `Version`
examples' actual output, and the pull request states whether the signature
appeared. Papering over it — by passing literal `PPart`s here too — is
explicitly rejected: this is the repository where the fault would do real
damage, and the examples over registered types are the ones worth having.

## R11 — Release workflow: filename and environment are fixed by the PyPI side

**Decision**: `.github/workflows/cd.yml`, GitHub environment `pypi`, URL
`https://pypi.org/p/wadler-lindig-parts`, gated on `refs/tags/v*`. Modelled on
the sibling project's `cd.yml`, actions pinned by SHA with the version in a
trailing comment.

**Source**: a peer session configuring PyPI trusted publishing for this
distribution reported that the publisher is being registered against that exact
workflow filename and environment name, and that a mismatch fails the upload
without a useful error. The sibling project's `cd.yml` already has this shape,
so following it satisfies both.

**Unchanged**: nothing is published and no tag is created by this work
(FR-023). The workflow exists, is correct, and is gated on a tag nobody pushes.

**Note recorded for the owner**: a PyPI pending publisher does not reserve the
project name — the name stays claimable until the first actual publish.

## Residual unknowns

None blocking. Two things are verified during implementation rather than
asserted now, because the only honest way to settle them is to run them:

1. **Which Sybil parser collects `>>>` prompts in Python docstrings** (R8) —
   settled by collecting and counting the resulting test items.
2. **Whether any zensical warning survives `--strict`** on a site this small,
   and whether `mkdocstrings` actually renders under zensical (per the
   constitution's warning that zensical ignores MkDocs plugins silently) —
   settled by building the site and reading the built HTML for the API page's
   rendered members. If `mkdocstrings` turns out to be inert, the API page is
   written as hand-maintained Markdown and the pull request says so, rather
   than shipping a page that silently renders nothing.
