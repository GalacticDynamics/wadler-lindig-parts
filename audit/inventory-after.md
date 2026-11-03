# Documentation inventory — `docs`

18 pages · 6,700 words

## Mode distribution (heuristic)

| Mode | Pages |
|---|---|
| tutorial | 4 |
| how-to | 7 |
| reference | 5 |
| explanation | 2 |
| non-practitioner | 0 |

## Seams — sections that disagree with their page

**Start here.** Each row is a substantial section whose signals point at a different mode from the rest of its page. These are the EXTRACT, DRAIN and SPLIT candidates: the seams where two pieces of documentation have been fused together. Confirm each one with the compass before acting.

| Page | Page reads as | Section | Line | Words | Section reads as |
|---|---|---|--:|--:|---|
| `reference/registration-rules.md` | reference | Axes | 26 | 45 | **explanation** |
| `reference/registration-rules.md` | reference | Reserved characters | 132 | 59 | **explanation** |
| `reference/registration-rules.md` | reference | Keyword collisions | 151 | 60 | **explanation** |
| `reference/registration-rules.md` | reference | See also | 196 | 36 | **how-to** |
| `how-to/add-a-markup.md` | how-to | Register a markup row | 8 | 63 | **reference** |
| `how-to/add-an-axis.md` | how-to | Register the axis | 10 | 54 | **reference** |
| `how-to/index.md` | how-to | How-to guides | 2 | 52 | **tutorial** |
| `how-to/make-a-type-formattable.md` | how-to | Register `pparts` and inherit `ReprMixin` | 11 | 74 | **explanation** |
| `how-to/nest-formattable-values.md` | how-to | Accept `**kw` and forward it | 7 | 61 | **explanation** |
| `how-to/render-your-own-payload-type.md` | how-to | Escape for the markup | 59 | 61 | **explanation** |
| `how-to/write-a-constructor-repr.md` | how-to | Implement `__pdoc__` | 15 | 59 | **explanation** |
| `index.md` | tutorial | Where to go | 33 | 82 | **explanation** |
| `reference/api.md` | reference | Example types | 87 | 41 | **explanation** |
| `reference/axes.md` | reference | See also | 235 | 35 | **how-to** |
| `tutorials/teach-the-grammar-a-new-word.md` | tutorial | What we built | 163 | 104 | **how-to** |

## All pages, ordered by how mixed they are

`mix` is the runner-up mode's score as a fraction of the winner's — 0.80 means the page is doing two jobs almost equally. The `reads as` column is a prompt for the compass, not a verdict; it counts words and cannot know what a user needs.

| Page | Title | Words | Reads as | Runner-up | mix | In-links | Code | Steps | Tables |
|---|---|--:|---|---|--:|--:|--:|--:|--:|
| `index.md` | wadler-lindig-parts | 193 | tutorial | explanation | 1.00 ⚠️ | 0 | 3 | 0 | 0 |
| `how-to/add-a-markup.md` | How to add a markup | 177 | how-to | reference | 0.38 | 4 | 4 | 0 | 6 |
| `reference/api.md` | API | 159 | reference | explanation | 0.25 | 12 | 0 | 0 | 0 |
| `reference/axes.md` | Axes, layouts and markups | 713 | reference | how-to | 0.24 | 13 | 13 | 0 | 20 |
| `tutorials/teach-the-grammar-a-new-word.md` | Teach the grammar a new word | 475 | tutorial | how-to | 0.20 | 3 | 11 | 0 | 0 |
| `explanation/index.md` | Explanation | 90 | explanation | how-to | 0.18 | 2 | 0 | 0 | 0 |
| `reference/registration-rules.md` | Registration rules | 444 | reference | how-to | 0.17 | 9 | 11 | 0 | 9 |
| `how-to/write-a-constructor-repr.md` | How to write a constructor-form repr | 280 | how-to | explanation | 0.14 | 3 | 5 | 0 | 0 |
| `how-to/make-a-type-formattable.md` | How to make a type formattable | 310 | how-to | explanation | 0.13 | 6 | 3 | 0 | 0 |
| `tutorials/your-first-formattable-type.md` | Make your first formattable type | 490 | tutorial | explanation | 0.13 | 3 | 9 | 0 | 0 |
| `tutorials/index.md` | Tutorials | 112 | tutorial | how-to | 0.12 | 1 | 0 | 2 | 0 |
| `explanation/why-formatting-is-one-engine.md` | Why formatting is one engine | 1749 | explanation | how-to | 0.09 | 7 | 6 | 0 | 0 |
| `how-to/index.md` | How-to guides | 189 | how-to | tutorial | 0.07 | 4 | 0 | 0 | 0 |
| `reference/spec-grammar.md` | Format spec grammar | 488 | reference | explanation | 0.05 | 9 | 12 | 3 | 13 |
| `how-to/nest-formattable-values.md` | How to nest formattable values | 174 | how-to | explanation | 0.03 | 3 | 3 | 0 | 0 |
| `how-to/render-your-own-payload-type.md` | How to render your own payload type | 300 | how-to | explanation | 0.03 | 1 | 3 | 0 | 0 |
| `how-to/add-an-axis.md` | How to add an axis | 260 | how-to | reference | 0.02 | 5 | 5 | 0 | 0 |
| `reference/index.md` | Reference | 97 | reference | tutorial | 0.00 | 2 | 0 | 0 | 0 |

