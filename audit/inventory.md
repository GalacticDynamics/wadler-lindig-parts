# Documentation inventory — `docs`

4 pages · 2,912 words

## Mode distribution (heuristic)

| Mode | Pages |
|---|---|
| tutorial | 0 |
| how-to | 1 |
| reference | 2 |
| explanation | 1 |
| non-practitioner | 0 |

> **No page scores as a tutorial.** This is the most common gap in a doc set and usually means real teaching material has to be written, not moved.

## Seams — sections that disagree with their page

**Start here.** Each row is a substantial section whose signals point at a different mode from the rest of its page. These are the EXTRACT, DRAIN and SPLIT candidates: the seams where two pieces of documentation have been fused together. Confirm each one with the compass before acting.

| Page | Page reads as | Section | Line | Words | Section reads as |
|---|---|---|--:|--:|---|
| `how-to/make-a-type-formattable.md` | how-to | Pass the axes down to nested values | 69 | 83 | **explanation** |
| `how-to/make-a-type-formattable.md` | how-to | What registration refuses | 189 | 225 | **explanation** |
| `how-to/make-a-type-formattable.md` | how-to | See also | 260 | 37 | **explanation** |
| `index.md` | reference | wadler-lindig-parts | 1 | 110 | **how-to** |
| `index.md` | reference | The two layouts | 147 | 59 | **how-to** |
| `index.md` | reference | Layout is wadler-lindig's, not ours | 168 | 84 | **explanation** |
| `api.md` | reference | Example types | 82 | 32 | **explanation** |

## All pages, ordered by how mixed they are

`mix` is the runner-up mode's score as a fraction of the winner's — 0.80 means the page is doing two jobs almost equally. The `reads as` column is a prompt for the compass, not a verdict; it counts words and cannot know what a user needs.

| Page | Title | Words | Reads as | Runner-up | mix | In-links | Code | Steps | Tables |
|---|---|--:|---|---|--:|--:|--:|--:|--:|
| `index.md` | wadler-lindig-parts | 595 | reference | how-to | 0.43 | 3 | 10 | 0 | 8 |
| `api.md` | API reference | 132 | reference | explanation | 0.40 | 2 | 0 | 0 | 0 |
| `how-to/make-a-type-formattable.md` | How to make your own type formattable | 706 | how-to | explanation | 0.21 | 2 | 10 | 0 | 0 |
| `explanation/why-formatting-is-one-engine.md` | Why formatting is one engine | 1479 | explanation | how-to | 0.09 | 5 | 6 | 0 | 0 |

## Full section breakdown

Apply the compass heading by heading. `⟵` marks a section that disagrees with its page.

### `index.md` — page reads as reference (mix 0.43)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 1 | wadler-lindig-parts | 110 | how-to ⟵ |
| 45 | &nbsp;&nbsp;&nbsp;&nbsp;The scan goes left to right, and stops | 83 | reference |
| 65 | &nbsp;&nbsp;&nbsp;&nbsp;Keywords share one flat namespace | 88 | — |
| 113 | &nbsp;&nbsp;The six axes | 155 | reference |
| 147 | &nbsp;&nbsp;The two layouts | 59 | how-to ⟵ |
| 168 | &nbsp;&nbsp;Layout is wadler-lindig's, not ours | 84 | explanation ⟵ |

### `api.md` — page reads as reference (mix 0.40)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 1 | API reference | 36 | reference |
| 82 | &nbsp;&nbsp;Example types | 32 | explanation ⟵ |

### `how-to/make-a-type-formattable.md` — page reads as how-to (mix 0.21)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 1 | How to make your own type formattable | 67 | how-to |
| 11 | &nbsp;&nbsp;Register `pparts`, inherit `ReprMixin` | 185 | — |
| 69 | &nbsp;&nbsp;Pass the axes down to nested values | 83 | explanation ⟵ |
| 109 | &nbsp;&nbsp;Add a keyword of your own | 109 | how-to |
| 189 | &nbsp;&nbsp;What registration refuses | 225 | explanation ⟵ |
| 260 | &nbsp;&nbsp;See also | 37 | explanation ⟵ |

### `explanation/why-formatting-is-one-engine.md` — page reads as explanation (mix 0.09)

| Line | Heading | Words | Reads as |
|--:|---|--:|---|
| 1 | Why formatting is one engine | 86 | explanation |
| 13 | &nbsp;&nbsp;Why one renderer and not four | 225 | explanation |
| 44 | &nbsp;&nbsp;Why the spec grammar scans left to right | 204 | explanation |
| 74 | &nbsp;&nbsp;Why keywords share one namespace | 243 | explanation |
| 103 | &nbsp;&nbsp;Why the constructor form is not built from fragments | 294 | explanation |
| 160 | &nbsp;&nbsp;Why an inert axis is allowed to do nothing | 187 | explanation |
| 199 | &nbsp;&nbsp;Why the engine is a package of its own | 240 | explanation |

---

Next: read the flagged pages and fill in the migration map (`assets/audit-template.md`).
