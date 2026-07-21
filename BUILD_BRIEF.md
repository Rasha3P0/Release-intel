# Release Intelligence — build brief

You are building a public GitHub repository called `release-intelligence`. It demonstrates predictive release governance and incident intelligence methods on fully public data. The author directs; you build. Treat this brief as the specification and decision log.

## Hard constraints — read before anything else

1. **Public data only.** Every dataset must be publicly available and cited with a URL. Never ask for, accept, or reference the author's employer data, internal documents, incident records, or release notes. If the author pastes anything that looks like internal work data, stop and flag it instead of using it.
2. **Clean-room framework.** The 5R specification in this brief is the complete and only source. Do not ask for internal calibration data, internal wording, or company examples.
3. **Tense-correct claims.** This repo demonstrates a method on public data. Never claim production results, accuracy percentages, or enterprise adoption. Banned phrases: "100% accurate", "battle-tested", "production-proven", "revolutionary", any branded product-noun naming of scripts.
4. **Voice.** British English. No em dashes. No exclamation marks. No motivational or marketing language. Plain declarative sentences; design-contract register (state what the method does and what it deliberately does not do).
5. **Licence and attribution.** MIT licence. Every data source credited in the README with a link.
6. **Pre-publish verification.** Before final commit: grep the entire repo for any employer name, colleague name, internal system name, or internal URL. Confirm every script runs headless from a clean clone. Confirm all dataset links resolve.

## Repo shape

```
release-intelligence/
  README.md                  # index + provenance, see README rules below
  LICENSE
  5r-release-scoring/
    README.md                # the framework spec + method + findings
    framework.md             # generic 5R specification (from this brief)
    data/                    # fetched public release notes (markdown/text)
    scored/                  # per-note scoring output (CSV + JSON)
    score_notes.py           # the scorer
  incident-intelligence/
    README.md                # method + findings
    crowdstrike-5r-retro/    # case study: sources, scored analysis
    aiid-topic-model/        # data fetch script, analysis, charts
    findings/                # summary + charts
```

## Workstream 1 — 5R scoring on public release notes

**Source.** GitLab monthly release notes, versions 19.0 to 19.2, from https://docs.gitlab.com/releases/. Fetch the pages, split into individual release-note items, store as structured text in `data/`. Cite GitLab as the source; the notes are quoted for analysis under fair-dealing review purposes with links back.

**The framework (complete generic specification — build from this, nothing else):**

5R is a categorical risk classification applied to every release note before test planning. Yes/no per category; no weights, no severity scores. Proposing a weighted or numeric scoring system is an anti-pattern; if the analysis tempts you toward weights, reframe as protocol refinement.

- **R1 Data Structure** — the change touches schema, stored data shape, calculations, or interpretation logic.
- **R2 Blast Radius** — the change touches high-volume processes, batch jobs, or critical feeds.
- **R3 Integration** — the change affects downstream consumers, interfaces, APIs, or reports.
- **R4 Hidden Complexity** — the release note uses innocuous-label language (performance, refactor, optimisation, cleanup, tech debt, minor, behind-the-scenes) or is three sentences or fewer. R4 is a hard gate: in an operational setting the note would be held until the author and a technical lead jointly re-score it.
- **R5 Rollback** — the change involves one-way operations, forward-only migrations, or anything that cannot be cleanly reversed.

Threshold rule: 0 stamps proceeds normally; 1 stamp triggers that category's testing protocol; 2 or more stamps adds a coordination sign-off before planning begins.

**Scoring method.** For every note: assess each R-code with quoted evidence from the note text, stamp yes / no / unclear, apply the threshold rule, and flag R4 hard-gate triggers explicitly. Unclear stamps must name what missing information would resolve them; never stamp on speculation.

**Build.** `score_notes.py` takes a directory of release-note text files and produces the scored CSV/JSON. Rule-assisted scoring is acceptable for R4's lexical triggers; LLM-assisted scoring is acceptable for the judgement codes if the prompt used is committed to the repo so the method is reproducible.

**Findings section of the README.** Base rates per R-code across the three releases, co-occurrence patterns (which codes co-fire), the proportion of notes tripping the R4 hard gate, and three worked examples: one clean multi-stamp note, one R4 trigger on innocuous language, one genuinely low-risk note. Present as: this is what categorical scoring surfaces that a severity scale hides.

## Workstream 2 — incident intelligence on public data

Two public sources, two analyses. Both fully public; do not substitute employer data under any circumstances.

**2a. 5R retrospective — the CrowdStrike Falcon outage, 19 July 2024.**
Source: CrowdStrike's own published Preliminary Post Incident Review and Root Cause Analysis (public documents on crowdstrike.com), plus dated primary reporting for impact figures only. Verify the documents are still accessible; cache citations with URLs; quote sparingly.
Method: run the 5R specification from Workstream 1 retrospectively over the change as CrowdStrike's RCA describes it. Score each R-code with evidence quoted from the RCA, apply the threshold rule, and show explicitly which gates would have fired pre-release — the R4 hard gate on a routine content-update label is the centrepiece. Close with what the RCA's own remediation list (staged deployment, canary rings, validation) shares with the protocol overlays a categorical gate triggers.
Register rule: neutral and clinical. The analysis works from CrowdStrike's published account only, credits them for publishing it, and draws no conclusions about individuals or culture. This incident is the industry's shared case study, not a target.

**2b. Topic and tone modelling — AI Incident Database.**
Source: the AI Incident Database (incidentdatabase.ai) public snapshot download.
Data rules: use AIID's own editorial fields (incident titles, descriptions, taxonomies) and report metadata. Do not republish full third-party article text — the underlying news reports are copyrighted. Credit AIID per their citation guidance.
Analysis: topic modelling across incident descriptions (recurring failure classes), tone and urgency signals in the narratives, and a governance lens that ties the corpus back to Workstream 1: classify a sample of incidents by whether the failure mode maps to a 5R category — would a categorical pre-release gate plausibly have flagged it — reporting honest proportions including not-mappable. Small or null findings stay in.

**Findings.** One README per workstream half: method, dataset, what was found, and one conditional closing sentence on what the method would enable applied to an organisation's own data. That sentence is the only permitted gesture at operational use.

## Root README rules

Structure: one-paragraph opening (what this repo demonstrates, on what data), the two workstreams with one-line summaries and links, a provenance section, licence.

Provenance section, same register as the author's other public work: these methods were developed through the author's release governance practice; this repository is a clean-room demonstration on public data built by AI-directed development, with the author as product owner and release manager. The code was generated; the specification, verification and publication judgement were not. Do not name any employer.

## Working method for this session

- Work in small verified increments: fetch data, show a sample, get confirmation; build the scorer, run on three notes, show output, get confirmation; then scale.
- Commit messages are plain and factual.
- When a judgement call arises that this brief does not cover, ask; do not improvise on constraints 1 to 3.
