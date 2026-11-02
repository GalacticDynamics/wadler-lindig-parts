# Phase 1 data model

This package has no persistent storage. Its "data" is three process-wide
registries populated at import, plus the fragment tree a type reports. All of
it already exists in `engine.py` and `generic.py`; this document records the
entities and the rules this feature must test or document, not new structures.

## Registries

Three module-level dicts in `engine.py`, each exposed read-only via a
`MappingProxyType` view. The views are public (`AXES`, `ALIASES`, `MARKUPS`);
the dicts are not (`_AXES`, `_ALIASES`, `_MARKUPS`). A fourth, `_KEYWORDS`, is
an index rather than a registry and has no public view.

| Registry | Public view | Key | Value | Written by |
|---|---|---|---|---|
| `_AXES` | `AXES` | axis name | `Axis` | `register_axis` / `unregister_axis` |
| `_ALIASES` | `ALIASES` | alias name | whole spec string | `register_alias` / `unregister_alias` |
| `_MARKUPS` | `MARKUPS` | markup name | markup row | `register_markup` / `unregister_markup` |
| `_KEYWORDS` | — | keyword | `list[str]` of claiming axis names | all of the above, as a side effect |

**State at import of this package alone**, measured and asserted by T-014:

```text
AXES      6   indent layout markup sep value width
ALIASES   0
MARKUPS   3   html latex text
```

Zero aliases is the interesting one: the engine ships no shorthand. Every alias
in existence is registered by a consumer, which is why the count is 0 here and
3 inside `unxt`.

## `Axis`

A `NamedTuple`. Fields, from `engine.py`:

| Field | Meaning |
|---|---|
| `name` | the axis's own name; the key in `_AXES`, and the left side of `axis=word` |
| `keywords` | `Mapping[str, Any]` — bare word → the value it sets |
| `default` | the value the axis holds when no keyword sets it |
| `layouts` | `Mapping[str, Callable]` — which layouts honour it, and how its value becomes a renderer argument |
| `free_text` | whether this axis claims the spec's trailing free-text run |

### Validation rules enforced at registration

`register_axis` rejects, in this order, touching no registry until all pass:

1. **Duplicate axis name** — unless `replace=True`. `axis 'x' is already registered`.
2. **A second claim on free text** — `axis 'x' claims free text, but 'y' already does; a spec has only one trailing run to give`.
3. **A keyword that is already an alias** — `keyword 'w' is already an alias`. An alias is a whole spec, so it has no qualified form to fall back on.

### The rule it deliberately does *not* enforce

**A keyword already claimed by another axis is allowed.** `_KEYWORDS[word]` is
a *list*, and registration appends to it. Two axes may claim one word.

