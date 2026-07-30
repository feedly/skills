# Source reliability and credibility evaluator (Admiralty / NATO system)

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Source evaluation prompts (Prompt 1), contributed by Omar Aboelrous, DFIR Analyst at a cybersecurity vendor

## What this prompt does
Evaluates the reliability and credibility of source material using the Admiralty Code (NATO System) to make provenance explicit before intelligence is acted upon. It grades every distinct source, evaluates the key claims they carry, flags provenance problems (single-sourcing, circular reporting, vendor-marketing bias), and assigns an overall confidence statement using ICD 203 estimative language. It assesses the trustworthiness of the reporting, not the threat itself.

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
Evaluate the reliability and credibility of the source material in [data] using the Admiralty Code (NATO System) and produce a source-grading assessment that makes provenance explicit before any intelligence is acted upon. Grade every distinct source, evaluate the key claims they carry, flag provenance problems (single-sourcing, circular reporting, vendor-marketing bias), and assign an overall confidence statement using ICD 203 estimative language. Do NOT assess the threat itself. Assess the trustworthiness of the reporting about it.
</task>

<output_format>
## 1. Source Inventory
List every distinct source identified in [data]. Treat a source as the originating author or organization, not each document.
| # | Source Name/Org | Source Type (vendor blog, gov advisory, researcher, news, social, forum) | Date | Primary or Secondary | Originator (who first reported this, if traceable) |
|---|-----------------|--------------------------------------------------------------------------|------|----------------------|----------------------------------------------------|

## 2. Admiralty Code Grading
Grade each source on reliability (A to F) and each key claim on credibility (1 to 6). Reliability assesses the SOURCE's track record and competence. Credibility assesses whether the INFORMATION is corroborated and plausible. Do not conflate the two.

**Reliability scale (source):** A = Completely reliable; B = Usually reliable; C = Fairly reliable; D = Not usually reliable; E = Unreliable; F = Reliability cannot be judged.
**Credibility scale (information):** 1 = Confirmed by other sources; 2 = Probably true; 3 = Possibly true; 4 = Doubtful; 5 = Improbable; 6 = Truth cannot be judged.

| Source | Reliability (A-F) | Reliability Justification | Key Claim | Credibility (1-6) | Credibility Justification | Admiralty Rating (e.g., B2) |
|--------|-------------------|---------------------------|-----------|-------------------|---------------------------|-----------------------------|

Rules:
1. A claim may only score 1 (Confirmed) if at least two INDEPENDENT sources report it. If apparent corroboration traces back to a single originator, it is NOT independent. Score accordingly and flag in Section 3.
2. Reserve grade A for sources with a demonstrated, verifiable track record. Default unknown or first-seen sources to F (reliability cannot be judged), not to a mid-scale guess.
3. Reserve credibility 6 and reliability F for genuinely unjudgeable cases. Do not use them as a dumping ground to avoid assessment.

## 3. Provenance and Bias Flags
Document each issue found. If a category has no findings, state "None identified."
| Flag Type | Affected Source/Claim | Evidence | Impact on Confidence |
|-----------|-----------------------|----------|----------------------|
Required flag categories to check:
1. **Single-sourced claims.** Assertions resting on one originator with no independent corroboration.
2. **Circular reporting.** Multiple outlets repeating one original source, creating false corroboration.
3. **Vendor-marketing bias.** Claims that advance a commercial product, inflate attribution certainty, or use sensational naming without supporting evidence.
4. **Anonymous or unverifiable sourcing.** "Sources tell us," undisclosed telemetry, unnamed researchers.
5. **Recency or version drift.** Outdated reporting presented as current, or claims superseded by later disclosure.
6. **Translation or context loss.** Relevant where [data] includes non-English or region-specific sourcing.

## 4. Overall Confidence Assessment
Provide an overall confidence statement on the body of reporting using ICD 203 estimative language. Use ONLY the standard terms: **almost no chance / very unlikely / unlikely / roughly even chance / likely / very likely / almost certain** for likelihood, and **low / moderate / high** for analytic confidence. State both, and never substitute a numeric probability for the estimative term.
1. Overall confidence level (low / moderate / high) in the reporting body
2. One-paragraph justification tied to the gradings above
3. Explicit statement of what is corroborated versus single-sourced versus uncorroborated

## 5. Intelligence Gaps and Collection Recommendations
1. Key claims that require independent corroboration before operational use
2. Source types or originators that would strengthen the assessment
3. Claims that should NOT be actioned at current confidence
</output_format>

<guidelines>
1. Grade reliability and credibility as SEPARATE axes. A usually-reliable vendor (B) reporting an uncorroborated claim still yields a B3, not a B1.
2. Use only the source material in [data]. Do not introduce outside knowledge to corroborate or contradict a claim. If corroboration is not present in the provided material, the claim is single-sourced by definition. State "Not available in provided reports" where information is missing rather than inferring it.
3. Do NOT fabricate source track records, dates, or originator chains. If provenance cannot be traced from the material, grade reliability as F and say so.
4. Actively trace corroboration to its origin before scoring a claim as confirmed. Treat apparent multi-source agreement as suspect until independence is established (this guards against circular reporting and source laundering).
5. Default to the more conservative grade when evidence is ambiguous. Do not inflate confidence to produce a cleaner-looking assessment.
6. Prioritize evaluation of claims most relevant to the specified industry and region, but grade all key claims regardless.
7. Use only ICD 203 estimative terms for likelihood and confidence. Do not invent intermediate terms or attach false precision.
8. Include inline citations to the specific source or document for every grading and flag.
9. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Attach the gradings and confidence statement to finished intelligence so the CISO and decision-makers understand reliability, and hand the Intelligence Gaps section to your collection manager before single-sourced claims drive decisions.
