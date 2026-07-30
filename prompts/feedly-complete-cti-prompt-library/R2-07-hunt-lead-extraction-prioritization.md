# Hunt lead extraction and prioritization

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Threat hunting prompts (Prompt 6), contributed by Nathan Hoffman, Security Data Engineer

## What this prompt does
Reads the source intelligence and breaks it into a prioritized list of candidate threat hunt leads, where a hunt lead is a specific, observable adversary behavior or artifact worth investigating (not yet a formed hunt hypothesis). It surfaces and ranks candidate leads with ATT&CK mapping, relevance, confidence, and citations, without writing detection logic or hypotheses.

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
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: threat hunting team
[product/service]: prioritized threat hunt lead list
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service]. The output will be used to decide which leads are worth scoping for a hunt, so it needs to surface and rank candidate leads, not write the hunt itself.
</context>

<task>
Read the [data] and break the intelligence down into a prioritized list of candidate threat hunt leads. A hunt lead is a specific, observable adversary behavior or artifact worth investigating in our environment. It is not yet a formed hunt hypothesis. Do not write detection logic, search queries, or hypotheses at this stage.
</task>

<output_format>
## 1. Lead Summary
Two or three sentences describing the most significant hunt-worthy activity in the source.
## 2. Prioritized Hunt Lead Table
| Lead ID | Hunt Lead (observable behavior or artifact) | Associated ATT&CK Technique (ID and name) | Threat actor / malware / campaign | Relevance to [sector name] and [country/region] | Data likely needed to hunt | Priority (High / Medium / Low) | Confidence (High / Medium / Low) | Source citation |
|---|---|---|---|---|---|---|---|---|
Always print the complete table. If this is a re-run or revision, re-emit every row, not only the rows that changed.
## 3. Leads Needing Analyst Review
Leads where the source evidence is ambiguous or insufficient to rank, with one line on what is missing.
## 4. Signals Considered but Discarded
Activity from the source that is not hunt-worthy (for example fully patched issues or behavior with no observable telemetry), each with a one-line reason.
## 5. Validation Status
State which ATT&CK IDs you confirmed against the matrix, which need a human check, and that prioritization reflects the source plus assumed typical telemetry, not the reader's actual environment.
</output_format>

<guidelines>
1. Use information from the [data] ONLY. If a detail is not in the source, write "Not stated in source" rather than filling the gap with general knowledge.
2. Do not write search queries, detection rules, or full hunt hypotheses. This prompt produces leads; scoping and hypotheses come later.
3. Prioritize leads by relevance to the specified sector and region, and by how observable the behavior is likely to be in typical telemetry.
4. Use estimative probability language rather than absolute statements, and assign a confidence level to every lead: High when the source states the behavior explicitly, Medium when it is implied or partially described, Low when it is only suggested.
5. Be specific. A good lead reads "Scheduled task created under \Microsoft\Windows\ for persistence (T1053.005)"; a weak lead reads "the actor used persistence."
6. Do not fabricate ATT&CK IDs, threat actor names, malware names, or campaigns. Use the correct technique for the behavior and use technique semantics correctly (for example, classify a port as standard or non-standard correctly, and pick the sub-technique that matches the protocol or mechanism actually described). If the technique is unclear, write "Unmapped, analyst review needed."
7. Cite the source for each lead.
8. Before you finish, verify each lead against the source, confirm every ATT&CK ID exists and is the best fit, and confirm the full table was emitted. Flag any you could not confirm.
9. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Turns a dense report into a ranked shortlist of hunt-worthy leads, separating "worth a look" from "worth a full hypothesis". Take the High-priority leads into the feasibility prompt (Prompt 7) before assigning them to hunters, and feed the leads you pursue into your hunt hypothesis prompt to build the actual searches. This is step 1 of Chain 2 (Report to prioritized, feasible hunt).
