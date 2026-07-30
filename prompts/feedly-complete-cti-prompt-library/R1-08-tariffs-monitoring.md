# Tariffs monitoring

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Geopolitics Prompts

## What this prompt does
Tracks tariffs that can impact supply chains, vendor relationships, and business operations for global organizations, providing structured updates that non-technical stakeholders can use to understand business risk from government policy changes. It serves CTI analysts monitoring geopolitical risk, risk management teams assessing vendor-ecosystem impact, and leadership needing concise strategic updates. Output covers an overview, a proposed-tariffs table, an outlook, and a conclusion with monitoring indicators.

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
Generate an update on recent news about U.S. Tariffs using the [data] and any relevant current information.
</task>

<output_format>
## 1. Overview
Include an overview of the current tariff situation and recent developments.

## 2. Proposed Tariffs
| Parties Involved | Amount/Rate | Industries Impacted | Effective Date |
|------------------|-------------|---------------------|----------------|
| Country/Entity   | X%          | Industry names      | Date           |

## 3. Outlook
Provide the outlook going forward, including:
1. Expected timeline for implementation
2. Potential escalation or de-escalation scenarios
3. Impact on supply chains and operations

## 4. Conclusion
1. Key takeaways for my organization
2. Recommended monitoring indicators
3. Suggested preparatory actions
</output_format>

<guidelines>
1. Focus on tariffs relevant to the specified industry and region
2. Include both enacted and proposed tariffs
3. Provide context for how tariffs may impact supply chains and vendor relationships
4. Identify indicators to monitor for policy changes
5. Prioritize actionable intelligence for business decisions
6. Include citations to source material
</guidelines>
```

## Notes
- Share the outlook section with procurement and vendor risk management teams to inform vendor risk assessments.
- Use the table of impacted industries to identify which parts of your supply chain may face disruption.
- Monitor the conclusion for indicators that should trigger contingency planning.
