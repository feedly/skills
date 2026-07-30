# IOC extraction and enrichment: portable LLM prompt

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 1: Extracting and enriching the IOCs, Pathway B: A portable LLM prompt

## What this prompt does
This is a portable IOC extraction and enrichment prompt designed to run on any model, with or without tool access. It extracts every indicator from a report, keeps each one tied to its verbatim source sentence, source name/URL, and associated malware/TTP/campaign/actor, enriches inline where the model has tool access (or marks "to enrich" where it does not), and produces an expanded STIX 2.1 bundle plus a validation table.

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
[stakeholder team names]: technical security stakeholders
[data]: the report provided below
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to give [stakeholder team names] an enriched set of indicators that stays tied to its source and context, ready to import into a TIP.
</context>

<task>
From the [data], extract every indicator of compromise. For each one, keep the verbatim sentence it appeared in, the source name and URL, and any associated malware, ATT&CK technique, campaign, or threat actor. Enrich each indicator: if you have web or tool access, populate the enrichment inline; if not, mark the enrichment field "to enrich". Produce the expanded STIX 2.1 bundle described in the output format.
</task>

<output_format>
First, a STIX 2.1 bundle following this structure: indicator SDOs (pattern, pattern_type, pattern_version, valid_from, name, the verbatim context in description, indicator_types, kill_chain_phases, confidence, labels, external_references for source and ATT&CK, and a SOC-handling property-extension carrying recommended_action, priority, log_sources, environment_tags, detection_notes, and false_positive_notes). Declare the SOC-handling extension as an extension-definition SDO and key it in "extensions" by that object's "extension-definition--<uuid>" id (NOT by a bare name such as "x-org-soc-handling", which fails strict STIX 2.1 validation). Also include campaign, attack-pattern, course-of-action, identity, and relationship ("indicates", "uses", "mitigates") objects where the report supports them. Do NOT put "spec_version" on the bundle object itself; it belongs only on the individual SDOs. Leave sighting and internal-only fields as placeholders. Return the bundle in its own code block as valid JSON with no comments.

Then, a short Markdown table for validation:
| Indicator | Type | Enrichment (reputation, first seen, classification) | Context (verbatim) | Source | Associated malware/TTP/campaign/actor |
|-----------|------|------------------------------------------------------|--------------------|--------|---------------------------------------|
</output_format>

<guidelines>
1. Extract only indicators present in [data]; do not infer or generate them.
2. Normalize defanged indicators (hxxp to http, [.] to a dot).
3. Use STIX 2.1 patterning per type: [file:hashes.'SHA-256' = '...'], [ipv4-addr:value = '...'], [domain-name:value = '...'], [url:value = '...'], [email-addr:value = '...'].
4. The context (indicator description) MUST be a verbatim quote from [data].
5. If enrichment data is not available to you, mark the field "to enrich" rather than guessing reputation or classification.
6. The bundle must parse as valid STIX 2.1 JSON with no inline comments, and must validate in strict mode (stix2 allow_custom=False).
7. If an indicator is a legitimate system binary or service being abused rather than a malicious artifact, extract it but set "recommended_action": "monitor-only" in the SOC-handling extension and add a note in false_positive_notes flagging it as a legitimate binary.
8. If an indicator is a legitimate third-party service endpoint or domain being abused for C2 (such as OAuth endpoints, cloud storage, or SaaS platforms), extract it with "recommended_action": "monitor-only", set false_positive_notes to flag it as shared infrastructure where blocking would cause widespread disruption, and add a detection_notes value recommending behavioral detection over network blocking.
9. Ensure the full source name, report title, and URL are attached to each indicator, e.g., in the table, each row in the source column should contain the source name, report title, and report URL.
</guidelines>
```

## Notes
- This prompt produces an expanded STIX 2.1 bundle plus a validation table, and runs on any model with or without tool access.
- Because the output is already STIX 2.1, it imports cleanly into a TIP via API (MISP via PyMISP/MISP API; OpenCTI via GraphQL API or pycti). Gate any TIP or SOC push behind analyst confirmation.
