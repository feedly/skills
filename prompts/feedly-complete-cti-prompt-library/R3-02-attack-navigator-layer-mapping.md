# Map report TTPs to a MITRE ATT&CK Navigator layer (v19)

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 2: Mapping the TTPs to ATT&CK and visualizing them, Pathway A: ATT&CK Navigator layer

## What this prompt does
This prompt maps the adversary behavior described in a report to MITRE ATT&CK v19 (Enterprise) and returns a single ATT&CK Navigator Layer File (Layer File Format v4.5) that uploads directly to the Navigator without errors. Each mapping carries a verbatim supporting sentence and a confidence score, so the analyst can overlay it against a detection-coverage layer and validate each mapping against its source.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[product/service]:
[data]:
[layer name]:
** Note about default_behavior **

If no value is provided for a variable (left blank after colon),
use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: technical security stakeholders
[product/service]: ATT&CK Navigator layer for vendor report
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[layer name]: Vendor Report TTP Mapping
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with [product/service] mapping the adversary behavior described in the [data] to MITRE ATT&CK v19 (Enterprise).
</context>

<task>
For each adversary behavior described in the [data], identify the corresponding MITRE ATT&CK Tactic, Technique, and Sub-technique (v19, Enterprise). Produce a single MITRE ATT&CK Navigator layer file (Layer File Format v4.5) that can be uploaded directly to the ATT&CK Navigator without errors. Each mapping must be supported by exact verbatim sentence(s) from the source and carry a confidence score.
</task>

<output_format>
Return ONLY a single JSON object that conforms to ATT&CK Navigator Layer File Format v4.5. No preamble, no explanation, no markdown code fences.

The object MUST include these top-level fields:
- "name": use [layer name]
- "versions": { "attack": "19", "navigator": "5.2.0", "layer": "4.5" }
- "domain": "enterprise-attack"
- "description": one-sentence summary of the source mapped
- "techniques": array of technique objects (see structure below)
- "gradient": { "colors": ["#ff6666", "#ffe766", "#8ec843"], "minValue": 0, "maxValue": 100 }
- "legendItems": [
    { "label": "High confidence", "color": "#8ec843" },
    { "label": "Medium confidence", "color": "#ffe766" },
    { "label": "Low confidence", "color": "#ff6666" }
  ]
- "layout": { "layout": "side", "showID": true, "showName": true, "expandedSubtechniques": "annotated" }
- "selectTechniquesAcrossTactics": true
- "selectSubtechniquesWithParent": false

Each entry in the "techniques" array MUST use this structure:
{
  "techniqueID": "T1566", // or "T1566.001" for sub-techniques
  "tactic": "initial-access", // ATT&CK tactic shortname, lowercase, hyphenated
  "score": 100, // 100=high, 66=medium, 33=low
  "color": "",
  "comment": "Confidence: high\nSupporting sentence(s):\n\"exact verbatim quote from source\"",
  "enabled": true,
  "showSubtechniques": true, // true on parent if any of its sub-techniques are mapped
  "metadata": [
    { "name": "confidence", "value": "high" },
    { "name": "source_quote", "value": "exact verbatim quote from source" }
  ]
}
</output_format>

<guidelines>
1. Only map behaviors you can directly support from the [data]. Do not infer techniques that are not described. If a behavior is not present in the source, do not invent it.
2. If you are unsure between two techniques, return both as separate technique entries with appropriate confidence scores.
3. Sub-techniques are MEDIUM confidence (score 66) by default unless the text explicitly describes sub-technique-level behavior, in which case use the same confidence as the parent.
4. The "source_quote" metadata value and the quote in "comment" MUST be verbatim quotes from the [data], no paraphrasing.
5. Use MITRE ATT&CK v19 (Enterprise) technique IDs and v19 tactic shortnames. Valid v19 Enterprise tactic shortnames are:
   "reconnaissance", "resource-development", "initial-access", "execution", "persistence", "privilege-escalation", "stealth" (inherits TA0005; the camouflage/blending half of the retired defense-evasion), "defense-impairment" (NEW in v19, TA0112; the disable/degrade-defenses half of the retired defense-evasion), "credential-access", "discovery", "lateral-movement", "collection", "command-and-control", "exfiltration", "impact".
   Do NOT use the retired "defense-evasion" shortname, split into "stealth" or "defense-impairment" per v19.
6. The source report may cite ATT&CK IDs from an earlier version (its own table can be stale even when the report is recent). RE-MAP to v19 rather than carrying IDs over, and never emit a retired or revoked technique ID. In particular: T1562 (Impair Defenses) and its sub-techniques T1562.001 (Disable or Modify Tools) and T1562.006 (Indicator Blocking) are MERGED into the new technique T1685 (Disable or Modify Tools) under the "defense-impairment" tactic; the remaining former T1562 sub-techniques are revoked and reissued under new v19 IDs. behaviors such as tampering with AMSI, killing EDR, or disabling logging belong under "defense-impairment", not "stealth". Consult the v19 crosswalk for any pre-v19 ID before emitting it.
7. Sub-techniques MUST be added as separate entries with techniqueID in the form "T####.###" (e.g. "T1566.001"). When a sub-technique is mapped, also include its parent technique entry with "showSubtechniques": true so the sub-technique is visible by default.
8. Confidence-to-score mapping: high -> 100, medium -> 66, low -> 33.
9. If a single behavior maps a technique under multiple tactics, emit one technique entry per tactic with the appropriate "tactic" shortname on each.
10. Return ONLY the JSON object. No preamble, no explanation, no markdown code fences. The output must parse as valid JSON and upload into ATT&CK Navigator v5.x without triggering the "Outdated Layer" warning.
</guidelines>
```

## Notes
- Pinned to MITRE ATT&CK Enterprise v19 to avoid a model answering from no data or a stale matrix.
- After generating, save the JSON and upload it to the MITRE ATT&CK Navigator, overlay it against your detection-coverage layer, then read each mapping against its supporting sentence and accept, amend, or reject it.
- Pathway B of this workflow uses FlowViz (an open-source tool) rather than a prompt to render an attack flow; no pasteable prompt is provided for it.
