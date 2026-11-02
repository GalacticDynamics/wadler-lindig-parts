# Phase 1 contracts

Two kinds of contract. **The surface** — what a consumer may import, which
this feature makes reachable for the first time. **The four behaviours** —
properties a consumer relies on, which were implementation detail inside `unxt`
and are contract now that the registrants are separate distributions.

## The public surface

Importing `wadler_lindig_parts` makes available the union of `engine.__all__`
and `generic.__all__`, plus the `examples` submodule. **32 names**, measured
(R1). There is no private-but-documented tier: a name a consumer needs is
public, and a name that is public is tested.

### From `engine` — 28

| Name | Kind | What a consumer uses it for |
|---|---|---|
| `pparts` | dispatcher | **The extension point.** `@pparts.dispatch` registers how a type decomposes. |
| `PPart` | NamedTuple | one roled fragment |
| `PGroup` | type | a named subtree, so a composite forwards axes into its parts |
| `doc_part` | function | builds a `PPart` carrying a wadler-lindig document |
| `ReprMixin` | class | `repr`/`str`/`format`/Jupyter/`__pdoc__` from one spec string |
| `Axis` | NamedTuple | the thing `register_axis` takes |
| `register_axis` | function | contribute an axis to the grammar |
| `unregister_axis` | function | remove one (tests, reloads) |
| `register_alias` | function | contribute a whole-spec shorthand |
| `unregister_alias` | function | remove one |
| `AXES` | read-only view | axis name → `Axis` |
| `ALIASES` | read-only view | alias name → spec string |
| `MARKUPS` | read-only view | markup name → row |
| `REQUIRED_MARKUP_KEYS` | tuple | `("_content", "wrap", "vsep", "escape")` |
| `markup_table` | function | the resolved row for a markup |
| `Spec` | Mapping | a parsed spec |
| `parse_spec` | function | spec string → `Spec` |
| `pspec` | function | render an object under a spec string |
| `render` | function | render an object under a parsed `Spec` |
| `parts_to_doc` | function | fragment tree → wadler-lindig document (layout, breaking, nesting) |
| `parts_to_markup` | function | the same document laid out flat — what HTML and LaTeX want |
| `pparts_to_pdoc` | function | fragment tree → a `__pdoc__`-compatible document |
| `doc_to_str` | function | lay a document out at a width |
| `FLAT` | `Final[int]` | `10**9` — the width meaning "never break" |
| `math_doc` | function | a document for LaTeX math context |
| `unwrap_math` | function | strip the `$…$` a LaTeX rendering carries |
| `inert_axes` | function | which axes a spec asked for that changed nothing — a debugging call, not a setting, because each check costs a second render |
| `bad_spec` | function | build the error a spec failure raises |

### From `generic` — 4

| Name | Kind | What a consumer uses it for |
|---|---|---|
| `pvalue` | dispatcher | render a value under the `value` axis |
| `register_markup` | function | add an output format beside `text`/`html`/`latex` |
| `unregister_markup` | function | remove one |
| `SHORT_ARRAYS` | dict | the `value` axis's three-way choice as `__pdoc__`'s `short_arrays` argument |

### Plus

`wadler_lindig_parts.examples` — the submodule holding `Version`, `Term` and
`Point`, which the documentation demonstrates on. Reachable as an attribute of
the top-level package, not only as an importable submodule.

### Surface rules

- **S1** — every name above is an attribute of `wadler_lindig_parts` after a
  bare `import wadler_lindig_parts`.
- **S2** — `wadler_lindig_parts.__all__` is exactly that set plus `"examples"`.
- **S3** — a name in a module's `__all__` but absent from the module makes the
  import **fail**, loudly. A silently shrinking public surface is the failure
  mode this rule exists to prevent.
- **S4** — a consumer never needs an underscore name. Across a distribution
  boundary an underscore name may change in a patch release.

## The four behaviours

### C1 — Keyword collisions

Keywords live in one flat namespace shared by every registering distribution.
`unxt`, `coordinax` and `galax` write into the same `_KEYWORDS` index.

**The contract**:

