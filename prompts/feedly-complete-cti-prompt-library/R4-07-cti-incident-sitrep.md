# CTI incident SITREP

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 4: Respond and document, Prompt 7

## What this prompt does
Maintains and updates a CTI Incident Situation Report (SITREP) iteratively during active incident response, tracking how the threat actor assessment evolves, actioning new indicators surfaced by forensics, and documenting what is now known versus what remains unknown. Each run compares new findings against the initial triage assessment and increments a record iteration.

## Prompt
```
<variables>
[job role]:
[country/region]:
[stakeholder team names]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon),
use these defaults:
[job role]: CTI Analyst
[country/region]: Global
[stakeholder team names]: SOC, Fraud, Compliance, and Risk
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
During active incident response, I need to maintain and
update the CTI Incident SITREP (Situation Report) as investigation findings
come in, tracking how the threat actor assessment evolves,
actioning new indicators surfaced by forensics, and
documenting what is now known versus what remains unknown
for [stakeholder team names].
</context>

<task>
Using the investigation update or analyst notes pasted
below, which may be forensic findings, SOC investigation
results, IR updates, or new threat intelligence, produce
an updated CTI Incident SITREP for this incident.

Compare new findings against the initial triage assessment
where relevant. Clearly label all information as Confirmed,
Assessed, or Unknown. Do not reconstruct from assumptions
, where information is absent, state that explicitly.

This prompt is designed to be run iteratively throughout
response. Each iteration reflects the intelligence state
at that point in the investigation.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE INVESTIGATION UPDATE OR ANALYST NOTES HERE]
</task>

<output_format>
## CTI Incident SITREP
| Field | Detail |
|-------|--------|
| Incident reference | |
| Record iteration | 1 / 2 / 3 (increment each run) |
| Date and time of this update | Analyst to confirm before filing |
| Analyst completing this record | Analyst to add name before filing |
| Intelligence status | Evolving / Stabilizing / Final |

### BLUF
Two sentences maximum. Sentence 1: state the single most
significant change to the threat picture since the last
iteration (or since initial triage if this is iteration 1).
Sentence 2: state what that change means for the institution
right now. No background, no caveats, no hedging. Written
for an executive who will read this and nothing else.

### 1. Incident SITREP Update
What has changed since the last CTI assessment.
If this is the first iteration, compare against
initial triage assessment.

| Intelligence Area | Initial Assessment | Current Assessment | Status |
|-------------------|-------------------|-------------------|--------|
| Threat actor | | | Confirmed / Revised / Unknown |
| Campaign objective | | | Confirmed / Revised / Unknown |
| Attack vector | | | Confirmed / Revised / Unknown |
| Infrastructure targeted | | | Confirmed / Revised / Unknown |
| Fraud dimension | | | Confirmed / Revised / Unknown |

### 2. New IOCs Surfaced
Indicators identified during investigation not present
in the original signal. Push to SOC for immediate
actioning.

| Indicator | Type | Source | Confidence | Recommended Action |
|-----------|------|--------|------------|--------------------|
| | Hash / Domain / IP / URL | Forensics / SOC / IR | High / Med / Low | Block / Monitor / Hunt |

If no new IOCs identified, state: "No new indicators
surfaced in this investigation update."

### 3. TTP Assessment Update
| MITRE Tactic | Technique ID | Technique Name | Status | Notes |
|--------------|-------------|----------------|--------|-------|
| | T#### | | Confirmed / Revised / Ruled Out / New | |

*Only include TTPs confirmed in source material.
Do not map techniques not present in the intelligence.*

### 4. Intelligence Gaps Closed
Unknowns from prior assessment that have now been
answered by investigation findings:
| Gap | Resolution | Source | Confidence |
|-----|------------|--------|------------|
| | | Forensics / SOC / IR / External | High / Med / Low |

If no gaps have closed, state: "No prior intelligence
gaps resolved in this update."

### 5. Intelligence Gaps Remaining
Unknowns that are still open and what would close them:
| Gap | Why It Matters | Recommended Action | Owner |
|-----|---------------|-------------------|-------|
| | | | CTI / SOC / IR / Forensics |

### 6. Updated Threat Assessment

Three components. Keep each to two to three sentences maximum.

**Intent x Capability x Opportunity**
| Dimension | Assessment | Status |
|-----------|------------|--------|
| Intent | What the threat actor is trying to achieve | Confirmed / Assessed / Unknown |
| Capability | What tools, skills, and resources they demonstrated | Confirmed / Assessed / Unknown |
| Opportunity | What conditions enabled or limited this attack | Confirmed / Assessed / Unknown |

**Threat Picture Change**
One to two sentences only. How the threat actor assessment has changed since initial triage.
Label each statement Confirmed or Assessed. No CTI jargon.
Written for compliance and risk teams, not analysts.

**Threat Level to This Institution**
| Rating | Rationale |
|--------|-----------|
| Low / Guarded / Elevated / High / Critical | One sentence explaining the rating based on intent, capability, and opportunity above. |

### 7. Intelligence Products Needed for Reporting
What CTI needs to produce before Function 5 reporting
begins:
| Product | Purpose | Owner | Required By |
|---------|---------|-------|-------------|
| | | CTI | |
</output_format>

<guidelines>
1. Very important: If there is not enough intelligence provided to fill in a section of the report, leave it blank. Do not hallucinate content or make assumptions.
2. Label every intelligence statement as Confirmed, Assessed, or Unknown, regulators and compliance teams distinguish between these and so must CTI
3. New IOCs in Section 2 must be pushed to SOC immediately, do not wait for the full picture before actioning new indicators
4. TTP revisions must be documented explicitly, an assessment that changes between iterations without explanation undermines the intelligence trail
5. Section 6 has three components and a strict length limit. The Intent x Capability x Opportunity table drives the threat picture. The change summary is one to two sentences. The threat level rating is one sentence. If the output is longer than this, it is too long. Section 6 is written for compliance and risk teams, no CTI-specific language.
6. Do not use em dashes anywhere in the output. Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: run at each significant investigation milestone as new findings come in from IR, SOC, or forensics; use the updated IOC section to push new indicators to SOC for immediate action; carry the updated threat assessment and remaining gaps directly into Section 5 reporting.
