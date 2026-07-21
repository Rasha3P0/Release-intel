# The 5R framework, generic specification

5R is a categorical risk classification applied to every release note before
test planning. Each category is stamped yes or no; there are no weights and
no severity scores. A weighted or numeric scoring system is an anti-pattern
for this method: the value of the classification is that it forces a
protocol, not a number.

## The five categories

- **R1 Data Structure.** The change touches schema, stored data shape,
  calculations, or interpretation logic.
- **R2 Blast Radius.** The change touches high-volume processes, batch jobs,
  or critical feeds.
- **R3 Integration.** The change affects downstream consumers, interfaces,
  APIs, or reports.
- **R4 Hidden Complexity.** The release note uses innocuous-label language
  (performance, refactor, optimisation, cleanup, tech debt, minor,
  behind-the-scenes) or is three sentences or fewer. R4 is a hard gate: in
  an operational setting the note would be held until the author and a
  technical lead jointly re-score it.
- **R5 Rollback.** The change involves one-way operations, forward-only
  migrations, or anything that cannot be cleanly reversed.

## Threshold rule

- **0 stamps**: the note proceeds normally.
- **1 stamp**: that category's testing protocol is triggered.
- **2 or more stamps**: a coordination sign-off is added before planning
  begins.

## Scoring rules

For every note, each R-code is assessed with quoted evidence from the note
text and stamped yes, no, or unclear. The threshold rule is then applied,
and R4 hard-gate triggers are flagged explicitly.

An unclear stamp must name what missing information would resolve it. A
stamp is never made on speculation: no evidence in the text means unclear,
not yes.