That is not an oversight; it is what makes `axis=word` work for both of them.
See the contract in [contracts/public-surface.md](./contracts/public-surface.md#c1--keyword-collisions)
and R3 in [research.md](./research.md).

### State transitions

```text
                  register_axis(ax)
    absent  ──────────────────────────────▶  registered
       ▲                                       │    │
       │      unregister_axis(name)             │    │ register_axis(ax', replace=True)
       └───────────────────────────────────────┘    └──▶ registered (replaced)
```

A **failed** `replace=True` leaves the axis it meant to replace in place —
validation completes before any registry is written. Already pinned by
`test_a_failed_replace_leaves_every_registry_untouched`.

## Markup row

A `Mapping[str, Any]` with four required keys. `REQUIRED_MARKUP_KEYS` names
them; any other key is a per-role override.

| Key | Type | Used for |
|---|---|---|
| `_content` | `str` | the template a content fragment is formatted into; consumed by `str.format` with one argument |
| `wrap` | `str` | the wrapper the whole rendering goes in; consumed by `split("{}")`, so exactly one `{}` |
| `vsep` | `str` | the separator between vertically laid-out fragments |
| `escape` | `None \| Callable` | how a content fragment is escaped, or `None` for no escaping |

Keys beyond these four are role names (`"value"`, `"unit"`, `"sep"`, …) whose
value overrides the rendering of that role.

### Validation rules enforced at registration

`_check_markup_row` runs as `register_markup`'s **first** statement, before any
other check and before any registry is written. In order:

1. **Missing required keys** — `markup row is missing required keys ['vsep']`. **Untested today** — see C2.
2. `wrap` and `_content` must be `str`.
3. `wrap` must contain exactly one `{}`.
4. `escape` must be `None` or callable.
5. `_content` must survive `.format("x")`.

Then `register_markup` itself rejects a duplicate markup name (unless
`replace=True`) and a name already taken as a keyword or alias.

## Fragment tree

What a type reports from `pparts`. A tuple of `PPart` and `PGroup`.

### `PPart`

A `NamedTuple` — one roled fragment.

| Field | Default | Meaning |
|---|---|---|
| `role` | — | what the fragment *is* (`"major"`, `"value"`, `"mul"`, …). Open vocabulary: a markup row may override a role it knows and falls back to `text` for one it does not, so a new role needs no markup change. |
| `text` | — | the plain-text rendering; doubles as the fallback for any markup with no override for this role |
| `kind` | `"content"` | `"content"` (escaped, then wrapped), `"markup"` (wrapped, not escaped), `"sep"` (not wrapped; may offer a line break) |
| `doc` | `None` | an optional wadler-lindig document, so text-mode line breaking reaches inside the fragment |

`kind` defaults to `"content"` so the failure mode is closed: a fragment
carrying real markup must say so.

### `PGroup`

A named subtree, so a composite type can nest another type's fragments and the
axes it does not handle forward down into them.

### The example types

Three, in `examples.py`, each chosen for a property the others lack. None
reaches for a consumer — principle III forbids it, since `unxt` depends on this
package.

| Type | `ReprMixin`? | `pparts`? | `__repr_spec__` | Demonstrates |
|---|---|---|---|---|
| `Version` | yes | yes | `"bare"` | roles and a `sep` fragment; `2.1` not `2 * 1` under `mul`, because the `sep` axis leaves an object's own separator alone |
| `Term` | yes | yes | `"mul"` | the `<payload> <operator> <label>` shape; a sequence coefficient, so line breaking at narrow width; the `sep` axis |
| `Point` | **no** | **no** | — | the `call` layout reconstructing a value through `wadler_lindig`'s free dataclass `__pdoc__`, with the type having told the engine nothing |

## `Spec`

A `Mapping[str, Any]` of axis name → value, produced by `parse_spec` from a
spec string. The grammar: a run of keywords, optionally ending in a Python
format spec.

### Scanning rule

Strictly left to right. Scanning stops at the first token that is not a keyword
(an alias counts, and is expanded in place); everything from there on is the
format spec, `-` and all.

This is load-bearing, not stylistic: a Python format spec may itself contain
`-`, as a sign flag in `-.2f` or a fill character in `->10.2f`. Splitting on
`-` and sorting the pieces would make `->10.2f` two meaningless tokens.

The price is one rule the reader carries: **the format spec goes last.**

### Keyword resolution

For each token:

1. **Contains `=`** → split on it. `axis=word`: look up the axis, then the
   word in that axis's keywords. Resolves regardless of how many axes claim
   the word. A Python format spec may also contain `=` (as a fill or an align
   flag), but such tokens are reached only after the scan has already stopped,
   so they fall through untouched.
2. **Claimed by exactly one axis** → that axis, that value.
3. **Claimed by two or more** → raises, naming every claimant and every
   qualified form. See C1.
4. **Claimed by none** → not a keyword; the scan stops here.

## `ReprMixin`

Supplies `__repr__`, `__str__`, `__format__`, `_repr_html_`, `_repr_latex_` and
`__pdoc__` from one spec string, `__repr_spec__`.

**`__repr_spec__` is resolved in `__init_subclass__`** — at class creation, not
at first print. So a bad spec, or an axis or alias registered too late, fails at
`class` definition. Reassigning `__repr_spec__` afterwards is not re-parsed.

Inside one package that was an implementation detail. Across two installed
distributions it is **load order**, and it is C3.

`@dataclass(repr=False)` is required: the generated `__repr__` would shadow the
mixin's, silently.
