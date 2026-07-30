# Fraud-cyber assessment

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 2: Enrich, assess relevance and impact, Prompt 4

## What this prompt does
Takes enriched threat intelligence and produces a fraud-specific impact assessment, mapping threat activity to payment authorization and identity verification risk in fraud language before it reaches the fraud team. It maps cyber activity to known fraud types (BEC, payment redirection, ATO, SIM swap) and flags mule network indicators and monitoring gaps.

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
[stakeholder team names]: Fraud and SOC Teams
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
I need to produce a fraud-specific impact assessment of enriched
cyber threat intelligence, mapping threat activity to payment
authorization and identity verification risk before it reaches
[stakeholder team names].
</context>

<task>
Using the intelligence pasted below produce a fraud impact assessment.

Map cyber activity to known fraud types: BEC, payment
redirection, ATO, SIM swap. Assess direct risk to payment
and identity infrastructure.

If no clear fraud dimension exists, state that explicitly
with rationale.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE THREAT INTELLIGENCE HERE]
</task>

<output_format>
## Fraud Impact Assessment

### 1. Impact Summary, Read First
- Fraud dimension: Confirmed / Probable / Possible /
  Not Identified
- Primary fraud type implicated:
- Recommended immediate action for fraud team:

### 2. Fraud Signal Mapping
| Cyber Indicator | Fraud Type | Payment Type at Risk | Identity System at Risk |
|-----------------|------------|---------------------|------------------------|
| | BEC / Redirection / ATO / SIM Swap | ACH / Wire / Card / RTP | MFA / SSO / Credentials |

### 3. Payment and Identity Risk
| Risk Area | Attack Vector | Recommended Monitoring Adjustment |
|-----------|---------------|-----------------------------------|
| Payment authorization | | |
| Identity verification | | |

*Note: Flag institution-specific thresholds and parameters
before sharing this output with the fraud team.*

### 4. Mule Network Indicators
- Mule activity identified: Yes / No / Unknown
- If yes, describe:

### 5. Gaps
| Gap | Recommended Data Source | Owner |
|-----|------------------------|-------|
| | | Fraud / CTI / SOC |
</output_format>

<guidelines>
1. Do not force a fraud dimension, if no clear fraud
   dimension exists, state that with rationale
2. Payment and identity risks require separate assessments
, they drive different fraud team responses
3. Monitoring adjustments must be immediately operationalizable
, not general best practice guidance
4. Flag all institution-specific thresholds for analyst
   completion before the output is shared
5. Do not use em dashes anywhere in the output.
   Use a comma, colon, or period instead.
6. Base the assessment only on the provided material. Mark any field the source does not support as "Not available in source material" rather than assuming it.
</guidelines>
```

## Notes
How to action the output: use the impact summary to determine whether the threat intelligence has a fraud dimension before it reaches the fraud team; use the payment and identity risk section to identify which monitoring thresholds need flagging before any cross-functional briefing begins; use the gaps section to identify what fraud-side data would complete the picture before moving into cross-functional coordination.
