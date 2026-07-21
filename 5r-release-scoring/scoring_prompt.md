# LLM-assisted scoring prompt

This is the complete prompt used for LLM-assisted judgements on the
judgement codes R1, R2, R3 and R5. It is committed so the method is
reproducible. R4 is never LLM-scored; its triggers are lexical and handled
by `score_notes.py`. Output from this prompt is saved as a JSON file and
merged with `score_notes.py --llm-scores`.

---

You are scoring software release notes with the 5R categorical risk
classification. For each note, assess four categories. Stamp each one
yes, no, or unclear. There are no weights and no severity scores.

- R1 Data Structure: the change touches schema, stored data shape,
  calculations, or interpretation logic.
- R2 Blast Radius: the change touches high-volume processes, batch jobs,
  or critical feeds.
- R3 Integration: the change affects downstream consumers, interfaces,
  APIs, or reports.
- R5 Rollback: the change involves one-way operations, forward-only
  migrations, or anything that cannot be cleanly reversed.

Rules:

1. Evidence must be quoted from the note text. A yes stamp with no quote
   is invalid.
2. Never stamp on speculation. If the note gives no basis either way,
   stamp unclear and name exactly what missing information would resolve
   it.
3. A no stamp is permitted only when the note's own description of the
   change makes the category implausible, and the evidence field must say
   why.
4. Do not propose weights, scores, or severity levels.

Return JSON keyed by note id:

{
  "<note-id>": {
    "R1": {"stamp": "yes|no|unclear", "evidence": "quoted text or named missing information"},
    "R2": {...},
    "R3": {...},
    "R5": {...}
  }
}
