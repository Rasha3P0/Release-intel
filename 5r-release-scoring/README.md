# Workstream 1: 5R scoring on public release notes

This workstream applies the 5R categorical risk classification to GitLab's
monthly release notes, versions 19.0 to 19.2, and reports what categorical
scoring surfaces that a severity scale hides.

## The framework

The complete generic specification is in [`framework.md`](framework.md).
In short: five yes/no categories (Data Structure, Blast Radius,
Integration, Hidden Complexity, Rollback), no weights, no severity scores.
Zero stamps proceeds normally; one stamp triggers that category's testing
protocol; two or more add a coordination sign-off. R4 (Hidden Complexity)
is a hard gate on innocuous-label language and very short notes.

How the same categories apply earlier in the lifecycle, at the point where
functional specs are created from requirements, is covered in
[`../5R_SHIFT_LEFT.md`](../5R_SHIFT_LEFT.md).

## Data source

GitLab monthly release notes, versions 19.0 to 19.2, published at
<https://docs.gitlab.com/releases/>:

- 19.0: <https://docs.gitlab.com/releases/19/gitlab-19-0-released/>
- 19.1: <https://docs.gitlab.com/releases/19/gitlab-19-1-released/>
- 19.2: <https://docs.gitlab.com/releases/19/gitlab-19-2-released/>

GitLab is credited as the source. Notes are quoted for analysis under
fair-dealing review purposes, with links back to the source pages. GitLab's
own documentation licence is Creative Commons Attribution-ShareAlike 4.0:
all content under the `doc/` directory of the `gitlab-org/gitlab`
repository, which is what generates the pages at docs.gitlab.com
including the release notes, is licensed CC BY-SA 4.0. That licence
independently permits this quotation and reuse; it is cited here
alongside the fair-dealing basis rather than instead of it.
`fetch_notes.py` fetches the pages and splits them into individual
release-note items in `data/`.

Provenance of the committed corpus: the build environment for this
repository has no outbound network access, so the three public pages were
captured to PDF by the author on 21 July 2026 and split into `data/` with
`extract_pdf_notes.py` (requires pypdf). The capture PDFs themselves are
not committed; `fetch_notes.py` reproduces the same corpus from the live
pages on any normally connected machine. Text extracted from PDF carries
minor artefacts (occasional joined words at line breaks); titles and
quoted evidence were checked against the source pages' wording.

## Method

1. `fetch_notes.py` fetches the three release pages and writes one text
   file per release-note item into `data/` (or `extract_pdf_notes.py`
   does the same from PDF captures of the pages, see above).
2. `score_notes.py` scores every item against the five R-codes and writes
   `scored/scores.csv` and `scored/scores.json`.
3. Scoring is rule-assisted for R4, whose triggers are lexical by
   definition. For the judgement codes (R1, R2, R3, R5), the rules stamp
   yes only on quoted trigger language and otherwise stamp unclear, naming
   the missing information; they never stamp no, because absence of a
   keyword is not evidence of absence. LLM-assisted judgements made with
   the committed prompt in [`scoring_prompt.md`](scoring_prompt.md) can be
   merged with `--llm-scores` and may stamp no with quoted reasoning.
4. The threshold rule and the R4 hard gate are applied per note.

The scorer is validated against three synthetic fixtures in
[`tests/`](tests/), one per expected outcome, with the sample output
committed. Fixtures are not data and are never counted in findings.

## Findings

Corpus: 99 release-note items (19.0: 42, 19.1: 29, 19.2: 28), every item
scored. Full output in [`scored/scores.csv`](scored/scores.csv) and
[`scored/scores.json`](scored/scores.json); summary statistics reproduce
with `python3 analyze_findings.py scored/scores.json`. Borderline stamps
flagged during scoring were reviewed before acceptance; two were changed,
recorded in [`scored/adjudications.md`](scored/adjudications.md).

### Base rates per R-code

| Code | Yes | No | Unclear |
|------|-----|----|---------|
| R1 Data Structure | 23 (23%) | 74 (75%) | 2 (2%) |
| R2 Blast Radius | 27 (27%) | 68 (69%) | 4 (4%) |
| R3 Integration | 41 (41%) | 53 (54%) | 5 (5%) |
| R4 Hidden Complexity | 38 (38%) | 61 (62%) | 0 |
| R5 Rollback | 8 (8%) | 82 (83%) | 9 (9%) |

Integration is the most common risk surface in this corpus: two in five
notes touch an interface, API, report, or downstream consumer. Rollback
risk is rare but carries the highest unclear rate; release notes seldom
say whether a change can be reversed, and every unclear stamp names that
as the missing information.

### Threshold outcomes

23 notes (23%) proceed normally with zero stamps. 35 (35%) carry exactly
one stamp and trigger a single category protocol. 41 (41%) carry two or
more stamps and would require a coordination sign-off before test
planning. The strongest co-occurrences are R1 with R3 (17 notes) and R2
with R3 (15 notes): changes to data shape or high-volume processes
usually surface somewhere downstream, which is what makes them
coordination cases rather than single-team cases.

### The R4 hard gate

38 of 99 notes (38%) trip the hard gate: 3 on innocuous-label language
and 35 on brevity (three sentences or fewer). Per release: 19.0 48%,
19.1 28%, 19.2 36%. In an operational setting these notes would go back
to their authors for a joint re-score with a technical lead; on a public
corpus the gate reads as a measure of how often release notes give a
tester too little to plan from.

Public release notes are written in a marketing register: GitLab is
writing for customers deciding whether to upgrade, not for a tester
planning coverage, so innocuous internal labels such as "minor" or
"cleanup" are rare here, and short notes are simply house style rather
than a sign of anything being hidden. On this corpus the gate is
functioning almost entirely through its brevity arm, not its
label-detection arm. Internal change records, written by engineers
describing their own work to other engineers, are where the label
trigger is expected to carry more of the weight; testing it against
public release notes tests one arm of the gate more than the other.

### Worked examples

**A clean multi-stamp note.** "GitLab Duo Core moves to usage-based
billing" (19.0) stamps R1, R2, R3 and R5: the billing calculation model
changes, every code suggestion becomes a metered event, consuming
products change behaviour, and the note presents the transition as
unconditional with no return path. Four stamps, coordination sign-off.
A severity scale would compress this into one number; the categorical
result instead names the four separate conversations the change needs.

**The R4 gate on innocuous language.** "Redesigned repository commit
list" (19.1) scores no on R1, R2, R3 and R5, but the phrase "Improved
performance and pagination for large repositories" trips the innocuous
label trigger. The gate does not claim the change is dangerous; it
claims the note's register is the kind under which complexity hides, and
routes it to a human re-score rather than past one.

**A genuinely low-risk note.** "Emoji reactions on wiki pages" (19.1)
scores a clean no on every judgement code with evidence for each, and
R4 does not fire. Zero stamps, proceed normally. A gate that cannot say
"proceed" cheaply is a gate teams route around; most of this corpus (58
notes) needs no coordination at all.

The method note the corpus itself produced: the widest-impact change in
the three releases, a mandatory PostgreSQL major-version upgrade, arrived
as a two-sentence note. The judgement codes could not stamp R5 without
speculating beyond the text, and the method forbids that; it was the R4
brevity gate that caught it. That is the design working as intended, and
it is what categorical scoring surfaces that a severity scale hides: not
how bad the change is, but whether anyone has been given enough
information to know.

Applied to an organisation's own release notes, the same method would show
which changes carry structural risk before test planning begins.
