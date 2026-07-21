# Governance lens prompt

This is the complete prompt used to classify a sample of AI Incident
Database entries against the 5R categories from
[`../../5r-release-scoring/framework.md`](../../5r-release-scoring/framework.md).
It is committed here so the method is reproducible. Output is saved as
JSON and merged with `governance_lens.py`.

This classification is an analogy, not a scoring. AIID incidents are not
software release notes; a pre-release change description does not exist
for most of them. The question the lens asks is narrower: if the failure
mode behind this incident had first appeared as a one-line description of
a pending change, would it have plausibly landed in one of the five 5R
categories, or does the failure not correspond to a software-change risk
category at all. Multi-label is not used; each incident gets exactly one
best-fit label. Honesty about not-mappable outcomes matters more than
forcing a fit.

---

You are applying a governance lens from the 5R risk classification to an
AI incident record from the AI Incident Database (AIID). 5R has five
categories, defined for software release notes:

- R1 Data Structure: the change touches schema, stored data shape,
  calculations, or interpretation logic.
- R2 Blast Radius: the change touches high-volume processes, batch jobs,
  or critical feeds.
- R3 Integration: the change affects downstream consumers, interfaces,
  APIs, or reports.
- R4 Hidden Complexity: the change hides behind innocuous-label language
  or a very short description.
- R5 Rollback: the change involves one-way operations or anything that
  cannot be cleanly reversed.

Given an incident's AIID-authored title and description, decide which
single category the incident's failure mode best resembles, by analogy,
if it had been the description of a pending software change. Categories
to choose from: R1, R2, R3, R4, R5, or not_mappable.

Guidance on the analogy, not rules to apply mechanically:

- R1 fits failures traceable to how data was structured, labelled,
  stored, or interpreted (a training-data problem, a misread field, a
  miscalibrated score).
- R2 fits failures whose harm came from operating at high volume or
  scale (an automated system applied across many users or cases at
  once).
- R3 fits failures that arose at a handoff between systems or with a
  downstream consumer of the AI system's output (a decision feeding into
  another process, an API integration).
- R4 fits failures where the system or feature was described, marketed,
  or perceived as simple or routine when its actual behaviour was not
  (this is about the incident's own framing, not about how short the
  AIID description you are reading happens to be).
- R5 fits failures that caused irreversible or practically irreversible
  harm (a wrongful decision with lasting consequences, physical harm,
  loss of life, an action that could not be undone once taken).
- not_mappable fits failures that are fundamentally about something
  other than a software change's risk shape: intent and misuse, a
  values or policy judgement, an incident that is really about human
  behaviour using an AI tool as an instrument rather than about the
  system's own change risk.

Rules:

1. Choose exactly one label.
2. The evidence field may quote the incident's own title or description
   text, or paraphrase it in your own words, or both. These are not
   interchangeable: anything inside quotation marks must be copied
   verbatim from the title or description, character for character
   (aside from surrounding whitespace). Never put your own wording, a
   paraphrase, or a phrase from the 5R category definitions themselves
   inside quotation marks. Use double quotes only for verbatim
   quotation; do not use single quotation marks to mark a quote (this
   avoids confusion with contractions and possessives such as
   "driver's"). Do not use an ellipsis or bracketed insertions to
   splice together non-adjacent parts of the source text into one
   quotation; quote a single contiguous run of the source text, or use
   two separate double-quoted fragments joined by your own words.
   `governance_lens.py` mechanically checks every double-quoted
   fragment against the source text and rejects the batch if any
   fragment is not found verbatim, so treat this as a hard requirement,
   not a style preference.
3. If the description does not give enough basis to choose confidently
   between two categories, prefer not_mappable and say why in the
   evidence field, rather than guessing.
4. Do not invent facts about the incident beyond what the title and
   description state.

Return JSON keyed by incident id:

{
  "<incident_id>": {
    "label": "R1|R2|R3|R4|R5|not_mappable",
    "evidence": "quoted or paraphrased text and brief reasoning"
  }
}
