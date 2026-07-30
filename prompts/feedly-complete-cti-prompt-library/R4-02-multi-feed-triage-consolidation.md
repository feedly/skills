# Multi-feed triage consolidation

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 1: Detect and triage, Prompt 2

## What this prompt does
Consolidates threat data pulled from multiple sources (open source feeds, commercial threat feeds, internal telemetry, OSINT) into a single prioritized triage output. It scans across sources for correlations, shared IOCs, overlapping infrastructure, or behavioral patterns, before producing the full breakdown, so cross-source patterns are not missed.

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
[stakeholder team names]: SOC and Fraud Teams
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
I have received threat data/information from multiple feeds, open source feeds, commercial threat feeds, internal telemetry, and OSINT. My goal is to consolidate these into a single prioritized triage output for [stakeholder team names].
</context>

<task>
Review the threat data/information below from multiple sources and produce a consolidated triage assessment.

Before producing the full assessment, scan all threat data/information for correlations first, shared IOCs, overlapping infrastructure, or behavioral patterns that appear across more than one source. If a correlation materially changes
the severity of any threat data/information, flag it in the correlation key before the full breakdown.

For each piece of information/data source, determine BFSI relevance and recommended prioritization. If any signal is sparse or incomplete, flag what enrichment is needed before a priority decision can be made.

Before using this prompt, confirm all threat data/information has been sanitized in accordance with your institution's data handling and TLP compliance requirements.

[PASTE THREAT DATA/INFORMATION HERE, label each with its source,
e.g., CISA / Mandiant / Krebs on Security / Telegram / Internal]
</task>

<output_format>
## Multi-Feed Triage Summary

### BLUF
Two to three sentences maximum. What the combined threat data/information picture shows, whether correlations exist, and the single most important action required right now.

### Correlation Key
Define any threat data correlations before the table.
If none exist, state: "No correlations identified."
| ID | Correlation | Data Involved | Severity Impact |
|----|-------------|-----------------|-----------------|
| C1 | | | Elevated / Critical |
| C2 | | | Elevated / Critical |

### Data Comparison
| Data | Source | BFSI Relevant? | Correlation | Prioritization | Immediate Action | Owner |
|--------|--------|----------------|-------------|-------------|-----------------|-------|
| | CISA / Mandiant / Krebs on Security / Telegram / Internal | Yes / No / Possible | C1, C2 / None | Escalate / Enrich / Close | | SOC / Fraud / CTI / Risk |

### Enrichment Needed
For data prioritized and tagged as Enrich:
| Data | What Is Needed | Suggested Source | Owner |
|--------|---------------|-----------------|-------|
| | | | |

If no data require enrichment, state: "No enrichment required at this time."
</output_format>

<guidelines>
1. Always scan for threat data correlations before producing the full breakdown, a shared IOC between an external alert and internal telemetry should always be treated as elevated priority
2. If a correlation changes overall incident severity, define it in the correlation key before anything else, do not bury it after the data inventory
3. If threat data/information arrives in inconsistent formats, note where format gaps affect confidence in the assessment
4. If no correlations exist, state that outcome. Do not invent correlations if none exist.
5. Do not use em dashes anywhere in the output. Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: act on critical correlations immediately; prioritize threat data based on triage (escalate, enrich, or close); if a correlation elevates severity, treat it as a new incident and carry the consolidated assessment into Function 2.
