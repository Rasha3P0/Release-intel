# Workstream 2: incident intelligence on public data

Two analyses on fully public sources. Neither uses any private or
employer data.

- [`crowdstrike-5r-retro/`](crowdstrike-5r-retro/): a retrospective 5R
  scoring of the change behind the CrowdStrike Falcon outage of 19 July
  2024, worked entirely from CrowdStrike's own published Preliminary
  Post Incident Review and Root Cause Analysis. The analysis shows which
  categorical gates would have fired before release, with the R4 hard
  gate on a routine content-update label as the centrepiece.
- `aiid-topic-model/`: topic and tone modelling across the AI Incident
  Database public snapshot, with a governance lens that asks which
  failure modes map to a 5R category. Not yet started.

The 5R specification applied here is the one in
[`../5r-release-scoring/framework.md`](../5r-release-scoring/framework.md).
