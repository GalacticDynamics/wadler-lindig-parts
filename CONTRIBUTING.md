# Contributing

Changes arrive by pull request on a branch, never by committing to `main`.

## Setup

```bash
uv sync                      # the dev group: docs, lint, tests
```

Python 3.10 is the floor and 3.15 the ceiling; CI runs every version in
between, and the 3.10 job is what keeps the floor a fact rather than a claim
about syntax.

## The gates

These three are what CI checks, and they are worth running before pushing:

```bash
uv run pytest                            # includes the doctests in src/ and docs/
uv run pre-commit run --all-files        # the lint gate: ruff, pyright, taplo
uv run zensical build --clean --strict   # the docs site
```

Every fenced code block under `docs/` and in `README.md` is collected by
Sybil and executed, so a documented output that nobody ran will fail. That is
deliberate — see principle III in `.specify/memory/constitution.md`.

Note that `zensical build --strict` reports "No issues found" for a config
that emits nothing, so `.github/workflows/build_docs.yml` checks the built
site itself rather than trusting the build's own word.

## Exploring the codebase

This package is wired up for
[graphify](https://github.com/Graphify-Labs/graphify), which turns the source
into a queryable knowledge graph. Extraction is local tree-sitter AST
parsing: no LLM, and nothing leaves your machine. The one LLM step is naming
communities, which `--no-label` skips.

There is no task runner here, so the two steps are run directly. `--no-project`
keeps graphify out of the project environment, so nothing reaches `uv.lock`:

```bash
alias gf='uv run --no-project --with graphifyy graphify'

gf extract . --code-only     # AST pass, no LLM
gf cluster-only .            # communities and labels ("--no-label" to skip the LLM)
```

That writes `graphify-out/` — `graph.html` (clickable), `GRAPH_REPORT.md`
(hubs, communities, suggested questions) and `graph.json`. The whole directory
is generated and gitignored: it is rewritten whole on every build, and a
committed copy would go stale while still looking authoritative. graphify's
own repository gitignores it for the same reason.

Then query it:

```bash
gf god-nodes                              # the architectural hubs
gf explain "parse_spec"                   # one symbol and its neighbours
gf path "pparts" "parts_to_markup"        # how two things connect
gf query "how does a spec reach a markup" # a scoped subgraph for a question
gf update .                               # refresh after code changes, no LLM
```

Every edge is tagged `EXTRACTED` (explicit in the source) or `INFERRED`
(resolved by graphify), so you can tell what was read from what was guessed.

`graphifyy` (two y's) is the PyPI name; the command it installs is `graphify`.
`uv tool install graphifyy` puts it on `PATH` if you use it often.
