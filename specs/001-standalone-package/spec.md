# Feature Specification: Standalone package

**Feature Branch**: `claude/adoring-cannon-e140c6`

**Created**: 2026-11-02

**Status**: Draft

**Input**: User description: "Stand up wadler-lindig-parts as an installable, tested, documented standalone package: packaging (pyproject, `__init__` re-exporting the full public surface), a zensical-native docs site modelled on quax main, Sybil wiring so every example is a test, adjustment of the three tests left behind by the extraction from unxt, and tests pinning three behaviours that became cross-distribution contract. No PyPI publish, no release tag."

## User Scenarios & Testing *(mandatory)*

The "users" of this feature are three distinct parties, and most requirements
serve exactly one of them:

- **The consumer** — a library author (`unxt`, `coordinax`, `galax`) who
  installs this package and registers axes into it.
- **The maintainer** — whoever next changes this repository and relies on the
  suite and the lint gate to tell them whether they broke something.
- **The reader** — somebody deciding whether this package solves their problem,
  who arrives at the documentation site knowing nothing.

### User Story 1 - The consumer can install the package and reach every public name (Priority: P1)

A consumer adds `wadler-lindig-parts` to their dependencies, imports it, and
finds the whole documented surface at the top level. They never need to know
which of the three modules a name lives in, and they never reach for an
underscore name, because across a distribution boundary an underscore name can
change in a patch release.

**Why this priority**: Nothing else in this feature is reachable without it.
The modules exist but there is no `__init__.py`, no `pyproject.toml`, and no
build backend — the package cannot be installed, and therefore cannot be
imported, tested, or documented. Every other story depends on this one.

**Independent Test**: Install the package into a fresh environment, import it,
and compare `dir()` against the union of the two modules' `__all__`. Delivers
a usable library even with no new tests and no documentation site.

**Acceptance Scenarios**:

1. **Given** a clean checkout, **When** the package is installed, **Then** the
   install succeeds on Python 3.10 and on the newest supported interpreter.
2. **Given** the installed package, **When** `import wadler_lindig_parts` runs,
   **Then** every name in `engine.__all__` and `generic.__all__` is an
   attribute of the top-level package, and the `examples` submodule is
   reachable as an attribute of it.
3. **Given** the installed package, **When** a consumer imports a name the
   package does not document, **Then** that name is absent from the top-level
   namespace — the public surface and the documented surface are the same set.
4. **Given** the installed package, **When** its runtime dependency metadata is
   read, **Then** it declares exactly two runtime dependencies and no others.

---

### User Story 2 - The suite passes with no consumer installed (Priority: P2)

A maintainer runs the suite. It passes, on the floor interpreter as well as on
the newest, in an environment where no consumer of this package is installed.
Nothing in the suite assumes `unxt` is importable, reads a file `unxt` owns, or
escapes into a subprocess to dodge a registry a consumer populated.

**Why this priority**: Three tests were written while these modules lived
inside `unxt` and are now either broken or vacuous (measured below). A suite
that cannot run is worse than no suite, because it hides the gap. This story is
what makes constitution principles I, IV and V checkable commands rather than
claims.

**Independent Test**: In an environment with this package installed and no
consumer, confirm `import unxt` fails, then run the suite and see it green —
on the floor interpreter and on the default one.

**Acceptance Scenarios**:

1. **Given** an environment with no consumer installed, **When** the suite
   runs, **Then** it passes with no skips attributable to a missing consumer.
2. **Given** that same environment, **When** `import unxt` is attempted,
   **Then** it fails — proving the previous scenario was not passing by
   accident.
3. **Given** the suite, **When** the test that counts registered axes runs,
   **Then** it reads this package's own registry directly rather than copying
   modules into a temporary package and importing them in a subprocess, and
   asserts six axes, zero aliases, and three markups.
4. **Given** the suite, **When** the test guarding the import discipline runs,
   **Then** it asserts of every module in `src/wadler_lindig_parts/` that each
   import resolves to the standard library, `wadler_lindig`, `plum`, or a
   sibling module of this package — the inverted form of the discipline, so it
   fails on a *new* dependency rather than on a *named* one.
5. **Given** the suite, **When** it runs on the floor interpreter, **Then** it
   passes there too — which is what turns the declared floor into a fact rather
   than a syntax check.
6. **Given** the suite, **When** it is collected, **Then** every example in a
   module docstring is collected as a test and runs.

---

### User Story 3 - Three behaviours that became contract are pinned by tests (Priority: P3)

