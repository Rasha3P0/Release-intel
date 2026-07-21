# Scoring adjudications

Borderline stamps flagged during the LLM-assisted scoring pass were
reviewed by the author before the scored output was accepted. Two were
changed; the reasoning is recorded here so the published scores are
reproducible from `llm_scores.json` plus this record.

1. `017-postgresql-17-minimum-requirement` R5: yes changed to unclear.
   The original stamp relied on domain knowledge that major PostgreSQL
   upgrades lack a clean downgrade path. The note does not state this,
   and the method forbids stamping on anything but the note text. The
   note still trips the R4 hard gate on brevity, which is the mechanism
   the framework intends for exactly this case.
2. `018-usage-billing-checks-for-gitlab-duo-agent-platform-self-host`
   R3: yes changed to no. The change adds a connectivity diagnostic for
   existing endpoints; the interfaces themselves are unchanged.

Two further yes stamps failed the automated quote check only because the
PDF text extraction joins words across line breaks; the quoted wording
matches the source pages and the stamps stand unchanged.
