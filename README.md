# Release intelligence

This repository demonstrates predictive release governance and incident
intelligence methods on fully public data. At its centre is 5R, a categorical
risk classification applied to change descriptions before test planning:
five yes/no categories, no weights, no severity scores.

An overview page for readers who want the high-level picture is published
from [`docs/`](docs/) via GitHub Pages.

## Contents

- [`5r-release-scoring/`](5r-release-scoring/): Workstream 1, 5R scoring
  applied to GitLab's public release notes 19.0 to 19.2. Contains the
  framework specification, the ingestion and scoring scripts, the
  committed LLM scoring prompt, the 99-note corpus, and the scored
  output with findings in its README.
- [`incident-intelligence/`](incident-intelligence/): Workstream 2,
  incident intelligence on public data. Contains the retrospective 5R
  scoring of the CrowdStrike Falcon outage of 19 July 2024, worked from
  CrowdStrike's published post-incident documents. The AI Incident
  Database analysis is not yet started.
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

## Data sources

- GitLab release notes, versions 19.0 to 19.2:
  <https://docs.gitlab.com/releases/>. Quoted for analysis under
  fair-dealing review purposes, with links back.
- CrowdStrike, Preliminary Post Incident Review (24 July 2024) and
  External Technical Root Cause Analysis: Channel File 291
  (6 August 2024), both published at <https://www.crowdstrike.com>.
  Quoted sparingly with credit; full citations in
  [`incident-intelligence/crowdstrike-5r-retro/sources.md`](incident-intelligence/crowdstrike-5r-retro/sources.md).
- Microsoft, Helping our customers through the CrowdStrike outage
  (20 July 2024), used for a single impact figure:
  <https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/>.

## Provenance

These methods were developed through the author's release governance
practice. This repository is a clean-room demonstration on public data,
built by AI-directed development with the author as product owner and
release manager. The code was generated; the specification, verification and
publication judgement were not.

## Licence

MIT. See [`LICENSE`](LICENSE).