A consumer relies on three behaviours that were implementation detail inside
`unxt` and are now contract between separate distributions. Each is asserted by
a test, and each test was observed failing before the behaviour was relied on.

**Why this priority**: Constitution principle IV says collisions are loud and
principle V says a rendering claim is pinned by a test that was watched fail.
These three are the places where the extraction changed the *kind* of thing a
behaviour is, without changing the code — so the tests are missing precisely
where they now matter most.

**Independent Test**: Delete the behaviour from the engine and watch exactly
one new test fail for each. Delivers value independently: the tests are
meaningful whether or not the documentation site exists.

**Acceptance Scenarios**:

1. **Given** two axes both claiming one keyword, **When** a spec containing
   that keyword bare is parsed, **Then** it raises an error naming **both**
   claiming axes and both qualified forms that disambiguate — and **When** the
   same keyword is written qualified as `axis=word`, **Then** each form
   resolves to its own axis, so the collision costs one word in one spec rather
   than a registration. Registration itself stays permissive; see Resolved
   Questions.
2. **Given** a markup row that omits one of the four required keys, **When** it
   is registered, **Then** registration is refused and the error names the
   missing key — the refusal happens at registration, not later at render.
3. **Given** a markup row that omits a required key, **When** registration is
   refused, **Then** no registry holds a partial entry for it.
4. **Given** a consumer whose classes name an axis in their repr spec,
   **When** such a class is defined before that axis is registered, **Then**
   class creation fails — and the README states this, because it is now load
   order between two installed distributions rather than within one package.

---

### User Story 4 - The reader finds documentation whose every example runs (Priority: P4)

A reader arrives at the documentation site, learns the grammar from the landing
page, follows a how-to to make their own type formattable, reads an explanation
of why formatting is one engine, and consults an API reference. Every example
they copy works, because every example is executed by the suite.

**Why this priority**: Constitution principle III makes examples tests. The
package's argument for existing is almost entirely made in its documentation,
and an example that cannot run is a broken test. But the package is usable
without the site, so this ranks below a passing suite.

**Independent Test**: Build the site and read it; separately, run the suite and
confirm the Markdown examples are collected as tests. Either half is valuable
alone.

**Acceptance Scenarios**:

1. **Given** the documentation sources, **When** the site is built in strict
   mode, **Then** the build succeeds with no warnings.
2. **Given** the documentation sources, **When** the suite runs, **Then** every
   fenced Python example in every Markdown page is collected as a test and
   passes.
3. **Given** the two guides converted from the consumer's documentation,
   **When** a reader reads them, **Then** they argue over this package's own
   example types rather than over the consumer's quantities, and contain no
   cross-reference syntax or directive syntax belonging to the consumer's
   documentation toolchain.
4. **Given** the built site, **When** a reader looks for the public API,
   **Then** they find a reference page covering the public surface.
5. **Given** a plugin named in the site configuration, **When** its effect is
   claimed, **Then** that claim is verified by inspecting the built site —
   never inferred from the plugin being named, because the toolchain ignores
   plugins of the previous generation silently.

---

### User Story 5 - Automation enforces the gates on every change (Priority: P5)

A maintainer opens a pull request. Automation runs the lint gate, the suite on
every supported interpreter including the floor, and the documentation build.
A release path exists but is not exercised.

**Why this priority**: The constitution names these as the gates. They are last
because a human can run every one of them by hand today; automation makes them
unforgettable rather than possible.

**Independent Test**: Open a pull request and watch the checks run.

**Acceptance Scenarios**:

1. **Given** a pull request, **When** automation runs, **Then** the lint gate,
   the suite on each supported interpreter, and the documentation build all run
   and report.
2. **Given** the supported interpreter range, **When** the suite matrix runs,
   **Then** the floor interpreter is one of the jobs.
3. **Given** the repository, **When** a maintainer runs the lint gate locally
   over every file, **Then** it reports clean.
4. **Given** this feature's delivery, **When** it completes, **Then** nothing
   has been published to any package index and no release tag has been created.

---

### Edge Cases

- **A keyword claimed twice.** Covered by Story 3 scenario 1; the open question
  is whether the refusal lands at registration or at use.
- **A markup row missing a required key.** Refused at registration (Story 3).
- **An axis registered after the classes that name it.** Fails at class
  creation, which is now cross-distribution load order (Story 3).
- **A name in `__all__` that does not exist in its module.** The re-export must
  fail loudly at import rather than silently omitting the name, otherwise the
  public surface quietly shrinks.
