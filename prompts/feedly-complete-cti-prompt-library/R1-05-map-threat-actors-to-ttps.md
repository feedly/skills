# Map threat actors to TTPs

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Threat Hunting Prompts

## What this prompt does
Extracts which tactics and techniques multiple threat actors are using, helping teams prioritize defenses based on adversary behavior rather than theoretical threats, and identifies emerging TTP trends that signal shifts in adversary behavior. It serves CTI analysts tracking how actors evolve, security operations teams deciding where to focus defensive resources, and CTI managers reporting landscape trends. Output is a separate MITRE-linked TTP table per threat actor, emerging TTP analysis, and recommendations.

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
Map threat actors and their corresponding Tactics, Techniques, and Procedures (TTPs) using the [data]. For each threat actor mentioned, create a separate table.
</task>

<output_format>
## 1. Threat Actor TTP Mapping

### [Threat Actor Name]
| MITRE Tactic | Technique ID & Name (linked to attack.mitre.org) |
|--------------|--------------------------------------------------|
| Initial Access | T1566 - Phishing |

(Repeat table for each threat actor)

## 2. Emerging TTP Analysis
1. Are there emerging TTPs that are becoming more prevalent?
2. Which techniques are shared across multiple threat actors?
3. What defensive gaps do these TTPs reveal?

## 3. Recommendations
1. Priority techniques to detect based on prevalence
2. Defensive improvements aligned to observed TTPs
</output_format>

<guidelines>
1. Create a separate table for each threat actor identified in the [data]
2. Link all MITRE ATT&CK technique IDs to attack.mitre.org
3. Identify patterns and emerging TTPs across multiple actors
4. Prioritize TTPs relevant to the specified industry and region
5. Provide actionable recommendations based on the analysis
6. Include citations to source material
</guidelines>
```

## Notes
- Use the TTP mappings to assess your detection coverage against active threat actors targeting your sector or geography.
- Prioritize defensive improvements using MITRE D3FEND based on TTPs used by multiple threat actors.
- Track the emerging TTPs identified by the prompt to stay ahead of adversary innovation.
