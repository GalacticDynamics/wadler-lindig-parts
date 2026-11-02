---

description: "Task list for standing up wadler-lindig-parts as a standalone package"
---

# Tasks: Standalone package

**Input**: Design documents from `/specs/001-standalone-package/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md),
[research.md](./research.md), [data-model.md](./data-model.md),
[contracts/public-surface.md](./contracts/public-surface.md),
[quickstart.md](./quickstart.md)

**Tests**: Test tasks are included and are **mandatory**, not optional. The
constitution's Development Workflow says "Test first. Write the failing test,
run it, watch it fail, then implement," and principle V requires that every
pinned claim have a test that was *observed* failing. Each test task below says
how to make it fail when the behaviour it asserts already exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel — different files, no dependency on an
  incomplete task
- **[Story]**: which user story the task serves (US1–US5)
- Every task names its exact file path

## Path Conventions

Single project, src layout. `src/wadler_lindig_parts/`, `tests/`, `docs/` at
the repository root. Paths are relative to the repository root throughout.

---

## Phase 1: Setup

**Purpose**: make the package exist as a package. Nothing below Phase 1 can
even be collected by `pytest` until T003 lands.

- [X] T001 Create `pyproject.toml` at the repository root: `[project]` with `name = "wadler-lindig-parts"`, `version = "0.1.0"`, `requires-python = ">=3.10"`, `dependencies = ["wadler-lindig>=0.1.8", "plum-dispatch>=2.7.0"]` (exactly these two — constitution principle I), `authors` / `license` / `readme` / `classifiers` / `urls` modelled on `nstarman/quax@main`; `[build-system]` with `build-backend = "hatchling.build"` and `requires = ["hatchling"]` (no `hatch-vcs` — the version is static, see plan.md Complexity Tracking); `[tool.hatch.build.targets.wheel]` with `packages = ["src/wadler_lindig_parts"]`
- [X] T002 Add the dependency groups to `pyproject.toml`: `tests = ["pytest>=8.3.5", "sybil>=9"]`; `lint = ["prek>=0.3.11", "ruff>=0.15.9"]`; `docs = ['mkdocstrings[python]==1.0.8; python_version >= "3.11"', "pymdown-extensions==12.3", "zensical"]` — the marker is **required**, `uv lock` fails hard without it (research.md R5, measured); `dev` including all three. Omit `nbconvert` (no notebooks) and `hippogriffe` (zensical silently ignores it — R7)
- [X] T003 Create `src/wadler_lindig_parts/__init__.py` re-exporting the union of `engine.__all__` (28 names) and `generic.__all__` (4 names) plus the `examples` submodule, and setting the package's own `__all__` to exactly that set plus `"examples"` (surface rules S1–S4 in contracts/public-surface.md). A name listed in a module's `__all__` but absent from the module must make the import **fail**, not be silently dropped (S3) — a `from .engine import *` does not give that, so import the names explicitly or assert the sets match at import
- [X] T004 Add `[tool.pytest.ini_options]` to `pyproject.toml`: `addopts = ["-ra"]`, `minversion = "8.3"`, `pythonpath = ["src"]`, `testpaths = ["README.md", "docs", "src/", "tests"]` — all four roots, so docstring and Markdown examples are collected (principle III)
- [X] T005 [P] Add `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.isort]`, `[tool.ruff.format]` and `[tool.pyright]` sections to `pyproject.toml`, modelled on `nstarman/quax@main`. Set `docstring-code-format = true` under `[tool.ruff.format]`. Do **not** add `[tool.mypy]` — quax `main` dropped the static type checker from its lint group and type-checks through the pre-commit `pyright` hook instead (R7)
- [X] T006 Run `uv lock` then `uv sync` and confirm both succeed. If `uv lock` reports `No solution found when resolving dependencies for split (markers: python_full_version == '3.10.*')`, the docs-group marker from T002 is missing or wrong
- [X] T007 [P] Create `README.md` at the repository root: what the package is, the two-dependency rule, an installation line, and a short runnable example on `examples.Version`. The README is in `testpaths` (T004), so its examples are tests. The load-order note it also needs is T026 — do not write it yet
- [X] T008 [P] Create `.pre-commit-config.yaml` modelled on `nstarman/quax@main`: `no-commit-to-branch` (`--branch main`), `ruff-check` with `--fix`, `ruff-format`, `pyright` with `additional_dependencies` of `["pytest", "plum-dispatch", "wadler-lindig", "sybil"]` — **not** quax's list, which names `jax`, `equinox` and `jaxtyping` that this package must never depend on — and `taplo-format`

**Checkpoint**: `uv sync` succeeds and `uv run python -c "import wadler_lindig_parts"` works. The package is installable (US1 satisfied).

---

## Phase 2: Foundational

**Purpose**: make examples run. Blocking: until `conftest.py` exists, no
docstring example and no Markdown fence is a test, so principle III is
unenforced and every later verification is partly vacuous.

- [X] T009 Create `conftest.py` at the repository root wiring Sybil: one `Sybil` over `patterns=["*.md"]` with `sybil.parsers.markdown.PythonCodeBlockParser` and `SkipParser` (plain fences — **not** `sybil.parsers.myst`, which `unxt` uses because its pages carry `{code-block}` directives; R8), summed with one over `patterns=["*.py"]` carrying a doctest parser for the `>>>` prompts in this package's module docstrings. Install the sum as `pytest_collect_file`. Use `optionflags = ELLIPSIS | NORMALIZE_WHITESPACE`
- [X] T010 Verify T009 actually collects, with `uv run pytest --collect-only -q`: items must appear from `src/wadler_lindig_parts/engine.py`, `generic.py` and `examples.py`, not only from `tests/`. Record the counts. Zero items from `src/` means the `*.py` parser is wrong for `>>>` prompts — R8 flags this as unverified, so settle it by counting, not by assuming
- [X] T011 Run `uv run pytest` and fix every docstring example that fails. **Expect failures**: no example in `engine.py`, `generic.py` or `examples.py` has ever been executed — there has never been a runner. Principle V names this exact failure mode, "a docstring example showing output nobody ran". Fix the **examples** to the measured output; only change engine code if an example documents correct behaviour that the code gets wrong, and say so in the pull request
- [X] T012 While doing T011, watch for the carried-over rendering fault (research.md R10, quickstart.md): `pparts(Term(...))` returning one fragment instead of three; under `html`, the whole string in a single `<span>` instead of per-role wrappers; a separator the `sep` axis cannot override. Record whether the signature appeared. Do **not** work around it by passing literal `PPart`s — that workaround is unavailable here and explicitly rejected

**Checkpoint**: `uv run pytest` green, with every docstring example collected and running.

---

## Phase 3: US2 — The suite passes with no consumer installed (P2)

**Goal**: a suite that runs standalone, on the floor interpreter, with nothing
that assumes `unxt` is importable or reads a file `unxt` owns.

**Independent test**: `uv run --python 3.10 --no-default-groups --group tests pytest` passes, and `uv run --no-default-groups --group tests python -c "import unxt"` fails.

> US2 precedes US1's remaining verification and US3 because one of the three
> affected tests **raises on collection** (T013) — the suite cannot be green at
> all until it is dealt with.

- [X] T013 Delete `test_the_package_side_exposes_no_privates_across_the_seam` from `tests/test_engine.py` (line ~353). It reads `engine.__file__`'s sibling `axes.py`, which belongs to `unxt`'s layer and does not exist here, so it raises on collection. The property it guarded is now on the far side of a distribution boundary and is unobservable from this repository; leaving it would be a test that passes by doing nothing. Note the deletion and the reason for the pull-request body (FR-009)
- [X] T014 [US2] Rewrite `test_the_engine_alone_registers_six_axes_and_no_aliases` in `tests/test_engine.py` (line ~312) to read this package's registry directly — `sorted(AXES)`, `len(ALIASES)`, `sorted(MARKUPS)` — asserting `["indent", "layout", "markup", "sep", "value", "width"]`, `0`, and `["html", "latex", "text"]`. Remove the `tmp_path` parameter, the module copying, the `subprocess` call and the `json` round-trip: they existed only to escape `unxt.__init__`'s eagerly registered axes, and there is no consumer here. Also drop the now-unused `_PACKAGE_SIDE` copying machinery if nothing else uses it
- [X] T015 [US2] Replace `test_this_suite_reaches_only_for_the_package_side` in `tests/test_engine.py` (line ~774) with the inverted discipline test: `ast.parse` every `*.py` under `src/wadler_lindig_parts/` and assert every `Import` / `ImportFrom` resolves to the standard library (`sys.stdlib_module_names`), `wadler_lindig`, `plum`, or a sibling module of this package. Cover **absolute** imports, which the existing relative-import test at line ~384 does not — reconcile the two into one test rather than leaving them overlapping. This is contract C4 and the test principle I claims exists. **Watch it fail first**: add `import json` at the top of `generic.py`, run the test, record the failure, remove the import

**Checkpoint**: `uv run pytest` green; `uv run --python 3.10 --no-default-groups --group tests pytest` green; `import unxt` fails in that environment. US1 and US2 both verifiable.

---

## Phase 4: US3 — Three behaviours that became contract are pinned (P3)

**Goal**: each of the three cross-distribution contracts asserted by a test
that was watched failing.

**Independent test**: break each behaviour and watch exactly one new test fail.

- [X] T016 [P] [US3] Add a test to `tests/test_engine.py` pinning contract **C1**, both halves: register two temporary axes claiming one keyword, assert the registrations both **succeed** (`_KEYWORDS[word]` holds both names), assert a spec using the word bare raises with a message naming **both** claimants and both qualified forms (`pytest.raises(..., match="ambiguous keyword")`, then assert both axis names and both `a=w` forms appear in the message), and assert each qualified form resolves to its own axis. Unregister both in a `finally`. **Watch it fail first**: temporarily change `_KEYWORDS.setdefault(word, []).append(...)` in `engine.py` to `_KEYWORDS[word] = [axis.name]`, run, record the failure, revert. No test matching `ambiguous` exists today
- [X] T017 [P] [US3] Add a test to `tests/test_engine.py` pinning contract **C2**: for each of the four keys in `REQUIRED_MARKUP_KEYS` (`_content`, `wrap`, `vsep`, `escape`), register a row omitting that key, assert `ValueError` whose message names the missing key, and assert neither `MARKUPS` nor `_KEYWORDS` gained an entry — the "at registration, not at render" half of the claim is what the second assertion carries. Parametrise over the four keys. The existing `test_register_markup_rejects_a_malformed_template` supplies all four keys and corrupts a *value*, so the missing-key branch is unexercised. **Watch it fail first**: comment out the `if missing := ...` block in `_check_markup_row`, run, record, revert
- [X] T018 [P] [US3] Add a test to `tests/test_engine.py` pinning contract **C3**: define a class inheriting `ReprMixin` whose `__repr_spec__` names a keyword belonging to an axis that is **not yet registered**, and assert the `class` statement itself raises. Then register the axis, define the class again, and assert it succeeds. This is the registration-*order* case; `test_bad_repr_spec_fails_at_class_creation` in `tests/test_downstream.py` covers only a syntactically invalid spec. **Watch it fail first**: move the `parse_spec` call out of `__init_subclass__` into `__repr__`, run, record, revert
- [X] T019 [US3] Amend constitution principle IV in `.specify/memory/constitution.md`: bullet 1 ("The first registration of a word wins") is false — neither wins; the bare word becomes unusable and both qualified forms work. Bullet 2's placement is wrong — the refusal is at parse, not at registration. The claim "`register_axis` enforces the first two" is false; resolution does. Keep bullet 3 unchanged; it is the reason the others give way. State what evidence changed, as the Governance section requires, and bump **Last Amended** (FR-012a, research.md R3)

**Checkpoint**: all three contracts pinned, each watched failing. `uv run pytest` green.

---

## Phase 5: US4 — Documentation whose every example runs (P4)

**Goal**: four pages, built strict with no warnings, every fence a passing test.

**Independent test**: `uv run zensical build --clean --strict` succeeds silently, and `uv run pytest` collects and passes items from `docs/`.

- [X] T020 [US4] Create `zensical.toml` at the repository root, modelled on `nstarman/quax@main`'s: `[project]` with `site_name`, `site_description`, `site_author`, `site_url`, `repo_name = "GalacticDynamics/wadler-lindig-parts"`, `repo_url`; a `nav` covering the four pages of T021–T024; `[project.theme]` with the two light/dark palette entries; `[project.markdown_extensions]`; `[project.plugins.mkdocstrings.handlers.python.options]`. There must be **no `mkdocs.yml`** — quax `main` deleted its own (R7), and the constitution names `zensical.toml` as the config
- [X] T021 [P] [US4] Write `docs/index.md`: the spec grammar — the left-to-right scan rule and why (a Python format spec may contain `-`, so the format spec goes last), the flat keyword namespace and `axis=word`, the six built-in axes, the three markups. Every example runs on `examples.Version` / `Term` / `Point`; none imports a consumer (principle III)
- [X] T022 [P] [US4] Write `docs/api.md` covering the 32 public names. Prefer `mkdocstrings` directives over hand-maintained prose — but see T025, which decides whether that actually works
- [X] T023 [US4] Convert `docs/explanation/why-formatting-is-one-engine.md` from `GalacticDynamics/unxt@main` (89 lines). Mechanical: 1 `{doc}` role → an ordinary link, 3 ```` ```{code-block} python ```` → plain ```` ```python ```` fences. Then the rewrite, which is the larger half: its "Why the constructor form is not built from fragments" section runs entirely on `unxt.unitsystem` — re-ground it on `Point`, a plain dataclass with no `pparts` and no `ReprMixin`, which makes the same point via `wadler_lindig`'s free dataclass `__pdoc__`. Its final section is written in the future tense about an extraction that has now happened: rewrite it in the past tense and correct "intended to become a package of its own, named `pparts`" — this package is `wadler-lindig-parts`. Re-point `{doc}` targets at pages that exist here; a dead link is a `--strict` warning (R9)
- [X] T024 [US4] Convert `docs/how-to/make-a-type-formattable.md` from `GalacticDynamics/unxt@main` (135 lines). Mechanical: 5 `{doc}` roles → links, 5 `{code-block}` → plain fences. Rewrite: it defines `Version` inline, duplicating `examples.Version` — import the real one. Its "pass the axes down" section builds an `Interval` of two `u.Q`; re-ground on `Term`, whose coefficient may be a sequence. Its `register_markup` example formats a quantity under a `brackets` markup; substitute `Term`. **Correct its collision sentence** — "Registration raises on any collision rather than overwriting" is false of a keyword claimed by two axes (contract C1); it stays true of a duplicate axis name, alias or markup name, so the corrected sentence must distinguish them (FR-012b)
- [X] T025 [US4] Run `uv run zensical build --clean --strict` and fix every warning until it is silent. Then verify `mkdocstrings` is not inert: `grep -c 'register_axis' site/api/index.html` must be non-zero. The constitution warns that zensical silently ignores MkDocs plugins — a plugin named in the config neither works nor complains — so this is read from the built site, never inferred from `zensical.toml` (FR-020). If the count is zero, rewrite `docs/api.md` as hand-maintained Markdown and say so in the pull request
- [X] T026 [US4] Add the load-order note to `README.md` (contract C3, FR-014): `__repr_spec__` is resolved at class creation, so a consumer must register its axes **before** defining the classes whose repr specs name them. Across two installed distributions this is load order between them, and the error arrives at a `class` statement that looks unrelated — which is why it is documented rather than left to the message
- [X] T027 [US4] Run `uv run pytest` and fix every failing example in `docs/` and `README.md`. Watch again for the R10 signature (T012) — these pages are almost entirely examples over registered types, which is exactly where it would land

**Checkpoint**: site builds strict and silent; every documentation example passes; `mkdocstrings`'s effect verified in the built HTML.

---

## Phase 6: US5 — Automation enforces the gates (P5)

**Goal**: the gates run on every pull request; a release path exists and is
never exercised.

**Independent test**: open the pull request and watch the checks.

- [X] T028 [P] [US5] Create `.github/workflows/ci.yml` modelled on `nstarman/quax@main`'s: a `setup` job deriving oldest/newest from `PYTHON_VERSIONS: '["3.10", "3.11", "3.12", "3.13", "3.14"]"'`, a `lint` job running `uv run --frozen prek run --all-files` with `SKIP: no-commit-to-branch`, a `tests` matrix over every version using `uv sync --no-default-groups --group tests --locked`, `oldest-supported` (`--resolution lowest-direct`) and `newest-supported` (`--upgrade`) jobs, and an `alls-green` gate. **3.10 must be in the matrix** — it is what makes the floor a fact rather than a claim about syntax (constitution, Development Workflow; FR-021). Drop quax's `integration` job: there are no integration tests here. Keep every action pinned by SHA with the version in a trailing comment
- [X] T029 [P] [US5] Create `.github/workflows/build_docs.yml` modelled on quax `main`'s: build on pull requests and pushes to `main`, upload and deploy to Pages only on `main`. Run `uv run --frozen zensical build --clean --strict` — quax uses `--clean` alone; `--strict` is this package's requirement (FR-019). **Omit the notebook-conversion step**: this package has no notebooks
- [X] T030 [P] [US5] Create `.github/workflows/cd.yml` — **exactly that filename**, with GitHub environment `name: pypi` and `url: https://pypi.org/p/wadler-lindig-parts`, gated on `if: startsWith(github.ref, 'refs/tags/v')`, triggered on `push: tags: ["v*"]` and `workflow_dispatch`. Modelled on quax `main`'s `cd.yml`: a `build` job using `hynek/build-and-inspect-python-package` with build provenance, then a publish job downloading the `Packages` artifact to `dist/` and calling `pypa/gh-action-pypi-publish`. The filename and environment name are fixed by the trusted-publishing configuration being set up on PyPI's side; a mismatch fails the upload with no useful error. Actions pinned by SHA with the version in a trailing comment
- [X] T031 [US5] Run `uv run pre-commit run --all-files` and fix everything it reports until clean. This is the lint gate, not `ruff check` alone — the formatter and the other hooks catch what the linter does not (constitution, Development Workflow; FR-022). If `no-commit-to-branch` objects outside a commit, skip that one hook as CI does

