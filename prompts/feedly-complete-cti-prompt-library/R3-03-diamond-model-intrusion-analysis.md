# Populate the Diamond model of intrusion analysis

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 3: Populating the Diamond Model and translating threat into business risk, Step 2

## What this prompt does
This prompt conducts a Diamond Model of Intrusion Analysis (adversary, capabilities, infrastructure, victim) using only the pertinent information in the supplied report/extraction, plus a confidence-and-gaps section. It is intended to run inside a saved Claude Project (or a locally hosted model) preloaded with your standing context, with the source data being the validated extraction and mapping from Workflows 1 and 2. The final risk rating and attribution language are left to the analyst.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[data]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: technical security stakeholders
[data]: the validated extraction and report provided below
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to give [stakeholder team names] a Diamond Model analysis of the intrusion.
</context>

<task>
Conduct a Diamond Model of Intrusion Analysis using all pertinent information in [data]: adversary, capabilities, infrastructure, and victim.
</task>

<output_format>
## 1.1 Adversary
Alias, suspected origin, motivation, attribution confidence, known group associations.

## 1.2 Capabilities
Malware and tools, exploited CVEs, observed ATT&CK techniques (v19), sophistication, delivery.

## 1.3 Infrastructure
C2 domains and IPs, hosting and ASNs, certificate fingerprints, sender domains, pivot points.

## 1.4 Victim
Targeted sectors, geography, victimology patterns, known compromised organizations.

## 2. Confidence and Intelligence Gaps
What is confirmed versus assessed, key unknowns, recommended pivots.
</output_format>

<guidelines>
1. Fill every section from [data] ONLY. Where information for an element is not available, state 'Not available in provided reports' rather than filling the gap with general knowledge.
2. Provide attribution with a confidence level; treat any actor naming as an assessment, not a fact.
3. Use estimative language (likely, probable, possible).
4. Map any techniques to MITRE ATT&CK Enterprise v19 or above.
5. Include inline citations to the source material.
6. Return Markdown only.
</guidelines>
```

## Notes
- Set up a reusable Claude Project (or equivalent saved workspace) loaded with your standing context (sector, region, company profile, public tech-stack info, risk appetite) so you stop re-pasting the same context. Attach the validated extraction and mapping from Workflows 1 and 2 as source data.
- Be careful what you upload; keep standing context to your public, non-sensitive profile. Where the analysis needs sensitive input, run it against a locally hosted model (e.g., via LM Studio).
- The likelihood/impact risk rating (Step 2 of the manual workflow) stays with the analyst, the article does not automate it with a prompt.
