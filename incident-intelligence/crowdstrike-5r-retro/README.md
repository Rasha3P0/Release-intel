# A 5R retrospective: the CrowdStrike Falcon outage, 19 July 2024

This analysis applies the 5R categorical risk classification
([specification](../../5r-release-scoring/framework.md)) retrospectively
to the change behind the Falcon sensor outage of 19 July 2024. It works
exclusively from CrowdStrike's own published account: the Preliminary
Post Incident Review of 24 July 2024 and the External Technical Root
Cause Analysis of 6 August 2024 (full citations in
[`sources.md`](sources.md)). CrowdStrike deserves credit for publishing
both documents; that transparency is what makes an external methods
analysis like this one possible. The analysis draws no conclusions about
any individual or about CrowdStrike's culture. This incident is the
industry's shared case study, and it is treated here as exactly that.

## The change, as the RCA describes it

On 19 July 2024 CrowdStrike deployed two additional IPC Template
Instances as Rapid Response Content via Channel File 291. One of them
"introduced a non-wildcard matching criterion for the 21st input
parameter", a field no previous instance had used. The sensor's Content
Interpreter supplied 20 inputs where the Template Type definition
declared 21; reading the 21st value "produced an out-of-bounds memory
read beyond the end of the input data array and resulted in a system
crash" (RCA). The PIR describes the deployment as "a content
configuration update", released "as part of regular operations".
Microsoft estimated approximately 8.5 million Windows devices were
affected (Microsoft, 20 July 2024; see sources).

The question 5R asks is not whether the defect was foreseeable. It is
whether the change description, scored categorically before release,
would have triggered the protocols that the incident retrospectively
proved necessary. Each category below is stamped from the published
account, quoting it as evidence.

## The scoring

### R1 Data Structure: yes

The change altered how the sensor interprets configuration data. "These
new Template Instances resulted in a new version of Channel File 291
that would now require the sensor to inspect the 21st input parameter.
Until this channel file was delivered to sensors, no IPC Template
Instances in previous channel versions had made use of the 21st input
parameter field" (RCA). A change that makes interpretation logic read a
field it has never read before is a data-structure change in exactly the
sense R1 exists to catch.

### R2 Blast Radius: yes

The delivery mechanism is fleet-wide and the affected component is
load-bearing. The PIR scopes the impact to "Windows hosts running sensor
version 7.11 and above that were online between Friday, July 19, 2024
04:09 UTC and Friday, July 19, 2024 05:27 UTC and received the update";
the RCA notes the sensor's driver "is loaded from an early phase of
system boot". A cloud-delivered update consumed at boot by every online
host in the fleet is a high-volume critical feed by any reading of R2.

### R3 Integration: yes

The failure was an interface-contract mismatch between producer and
consumer components. The RCA states it plainly: "the mismatch between
the 21 inputs validated by the Content Validator versus the 20 provided
to the Content Interpreter". Content produced by the Content
Configuration System is consumed downstream by the Content Interpreter
across a declared parameter contract; the change exercised that contract
at a boundary no prior content had touched.

### R4 Hidden Complexity: yes, and this is the centrepiece

The change travelled under the most routine label available. "On Friday,
July 19, 2024 at 04:09 UTC, as part of regular operations, CrowdStrike
released a content configuration update for the Windows sensor to gather
telemetry on possible novel threat techniques. These updates are a
regular part of the dynamic protection mechanisms of the Falcon
platform" (PIR). As a change description this is two sentences, framed
as routine, for a deployment that in fact carried a first-ever
behaviour: the first non-wildcard use of a parameter field never before
exercised in production.

R4 is a hard gate precisely for this register. The gate does not require
anyone to have foreseen the out-of-bounds read. It requires only the
observation that "regular operations" language plus a description of
three sentences or fewer is the exact combination under which complexity
hides, and that such a note is held until its author and a technical
lead re-score it together. The joint re-score is the moment at which
"this instance uses the 21st field for the first time" has a chance to
be said out loud. The RCA's own findings confirm what the label
concealed: the parameter-count mismatch "evaded multiple layers of build
validation and testing" partly because prior testing and prior instances
had "the use of wildcard matching criteria for the 21st input".

### R5 Rollback: yes

The distribution point could be reverted; the affected endpoints could
not be reached by the reversion. "The defect in the content update was
reverted on Friday, July 19, 2024 at 05:27 UTC. Systems coming online
after this time, or that did not connect during the window, were not
impacted" (PIR). The reversion, by the PIR's own scoping, protected only
systems that had not yet received the content. For hosts that had
received it, the crash occurred in a component "loaded from an early
phase of system boot" (RCA), which is the same channel any corrective
content would arrive through. An operation whose reversal cannot reach
the systems it affected is not cleanly reversible.

## Threshold result

Five stamps of five. Under the threshold rule, two or more stamps add a
coordination sign-off before planning begins, and the R4 hard gate holds
the change for a joint re-score regardless. Scored categorically from
its own description, this change does not proceed as routine: it is the
strongest possible 5R case, a maximal-stamp change travelling under a
minimal-register label.

## What the RCA's remediations share with the gate's protocols

The most instructive part of CrowdStrike's account is the remediation
list, because it converges on the same overlays a categorical gate
exists to trigger:

- The RCA commits to staged deployment for Template Instances: canary
  testing, "successively promoted to wider deployment rings or rolled
  back if problems are detected", with bake-in time between rings. That
  is the R2 protocol: blast-radius containment for high-volume feeds.
- Customer control over "where and when Rapid Response Content updates
  are deployed" and rollback-aware deployment layers are the R5
  protocol: a reversal path that can actually reach affected systems.
- Compile-time validation of input-field counts and Content Validator
  checks that content "does not include matching criteria that match
  over more fields than are being provided" are the R1 and R3 protocols:
  contract verification on data shape and on the producer-consumer
  interface.
- "Content update details via release notes, to which customers can
  subscribe" addresses R4 directly: richer change descriptions are the
  antidote to the routine-label register.

None of this is offered as hindsight superiority. CrowdStrike's
engineering response derived these controls from the incident within
weeks, and published them. The point of the retrospective is narrower
and methodological: every one of those controls corresponds to a
protocol that a categorical pre-release gate triggers from the change
description alone, without knowing where the defect is. The gate does
not find bugs. It notices when a change's declared shape demands the
protections, and demands them before the incident does.

Applied to an organisation's own change records, this method would show
which pending changes are currently travelling under a register their
risk shape does not justify.
