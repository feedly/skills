# MITRE ATLAS mapping

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** AI threat analysis prompts (Prompt 2)

## What this prompt does
Analyzes source data and maps any relevant AI-related threat activity (threats using AI, abusing AI systems, targeting AI/ML systems, or enabling attacks through AI-related techniques) to the MITRE ATLAS framework. It produces a structured table with per-row confidence and a "review needed" flag so tentative mappings are not read as confirmed, and it avoids forcing a mapping where ATT&CK fits better.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[product/service]:
[data]:
** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst specializing in AI-related threats
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: technical security stakeholders
[product/service]: MITRE ATLAS mapping report
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service].
</context>

<task>
Analyze the [data] and map any relevant AI-related threat activity to the MITRE ATLAS framework.
Create a structured table with the following columns:
- Threat Actor / Software / Campaign
- ATLAS Tactic
- ATLAS Technique
- Mapping Basis
- Procedure
- Evidence From Report
- Reference / URL
- Confidence
</task>

<mapping_guidelines>
- Only map activity that involves threats using AI, abusing AI systems, targeting AI/ML systems, or enabling attacks through AI-related techniques.
- Use MITRE ATLAS tactic and technique IDs, and include both the ID and the technique/tactic name. Confirm the technique sits under the tactic you assign it to. If you cannot confirm the tactic name from memory, append "(verify against live ATLAS matrix)" to it rather than presenting it as certain.
- Do NOT force a mapping. If the behavior is best described by MITRE ATT&CK rather than ATLAS (for example, generic malware development or junk-code obfuscation), write "ATT&CK-only (no suitable ATLAS technique)" in the ATLAS Technique column and name the ATT&CK technique in the Procedure column. If neither applies, write "Unmapped / Analyst Review Needed."
- Do not hallucinate threat actors, campaigns, malware names, or ATLAS IDs.
- Create one row per distinct (actor, technique) pair. Do not list the same actor and technique twice; if one actor uses several techniques, use one row per technique and keep the actor name consistent.
- In the "Mapping Basis" column, state "Source-stated" if the report itself assigns this ATLAS ID, or "Analyst-inferred" if you derived the mapping from the described behavior.
</mapping_guidelines>

<procedure_guidelines>
For the "Procedure" column, explain specifically how the actor, software, or campaign used or targeted AI, based on the source. Avoid generic language.
Good example: "Famous Chollima operators used real-time AI face filters and deepfake technology during video interviews to impersonate stolen identities and bypass hiring verification."
Bad example: "The threat actor used AI for malicious activity."
</procedure_guidelines>

<evidence_guidelines>
For the "Evidence From Report" column, include a short supporting quote or paraphrased detail that justifies the mapping. Do not copy large blocks of text.
</evidence_guidelines>

<confidence_guidelines>
Assign a confidence level to each mapping:
- High: the report clearly describes the behavior and the ATLAS mapping is direct (or the report itself states the ATLAS ID).
- Medium: the behavior is described but the ATLAS mapping requires interpretation.
- Low: the report suggests AI-related activity but the exact technique is uncertain.
If confidence is Low, mark the ATLAS Technique as "Unmapped / Analyst Review Needed" unless there is enough evidence for a tentative mapping.
</confidence_guidelines>

<output_format>
Return the results as a markdown table using the columns above. After the table, add a short "Validation status" line stating which mappings are source-stated (and so need only spot-checking) versus analyst-inferred and any tactic label marked for live-matrix verification.
If no relevant AI-related threat activity is found, return: "No MITRE ATLAS-relevant AI threat activity was identified in the [data]."
</output_format>

<guidelines>
1. Use information from the [data] ONLY. If a detail is not in the source, do not invent it.
2. Use estimative probability language rather than absolute statements.
3. Before you finish, verify each row: confirm the ATLAS ID exists, the tactic is correct or marked for verification, the Mapping Basis is honest, and no (actor, technique) pair is duplicated. Flag any row you could not confirm. Apply the same verification to ATLAS technique IDs as to tactics: tag any ATLAS technique ID or name you cannot confirm from memory with "(verify against live ATLAS matrix)" and treat it as a candidate, not a confirmed mapping.
4. Do not use em dashes anywhere in the output.
5. ATLAS IDs follow the form AML.TXXXX for techniques and AML.TAXXXX for tactics. Do not emit ATT&CK-style T#### IDs for ATLAS mappings.
</guidelines>
```

## Notes
Brings AI-related threat activity into a framework your team can track, with per-row confidence and a "review needed" flag. Brief detection engineering on how AI shows up in real adversary activity, and route "review needed" rows to a senior analyst before publishing. This prompt is the first step of Chain 3 (AI threat activity to detection opportunities), feeding observable mapped techniques into Prompt 3.
