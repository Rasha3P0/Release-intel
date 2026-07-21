# 5R shifted left: scoring at the functional-spec stage

Companion note to `BUILD_BRIEF.md`. The brief defines 5R
as a categorical gate applied to release notes before test planning. This note
records how the same five categories shift left to the point where functional
specs are created from requirements. The framework itself does not change:
yes/no per category, no weights, no severity scores. What changes is when the
questions are asked and what a stamp obliges the spec to contain.

## The principle

At release-note time a stamp is a discovery: the change already exists and the
gate can only react to it. At spec time a stamp is an authoring instruction:
the requirement has not yet been turned into a functional spec, so the stamp
dictates what the spec must state before it is baselined. Shifting left turns
5R from a filter on finished work into a completeness contract on unstarted
work.

An unclear stamp at release time is almost always a specification gap that was
cheap to close months earlier. Scoring at requirements intake converts each
"unclear" into a named question for the requirement owner while the answer
costs a conversation, not a hotfix.

## What each R-code obliges a functional spec to contain

Score every requirement as it is taken into specification. A yes stamp does
not block the spec; it defines what the spec must include to be complete.

- **R1 Data Structure.** If the requirement changes stored data shape,
  calculations, or interpretation logic, the spec must state the data contract
  explicitly: before and after shape, the calculation rule, and what happens
  to existing records. A spec that stamps R1 without a data contract section
  is incomplete by definition.
- **R2 Blast Radius.** If the requirement touches high-volume processes,
  batch jobs, or critical feeds, the spec must name them and state the
  expected volume characteristics. "The nightly run" is not a named process;
  the spec identifies which run, at what volume, in which window.
- **R3 Integration.** If the requirement affects downstream consumers,
  interfaces, APIs, or reports, the spec must enumerate the consumers and
  state whether each interface contract changes. Consumers discovered at test
  planning are consumers the spec missed.
- **R4 Hidden Complexity.** Shifted left, R4 becomes an intake gate on the
  requirement itself. A requirement written in innocuous-label language
  (performance, refactor, optimisation, cleanup, tech debt, minor,
  behind-the-scenes) or expressed in three sentences or fewer is not ready to
  become a functional spec. It is held until the requirement author and a
  technical lead jointly re-score it. This is where R4 belongs most
  naturally: the innocuous label originates in the requirement's wording, and
  the release note that trips R4 months later usually inherited the label
  rather than invented it. Catching it at intake removes the downstream trip.
- **R5 Rollback.** If the requirement involves one-way operations or
  forward-only migrations, reversibility is written into the spec as a
  functional requirement, not left as an operational afterthought. The spec
  states either how the change is cleanly reversed or why it cannot be, and
  in the latter case what the forward-fix path is.

## The threshold rule, shifted

Same rule, earlier anchor point:

- **0 stamps**: the spec proceeds normally.
- **1 stamp**: the spec must contain that category's named artefacts (the
  obligations above) before it is baselined.
- **2 or more stamps**: coordination sign-off happens before the spec is
  baselined, instead of before test planning begins. The people who would
  have been coordinating at release time review the spec while the design is
  still cheap to change.

## What this buys downstream

Release-time 5R scoring does not disappear; it changes character. The spec
declares its stamps, and the release-note scoring becomes a verification pass:
does the built change still match the risk profile the spec declared. Two
signals fall out of the comparison:

- A release note that scores a stamp the spec did not declare is evidence of
  scope drift, surfaced categorically rather than by accident.
- A spec stamp that the release note no longer trips is evidence the risk was
  designed out, which is the outcome the protocol exists to encourage.

## What this deliberately does not do

It does not introduce weights, scores, or severity, at either end. It does not
replace release-time scoring with spec-time scoring; the two anchor points
check different things (what was intended, what was built). It does not claim
that spec-time scoring catches everything: risks introduced during build that
the spec never contemplated are exactly what the release-time gate remains
for.
