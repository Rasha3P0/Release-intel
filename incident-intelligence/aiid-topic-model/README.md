# Topic modelling and a governance lens: the AI Incident Database

This analysis works from a public snapshot of the AI Incident Database
(AIID), a catalogue of real-world AI harms maintained by the Responsible
AI Collaborative at <https://incidentdatabase.ai>. It uses AIID's own
editorial fields only: incident titles, descriptions, and taxonomy
classifications. It does not republish the underlying third-party news
reports the incidents cite, which remain copyrighted to their
publishers; AIID's own account of each incident is a short original
summary, not a reproduction of the source article.

Credit: incident data from the AI Incident Database
(<https://incidentdatabase.ai>), a project of the Responsible AI
Collaborative.

## Data and provenance

AIID publishes weekly database backups at
<https://incidentdatabase.ai/research/snapshots/> as MongoDB dumps. The
build environment for this repository has no outbound network access,
so the author downloaded the snapshot dated 13 July 2026 and extracted
two collections: `incidents` (1,571 records, title, description, date,
alleged parties, linked report ids) and `classifications_CSETv1` (214
records, the AIID Collaborative's own severity/harm taxonomy applied to
a subset of incidents). Both are committed in [`data/`](data/) as CSV.
Report full text and per-annotator raw coding files are not included:
the former is the copyrighted material the data rules exclude, the
latter is inter-rater working data rather than AIID's published
position.

`incidents.csv` spans 1983 to 2026, heavily weighted toward 2022
onward. Every record has a non-empty description (7 to 101 words,
median 52).

## Method

Three analyses, run in sequence:

1. **Topic modelling** ([`topic_model.py`](topic_model.py)). TF-IDF
   vectorisation of each incident's title and description, followed by
   k-means clustering (k=12, fixed seed). This is a standard,
   fully-reproducible topic modelling method that needs no external
   model calls and no labelled data; it surfaces recurring failure
   classes directly from AIID's own text.
2. **Tone and urgency signals** ([`tone_signals.py`](tone_signals.py)).
   A fixed, committed lexicon scan across the same descriptions, in the
   same rule-based spirit as `score_notes.py` in Workstream 1: no
   weights, quoted matches, reproducible from the lexicon alone.
3. **Governance lens** ([`governance_lens_prompt.md`](governance_lens_prompt.md),
   [`governance_lens.py`](governance_lens.py)). A simple random sample
   of 60 incidents (seed 20260721, fixed and reproducible) is classified
   by analogy against the 5R categories from
   [`../../5r-release-scoring/framework.md`](../../5r-release-scoring/framework.md):
   if this incident's failure mode had first appeared as a one-line
   description of a pending software change, which category would it
   most resemble, or does it not map at all. Each incident gets exactly
   one label, chosen from a committed prompt, with quoted evidence.
   `not_mappable` is a first-class, expected outcome, not a fallback to
   avoid: AI incidents are not software release notes, and the honest
   proportion of incidents this lens cannot place is itself a finding.

## Findings

### Topic modelling: recurring failure classes

Twelve clusters over 1,571 incidents. The largest four account for
nearly three in five incidents in the corpus:

| Cluster | Size | Top terms |
|---|---|---|
| Chatbots and generative assistants | 282 | google, chatgpt, chatbot, openai, user |
| Deepfake and AI-generated deception | 262 | generated, ai generated, voice, tools, court |
| Automated decision and detection systems | 229 | risk, automated, detection, black, drivers |
| Scam and fraud content | 166 | scam, deepfake, investment, scammers |
| Synthetic media and manipulated images | 128 | ai generated, generated, videos, images, media |
| Deepfake video specifically | 125 | video, deepfake, purported, deepfake video |
| Deepfakes involving minors/schools | 77 | school, students, images, student, deepfake |
| Content moderation platforms | 77 | content, facebook, moderation, automated, tiktok |
| Autonomous vehicles | 72 | robot, autonomous, waymo, cruise, vehicle |
| Facial recognition | 67 | facial, facial recognition, police, arrest |
| Driver-assistance systems | 48 | tesla, autopilot, driver, tesla model |
| Consumer AI products | 38 | amazon, products, alexa, search, translation |

Full assignments in [`findings/topic_clusters.csv`](findings/topic_clusters.csv);
per-cluster terms and sample titles in
[`findings/topic_clusters_summary.json`](findings/topic_clusters_summary.json).
Synthetic media (deepfakes, AI-generated deception, scam content) spans
four of the twelve clusters and is the single largest theme in the
corpus, ahead of the more release-governance-adjacent categories
(autonomous vehicles, facial recognition, driver-assistance) that
dominate public discussion of "AI safety incidents". That skew matters
for the governance lens below: most of this corpus is not shaped like a
software release at all.

### Tone and urgency signals

Full output in
[`findings/tone_signals_summary.json`](findings/tone_signals_summary.json).
Across all 1,571 incidents:

| Signal | Prevalence |
|---|---|
| Uncertainty/hedging (allegedly, reportedly, purported, claim) | 74.9% |
| Legal/regulatory language | 20.5% |
| Financial/business language | 19.7% |
| Fatality/injury language | 7.5% |
| Urgency/emergency language | 4.2% |

The dominant signal is hedging, not alarm. Three in four AIID
descriptions carry an evidentiary qualifier, which reflects AIID's own
editorial discipline: these are alleged harms pending fuller
investigation, not adjudicated facts, and the database's own language
says so consistently.

Description length echoes the R4 brevity trigger from Workstream 1: the
median AIID description is two sentences, and 57.2% of all 1,571
incidents are described in two sentences or fewer. This is not 5R
applied to incidents; AIID descriptions are editorial summaries of
events that already happened, not pre-release change notes, and the
comparison is structural rather than a claim that the same gate
applies. But the pattern is the same one Workstream 1 found in GitLab's
own release notes: a short, plain account is the default register for
describing a real-world AI failure, just as it was the default register
for describing a change to production software.

### Governance lens: does the failure mode map to 5R

60 incidents, simple random sample, seed 20260721. Full scored sample in
[`findings/governance_lens_scored.csv`](findings/governance_lens_scored.csv);
summary in
[`findings/governance_lens_summary.json`](findings/governance_lens_summary.json).

| Label | Count | Share |
|---|---|---|
| not_mappable | 28 | 46.7% |
| R1 Data Structure | 19 | 31.7% |
| R5 Rollback | 6 | 10.0% |
| R4 Hidden Complexity | 5 | 8.3% |
| R3 Integration | 2 | 3.3% |
| R2 Blast Radius | 0 | 0.0% |

Reported honestly: **not_mappable is the largest single outcome.**
Close to half the sample is not, by this lens' own rules, a software
change-risk story at all. The evidence field for each not_mappable
judgement names why: most are cases where the proximate cause is human
intent or negligence using an AI system as an instrument, rather than a
property of the system's own risk shape. A gallery owner defrauded over
months by a deepfake impersonation is a fraud case that happened to use
AI-generated media; a government department appending unverified
AI-drafted references to a Cabinet paper is a verification-process
failure, not a system defect. Two similar-looking cases in the sample,
alleged deliberate self-preferencing in a search algorithm and an
alleged AI safety-training decision, were also called not_mappable on
the same basis: the failure is about intent and judgement, not a
change's declared shape.

**R1 dominates the mappable share.** Nineteen of sixty incidents, close
to a third of the whole sample, trace to a misread, miscalibrated, or
misinterpreted input: Google Photos labelling a black couple as
gorillas, a facial recognition match on an outdated photo leading to a
wrongful arrest, a chatbot's classifier misjudging what it was shown.
This is the strongest signal the governance lens produces: when an AI
incident does map onto a software-change risk category, it
overwhelmingly maps onto data and interpretation, not onto scale,
integration, framing, or reversibility.

**R2 Blast Radius mapped to nothing in this sample.** Zero of sixty.
This is a real finding, not a scoring gap: R2 in the 5R framework means
a change riding a high-volume automated *process* (a batch job, a
critical feed). Most AIID incidents are framed as discrete events
happening to identifiable people, even when the underlying system
operates at platform scale: the harm is narrated at the scale of a
person, not a pipeline. It is plausible that R2 would surface more in a
larger sample, or in incidents specifically about content-moderation
systems (the fourth-largest topic cluster above), but it did not appear
in this one, and that absence is reported rather than smoothed over.

**R4 and R5 both appeared, in the register the framework predicts.**
The five R4 cases share a shape: a routine-sounding task, adding a
badge to a photo, yielding a driving lane, a personalised content feed,
concealed behavior with real consequences. "Purported AI-edited
police evidence image" is the clearest case: an officer's admittedly
routine edit altered evidentiary details in a photograph, the same
innocuous-task-hides-complexity pattern R4 exists to catch in release
notes. The six R5 cases are dominated by physical or reputational harm
with no clean undo: wrongful arrests, injuries.

**Two structurally similar incidents split across labels, and that
split is reported rather than reconciled.** Incidents 592 and 1191 are
both facial-recognition misidentifications leading to a wrongful
arrest. 592 was labelled R5 (the wrongful arrest is treated as the
defining, irreversible harm); 1191 was labelled R1 (the miscalibrated
match is treated as the defining, traceable cause). Both readings are
defensible from the same evidence-quoting discipline; forcing them to
agree would have hidden a genuine property of the lens rather than
revealed one. A compound failure, a data problem that becomes an
irreversible harm, does not have a single correct 5R label, and a
lens built for one-label-per-item scoring will sometimes split
near-identical cases on which half of the compound it weights first.

### What this does and does not show

The topic model and tone scan describe the corpus as it is: dominated by
synthetic media and deception, narrated with consistent evidentiary
caution, usually in a sentence or two. The governance lens shows that a
categorical software-release framework, applied by analogy to a
different kind of harm record, correctly declines to fit about half of
it, and where it does fit, concentrates heavily on data and
interpretation failures. Applied to an organisation's own AI system
incident log rather than to a public database of harms across many
organisations, this lens would show which of its own incidents share a
risk shape with the failures a pre-release 5R gate is built to catch,
and which are a different problem entirely.