**Checkpoint**: all three workflows present; the lint gate clean locally.

---

## Phase 7: Polish & verification

- [X] T032 Run every command in [quickstart.md](./quickstart.md) — V1 through V5 — and record each one's **actual output**. The pull request reports those outputs, not a claim that they passed (constitution principle V: measured values, not plausible ones)
- [X] T033 Verify surface rule S1 directly with the snippet in quickstart.md: 32 names, none missing, `examples` reachable, `__all__` matches
- [X] T034 Confirm `git tag --list 'v*'` is empty and nothing was published to any package index (FR-023, SC-008)
- [X] T035 Open the pull request. Its body must state, because the constitution's Governance section requires it and because each is a measured correction to the brief: **(a)** the public surface is 32 names, not 29 (research.md R1); **(b)** three tests needed attention, not two, and one was deleted rather than adjusted, with the reason (T013, R2); **(c)** constitution principle IV disagreed with the code and the principle was the bug — amended, with the evidence (T019, R3); **(d)** whether the R10 rendering signature appeared, either way (T012, T027); **(e)** `mkdocstrings`'s verified effect in the built site, or its replacement (T025); **(f)** that nothing was published and no tag created

---

## Dependencies & Execution Order

### Phase dependencies

```text
Phase 1 Setup ──────────────────▶ nothing can be collected before T003
    │
    ▼
Phase 2 Foundational ───────────▶ nothing is a test before T009
    │
    ▼
Phase 3 US2 ────────────────────▶ T013 unblocks a green suite at all
    │
    ├──▶ Phase 4 US3  ┐
    ├──▶ Phase 5 US4  ├─▶ these three are mutually independent
    └──▶ Phase 6 US5  ┘
                        │
                        ▼
                   Phase 7 Polish
```

