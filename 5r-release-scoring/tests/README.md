# Scorer validation fixtures

The notes in `fixtures/` are synthetic. They exist to validate that
`score_notes.py` behaves as the framework specifies, one per expected
outcome: a clean multi-stamp note, an R4 hard-gate trigger on innocuous
language, and a genuinely low-risk note. They are not GitLab data and are
never counted in findings.

`sample_scored/` is the committed output of running the scorer over the
fixtures, so the output format can be inspected without running anything:

    python3 score_notes.py tests/fixtures -o tests/sample_scored
