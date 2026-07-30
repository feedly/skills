# Diamond model of intrusion analysis

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Cyberattack Prompts

## What this prompt does
Transforms unstructured threat intelligence into a standardized Diamond Model framework, structuring findings across the four key elements (Adversary, Infrastructure, Capabilities, Victimology) to reveal relationships between attacks that might otherwise be missed. It is designed for CTI analysts producing threat assessments or incident analysis, and incident response teams documenting intrusions. The output includes a visual diamond diagram plus text analysis grounded only in the provided reports.

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
If no value is provided for a variable (left blank after colon),
use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: technical security stakeholders
[product/service]: Threat intelligence report
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with [product/service].
</context>

<task>
Conduct a Diamond Model of Intrusion Analysis using all pertinent information from the [data]. Additionally, create an image of the diamond model that depicts the key findings.
</task>

<output_format>
## 1. Diamond Model Analysis

### 1.1 Adversary
1. Threat Actor Name/Alias (if known or attributed)
2. Suspected Origin/Nation-State Affiliation
3. Motivation (financial, espionage, hacktivism, destruction)
4. Confidence Level in Attribution (low/medium/high)
5. Known Threat Group Associations

### 1.2 Capabilities
1. Malware Families/Tools Used
2. Exploits & CVEs Leveraged
3. MITRE ATT&CK Techniques Observed
4. Level of Sophistication (commodity, custom, advanced)
5. Delivery Mechanisms

### 1.3 Infrastructure
1. Command & Control Domains/IPs
2. Hosting Providers & ASNs
3. SSL/TLS Certificate Fingerprints
4. Email Addresses or Sender Domains
5. Pivot Points for Further Investigation

### 1.4 Victim
1. Targeted Sectors/Industries
2. Geographic Focus
3. Victimology Patterns (size, technology stack, access value)
4. Known Compromised Organizations (if public)

## 2. Meta-Features
1. Timestamps & Campaign Duration
2. Phase of Attack (initial access, persistence, exfiltration)
3. Direction of Attack
4. Methodology Notes

## 3. Analytical Confidence & Intelligence Gaps
1. What is confirmed vs. assessed
2. Key unknowns or collection gaps
3. Recommended pivots for further analysis

## 4. Indicators of Compromise (IOCs)
Table of actionable IOCs with type, value, and context

## 5. Diamond Model Visualization
Generate an image of the Diamond Model (e.g., SVG, PNG) with the four vertices (Adversary, Capabilities, Infrastructure, Victim) arranged as a diamond shape. Place key findings from the analysis at each vertex. Use the following specifications:
- Diamond shape with vertices at top (Adversary), right (Capabilities), bottom (Victim), left (Infrastructure)
- Connect all four vertices with lines showing relationships
- Include 2-3 key bullet points at each vertex summarizing critical findings
- Add a center label with the threat actor name or campaign identifier
- Use a clean, professional color scheme appropriate for security reporting
If you cannot produce an image, create an ASCII/text-based diagram of the Diamond Model

## 6. Recommendations
1. Immediate containment actions
2. Detection rules to deploy
3. Hunting hypotheses based on findings
</output_format>

<guidelines>
1. Extract detailed technical information from [data]
2. Ensure all elements (Adversary, Infrastructure, Capabilities,
Victimology) are addressed. Fill sections with details from the
provided data ONLY. If information for any element is not available in the source material, explicitly state 'Not available in provided reports' rather than filling gaps with generic knowledge
3. Provide accurate and actionable intelligence
4. Include citations and references where applicable using inline citations
5. Prioritize information relevant to the specified industry and region
6. VERY IMPORTANT: generate an image AND text in the response
</guidelines>
```

## Notes
- Use the structured output to brief stakeholders on attack patterns without requiring them to read full intelligence reports.
- Create visual diagrams showing adversary relationships and infrastructure that can be shared across security operations and threat hunting teams.
