# Threat trend identification

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Trends and feedback synthesis prompts (Prompt 8)

## What this prompt does
Identifies and ranks the most significant threat trends in structured source data for a reporting period, ranking them by evidence weight and grounding every claim in specific data points. A trend must recur across multiple independent data points, not a single noteworthy event. The output is a ranked set of trends with analyst-commentary placeholders for human judgement before publication.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[product/service]:
[data]:
[reporting period]:
** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: senior security leadership and executive stakeholders
[product/service]: threat trend identification report
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[reporting period]: the last calendar quarter
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service] covering [reporting period], using structured data from [data]. The output is a ranked set of identified threat trends, which an analyst will refine before publication.
</context>

<task>
Identify and rank the most significant threat trends in the [data] for [reporting period]. Rank them by evidence weight, describe each in a tone appropriate for senior stakeholders, and ground every claim in specific data points from the source. A trend is a pattern that recurs across multiple independent data points, not a single noteworthy event.
</task>

<output_format>
Return Markdown with this structure:
### Threat trends for [reporting period]
A two-to-three sentence framing paragraph describing the most important pattern in the period's data.
#### Trend 1: [short descriptive title] (Evidence: N data points; Confidence: High / Medium / Low)
- Two or three sentences describing the trend.
- A bulleted list of the supporting data points from [data], each with its source identifier (e.g. "MISP event 12345", "CVE-2026-NNNNN", "Jira ticket CTI-456").
- One sentence on the implication for the organization, marked as a placeholder for analyst commentary: `[ANALYST: insert organization-specific implication here]`.
Repeat the Trend structure for each of the top three to five trends.
#### Outlook for next period
Two or three sentences on what the data suggests for the next reporting period, marked as a placeholder for analyst commentary: `[ANALYST: insert outlook here]`.
#### Validation status
One or two sentences confirming every cited data point appears in [data], the evidence counts are accurate, and the analyst placeholders still require human judgement before publication.
</output_format>

<guidelines>
1. Every trend must be supported by at least three independent data points from [data]. If fewer than three support a candidate trend, omit it or flag it as "isolated signal worth monitoring". State the evidence count in the trend header.
2. Reference each data point by its source identifier so the analyst can trace it back to the source.
3. Set the per-trend confidence by evidence weight: High for many consistent data points, Medium for a moderate or mixed set, Low for thin or conflicting evidence.
4. Do not invent data points that are not in [data]. If a claim cannot be supported from the source, omit it.
5. Do not write the analytic commentary or organization-specific implications. Leave those as analyst placeholders.
6. Use estimative probability language ("the evidence suggests", "it appears that", "the data is consistent with") rather than absolute statements.
7. Before you finish, verify that every data point cited appears in [data], that each included trend meets the evidence threshold, and that the stated evidence counts are accurate. Derive each trend's evidence count by counting the specific source identifiers you listed for it, not from memory, and move any trend below the threshold to an "isolated signal worth monitoring" note rather than dropping or padding it.
8. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Takes the most data-heavy part of a recurring threat report and identifies and ranks the trends for you to refine. Write the analyst commentary into the placeholders (the "so what for our organization" the model leaves to you), and confirm each trend appears across multiple data points before you send it to leadership.
