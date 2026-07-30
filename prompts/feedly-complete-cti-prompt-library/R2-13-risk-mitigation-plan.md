# Risk mitigation plan

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Risk & threat assessment prompts (Prompt 12)

## What this prompt does
Synthesizes threat reporting into a risk mitigation plan tailored to your technology stack. It ties every mitigation, detection, and impact judgment to a specific finding in the reporting, tailors implementation to the tools in the stack summary, and covers threat summary, attack vector analysis, impact assessment, technical indicators, prioritized mitigations, detection opportunities, and gaps.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[product/service]:
[data]:
[stack summary]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: SOC, IT operations, and security leadership stakeholders
[product/service]: risk mitigation plan
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[stack summary]: Not provided. Give general implementation guidance, list the tooling each action would require, and mark coverage as "unknown, confirm against your stack."
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service], working from [data]. Our technology environment (logging sources, detection tooling, and key controls) is described in [stack summary].
</context>

<task>
Synthesize the threat reporting in [data] into a risk mitigation plan tailored to [stack summary]. Base ALL information strictly on what the source articles explicitly state; do not add background or context not present in the provided materials. Tie every mitigation, detection, and impact judgment to a specific finding in the reporting, and tailor implementation to the tools in [stack summary]. Do not fabricate IOCs, CVEs, TTPs, or tooling.
</task>

<output_format>
Return a Markdown report with these sections in order:

## 1. Threat Summary
Two to three sentences on what the threat is, who is behind it (if attributed), and its current activity status. Then:
- **Threat Actor/Origin**: named actor, or "Unattributed."
- **Campaign Status**: Active / Emerging / Historical.
- **Targeting**: specific industries, regions, or organization types named in the reporting.

## 2. Attack Vector Analysis
| Attack Phase | Technique Observed | Source Article Reference |
|--------------|--------------------|--------------------------|
Cover every attack phase mentioned across the articles (Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact). Be specific about the exact method (e.g. "Spearphishing with malicious PDF attachment", not "phishing"). If attack vector detail is limited, state "Attack vector details not comprehensively addressed in available reporting."

## 3. Impact Assessment
**Systems at Risk** (based on [stack summary]): for each relevant system/service, the specific risk per the articles, with the supporting article. Mark systems not mentioned in the reporting as "Not identified as at-risk in available reporting."
**Potential Business Impact**: impact types named in the articles (Data Breach, Operational Disruption, Financial Loss, Reputational Damage) with a severity (Critical/High/Medium/Low) and rationale from the reporting.
If [stack summary] does not align with the threat's targeting, note this explicitly as a reduced risk factor with rationale.

## 4. Technical Indicators
**CVEs Referenced**
| CVE ID | Affected Product | CVSS | Exploit Status | Patch Available |
|--------|------------------|------|----------------|-----------------|
(CVSS "Not specified" if absent; Exploit Status PoC/In-the-wild/Theoretical; Patch Available Yes/No/Unknown, per the articles.)
**MITRE ATT&CK TTPs**
| Tactic | Technique ID | Technique Name | Observed Usage |
|--------|--------------|----------------|----------------|
**Indicators of Compromise**
| Type | Value | Context |
|------|-------|---------|
Include all IOCs mentioned (IPs, domains, hashes, file paths, registry keys, user agents). If none, state "No specific IOCs included in available reporting." Do not generate or infer IOCs.

## 5. Risk Mitigation Recommendations
| Priority | Action | Specific Implementation (for [stack summary]) | Addresses (finding/TTP) | Owner |
|----------|--------|-----------------------------------------------|-------------------------|-------|
| IMMEDIATE (24 hrs) | ... | ... | ... | ... |
| SHORT-TERM (72 hrs) | ... | ... | ... | ... |
| MEDIUM-TERM (30 days) | ... | ... | ... | ... |
Each recommendation must counter a specific technique/vulnerability/finding cited in the articles, include implementation specifics tailored to [stack summary], be actionable, and cite the article finding. Do NOT include generic advice ("update systems", "train users") without specific context, and do not recommend tools not in [stack summary]. If the reporting lacks the detail to be specific, state "Available reporting does not contain sufficient technical detail to provide actionable mitigation steps beyond [list what IS supported]."

## 6. Detection Opportunities
| Detection Method | Tool (from [stack summary]) | Query/Rule Logic | What It Detects |
|------------------|------------------------------|------------------|-----------------|
Detection Method = type (Log analysis, EDR alert, Network monitoring, SIEM correlation). Provide pseudocode or search syntax that could be implemented. Base detections on IOCs and TTPs in the articles and the capabilities of [stack summary]. If the stack cannot detect an aspect, note "Detection of [technique] not feasible with current tech stack; consider [capability type] enhancement."

## 7. Gaps and Uncertainties
- **Information Not Addressed**: aspects of the threat the articles do not cover.
- **Low Confidence Areas**: conflicting reporting or uncertain language.
- **Tech Stack Misalignment**: if the threat mainly targets technologies not in [stack summary], note it.
- **Recommended Follow-up Intelligence Collection**: specific gaps to fill next.
If reporting is comprehensive, state "Available reporting provides comprehensive coverage of this threat with no significant intelligence gaps identified."

## 8. Source Articles Referenced
Numbered list, each as [Article Title] - [Source/Publisher] - [Publication Date], for traceability.
</output_format>

<guidelines>
1. Base ALL findings strictly on what the source articles explicitly state. Do not add outside background or context. Where information is missing, write "Not available in provided reporting" rather than inferring it.
2. Do not fabricate or infer CVEs, IOCs, TTPs, ATT&CK IDs, or tooling. Only include indicators explicitly present in the source. A CVE named in the source is not the same as a verified CVE: if it has no public advisory or NVD record, carry it forward as "UNVERIFIED, confirm against NVD before prioritizing" rather than asserting its severity or exploitation status as fact.
3. Every mitigation and detection must trace to a specific finding in the articles and, where relevant, a specific tool in [stack summary]. Do not recommend tools the user does not have.
4. Tailor implementation specifics to [stack summary]. If it is not provided, give general guidance, list the tooling each action requires, and mark coverage "unknown, confirm against your stack."
5. Exclude generic recommendations ("update systems", "train users", "improve awareness") unless tied to a specific finding and concrete steps.
6. Use estimative probability language (ICD 203) rather than absolute statements, and note conflicting or low-confidence reporting explicitly.
7. Detection logic and any queries are AI-generated; flag them for validation by a detection engineer before deployment.
8. Cite the source article for every finding, technique, indicator, and recommendation.
9. Before you finish, verify each recommendation and indicator against [data] and [stack summary], and flag anything you could not confirm.
10. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Share the IMMEDIATE row with the relevant control owners first, confirming each action maps to a real finding before committing resources, and feed the Gaps and Uncertainties section to your collection manager. This is step 2 of Chain 4 (Report to a risk-translated package), taking the Structured Threat Assessment (Prompt 10) plus your stack summary as input.
