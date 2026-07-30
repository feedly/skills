# Resilience gap assessment

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 6: Improve resilience and readiness, Prompt 10

## What this prompt does
Maps a threat landscape (actor TTPs with MITRE ATT&CK mapping) against existing controls and recovery plans to identify gaps before an incident exposes them. For each gap it surfaces the corresponding MITRE D3FEND defensive countermeasure and assesses regulatory exposure against the frameworks applicable to the institution, producing a prioritized gap list structured for handoff to risk and operational teams.

## Prompt
```
<variables>
[job role]:
[country/region]:
[primary regulator]: OCC / FDIC / Federal Reserve / State DFI
[applicable state(s)]: (e.g., NY, CA, for state breach notification)
[EU operations in scope]: Yes / No / Under assessment
[stakeholder team names]:
[applicable frameworks]:, REQUIRED, no default.
Delete/add all that apply before running this prompt:
- FFIEC CAT
- NIST CSF
- DORA
- NY DFS Part 500
- CA CCPA / breach notification
- PCI DSS
- MITRE ATT&CK / D3FEND
- Other: [specify]

** Note about default_behavior **
If no value is provided for a variable (left blank after colon),
use these defaults:
[job role]: CTI Analyst
[country/region]: Global
[primary regulator]: Not specified
[applicable state(s)]: Not specified
[EU operations in scope]: Under assessment
[stakeholder team names]: Risk and Operational Continuity Teams

Note: [applicable frameworks] has no default and must be
completed before running this prompt.
</variables>

<context>
I'm a [job role] at a financial institution in [country/region],
regulated by [primary regulator], operating in [applicable
state(s)], with EU operations in scope: [EU operations in scope].
I need to identify where current controls and recovery plans
do not adequately address active or emerging threats against
BFSI infrastructure, producing a prioritized gap assessment
for [stakeholder team names] before an incident exposes those
gaps. Gap prioritization and remediation recommendations must
be grounded in [applicable frameworks].
</context>

<task>
Using the threat landscape summary and control inventory
or recovery plan pasted below, produce a resilience gap
assessment.

For each gap identified:
- Map the offensive TTP to MITRE ATT&CK
- Identify the corresponding MITRE D3FEND defensive
  countermeasure and assess whether it is currently
  in place
- Assess potential impact if exploited and likelihood
  based on current threat actor behavior
- Assess whether the gap creates exposure under
  [applicable frameworks] and flag which framework
  drives remediation priority
- Where multiple frameworks apply to a single gap,
  identify the shortest applicable deadline as the
  controlling timeline

Prioritize gaps by potential impact to payment
infrastructure, customer access, and regulatory
compliance, not just technical severity.

Before using this prompt, confirm the inputs and intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE THREAT LANDSCAPE SUMMARY HERE]

[PASTE SANITIZED CONTROL INVENTORY OR RECOVERY PLAN HERE]
</task>

<output_format>
## Resilience Gap Assessment

### 1. Assessment Summary
| Field | Detail |
|-------|--------|
| Threat landscape basis | |
| Primary regulator | |
| Applicable states | |
| EU operations in scope | |
| Frameworks applied | |
| Controls or recovery plans assessed | |
| Total gaps identified | |
| Critical gaps requiring immediate action | |

### 2. Gap Analysis
| Gap | ATT&CK TTP | D3FEND Countermeasure | Countermeasure In Place? | Potential Impact | Likelihood | Regulatory Exposure | Controlling Framework | Priority |
|-----|------------|----------------------|--------------------------|-----------------|------------|--------------------|-----------------------|----------|
| | | | Yes / Partial / No | High / Med / Low | High / Med / Low | | Framework + deadline | Immediate / Near-term / Long-term |

### 3. Priority Gap Detail
For each Immediate priority gap:

**Gap:** [description]
- ATT&CK TTP: [tactic and technique]
- D3FEND countermeasure: [defensive technique]
- Countermeasure status: [in place / partial / absent,
  describe what exists and why it is insufficient]
- Threat basis: [which active threat actor behavior
  or campaign this gap exposes]
- Potential impact: [payment, customer, regulatory]
- Regulatory exposure: [applicable framework(s)
  and controlling deadline]
- Recommended remediation: [specific action, not
  general best practice]
- Owner: [which team is responsible]
- Target timeline: [driven by shortest applicable
  regulatory deadline]

### 4. Remediation Roadmap
| Gap | ATT&CK TTP | D3FEND Countermeasure | Recommended Action | Owner | Timeline | Controlling Framework |
|-----|------------|----------------------|--------------------|-------|----------|-----------------------|
| | | | | | Immediate / 30 days / 90 days | |

### 5. Residual Risk
Gaps that cannot be fully remediated in the near term
and the controls in place to manage residual risk:
| Gap | Residual Risk | Compensating Control | Framework Acknowledgment Required |
|-----|---------------|---------------------|----------------------------------|
| | | | Yes / No |
</output_format>

<guidelines>
1. Prioritize gaps by BFSI impact, payment infrastructure,
   customer access, and regulatory compliance take
   precedence over generic technical severity
2. Every gap must include both an ATT&CK TTP and a
   corresponding D3FEND countermeasure, if D3FEND
   does not map directly, note this explicitly rather
   than forcing an approximate match
3. Where multiple frameworks apply to a single gap,
   the shortest deadline controls the remediation
   timeline. Where deadlines are equivalent, apply
   this tiebreaker sequence: (1) the framework under
   which the institution is currently under examination
   or most recent audit finding, (2) the framework
   carrying the highest penalty exposure, (3) analyst
   judgment, document the basis for the decision
4. Residual risk must be documented for gaps that
   cannot be immediately remediated, unacknowledged
   residual risk is a compliance exposure under most
   applicable frameworks
5. D3FEND countermeasure mappings should be verified
   against the current D3FEND matrix at d3fend.mitre.org
   before sharing this assessment, taxonomy and technique
   identifiers are updated periodically and may not match
   what is generated here exactly
6. Do not use em dashes anywhere in the output.
   Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: share the prioritized gap list with risk and operational continuity teams as an input to resilience planning; use the remediation recommendations to drive control improvement priorities; file the assessment as part of your threat-informed defense program documentation alongside the tabletop exercise.