- **A documentation example that renders as though the type were unregistered.**
  One fragment where three are expected; under HTML markup, the whole string in
  a single wrapper; a separator the `sep` axis cannot override. This signature
  was seen in the consumer's repository while re-grounding these same doctests,
  was never root-caused, and was designed around there rather than fixed. This
  package's documentation is almost entirely examples over registered types, so
  the workaround used there is not available here. If the signature appears, it
  must be investigated and reported, not papered over.
- **A plugin that silently does nothing.** The documentation toolchain ignores
  plugins written for its predecessor without warning. Any plugin's effect is
  verified in the built output.

## Requirements *(mandatory)*

### Functional Requirements

**Packaging and public surface**

- **FR-001**: The package MUST be installable from the repository with a
  standard build, declaring the distribution name `wadler-lindig-parts`, the
  import name `wadler_lindig_parts`, version `0.1.0`, and an interpreter floor
  of 3.10.
- **FR-002**: The package MUST declare exactly two runtime dependencies:
  `wadler-lindig>=0.1.8` and `plum-dispatch>=2.7.0`. No third runtime
  dependency may be added without the reviewer knowingly deleting the test that
  forbids it (constitution principle I).
- **FR-003**: Importing the top-level package MUST make available every name in
  `engine.__all__` and in `generic.__all__`, plus the `examples` submodule.
  Measured: 28 names from `engine` and 4 from `generic`, 32 in total. See
  Assumptions for the discrepancy with the figure given in the request.
- **FR-004**: The top-level package's own `__all__` MUST be exactly that union
  plus `examples`, so the public surface and the documented surface are one set
  — there is no private-but-documented tier.
- **FR-005**: A name listed in a module's `__all__` but absent from that module
  MUST cause the import to fail, not be silently dropped.
- **FR-006**: The project's conventions — build backend, lint configuration,
  type-check configuration, dependency groups, metadata layout — MUST follow
  those of the sibling project named in the request, adapted where this package
  genuinely differs (no array library, no notebooks, a lower interpreter floor,
  a static version rather than one derived from tags).

**The suite, standalone**

- **FR-007**: The test that counts the engine's registered axes MUST read this
  package's registry directly and assert six axes (`layout`, `markup`, `sep`,
  `value`, `width`, `indent`), zero aliases, and three markups (`text`, `html`,
  `latex`). The subprocess-and-temporary-package machinery MUST be removed: it
  existed only to escape a consumer's eagerly registered axes, and there is no
  consumer here.
- **FR-008**: The test that checked for the consumer's imports MUST be replaced
  by its inverse: parse every module under `src/wadler_lindig_parts/` and
  assert that every import resolves to the standard library, `wadler_lindig`,
  `plum`, or a sibling module of this package. The replaced form was vacuous
  once the consumer was gone; the inverted form fails on a *new* dependency,
  which is the discipline constitution principle I actually names.
- **FR-009**: The test that read a file belonging to the consumer's layer in
  order to check that the layer reached the engine through public names only
  MUST be removed. Measured: that file does not exist in this repository, so
  the test raises on collection. The property it guarded now lives on the other
  side of a distribution boundary and cannot be checked from here; the pull
  request MUST say so rather than leave a test that passes by doing nothing.
- **FR-010**: The suite MUST collect and run every example in every module
  docstring under `src/`, and every fenced Python example in every Markdown
  page, using the plain-Markdown example parser rather than the directive-aware
  one the consumer uses — the pages here carry plain fences.
- **FR-011**: The suite MUST pass on the floor interpreter and on the default
  interpreter, in an environment where no consumer of this package is
  installed.

**Contracts that crossed the distribution boundary**

- **FR-012**: A keyword claimed by two axes MUST be refused when a spec uses it
  bare, with an error naming both claimants and both qualified forms, while
  each qualified form MUST still resolve to its own axis. A test MUST pin both
  halves. Registration MUST remain permissive — refusing the second
  registration would make the qualified form unreachable (Resolved Question 1).
- **FR-012a**: Constitution principle IV's first two bullets MUST be amended to
  say where the refusal lands and to drop the claim that the first registration
  wins, since neither wins: the bare word becomes unusable and both qualified
  forms work. The amendment MUST state what evidence changed, per the
  constitution's governance section.
- **FR-012b**: The converted how-to page MUST NOT repeat the sentence
  "Registration raises on any collision rather than overwriting", which is
  false of a keyword collision between axes. It remains true of a duplicate
  axis name, a duplicate alias and a duplicate markup name, so the corrected
  sentence MUST distinguish the two.
- **FR-013**: A markup row omitting any required key (`_content`, `wrap`,
  `vsep`, `escape`) MUST be refused at registration with an error naming the
  missing key, leaving no partial entry in any registry, and that behaviour
  MUST be pinned by a test. Measured: the refusal is already implemented and
  already correct; no test exercises a *missing* key, only malformed values for
  keys that are present.
