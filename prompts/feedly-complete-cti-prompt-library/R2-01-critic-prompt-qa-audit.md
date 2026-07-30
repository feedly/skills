# Critic prompt (verification and QA audit)

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Section 1: Setup, Verification and QA

## What this prompt does
Run as a separate step to have a second AI pass audit a draft produced by an earlier prompt. You give the AI the original source data, the prompt that produced the draft, and the draft itself, and this prompt audits the response. It makes the verdict deterministic, adds a framework-reference check that catches ATT&CK-versus-ATLAS mix-ups and invented IDs, and ends with an explicit statement of what it could and could not verify.

## Prompt
```
<variables>
[job role]:
[original task]:
[source data]:
[draft output]:
** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Senior CTI reviewer performing quality assurance
[original task]: the task described in the draft
[source data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[draft output]: the draft provided below
If more than one draft is provided, audit each one separately under its own heading.
</variables>

<context>
I'm a [job role]. I need you to audit a draft produced by another AI prompt before it is published or actioned. Your job is to find problems, not to rewrite the draft.
</context>

<task>
Compare the [draft output] against the [source data] and the [original task]. Identify every claim not supported by the source, every fabricated or unverifiable specific, every place the draft overstates confidence, drops a required element, or drifts from the requested format, and every framework reference (MITRE ATT&CK, ATLAS, CAPEC, CVE) that is wrong, misattributed, or assigned to the wrong tactic.
</task>

<output_format>
## 1. Verdict
One line: Pass, Pass with fixes, or Do not publish. Apply this rule strictly: choose Pass ONLY if there are zero outstanding items in sections 2 to 7. If any framework label needs live-matrix confirmation, any query or rule needs environment validation, any claim rests on a single uncorroborated source, or any High/Med issue is open, the verdict is at best "Pass with fixes." Use "Do not publish" when a High-severity unsupported or fabricated claim is present.
## 2. Unsupported or Fabricated Claims
| Claim in draft | Issue (unsupported / fabricated / overstated) | What the source actually says | Suggested correction | Severity (High / Med / Low) |
|---|---|---|---|---|
## 3. Framework and Reference Checks
For every framework ID in the draft (ATT&CK, ATLAS, CAPEC, CVE): confirm the ID exists, that the technique name matches the ID, and that it sits under the correct tactic. Flag any ATT&CK technique presented as ATLAS (or vice versa), any invented ID, any sub-technique used where only the parent is supported, and any tactic label you cannot confirm from memory (mark it "needs live-matrix check"). State the corrected ID or note "no suitable framework technique; describe in prose instead."
## 4. Confidence and Language Issues
List places where the draft's confidence rating or absolute language is not supported by the evidence, with the suggested estimative wording and confidence level.
## 5. Format and Completeness Gaps
List required elements that are missing, dropped, malformed, or duplicated (e.g. missing confidence column, missing source IDs, the same item counted twice, a re-run that shows only changed rows instead of the full table).
## 6. Technical Checks
For any detection logic, queries, or rule conversions: flag fields, log sources, telemetry tables, joins, or syntax that look invented, that target telemetry which would not actually capture the described behavior, that are not time-bounded, or that would not run as written. You are flagging for human review, not validating in an environment.
## 7. What to Verify Manually
The highest-priority items a human analyst should confirm before this draft is trusted, including any claim that rests on a single source and should be corroborated.
## 8. Validation Status
State plainly what you were able to check against the source versus what could not be verified here and needs a human or a live environment (framework tactic labels, query execution, second-source corroboration).
</output_format>

<guidelines>
1. Judge the draft ONLY against the [source data] and [original task]. If something cannot be checked against the source, list it as unverifiable rather than defending or attacking it with outside facts.
2. Do not rewrite the draft. The "Suggested correction" column is a pointer for the author, not a new version.
3. Be specific. Quote the offending text rather than describing it.
4. Verify framework IDs against your knowledge of the current MITRE ATT&CK and ATLAS matrices; when you are not certain an ID or tactic placement is correct, say so explicitly rather than asserting it.
5. Do not grade leniently because the draft is well written or because you may have produced similar work. Apply the verdict rule in section 1 mechanically.
6. If the draft is genuinely clean with nothing outstanding, say so plainly rather than inventing problems.
7. Do not use em dashes anywhere in the output.
8. Work through sections 2 to 7 before writing the Verdict in section 1, so the verdict reflects the completed analysis rather than a first impression.
</guidelines>
```

## Notes
Pair this with the article's red-flag checklist (a by-eye scan for unsourced claims, invented specifics, confidence without evidence, single-source themes, format drift, technical plausibility, and stale/out-of-scope detail). Treat a "Do not publish" verdict as a hard stop and work the High-severity rows first, then hand the "What to verify manually" list to the reviewing analyst as their final pre-publication checklist.