**Phase 1 and Phase 2 are hard blockers**, not conventions: without
`pyproject.toml` and `__init__.py` there is no importable package, and without
`conftest.py` no example is a test. US1 (packaging) is satisfied by Phase 1
itself, which is why it has no phase of its own.

**US2 precedes US3/US4/US5** for one specific reason: T013 removes a test that
*raises on collection*. Until it is gone, `uv run pytest` cannot be green, so
no later checkpoint means anything.

### Story dependencies

- **US1 (P1)** — Phase 1. Blocks everything.
- **US2 (P2)** — Phase 3. Depends on Phases 1–2. Contains the one collection-blocking fix.
- **US3 (P3)** — Phase 4. Depends on Phases 1–3. Independent of US4 and US5.
- **US4 (P4)** — Phase 5. Depends on Phases 1–3. Independent of US3 and US5.
- **US5 (P5)** — Phase 6. Depends on Phases 1–3. Independent of US3 and US4.

### Parallel opportunities

- **Phase 1**: T005, T007, T008 are `[P]` — different files, no mutual
  dependency. T001→T002→T006 are sequential (same file, then the lock).
- **Phase 4**: T016, T017, T018 are `[P]`. All three append to
  `tests/test_engine.py`, so if written literally in parallel they conflict on
  that one file — they are independent in *content*, and the "watch it fail"
  step of each touches a different function in a different module.