## Facts asserted on more than one page

Each entry below asserts the same thing — same type, same default, same description — on two or more pages, even where the key it hangs off differs (`--log-level` in a CLI reference and `log.level` in a config reference are one fact, not two). Atomic facts belong in exactly one table, with every other mention linking to it; duplicated copies drift apart and both look authoritative. Pick the canonical home and LINK from the rest. Skim for false positives — generic rows can collide harmlessly.

- `- [How to add an axis](../how-to/add-an-axis.md) · [How to add a markup](../how-to/add-a-m`
  — `reference/axes.md`:243, `reference/registration-rules.md`:204

## Full section breakdown

Apply the compass heading by heading. `⟵` marks a section that disagrees with its page.

### `index.md` — page reads as tutorial (mix 1.00)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | wadler-lindig-parts | 86 | — |
| 33 | &nbsp;&nbsp;Where to go | 82 | explanation ⟵ |
| 58 | &nbsp;&nbsp;What a spec looks like | 25 | — |

### `how-to/add-a-markup.md` — page reads as how-to (mix 0.38)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | How to add a markup | 35 | how-to |
| 8 | &nbsp;&nbsp;Register a markup row | 63 | reference ⟵ |

### `reference/api.md` — page reads as reference (mix 0.25)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | API | 54 | reference |
| 87 | &nbsp;&nbsp;Example types | 41 | explanation ⟵ |

### `reference/axes.md` — page reads as reference (mix 0.24)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | Axes, layouts and markups | 43 | — |
| 20 | &nbsp;&nbsp;Summary | 155 | reference |
| 34 | &nbsp;&nbsp;`layout` | 51 | — |
| 55 | &nbsp;&nbsp;`markup` | 27 | reference |
| 74 | &nbsp;&nbsp;`sep` | 32 | reference |
| 89 | &nbsp;&nbsp;`value` | 121 | reference |
| 137 | &nbsp;&nbsp;`width` | 55 | reference |
| 187 | &nbsp;&nbsp;Markups | 93 | reference |
| 215 | &nbsp;&nbsp;Registries | 82 | reference |
| 235 | &nbsp;&nbsp;See also | 35 | how-to ⟵ |

### `tutorials/teach-the-grammar-a-new-word.md` — page reads as tutorial (mix 0.20)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | Teach the grammar a new word | 59 | — |
| 48 | &nbsp;&nbsp;Step 2: watch the word do nothing | 73 | tutorial |
| 72 | &nbsp;&nbsp;Step 3: register the word | 77 | tutorial |
| 104 | &nbsp;&nbsp;Step 4: the part we did not write | 90 | tutorial |
| 140 | &nbsp;&nbsp;Step 5: put the registry back | 52 | tutorial |
| 163 | &nbsp;&nbsp;What we built | 104 | how-to ⟵ |

### `reference/registration-rules.md` — page reads as reference (mix 0.17)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | Registration rules | 35 | — |
| 11 | &nbsp;&nbsp;Summary | 121 | reference |
| 26 | &nbsp;&nbsp;Axes | 45 | explanation ⟵ |
| 74 | &nbsp;&nbsp;Aliases | 47 | — |
| 97 | &nbsp;&nbsp;Markup rows | 41 | reference |
| 132 | &nbsp;&nbsp;Reserved characters | 59 | explanation ⟵ |
| 151 | &nbsp;&nbsp;Keyword collisions | 60 | explanation ⟵ |
| 196 | &nbsp;&nbsp;See also | 36 | how-to ⟵ |

### `how-to/write-a-constructor-repr.md` — page reads as how-to (mix 0.14)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | How to write a constructor-form repr | 101 | how-to |
| 15 | &nbsp;&nbsp;Implement `__pdoc__` | 59 | explanation ⟵ |
| 56 | &nbsp;&nbsp;If you only want to override sometimes | 28 | — |
| 115 | &nbsp;&nbsp;Note on axes | 33 | — |
| 121 | &nbsp;&nbsp;See also | 39 | how-to |

