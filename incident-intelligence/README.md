# Workstream 2: incident intelligence on public data

Two analyses on fully public sources. Neither uses any private or
employer data.

- [`crowdstrike-5r-retro/`](crowdstrike-5r-retro/): a retrospective 5R
  scoring of the change behind the CrowdStrike Falcon outage of 19 July
  2024, worked entirely from CrowdStrike's own published Preliminary
  Post Incident Review and Root Cause Analysis. The analysis shows which
  categorical gates would have fired before release, with the R4 hard
  gate on a routine content-update label as the centrepiece.
- [`aiid-topic-model/`](aiid-topic-model/): topic and tone modelling
  across the AI Incident Database public snapshot, with a governance
  lens that asks which failure modes map to a 5R category. Topic
  clustering finds synthetic media and deception as the largest theme
  in the corpus; the governance lens finds close to half of a 60-incident
  sample does not map to a software-change risk category at all, and
  that data/interpretation failures (R1) dominate the half that does.

The 5R specification applied here is the one in
[`../5r-release-scoring/framework.md`](../5r-release-scoring/framework.md).
