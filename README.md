# Release intelligence

This repository demonstrates predictive release governance and incident
intelligence methods on fully public data. At its centre is 5R, a categorical
risk classification applied to change descriptions before test planning:
five yes/no categories, no weights, no severity scores.

## Contents

- [`BUILD_BRIEF.md`](BUILD_BRIEF.md): the specification and decision log for
  this repository, including the complete generic 5R framework and the two
  planned workstreams (5R scoring on public release notes; incident
  intelligence on public data).
- [`5R_SHIFT_LEFT.md`](5R_SHIFT_LEFT.md): how the same five categories shift
  left to the point where functional specs are created from requirements,
  turning each stamp from a release-time discovery into an authoring
  obligation on the spec.

The workstreams described in the brief are built here incrementally. Every
dataset used is publicly available and credited with a link.

## Provenance

These methods were developed through the author's release governance
practice. This repository is a clean-room demonstration on public data,
built by AI-directed development with the author as product owner and
release manager. The code was generated; the specification, verification and
publication judgement were not.

## Licence

MIT. See [`LICENSE`](LICENSE).