### `how-to/make-a-type-formattable.md` — page reads as how-to (mix 0.13)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | How to make a type formattable | 45 | how-to |
| 11 | &nbsp;&nbsp;Register `pparts` and inherit `ReprMixin` | 74 | explanation ⟵ |
| 58 | &nbsp;&nbsp;Register your axes before the class statement | 66 | — |
| 68 | &nbsp;&nbsp;If your type's repr is a constructor expression | 56 | how-to |
| 93 | &nbsp;&nbsp;See also | 45 | how-to |

### `tutorials/your-first-formattable-type.md` — page reads as tutorial (mix 0.13)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | Make your first formattable type | 64 | tutorial |
| 18 | &nbsp;&nbsp;Step 1: a type that cannot print itself yet | 73 | tutorial |
| 41 | &nbsp;&nbsp;Step 2: say what it is made of | 66 | tutorial |
| 77 | &nbsp;&nbsp;Step 3: the part we did not write | 74 | tutorial |
| 102 | &nbsp;&nbsp;Step 4: why the colon was marked | 65 | tutorial |
| 118 | &nbsp;&nbsp;Step 5: look at what the engine sees | 39 | tutorial |
| 134 | &nbsp;&nbsp;What we built | 109 | tutorial |

### `tutorials/index.md` — page reads as tutorial (mix 0.12)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | Tutorials | 67 | — |
| 13 | &nbsp;&nbsp;The sequence | 45 | tutorial |

### `explanation/why-formatting-is-one-engine.md` — page reads as explanation (mix 0.09)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 1 | Why formatting is one engine | 86 | explanation |
| 14 | &nbsp;&nbsp;Why one renderer and not four | 225 | explanation |
| 46 | &nbsp;&nbsp;Why the spec grammar scans left to right | 204 | explanation |
| 76 | &nbsp;&nbsp;Why keywords share one namespace | 243 | explanation |
| 105 | &nbsp;&nbsp;Why the constructor form is not built from fragments | 294 | explanation |
| 162 | &nbsp;&nbsp;Why an inert axis is allowed to do nothing | 187 | explanation |
| 201 | &nbsp;&nbsp;Why the engine is a package of its own | 240 | explanation |
| 228 | &nbsp;&nbsp;Why the layout is not ours | 270 | explanation |

### `how-to/index.md` — page reads as how-to (mix 0.07)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | How-to guides | 52 | tutorial ⟵ |
| 12 | &nbsp;&nbsp;Making your types renderable | 59 | how-to |
| 23 | &nbsp;&nbsp;Extending the grammar | 78 | how-to |

### `reference/spec-grammar.md` — page reads as reference (mix 0.05)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | Format spec grammar | 52 | — |
| 26 | &nbsp;&nbsp;The scan rule | 138 | reference |
| 53 | &nbsp;&nbsp;&nbsp;&nbsp;Separators inside the value spec | 62 | — |
| 99 | &nbsp;&nbsp;Qualified keywords | 59 | — |
| 127 | &nbsp;&nbsp;Reserved characters | 77 | reference |
| 146 | &nbsp;&nbsp;Layout scoping | 50 | — |
| 174 | &nbsp;&nbsp;See also | 27 | — |

### `how-to/nest-formattable-values.md` — page reads as how-to (mix 0.03)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 7 | &nbsp;&nbsp;Accept `**kw` and forward it | 61 | explanation ⟵ |
| 56 | &nbsp;&nbsp;If you drop `**kw` | 37 | — |
| 62 | &nbsp;&nbsp;If a nested field is not formattable | 29 | — |
| 67 | &nbsp;&nbsp;See also | 26 | how-to |

### `how-to/render-your-own-payload-type.md` — page reads as how-to (mix 0.03)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | How to render your own payload type | 76 | how-to |
| 12 | &nbsp;&nbsp;Register a method | 33 | — |
| 47 | &nbsp;&nbsp;Honour `value_spec` | 31 | — |
| 59 | &nbsp;&nbsp;Escape for the markup | 61 | explanation ⟵ |
| 75 | &nbsp;&nbsp;If you want `short_arrays` to mean something | 40 | — |
| 82 | &nbsp;&nbsp;Accept and forward `**kw` | 27 | — |
| 88 | &nbsp;&nbsp;See also | 32 | how-to |

### `how-to/add-an-axis.md` — page reads as how-to (mix 0.02)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 2 | How to add an axis | 38 | how-to |
| 10 | &nbsp;&nbsp;Register the axis | 54 | reference ⟵ |
| 45 | &nbsp;&nbsp;Register it at import, once | 39 | — |
| 58 | &nbsp;&nbsp;If you want shorthand for a combination | 33 | — |
| 75 | &nbsp;&nbsp;If another library might want your keyword | 68 | — |
| 98 | &nbsp;&nbsp;See also | 28 | how-to |

---

Next: read the flagged pages and fill in the migration map (`assets/audit-template.md`).
