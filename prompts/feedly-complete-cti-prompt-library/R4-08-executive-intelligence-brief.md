# Executive intelligence brief

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 5: Report to compliance and leadership, Prompt 8

## What this prompt does
Translates technical incident intelligence into a one-page business risk summary for executive leadership. It leads with business impact, surfaces decision points requiring leadership attention, and closes with recommended actions and named owners, using no CTI terminology or attack chain language.

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
[stakeholder team names]: Executive Leadership and Board
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
I need to communicate incident intelligence to
[stakeholder team names] in business language, leading
with impact, surfacing decision points, and summarizing
what the security team has already done and what happens
next. No technical detail or CTI language.
</context>

<task>
Using the incident record or intelligence pasted below,
produce a one-page executive intelligence brief.

Lead with business impact. Surface decision points
requiring leadership attention. Summarize actions
already taken and next steps with named owners.

Do not use CTI terminology, technical indicators, or
attack chain language. If a technical concept must be
referenced, explain it in one plain-language sentence.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE INCIDENT RECORD OR INTELLIGENCE HERE]
</task>

<output_format>
## Executive Intelligence Brief

### BLUF
One sentence. The single most important fact leadership
needs to know right now.

### 1. Business Impact
| Impact Area | Assessment |
|-------------|------------|
| Customer impact | |
| Financial exposure | |
| Service disruption | |
| Reputational risk | |
| Regulatory exposure | |

### 2. Situation Summary
Two to three sentences maximum. What happened, what is
confirmed, and what is the current status. Written for
an audience with no security background.

### 3. Actions Taken
What the security team has already done:
1. [Action], [team responsible], [outcome or status]
2. [Action], [team responsible], [outcome or status]
3. [Action], [team responsible], [outcome or status]

### 4. Decision Points Requiring Leadership Attention
Decision points for leadership, with context for each:
1. [Decision point], [why this requires leadership attention now]
2. [Decision point], [why this requires leadership attention now]
3. [Decision point], [why this requires leadership attention now]

### 5. Recommended Actions
Actions the security team recommends leadership
authorize or support, with named owner:
1. [Action], [team requesting authorization], [expected outcome]
2. [Action], [team requesting authorization], [expected outcome]
3. [Action], [team requesting authorization], [expected outcome]

### 6. Next Update and Next Steps
When leadership should expect the next briefing and
what new information will be available by then.

Next steps underway before that briefing:
| Next Step | Owner | Expected By |
|-----------|-------|-------------|
| | CTI / SOC / Legal / Fraud / IR | |
</output_format>

<guidelines>
1. No CTI language, technical indicators, or attack
   chain detail, if a technical concept is necessary,
   explain it in one plain-language sentence
2. Lead with business impact, executives need to
   understand consequences before context
3. Decision points must be specific, surface what
   requires a leadership decision, not what CTI has
   already decided
4. Name the owning team for every action and next
   step, leadership needs to know who is responsible
   without having to ask
5. Keep the brief to one page, if the output exceeds
   one page, compress the impact assessment and
   recommended actions
6. Do not use em dashes anywhere in the output.
   Use a comma, colon, or period instead.
7. Do not estimate financial figures, regulatory conclusions, or other specifics that are not in the source. Mark any such field "To be determined by [owner]" rather than inventing a plausible value.
</guidelines>
```

## Notes
How to action the output: share directly with executive leadership (it is formatted for that audience); use the decisions required section to drive the executive conversation; file as part of the incident record to document that executive notification occurred and what information was shared.