- **Phase 5**: T021 and T022 are `[P]` (different new files). T023 and T024
  are not marked `[P]`: both are conversions whose `{doc}` targets point at
  each other, so the link re-pointing has to see both.
- **Phase 6**: T028, T029, T030 are `[P]` — three separate new workflow files.
- **Phases 4, 5 and 6 as wholes** can proceed in parallel once Phase 3's
  checkpoint holds.

### Within each story

- The test is written and **watched failing** before the behaviour it asserts
  is relied upon. For C1, C2 and C3, whose behaviour already exists, each task
  names the specific edit that makes it fail and says to revert it.
- Configuration before the thing it configures: `zensical.toml` (T020) before
  the build (T025); `pyproject.toml`'s pytest section (T004) before collection
  (T010).

---

## Parallel Example: Phase 6

```bash
# Three independent new workflow files:
Task: "Create .github/workflows/ci.yml with the 3.10-3.14 matrix"
Task: "Create .github/workflows/build_docs.yml with --clean --strict"
Task: "Create .github/workflows/cd.yml, environment pypi, gated on v*"
```

---

## Implementation Strategy

### MVP first

Phase 1 alone is a coherent deliverable: an installable package exposing its
full public surface. Phases 1–3 are the real floor, though — an installable
package whose suite cannot run is worse than one with no suite, because the gap
is hidden rather than visible.

