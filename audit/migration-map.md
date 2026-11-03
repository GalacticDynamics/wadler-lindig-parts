# Migration map — `wadler-lindig-parts` docs

**Source files:** 4 (`docs/**/*.md`). **Map rows:** 4. Counts agree.

`README.md` is not in `docs/` and is not a doc page; it is listed under
*Repo references* below because it links into the tree.

## Per-page destinations

| # | Source | Reads as | Move | Destination(s) |
|---|---|---|---|---|
| 1 | `docs/index.md` | reference (mix 0.43) | **SPLIT** → 4 | `docs/index.md` (landing, URL kept) · `reference/spec-grammar.md` · `reference/axes.md` · `explanation/why-formatting-is-one-engine.md` (§ appended) |
| 2 | `docs/api.md` | reference | **MOVE** + RETITLE | `reference/api.md` |
| 3 | `docs/how-to/make-a-type-formattable.md` | how-to (mix 0.21) | **SPLIT** → 5 | `how-to/make-a-type-formattable.md` (kept, slimmed) · `how-to/nest-formattable-values.md` · `how-to/add-an-axis.md` · `how-to/add-a-markup.md` · `reference/registration-rules.md` |
| 4 | `docs/explanation/why-formatting-is-one-engine.md` | explanation (mix 0.09) | **KEEP** + receive | unchanged path; gains one § from #1 |

Nothing is deleted. No source content is dropped; every seam below names where
it lands.

## Seams resolved (from `audit/inventory.md`)

| Seam | Line | Move | Lands in |
|---|--:|---|---|
| `index.md` → "wadler-lindig-parts" reads as how-to | 1 | rewrite as landing page | `index.md` |
| `index.md` → "The scan goes left to right" | 45 | **DRAIN** | `reference/spec-grammar.md` |
| `index.md` → "Keywords share one flat namespace" | 65 | **DRAIN** + EXTRACT rationale | `reference/spec-grammar.md` + `how-to/add-an-axis.md` |
| `index.md` → "The six axes" | 113 | **DRAIN** | `reference/axes.md` |
| `index.md` → "The two layouts" | 147 | **DRAIN** | `reference/axes.md` |
| `index.md` → "Layout is wadler-lindig's, not ours" | 168 | **SPLIT**: behaviour vs argument | `reference/axes.md` (width/indent) + `explanation/…` (the argument) |
| `how-to/…` → "Pass the axes down to nested values" | 69 | **EXTRACT** | `how-to/nest-formattable-values.md` |
| `how-to/…` → "What registration refuses" | 189 | **DRAIN** | `reference/registration-rules.md` |
| `how-to/…` → "See also" | 260 | dissolve into per-page links | all how-tos |
| `api.md` → "Example types" | 82 | keep as a scope note | `reference/api.md` |

## New pages (written, not moved)

| Page | Mode | Why it exists |
|---|---|---|
| `tutorials/your-first-formattable-type.md` | tutorial | **The audit's headline gap: 0 tutorials.** Nothing in the tree teaches a newcomer; the how-to assumes they already know they want `pparts`. |
| `tutorials/teach-the-grammar-a-new-word.md` | tutorial | Lesson 2. The extension model is the package's whole point and was only ever documented as a task for someone who already wanted it. |
| `tutorials/index.md`, `how-to/index.md`, `reference/index.md`, `explanation/index.md` | landing | Section entry points; `navigation.indexes`. |

## Redirects

**Zensical has no redirect mechanism.** Mitigation, in order of what it costs:

1. **URLs kept stable** for the three pages anything could plausibly link to:
   `index.md`, `how-to/make-a-type-formattable.md`,
   `explanation/why-formatting-is-one-engine.md`. These do not move.
2. **Meta-refresh stub** at `/api/` for the one page that does move. Verified
   that Zensical copies non-Markdown files from `docs/` into `site/`
   verbatim, so a committed `docs/api/index.html` is served at the old URL.
3. **Fragment breakage accepted and recorded**: anchors under `index.md`
   (`#the-spec-grammar`, `#the-six-axes`, `#the-two-layouts`, …) move to
   `reference/`. The stub mechanism cannot rewrite a fragment on a page that
   still exists. The site went live 2026-11-02 and the package was published
   the same day, so inbound deep links are ~zero; this is the cheapest moment
   this restructure will ever happen.

## Repo references to check

Outside `docs/`, these name doc paths: `README.md`, `zensical.toml` (`nav`),
`pyproject.toml` (`testpaths` includes `docs`), `conftest.py` (Sybil collects
`*.md`), `.github/workflows/build_docs.yml`. All are checked with
`check_repo_refs.py` and by running the project's own gate.

## Gate

Every fenced block under `docs/` is a Sybil doctest collected by `pytest`, so
"the examples work" is enforced, not asserted. Baseline before this work:
**289 passed**, of which 89 come from `README.md` + `docs/`.

## Redirect table

| Old URL | New URL |
|---|---|
| `/api/` | `/reference/api/` |
