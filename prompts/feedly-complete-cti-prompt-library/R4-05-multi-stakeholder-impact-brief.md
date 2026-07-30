# Multi-stakeholder impact brief

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 3: Coordinate with fraud, SOC, and risk, Prompt 5

## What this prompt does
Produces three stakeholder-specific sections (fraud, SOC, risk) from the same enriched intelligence in a single pass, eliminating the re-briefing loop that slows cross-functional response. Each section is written in that team's language and priorities so it can be forwarded directly to the relevant team lead with minor editing.

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
[stakeholder team names]: Fraud, SOC, and Risk Teams
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
I need to communicate the same enriched intelligence to
fraud, SOC, and risk teams simultaneously, each in their
own language and focused on what is relevant to their
function, without running separate briefings for each team.
</context>

<task>
Using the enriched intelligence pasted below, which may
be a completed Third-Party and Ecosystem Risk Assessment
or Fraud Impact Assessment, produce a multi-stakeholder
impact brief with three stakeholder-specific sections.

Each section should be written for that team's priorities
and language. Do not repeat the same content across sections
, each team gets only what is relevant to them.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE ENRICHED INTELLIGENCE HERE]
</task>

<output_format>
## Multi-Stakeholder Impact Brief

### BLUF
Two to three sentences maximum. What the intelligence
shows, what is confirmed, and the single most important
action required right now. Written for all three teams
to read as shared context before reviewing their
specific section.

### Section A, Fraud Team
*Focus: payment exposure, fraud signal types,
monitoring adjustments*

| Field | Detail |
|-------|--------|
| Payment types at immediate risk | |
| Fraud types implicated | BEC / ATO / Payment redirection / SIM swap |
| Identity systems at risk | |
| Recommended monitoring adjustments | |
| Immediate actions required | |

*Note: Flag institution-specific thresholds before
sharing this section.*

### Section B, SOC Team
*Focus: indicators of compromise, containment priorities,
detection opportunities*

#### IOCs, Action Immediately
| Indicator | Type | Action | Priority |
|-----------|------|--------|----------|
| | Hash / Domain / IP / URL | Block / Monitor / Hunt | Immediate / 24hr |

#### MITRE ATT&CK TTPs
| Tactic | Technique ID | Technique Name | BFSI Relevance |
|--------|-------------|----------------|----------------|
| | T#### | | Payment / Identity / Core Banking |

*Note: Only include TTPs confirmed in source material.
Do not map techniques not present in the intelligence.*

#### Containment Priorities
1. [First priority action]
2. [Second priority action]
3. [Third priority action]

#### Detection and Hunting
| Opportunity | Hypothesis | Owner |
|-------------|------------|-------|
| | | SOC Tier 1 / Tier 2 |

### Section C, Risk Team
*Focus: business impact, regulatory exposure,
escalation requirements*

| Field | Detail |
|-------|--------|
| Financial exposure estimate | |
| Customer impact | |
| Service disruption risk | |
| Regulatory notification required | Yes / No / Requires Review |
| Recommended escalation | |
</output_format>

<guidelines>
1. Write each section for that team's language and
   priorities, fraud language for Section A, technical
   language for Section B, business language for Section C
2. Do not repeat content across sections, each team
   receives only what is relevant to their function
3. Flag institution-specific thresholds and regulatory
   determinations for analyst review before sharing
4. If the intelligence does not support a finding for
   a specific field, mark as "Not confirmed in source
   material" rather than leaving blank. All outputs must
   be validated against source material before sharing.
5. Only include TTPs confirmed in source material, do
   not map techniques not present in the intelligence
   and do not invent MITRE T-code mappings
6. Do not use em dashes anywhere in the output.
   Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: forward each stakeholder section directly to the relevant team lead; use the fraud section to drive immediate fraud detection controls before a joint call is scheduled; use the risk section to determine whether executive escalation or compliance review is required.
