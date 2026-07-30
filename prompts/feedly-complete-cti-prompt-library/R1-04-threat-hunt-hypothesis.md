# Threat hunt hypothesis

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Threat Hunting Prompts

## What this prompt does
Converts threat intelligence into actionable hunt hypotheses that analysts can immediately execute against their environment, providing the specific log sources and patterns needed to find adversary activity. It is aimed at threat hunters building proactive hunt campaigns and detection engineers needing detailed technical procedures. Output is a table of attack procedures framed as hunt hypotheses plus prioritization notes.

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
Create a table of attack procedures as threat hunt hypotheses. Go through the [data] and for each attack procedure, document the information specified below.
</task>

<output_format>
## 1. Threat Hunt Hypotheses Table

Create a table with the following columns:
| Procedure | Description | Logs |
|-----------|-------------|------|
| Short title of the procedure | Detailed description with patterns | Relevant logs and Event IDs |

## 2. Prioritization Notes
1. High-priority hypotheses based on relevance to your environment
2. Quick wins vs. comprehensive hunts
3. Required data sources and gaps
</output_format>

<guidelines>
1. Provide detailed technical information for each procedure
2. Include only actionable procedures for threat hunting
3. Focus on specific search patterns and detection logic
4. Avoid generic or ambiguous information
5. Prioritize hypotheses relevant to the specified industry and region
6. Include citations to source material
</guidelines>
```

## Notes
- Take each procedure from the table and execute the hunt in your SIEM or EDR using the provided log sources and search patterns.
- Build detection rules based on the procedures that produce positive findings.
- Share the table with your threat hunting team as a backlog of hunt hypotheses prioritized by relevance to your organization.
