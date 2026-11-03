# Documentation restructure — summary

## What changed

The tree was four pages with **no tutorial at all**, and a home page that was
really the entire spec-grammar reference wearing a welcome banner (scanner
mix 0.43, 8 tables). A newcomer had nowhere to land: the only task-shaped page
opened by assuming you already knew what `pparts` was. There are now two
executable lessons that build a type from nothing, and the grammar lives in
reference where it can be looked up instead of read.

- Pages before: **4** · after: **16** (1 moved, 2 split into 9, 6 written new, 0 deleted)
- Sections: tutorials 2 · how-to 4 · reference 4 · explanation 1 · landing 5
- Executed examples in `docs/` + `README.md`: **89 → 184**

## Key decisions

- **`index.md` kept its URL and lost its content.** It was the most-linked
  page and the most contaminated one; the grammar moved to
  `reference/spec-grammar.md` and `reference/axes.md`, leaving a real landing
  page. The fragments under it (`#the-six-axes`, …) break — see *Links*.
- **Two tutorials, not one per feature.** The second teaches the extension
  model, which is the package's whole point and previously existed only as a
  task for someone who already wanted it. Forced symmetry would have given
  four thin ones.
- **`how-to/make-a-type-formattable.md` kept its URL** and shed three of its
  four jobs. Its "What registration refuses" section (225 words of rules) was
  drained into `reference/registration-rules.md`.
- **`toc.integrate` removed from the theme.** It is incompatible with
  `navigation.indexes`, and section landing pages are what tell a reader which
  mode they are in.
- **`attr_list`, `md_in_html` and `tables` declared explicitly.** Zensical
  replaces its default extension set the moment one is declared, so the card
  grid and every table needed naming.

## Facts I invented or inferred

**None.** Every assertion in the new pages is either a doctest executed by the
project's own suite, or a value read off the live registry. Two cases where I
had written a plausible-looking fact and the doctests caught it:

| Claim I wrote | What was true | Caught by |
|---|---|---|
| `pspec(Term([1.0,2.0,3.0],"x"), ".1f")` returns a formatted list | `TypeError: unsupported format string passed to list.__format__` — a value spec formats the *payload*, not each element | `pytest docs/reference/axes.md` |
| A markup row without a `bare` key renders `'2.0 &lt;b&gt;'` | `'2.0 * &lt;b&gt;'` — an omitted separator key falls back to the engine default | `pytest docs/how-to/add-a-markup.md` |

The first also corrected a claim inherited from the old `index.md`, which
described the `value` axis as controlling "how each element is formatted".

## Things I claimed to verify, and how

- `pytest` (the project's own gate, as CI runs it) — **370 passed**, up from
  289. Every fenced block under `docs/` is a Sybil doctest, so "the examples
  work" is enforced, not asserted.
- `uv run --python 3.10 --no-default-groups --group tests --locked pytest` —
  **370 passed** on the support floor.
- `uv run zensical build --clean --strict` — `No issues found`, and verified
  beyond that: all 16 pages emit real HTML, the card grid renders, tables
  render (3 in `axes.md`, 2 in `spec-grammar.md`), mkdocstrings still produces
  API content (16 `register_axis` mentions), and all four mode sections appear
  in the nav. This repo has already caught zensical reporting "No issues
  found" while emitting no home page, so the build's own word is not enough.
- `uv run pre-commit run --all-files` — every hook passes (taplo reformatted
  `zensical.toml`; re-staged and re-run clean).
- `check_repo_refs.py . --old-docs <pristine> --new-docs docs/` — **clean**,
  96 files scanned outside the docs tree, 4 doc paths moved.
- `docs_inventory.py` over the **finished** tree — tutorial count 0 → 4. It
  reported one duplicated table row, which is the shared *See also* navigation
  line on `reference/axes.md` and `reference/registration-rules.md`; that is a
  link list, not a fact. Prose duplication was checked by reading.
- `check_links.py docs/` — **6 unresolved anchors, all false positives.** They
  are mkdocstrings targets (`api.md#wadler_lindig_parts.parse_spec`), which a
  stack-agnostic Markdown checker cannot see. Verified by hand that all five
  ids exist in `site/reference/api/index.html` and that the built pages link
  to them correctly; zensical's own `--strict` anchor validation passes.
- Both tutorials executed end to end; every "expected output" block is real
  output. Neither needs a network, an account or a key.

## Gaps found and not filled

Both appear under *Not yet written* on `how-to/index.md`.

- **How to write `__pdoc__` for a constructor-form repr.** The old how-to
  pointed at this and no page existed. A dataclass gets a usable `__pdoc__`
  from `wadler_lindig` for free, so the guide is only needed for types that
  are not dataclasses — and it would have to document `wadler_lindig`'s
  protocol, which I did not verify. Not written rather than guessed.
- **How to register `pvalue` for your own payload type.** `pvalue` is a
  public dispatch point and is how a library with array types decides what a
  value format spec means for them. The extension point is real; no worked
  example was written.

## Contradictions found in the source

- The old `index.md` described the `value` axis as controlling "how each
  element is formatted". Measured behaviour is that the spec is applied to the
  payload as a whole via `format()`. The engine's own error-message help text
  still says "applied per element" — **source, not docs**, so left alone and
  noted here.

## Links

- **Redirect mechanism: generated meta-refresh stubs.** Zensical has no
  redirect support. Verified that it copies non-Markdown files from `docs/`
  verbatim, so `docs/api/index.html` is served at the old `/api/` URL. The
  stub was generated by `make_redirect_stubs.py`, then its target changed from
  absolute to relative (`../reference/api/`) because the site is served under
  a base path. It preserves fragments.
- **1 old URL mapped.** The other three pages did not move.
- **Accepted breakage:** anchors under `index.md` whose sections moved to
  `reference/`. A stub cannot rewrite a fragment on a page that still exists.
  The site went live and the package was published on 2026-11-02, so inbound
  deep links are approximately zero — this is the cheapest moment this
  restructure will ever happen.
- **Enforcement:** `zensical build --strict` fails on broken internal links
  and anchors, and runs in `build_docs.yml` on every push and pull request.
