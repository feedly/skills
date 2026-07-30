# Industry threat intelligence report

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Intelligence Product Prompts

## What this prompt does
Produces sector-specific threat reports that help organizations understand the threat landscape relevant to their industry rather than generic threats, with best practices and recommendations tailored to sector-specific challenges and regulatory requirements. It serves CTI analysts creating leadership or board briefings, security operations teams tracking sector-targeting threats, and risk management teams assessing industry-specific risk. Output is a full industry report from executive summary through case studies.

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
Generate an Industry-specific Cybersecurity Report focused on the [Industry] sector using the [data].
</task>

<output_format>
## 1. Title
[Industry] Sector Cybersecurity Threat Report - [Date Range]

## 2. Executive Summary
High-level overview of the threat landscape for the sector.

## 3. Industry Threat Landscape
1. Active threat actors targeting the sector
2. Prevalent attack vectors
3. Trends and shifts in adversary behavior

## 4. Notable Incidents and Breaches (if mentioned)
1. Incident 1: Description, impact, lessons learned
2. Incident 2: Description, impact, lessons learned

## 5. Regulatory and Compliance Landscape (if mentioned)
1. Recent regulatory changes
2. Compliance implications
3. Enforcement trends

## 6. Attacker Motivations and Targets (if mentioned)
1. Primary motivations (financial, espionage, disruption)
2. High-value targets within the sector
3. Data and assets at risk

## 7. Industry-Specific Challenges (if mentioned)
1. Unique vulnerabilities
2. Legacy system risks
3. Supply chain considerations

## 8. Best Practices and Recommendations
1. Immediate actions
2. Short-term improvements
3. Long-term strategic initiatives

## 9. Case Studies (if mentioned)
1. Case study 1: Context, attack details, response, outcomes
2. Case study 2: Context, attack details, response, outcomes
</output_format>

<guidelines>
1. Focus on threats and incidents relevant to the specified industry
2. Include sector-specific regulatory and compliance context
3. Provide actionable best practices tailored to industry challenges
4. Balance technical detail with executive-level accessibility
5. Highlight trends that indicate future threat evolution
6. Include citations to source material
</guidelines>
```

## Notes
- Use the notable incidents section to brief stakeholders on real-world attacks affecting peer organizations.
- Implement the best practices and recommendations to improve defensive posture against sector-specific threats.
- Share the report with board members or executives as part of quarterly threat briefings.