| | Behaviour |
|---|---|
| Two axes claim one word | **Both registrations succeed.** `_KEYWORDS[word]` holds both claimants. |
| A spec uses the word bare | **Raises**, naming every claimant and every qualified form: `ambiguous keyword 'w'; claimed by 'a', 'b'. Write it as one of: a=w, b=w` |
| A spec uses `a=w` | Resolves to axis `a`. |
| A spec uses `b=w` | Resolves to axis `b`. |

So a collision costs **one word in one spec** — `latex-mul-unit=dim-.3f` — not
a rewrite, and not a registration. A package expecting to share vocabulary can
write the qualified form from the start and never be affected.

**Where the refusal is *not***: `register_axis`. It rejects a duplicate axis
*name*, a second claim on free text, and a keyword that is already an *alias* —
but not a keyword another axis claims. That is deliberate: refusing the second
registration would leave nothing for `axis=word` to resolve to, and a shared
word would become a defeat instead of an inconvenience.

**Constitution status**: principle IV's bullets 1 and 2 misdescribe this. "The
first registration of a word wins" is false — neither wins; the bare word
becomes unusable and both qualified forms work. "`register_axis` enforces the
first two" is false — resolution does. Bullet 3 is correct and is the reason
the others give way. Amended under this feature, with the evidence stated, per
the governance section. Decided by the repository owner, 2026-11-02.

**Also still true, and not what C1 is about**: registration *does* raise on a
duplicate axis name, a duplicate alias and a duplicate markup name. The
converted how-to page's sentence "Registration raises on any collision rather
than overwriting" is too broad and must distinguish these from a keyword
claimed twice.

**Test**: both halves. Bare word raises naming both claimants; each qualified
form resolves to its own axis. No test matching `ambiguous` exists today.

### C2 — A markup row missing a required key is refused at registration

A row omitting any of `_content`, `wrap`, `vsep`, `escape` is refused when it
is registered, with an error naming the missing key, and **no registry holds a
partial entry** for it.

"At registration, not at render" is the substance. A row that passed
registration and failed at render would fail in whichever consumer happened to
format an object first, at a call site that has nothing to do with the
registration — and the registration might be in a different distribution
entirely.

**Status**: implemented and correct. `_check_markup_row` is `register_markup`'s
first statement and the missing-key branch is its first check, so it runs before
any registry is written. **No test exercises it** — the six parametrised bad
rows all supply four keys and corrupt a value.

**Test**: for each of the four keys, a row omitting it is refused, the error
names that key, and neither `MARKUPS` nor the keyword index gained an entry.

### C3 — `__repr_spec__` resolves at class creation

`ReprMixin.__init_subclass__` parses `__repr_spec__` when the class is created.
A spec naming an axis or alias that is not yet registered fails **at the
`class` statement**, not at first print. Reassigning `__repr_spec__` afterwards
is not re-parsed.

**Why this is now contract**: inside one package, "register your axes before
defining your classes" was a statement about the order of lines in
`__init__.py`. Across two installed distributions it is load order between
them: a consumer must register its axes before importing or defining the
classes whose repr specs name them.

**Obligation**: a test pins the class-creation timing, and the README states
the load-order consequence for consumers — it is the one contract here that a
consumer cannot discover from an error message alone, because the error arrives
at a `class` statement that looks unrelated.

**Partially pinned today**: `test_bad_repr_spec_fails_at_class_creation` covers
a syntactically invalid spec. What is missing is the *registration-order* case:
a spec naming a word that would be valid once an axis is registered, used
before it is.

### C4 — Exactly two runtime dependencies, enforced by parsing every module

`wadler-lindig>=0.1.8` and `plum-dispatch>=2.7.0`. Nothing else, ever.
Anything a module needs beyond those two and the standard library is a design
error in that module, not a reason to add a dependency.

**Enforcement**: a test parses every module under `src/wadler_lindig_parts/`
and asserts every import resolves to the standard library, `wadler_lindig`,
`plum`, or a sibling module of this package. A new dependency cannot be added
without deleting that test, which a reviewer sees.

**Status**: half-enforced. A test checks *relative* imports today; the test
that was to cover the rest was written against `unxt` and is vacuous here. The
inverted form is what principle I describes and what this feature delivers —
it fails on a *new* dependency rather than on a *named* one.

**Why the inversion matters**: the old test asked "does anything import
`unxt`?" The answer is permanently no, and will stay no while somebody adds
`numpy`. The new test asks "does anything import something it may not?", which
is the question.
