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
fair-dealing review purposes, with links back to the source pages.
`fetch_notes.py` fetches the pages and splits them into individual
release-note items in `data/`.

## Method

1. `fetch_notes.py` fetches the three release pages and writes one text
   file per release-note item into `data/`.
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

Pending. The build environment for this repository has no outbound network
access, so the data fetch has not yet run; `data/` and `scored/` are
populated by running the two scripts from any normally connected machine:

    python3 fetch_notes.py --sample 5
    python3 score_notes.py data/ -o scored/

When the scored corpus is in, this section reports base rates per R-code
across the three releases, co-occurrence patterns, the proportion of notes
tripping the R4 hard gate, and three worked examples from the real corpus:
one clean multi-stamp note, one R4 trigger on innocuous language, and one
genuinely low-risk note.

Applied to an organisation's own release notes, the same method would show
which changes carry structural risk before test planning begins.
