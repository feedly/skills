# Detection rule to Splunk SPL converter

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Detection engineering prompts (Prompt 4)

## What this prompt does
Extracts all detection rules from the source data and converts them to Splunk SPL format. It reproduces each original rule exactly and in full alongside the conversion, marks approximations inline, documents translation fidelity (data source assumptions, features that could not be represented, counting integrity, escaped metacharacters), and flags the SPL as AI-generated and untested.

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
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Detection Engineer
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: detection engineering team
[product/service]: Splunk SPL detection ruleset
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with [product/service].
</context>

<task>
You are a detection engineering assistant. Extract all detection rules from the [data] and convert them to Splunk SPL format.
</task>

<output_format>
For each detection rule found, output the following structure:
---
***Rule Name:*** [Descriptive name based on what the rule detects]
**Rule Type:** [Sigma / YARA / Snort / KQL / SPL / Other]
**Original Rule:**
[Paste the original rule EXACTLY and IN FULL as written in the source. Do not truncate, summarize, or omit any string, variant, or condition. If the rule is long, reproduce all of it.]
**Splunk SPL:**
[Splunk SPL query here] (NOTE: AI-generated conversion, validate with a detection engineer before deploying.)
Inline in the SPL, mark any line that only approximates the original (for example a byte-offset or filesize check rendered as a regex or length proxy) with a trailing SPL comment noting something like "APPROX: original YARA offset condition". SPL wraps comments in backticks; do not use //, which SPL does not support.
**Translation fidelity:**
- Data source assumed (e.g. file-content index, EDR/FIM file text, network logs) and why the SPL only works against that data.
- Rule features that could NOT be represented faithfully in SPL (for example YARA byte offsets, filesize bounds, base64/wide string modifiers, or nested condition logic) and how each was approximated or dropped.
- Counting integrity: confirm that no string used as a gate condition is also added into a separate hit-count total, so thresholds are not inadvertently inflated.
- Any place where literal strings contain regex metacharacters; confirm they are escaped in the SPL (or matched as literals) so the search runs without error.
**Validation status:**
State that the SPL is AI-generated and untested, that content-matching only works if the relevant file or payload content is indexed, and which approximations need a detection engineer to confirm before use.
---
If the original rule is already Splunk SPL, omit the conversion block and note: "Already in Splunk SPL format."
If no detection rules are found in the [data], output: "No detection rules identified in this data."
</output_format>

<guidelines>
1. Use only the detection rules present in the [data]. Do not invent rules.
2. Preserve the original rule exactly and in full so a reviewer can compare it against the conversion. Truncating the rule is a failure condition.
3. Produce SPL that would run as written: escape regex metacharacters ($ . ( ) | [ ] etc.) in literal strings, or match them as literals, and use valid SPL search and eval/rex syntax.
4. Do not double-count: if a string is used to gate the match, do not also add it into a hit-count that feeds a threshold, or the threshold logic will be wrong.
5. Always flag SPL conversions as AI-generated and requiring validation before deployment, and be explicit that content-matching SPL only works if the relevant file or payload content is actually indexed.
6. Before you finish, re-read the original rule and confirm nothing was dropped, every metacharacter is handled, every approximation is labeled inline, and the counting logic is sound. Flag anything you could not translate.
7. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Review each converted query against the original before deploying with engineers, since fields and data models rarely map one to one, and test in a non-production search before promoting the rules that hold up. Used as step 2 of Chain 1 (Report to Sentinel detection) when you run Splunk rather than Sentinel.
