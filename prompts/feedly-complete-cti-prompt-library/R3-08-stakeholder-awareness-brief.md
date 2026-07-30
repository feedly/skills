# Draft a stakeholder awareness brief

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 5: Creating detection rules, hunt hypotheses, and briefs, Step 4: Draft the stakeholder brief

## What this prompt does
This prompt translates the validated analysis into a short, plain-language awareness note for a non-technical audience (e.g., senior leadership): what the threat is, whether you appear exposed, the likely business impact in estimative terms, and what you are doing plus any decision needed from leadership.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[data]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: senior leadership
[data]: the validated analysis provided below
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to tell [stakeholder team names], in plain language, that we are aware of a threat, what it means for us, and what we are doing.
</context>

<task>
Using the validated analysis in [data], draft a short awareness note for a non-technical audience.
</task>

<output_format>
Four short paragraphs, with headers and a brief title:
0. Title: Intelligence brief [insert suitable title, including name of threat]
1. What the threat is, in plain language.
2. Whether we appear exposed. [ANALYST CONFIRMS]
3. The likely business impact, in estimative terms.
4. What we are doing, and any decision we need from leadership.
</output_format>

<guidelines>
1. Keep the whole note under 150 words (excluding title and headers).
2. Use estimative language (likely, probable, possible). No fear-uncertainty-doubt framing and no absolute claims.
3. Do not include technical indicators or jargon; this is for a business audience.
4. Leave the exposure statement for the analyst to confirm; mark it [ANALYST CONFIRMS].
5. Base the note only on [data]; do not introduce new claims.
6. Add headers in bold for each section of the brief.
</guidelines>
```

## Notes
- The analyst must confirm the exposure statement ([ANALYST CONFIRMS]) before the note circulates, a note that overstates exposure damages credibility more than saying you are still assessing.