- **FR-014**: The resolution of a class's repr spec at class creation MUST be
  pinned by a test, and the README MUST state the consequence: a consumer
  registers its axes before defining classes whose repr specs name them. That
  is now load order between two installed distributions.

**Documentation**

- **FR-015**: The documentation site MUST be configured for the current
  generation of the toolchain, in its own configuration file, with no
  configuration file belonging to the previous generation present.
- **FR-016**: The documentation dependency group MUST contain exactly the
  packages the sibling project uses, minus the notebook converter — this
  package has no notebooks — and MUST NOT contain the plugin the sibling
  project removed, which the toolchain was silently ignoring.
- **FR-017**: The site MUST provide at minimum: a landing page explaining the
  spec grammar, an API reference page, an explanation page on why formatting is
  one engine, and a how-to page on making a type formattable.
- **FR-018**: The two converted guides MUST be rewritten to argue over this
  package's own example types (`Term`, `Version`, `Point`) rather than over the
  consumer's quantities. This is a rewrite: the guides' arguments currently run
  through units and quantities, which this package does not have. Measured
  mechanical conversions required alongside the rewrite: 6 cross-reference
  roles become ordinary links, and 8 directive-style code blocks become plain
  fences.
- **FR-019**: The site MUST build in strict mode with no warnings.
- **FR-020**: Any claim about a documentation plugin's effect MUST be verified
  by inspecting the built site, never inferred from the plugin appearing in the
  configuration.

**Automation**

- **FR-021**: Automation MUST run, on every pull request: the lint gate, the
  suite on each supported interpreter from the floor upward, and the
  documentation build.
- **FR-022**: The lint gate MUST be the hook runner over all files, not the
  linter alone — the formatter and the other hooks catch what the linter does
  not.
- **FR-023**: A release path MUST exist in the repository but MUST NOT be
  exercised: nothing is published to any package index and no release tag is
  created by this work. Configuring trusted publishing is the repository
  owner's separate step.

### Key Entities

- **Public surface**: the union of the two modules' `__all__` plus the
  `examples` submodule — 32 names and one submodule, measured. The one set that
  is simultaneously what is exported, what is documented, and what is tested.
- **Axis**: a named dimension of the format-spec grammar, contributed by
  registration. Keywords live in one flat namespace shared across every
  registering distribution.
- **Markup row**: a table of four required keys describing how one output
  format wraps and escapes fragments.
- **Example**: a fenced Python block in a Markdown page, or a prompt-style
  example in a docstring. Simultaneously documentation and a test.
- **Example type**: `Version`, `Term`, `Point` — the types the documentation
  demonstrates on, each chosen for a property the others lack, and none of them
  reaching for a consumer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A consumer can install the package and reach all 32 public names
  plus the `examples` submodule from the top-level import, in one step, with no
  underscore imports.
- **SC-002**: The suite passes on the floor interpreter and on the default
  interpreter with zero failures and zero errors, in an environment where
  importing any consumer of this package fails.
- **SC-003**: Every example in the package — docstrings and Markdown pages
  alike — is collected as a test, and all of them pass. Zero examples are
  excluded from collection.
- **SC-004**: The documentation site builds in strict mode with zero warnings.
- **SC-005**: The lint gate reports clean over every file in the repository.
- **SC-006**: Each of the three contract behaviours fails exactly one new test
  when the behaviour is removed — demonstrated by watching each test fail
  before its behaviour is relied upon.
- **SC-007**: The package's declared runtime dependency count is exactly two,
  and a test proves no module imports anything outside that set plus the
  standard library.
- **SC-008**: Nothing has been published to any package index, and the
  repository carries no new release tag.
- **SC-009**: If the unresolved rendering fault described in the Edge Cases
  appears in any example, it is reported with what was found — its presence or
  its absence is stated explicitly rather than left unmentioned.

## Resolved Questions

### Resolved Question 1: where a keyword collision is refused

**Answer: option A, chosen 2026-11-02.** Registration stays permissive; the
parse-time error is the contract. Principle IV's first two bullets are amended
(FR-012a) and the how-to page's sentence is corrected (FR-012b).

**Context**: Constitution principle IV states three rules as contract: "The
first registration of a word wins"; "A second claim on the same word raises,
and the error names both claimants"; and "`axis=word` always resolves
explicitly, so two libraries wanting one word is an inconvenience rather than a
defeat." It then says `register_axis` enforces the first two.