1. Phase 1 → the package installs and imports (US1)
2. Phase 2 → every example is a test (principle III enforced)
3. Phase 3 → the suite is green standalone, on 3.10, with no consumer (US2)
4. **Stop and validate**: quickstart V1 and V2
5. Phases 4–6 in any order, or in parallel
6. Phase 7 → run everything, report actual output

### Incremental delivery

Each checkpoint is a working state:

| After | True |
|---|---|
| Phase 1 | installable, importable, 32 names reachable |
| Phase 2 | every docstring example runs |
| Phase 3 | green on the floor interpreter with no consumer installed |
| Phase 4 | the three cross-distribution contracts pinned |
| Phase 5 | documented, site builds strict and silent |
| Phase 6 | the gates run themselves |

### What is explicitly out of scope

Publishing to PyPI and tagging a release. `cd.yml` exists, is correct, and is
gated on a tag nobody pushes. Configuring trusted publishing is the repository
owner's separate step.

---

## What differed from the plan

Recorded because the constitution's Governance section asks for disagreements
to be stated rather than quietly absorbed.

**The extraction had broken nine tests, not three.** T013–T015 covered three.
Running the suite found six more, all reaching for `unxt`'s vocabulary — and
one of them was hiding three others:

| Test | Reached for | Replaced with |
|---|---|---|
| `test_a_downstream_package_can_register_its_own_axis` | `abbrev` keyword | `type`, from the `value` axis |
| `test_an_alias_never_collides_silently[compact]` | `compact` alias | `mul`, from the `sep` axis |
| `test_an_alias_name_may_not_be_claimed_as_a_keyword` | `compact` being an alias | registers its own alias first |
| `test_a_probe_that_raises_is_skipped_not_propagated` | `unit_style` axis, `name` keyword | an axis the test registers itself |
| `test_a_keyword_clash_on_replace_leaves_the_old_axis` | `compact` alias | an alias the test registers itself |

