# Phishing awareness newsletter

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Risk & threat assessment prompts (Prompt 11)

## What this prompt does
Writes a Phishing Awareness Newsletter for a non-technical, general audience, summarizing the phishing themes observed in the source data for a reporting period. It translates technical reporting into plain language an employee with no security background can act on, basing trends and the weekly focus only on what appears in the source.

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
[job role]: Threat Intelligence Analyst supporting the Security Awareness team
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: all staff (non-technical, general audience)
[product/service]: Phishing Awareness Newsletter
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[reporting period]: the past week
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] with a [product/service] covering [reporting period], using the phishing reporting in [data]. The audience is non-technical and busy, so the newsletter must read at a high school level and stay clear, concise, and engaging.
</context>

<task>
Write a Phishing Awareness Newsletter for a non-technical, general audience, summarizing the phishing themes observed in [data] for [reporting period]. Translate technical reporting into plain language an employee with no security background can act on. Base the trends and the weekly focus ONLY on what appears in [data]; do not invent campaigns, statistics, or examples.
</task>

<output_format>
Return a Markdown newsletter with consistent headers and short sections, in this order:

## [Catchy Headline]
A short introduction of two to three sentences explaining why phishing is a current risk this period.

## Phishing Trends This [Period]
The common phishing themes observed in [data] (e.g. fake package delivery, QR code scams, MFA fatigue), as short paragraphs or bullet points. Each theme should be one or two plain-language sentences. Use only themes present in the source.

## Tips You Can Use Right Now
Three to five practical, immediately actionable security awareness tips, as a bulleted list. Each tip is one to two sentences and describes a concrete action (e.g. "Hover over a link before you click to see where it really goes").

## Education Topic of the Week: [Topic]
Highlight one topic (e.g. QR code phishing). Two short paragraphs: what it is in plain language, and how to stay safe.

## A Quick Reminder
A friendly closing of one to two sentences reinforcing that staying alert protects both the individual and the organization, and noting how to report a suspicious message.
</output_format>

<guidelines>
1. Write at a high school reading level. No jargon, and no acronyms except widely known ones; spell out or briefly explain anything technical (e.g. "MFA, the code or prompt you approve when logging in").
2. Base the trends, the weekly focus, and any examples ONLY on [data]. Do not invent campaigns, brand names, statistics, or incidents. If [data] is thin, cover fewer themes rather than padding.
3. Keep it professional and encouraging. Do not blame or alarm readers; the goal is confidence and action, not fear.
4. Keep sections short and scannable: headers, bullets, and brief paragraphs for busy readers.
5. Make every tip concrete and immediately doable, not abstract advice like "be careful online."
6. Do not use emojis.
7. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Share the draft into your newsletter template and confirm every trend traces to this period's reporting before your security awareness lead sends it to employees, pairing the Education Topic of the Week with a lunch-and-learn to reinforce the message. Used as an optional step of Chain 4 when the threat is socially engineered.
