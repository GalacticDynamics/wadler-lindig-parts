# Specification Quality Checklist: Tag-derived version

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-11-06
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
      — *Partial by design, as in feature 001.* Where the version lives is the
      requirement, not an implementation choice, so `pyproject.toml` and
      `uv.lock` are named as the two files the duplication lives in. The
      release workflow is named in FR-008 because its filename is a fixed
      external contract, which is the whole point of that requirement. The
      version-derivation tool is named only in the Context quotation of
      feature 001's own wording and in the Assumptions that identify the
      project the mechanism comes from; which tool and how it is configured
      belong to the plan.
- [x] Focused on user value and business needs
      — the value is that a release costs one action instead of three, and
      that a published version cannot disagree with its tag.
- [x] Written for non-technical stakeholders
      — *As far as the domain allows.* The two "users" are named at the top of
      the scenarios section.
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
      — none were needed. The one open choice, which milestone this lands on,
      is a label rather than a requirement and is recorded in Assumptions with
      the reasoning for `v0.2.1`.
- [x] Requirements are testable and unambiguous
      — FR-002, FR-003, FR-005 and FR-006 are each a build whose output is
      read; FR-009 and FR-010 are each a comparison against what is true
      today; FR-013 is a step run with two inputs and its exit codes read.
- [x] Success criteria are measurable
      — four of the six are counts that fall to zero or one; SC-005 is the
      existing gate set; SC-006 is an exit code.
- [x] Success criteria are technology-agnostic (no implementation details)
      — SC-001 to SC-004 count files, steps and strings. SC-005 names the
      gates by role rather than by command. SC-006 names an outcome, a release
      that publishes nothing, rather than the check that produces it.
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
      — seven, including the one already in the record, and it was measured
      rather than assumed: `v0.2.0` was force-updated once and the queued
      re-run went green on all three jobs while publishing nothing. An earlier
      version of this spec said that run failed at the upload step. It did
      not, and correcting it is what added FR-013.
- [x] Scope is clearly bounded
      — nothing is tagged, published or merged; no index-side setting is
      touched; no GitHub Release is created; no name is added to the public
      surface. FR-008, FR-010 and three Assumptions each hold one edge of the
      boundary. FR-013 is the one addition to scope, and the Notes below say
      why it was added after the spec was first written.
- [x] Dependencies and assumptions identified
      — six assumptions. Two of them exist because the request asked for them
      explicitly: which project the mechanism comes from, and every way this
      repository differs from it.

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
      — the release itself (P1), the mismatch that can no longer happen (P2),
      and every build that is not a release (P3).
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification
      — with the exception annotated under Content Quality, which is the same
      exception feature 001 recorded.

## Notes

- Feature 001 recorded the static version three times as a deliberate
  deviation: in `plan.md`'s Complexity Tracking, in `research.md`, and in the
  `tasks.md` entry that created `pyproject.toml` ("no `hatch-vcs` — the
  version is static"). FR-012 leaves all three as they are: they record a
  decision made under a constraint that has since expired, and this
  specification is where the lifting is written down. Ready for
  `/speckit-plan`.
- **Amended after the first draft.** This spec originally said that a moved
  tag produces a failed release run, and listed "change nothing" as the
  design's answer. Run `42186814040` was then read: it went green on all three
  jobs, PyPI's upload timestamps did not move, and the attestation digests
  matched the files already published, because both runs built the same commit.
  A release that reports success and publishes nothing is the outcome worth
  acting on, so FR-013, SC-006, a fourth acceptance scenario on User Story 1
  and Phase 4b of the task list were added. The evidence for the change is in
  research.md R9, including what it does not cover: a tag moved to a
  *different* commit, which that run never reached.