The last one is why the count was hard to see. With `compact` no longer an
alias, its `register_axis(..., replace=True)` *succeeded*, swapping the real
`sep` axis for one whose only keyword was `compact` — and because the test
then failed on `DID NOT RAISE`, it never restored it. Two later tests
(`test_a_successful_replace_keeps_keywords_consistent`,
`test_register_markup_rejects_a_keyword_clash`) failed only in a full run and
passed in isolation. A third,
`test_an_alias_name_may_not_be_claimed_as_a_keyword`, passed *because* of the
leak. Fixing the one test fixed all three.

**Two engine docstrings were also unxt-shaped**, and nothing had ever executed
them: `Spec.of(layout="call")["unit"]` and
`parse_spec("compact") == parse_spec("call-abbrev")`. Both re-grounded on
package vocabulary. This is exactly what T011 predicted.

**The engine took five annotation-only changes**, which the plan said would
not happen. Adding `pyright` (quax's gate; `unxt` used mypy) surfaced them,
and they are genuine defects rather than checker noise:

| Site | Was | Why it was wrong |
|---|---|---|
| `Axis.layouts` | `Mapping[str, Callable[...]]` | `None` is a legitimate value — `_layout_kwargs` guards `if translate is not None`, and `width`/`indent` register with `dict.fromkeys(_LAYOUTS)` precisely to mean "valid everywhere, translates to nothing". The annotation forbade what the code relies on. |
| `Spec.__init__(mapping=())` | `Mapping[str, Any]` | the default `()` is not a `Mapping`; `dict()` accepts a mapping *or* an iterable of pairs, which is why it works |
| `_free_text(spec)` | `axis.keywords` after an `axis is None` branch | correlated conditions a reader can see and a checker cannot; an early return says it to both |
| `examples.pparts_term(**kw: object)` | `object` | too tight — the engine forwards values typed more precisely downstream (`value_spec: str | None`) |

No behaviour changed; the suite was 287 passing before and after.

**Three suppressions were added, each scoped and argued**: ruff `F811` under
`src/**` only and pyright `reportRedeclaration`, both for the plum-dispatch
`@dispatch.abstract` + per-type-overload pattern — following `unxt`'s own
precedent, which scopes `F811` to `src` because outside it a redefinition is a
real bug; and ruff `F401` on `__init__.py` alone, whose whole job is
re-export and whose names are checked at import instead.

**`zensical` needed a lower bound to tell the truth.** See research.md R5:
unpinned, uv silently satisfied the 3.10 resolution split with a years-old
zensical rather than reporting that the current one needs >=3.11. The group
looked 3.10-installable while being nothing of the kind.

**`.taplo.toml` was added**, which no task named. The `taplo-format` hook
modelled on quax reformats TOML, and without quax's own `.taplo.toml` it
stripped the aligned `=` that quax's files have — so the config is part of
modelling those conventions, not an extra.

**`pre-commit` rather than `prek`.** quax `main` uses `prek`, its faster
drop-in. The constitution names `uv run pre-commit run --all-files` as the
lint gate, so following quax here would have left the constitution naming a
command that does not exist in this environment.

**A note on the lint gate.** `pre-commit run --all-files` means
*git-tracked* files. Run before `git add`, it reported `check toml` and
`taplo-format` as "no files to check" while `pyproject.toml` sat untracked in
the working tree. The gate is only meaningful after staging.

## What was looked for and not found

**The R10 rendering fault did not reproduce.** `pparts(Term(2.0, "x"))`
returns three fragments under Sybil and in a fresh interpreter alike, and the
per-role `<span>` wrappers are present under `html`. The one apparent
mismatch while probing was the probe's own expected value: `html` alone
renders `'<span>2.0</span> <span>x</span>'` because the `sep` axis defaults to
`bare`, and `html-mul` gives `'<span>2.0</span> * <span>x</span>'`. Both
environments agreed on both. Nothing was worked around.

**`mkdocstrings` is not inert under zensical.** `site/api/index.html` contains
the rendered docstring text (`Add an axis to the grammar`,
`rejecting any keyword collision`) and no echoed `:::` directive, so the API
page is genuinely generated rather than silently empty. Checked in the built
HTML, per FR-020, and the check is now a step in `build_docs.yml` so it cannot
rot.

**But zensical's `--strict` did not catch a missing page.** With `index.md`
listed in `nav` and absent from `docs/`, `zensical build --clean --strict`
reported `No issues found` and simply produced no `site/index.html`. That is
the constitution's silent-plugin hazard in a second form, and it means a clean
strict build is not by itself evidence that the nav is intact. Internal links
were therefore validated separately against the built HTML: 0 dead, 0
unconverted `.md`.
