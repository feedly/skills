# Cross-functional course of action

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 3: Coordinate with fraud, SOC, and risk, Prompt 6

## What this prompt does
Makes cross-team dependencies explicit so coordination does not stall. It maps what each team (fraud, SOC, risk, CTI) needs to do, in what order, and what each team is waiting on from the others, producing a course of action brief designed to be read across teams without requiring a joint call.

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
I need to coordinate action across fraud, SOC, and risk teams
based on the intelligence below, mapping what each team needs
to do, in what order, and what dependencies exist between teams
so that coordination happens without requiring a joint call.
</context>

<task>
Using the intelligence pasted below, which may be a
multi-stakeholder impact brief, enriched intelligence report,
or any CTI output, produce a cross-functional course of action brief.

For each team, identify their required actions, the
intelligence basis for those actions, and what they are
dependent on from other teams before they can proceed.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE INTELLIGENCE OR IMPACT BRIEF HERE]
</task>

<output_format>
## Cross-Functional Course of Action Brief

### 1. Situation Summary
One paragraph, what happened, what is confirmed,
what is still being assessed. Written for all teams
to read as shared context before reviewing their
specific actions.

### 2. Team Action Mapping
| Team | Required Action | Intelligence Basis | Priority | Dependency |
|------|----------------|-------------------|----------|------------|
| SOC | | | Immediate / 24hr / 72hr | Waiting on: |
| Fraud | | | Immediate / 24hr / 72hr | Waiting on: |
| Risk | | | Immediate / 24hr / 72hr | Waiting on: |
| CTI | | | Immediate / 24hr / 72hr | Waiting on: |

### 3. Sequencing
Based on dependencies above, the recommended action
sequence is:
1. [First action, team responsible]
2. [Second action, team responsible]
3. [Third action, team responsible]

### 4. Shared Indicators
IOCs and behavioral indicators all teams should be
monitoring regardless of their specific actions:
| Indicator | Type | All Teams: Monitor For |
|-----------|------|----------------------|
| | | |

### 5. Open Items
| Item | Owner | Required By |
|------|-------|-------------|
| | | |
</output_format>

<guidelines>
1. The situation summary must be written for a mixed
   audience, avoid CTI-specific language that fraud
   or risk teams would not understand
2. Dependencies must be explicit, "waiting on SOC
   containment confirmation" is actionable,
   "pending further analysis" is not
3. Sequencing should reflect operational reality,
   list actions in the order they must happen,
   not the order they are discovered
4. Open items should be specific enough to be tracked
   without a follow-up conversation
5. Do not use em dashes anywhere in the output.
   Use a comma, colon, or period instead.
6. Base every action and shared indicator strictly on the provided intelligence. Where the basis for an item is not in the source, mark it "Unknown, confirm before action" rather than inventing details.
</guidelines>
```

## Notes
How to action the output: share the full course of action brief with all team leads simultaneously (it is designed to be read across teams, not just within one); use the dependency mapping to sequence actions correctly before any team starts work; track open items at the bottom of the brief as the live coordination record until the incident is resolved.
