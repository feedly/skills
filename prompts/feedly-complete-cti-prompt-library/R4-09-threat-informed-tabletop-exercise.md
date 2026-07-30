# Threat-informed tabletop exercise

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 6: Improve resilience and readiness, Prompt 9

## What this prompt does
Takes current threat intelligence and produces a realistic BFSI-specific tabletop exercise grounded in the specific TTPs, infrastructure targets, and fraud dimensions in the intelligence. It generates an inject timeline that can be run without additional facilitation preparation, plus decision points mapped to each team (CTI, SOC, fraud, incident response, compliance/legal).

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
[stakeholder team names]: CTI, SOC, Fraud, Incident Response, Compliance/Legal
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
I need to produce a threat-informed tabletop exercise
for [stakeholder team names] grounded in current threat
intelligence, not a generic template, that tests realistic
response to active threats against BFSI infrastructure.
</context>

<task>
Using the threat intelligence pasted below, produce a
tabletop exercise for a BFSI institution.

Ground the scenario in the specific TTPs, infrastructure
targets, and fraud dimensions present in the intelligence.
Map decision points to each participating team. Include
an inject timeline that can be run without additional
facilitation preparation.

Flag assumptions about the institutional environment
where the scenario requires details not present in
the source intelligence.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE THREAT INTELLIGENCE HERE]
</task>

<output_format>
## Threat-Informed Tabletop Exercise

### 1. Exercise Overview
| Field | Detail |
|-------|--------|
| Threat actor / campaign basis | |
| Primary target | Payment rails / Identity systems / Core banking |
| Exercise objective | What this exercise is designed to test |
| Participating teams | |
| Estimated duration | |

### 2. Exercise Narrative
Two to three paragraph description of the cyberattack incident
written for exercise participants, realistic, specific
to BFSI infrastructure, grounded in the source intelligence.

### 3. Inject Timeline
| Time | Inject | Team | Decision Required |
|------|--------|------|-------------------|
| T+0 | Opening scenario | All | Initial assessment and escalation decision |
| T+X | | | |
| T+X | | | |
| T+X | | | |
| T+X | Scenario conclusion | All | Resolution and lessons learned |

### 4. Team Decision Points
| Team | Key Decision | What Good Response Looks Like | What Poor Response Looks Like |
|------|-------------|-------------------------------|-------------------------------|
| CTI | | | |
| SOC | | | |
| Fraud | | | |
| Incident Response | | | |
| Compliance/Legal | | | |

### 5. Stress Test Questions
Questions the exercise should force each team to answer:
1. [Question]
2. [Question]
3. [Question]

### 6. Environmental Assumptions
Assumptions made about the institutional environment
where the exercise requires details not in the source
intelligence, flag for facilitator review before running.
</output_format>

<guidelines>
1. Ground every inject in the source intelligence,
   do not introduce attack vectors or TTPs not present
   in the threat intelligence
2. Decision points must reflect how the threat actor
   actually operates, not generic incident response process
3. Flag all environmental assumptions explicitly,
   facilitators need to validate these before running
   the exercise
4. Stress test questions should expose gaps in
   cross-team coordination, not just individual
   team process
5. Do not use em dashes anywhere in the output.
   Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: use the inject timeline to run the exercise without additional facilitation preparation; use the decision points to assess whether each team's response reflects current threat actor behavior, not just standard process; operationalize the tabletop exercise as part of your threat-informed defense program documentation.
