# Geopolitical implications of cyberattacks

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Geopolitics Prompts

## What this prompt does
Analyzes cyberattacks through a geopolitical lens to forecast escalation risks, political responses, and broader impacts beyond technical intrusion details, synthesizing sources in multiple languages to capture narratives that English-only analysis could miss. It serves CTI analysts where geopolitical risk affects operations (especially critical infrastructure) and risk or geopolitical intelligence teams briefing leadership. Output is a long-form report with a BLUF, source analysis, actor profile, forecasts, and indicators to watch.

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
Produce a long-form threat intelligence report on the threat actor's recent campaigns that focuses on the geopolitical risk implications.
</task>

<output_format>
## 1. BLUF Statement
Provide a bottom line up front statement (paragraph format).

## 2. Context on Recent Campaigns
Provide context on recent threat actor campaigns (paragraph format).

## 3. Source Analysis
Flag differences or similarities in narrative between the selected sources in different languages:
1. Source 1 perspective
2. Source 2 perspective
3. Key discrepancies or alignments

## 4. Threat Actor Profile
1. Attribution and confidence level
2. Connection to government(s)
3. Historical activity and evolution
4. Known motivations and objectives

## 5. Geopolitical Risk Implications
Analyze geopolitical risk implications from the campaigns (paragraph format).

## 6. Forecast of Cyber and Political Response
Provide a forecast of likely cyber and political response from the targeted nation (paragraph format).

## 7. Forecast Risk to [Sector] Sector
Provide a forecast risk of similar attacks to the specified sector (paragraph format).

## 8. Mitigations and Recommendations
1. Technical team recommendations
2. Executive team recommendations
3. Strategic planning considerations

## 9. Indicators to Watch
1. Indicator 1
2. Indicator 2
3. Indicator 3
</output_format>

<guidelines>
1. Synthesize sources in multiple languages to capture different perspectives. The report should be in English but use [data] that is in any language.
2. Provide clear attribution with confidence levels
3. Forecast escalation risks and political responses
4. Tailor risk assessment to the specified industry and region
5. Include actionable recommendations for both technical and executive audiences
6. Include citations to source material
</guidelines>
```

## Notes
- Use the forecast sections to inform strategic intelligence recommendations based on forecast adversary or political responses.
- Share the BLUF statement with leadership to communicate geopolitical cyber risk in concise terms.
- Monitor the indicators to watch section for early warning signs of escalation or expanded targeting.