**Measured behaviour**: `register_axis` does *not* refuse a keyword another
axis already claims. It appends the new axis to a list of claimants for that
word. The refusal happens later, when a spec containing the bare word is
parsed: the error reads `ambiguous keyword 'x'; claimed by 'a', 'b'. Write it
as one of: a=x, b=x` — which does name both claimants, and does offer the
disambiguating form. First registration does not "win"; neither wins, and the
bare word becomes unusable while the qualified forms both work.

**Why this matters**: the request asks for registration-time refusal, extending
the error to name both claimants if it names only the incoming one. But
registration-time refusal would make the third bullet of principle IV
unreachable: if the second registration is rejected, there is no second axis for
`axis=word` to resolve to, and a word collision becomes a defeat rather than an
inconvenience. The explanation page being converted for this package's docs
already describes the measured behaviour correctly — "A bare word resolves while
exactly one axis claims it; when two do, it raises and names both ways to
disambiguate" — while the how-to page being converted describes the other
— "Registration raises on any collision rather than overwriting."

So three documents disagree, and the constitution's governance section says
that when a principle and the code disagree, the pull request must say which is
the bug rather than quietly changing both.

**Suggested answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | Pin the measured behaviour. Keep registration permissive; the collision is refused at parse, naming both claimants and both qualified forms. Amend principle IV's first two bullets to say where the refusal lands, and correct the how-to page's sentence. | Keeps `axis=word` disambiguation working, so a shared word stays an inconvenience. No engine change; one test added, the constitution and one doc page corrected. Costs: a collision is silent until somebody writes a spec using the bare word. |
| B | Make `register_axis` refuse the second claim, naming both claimants. | Matches the request and the how-to page literally, and makes the collision loud at import. Costs: contradicts principle IV's third bullet — the loser is never registered, so `axis=word` cannot resolve it, and a shared word becomes a defeat. Breaks a consumer that registers an axis sharing a word with another consumer, at import, with no recourse but renaming. |
| C | Both: refuse at registration unless the caller opts in to sharing, and keep the parse-time ambiguity error for those who do. | Loud by default, with the escape hatch principle IV's third bullet promises. Costs: a new parameter on the registration call, which is public API surface added for a collision that has not happened yet. |

**Why A**: The third bullet of principle IV is the substantive
design commitment — it is what the explanation page spends a section arguing for
— and options B and C either break it or buy it back with new API. A also means
the engine is already correct and only the claims about it need fixing, which is
what the governance section's "say which is the bug" is for.

## Assumptions

- **The public-surface count.** The request states 29 names. Measured from the
  two modules' `__all__` tuples: 28 from `engine`, 4 from `generic`, 32 in
  total. The spec uses 32. The requirement is "the union of the two `__all__`
  tuples", so the count follows the code rather than the other way round; if
  the intent was that some names should not be public, that is a separate
  change to a module's `__all__`.
- **A third test needs attention, not two.** The request names two tests left
  behind by the extraction. Measured: a third,
  `test_the_package_side_exposes_no_privates_across_the_seam`, reads a file
  belonging to the consumer's layer that does not exist in this repository, so
  it raises on collection. FR-009 removes it and the pull request says why.
- **The sibling project's merged state is read from its default branch, not
  from the local checkout.** The local checkout of that project sits on a
  feature branch predating the migration and still carries the old
  configuration file and the removed plugin. Everything cited about it here was
  read from its default branch.
- **The sibling project also dropped the static type checker from its lint
  dependency group**, moving type checking into the hook runner. This package
  follows that, since the request says to model conventions on it.
- **Version is static, not derived from tags.** The request fixes it at
  `0.1.0`. The sibling project derives its version from git tags, which cannot
  work here — there are no tags, and the request forbids creating one.
- **Strict-mode documentation builds.** The sibling project's automation builds
  the docs with a clean rebuild but not in strict mode. The request requires
  strict mode, so this package is stricter than its model. If the toolchain
  offers no strict flag, the equivalent is a build whose output contains no
  warnings, and the pull request says which was used.
- **No notebooks.** The sibling project's documentation group carries a notebook
  converter and its automation runs a conversion step. This package has no
  notebooks, so both are omitted.
- **The interpreter range** is 3.10 through 3.15, per the constitution
  (amended once 3.15.0 final was released and the suite was run on it).
- **The unresolved rendering fault may not appear at all.** It was never
  root-caused in the consumer's repository, and nothing establishes it will
  reproduce here. The requirement is to investigate and report if the signature
  appears, and to state its absence if it does not — not to find the cause
  before this feature can land.
