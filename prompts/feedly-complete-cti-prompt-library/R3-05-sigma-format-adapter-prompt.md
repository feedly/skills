# Adapter prompt: retarget the Sigma rule prompt to another detection format

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 5: Creating detection rules, hunt hypotheses, and briefs, Step 1 (adapting the detection format)

## What this prompt does
This short adapter prompt retargets the Sigma detection-rule prompt (the next resource in this workflow) to a different detection format, YARA, Suricata, KQL, or SPL, while keeping the same structure, source-grounding, and experimental-status guidelines, and noting the matching validator to run before deployment.

## Prompt
```
Take the Sigma detection-rule prompt below and adapt it to produce [choose exactly one: YARA, Suricata, KQL, or SPL] rules instead, keeping the same source-grounding and experimental-status guidelines, and note the matching validator to run before deployment.
```

## Notes
- Sigma is SIEM-agnostic but not the only format: YARA suits file/malware matching; Suricata and Snort suit network traffic; vendor query languages (Splunk SPL, Microsoft Sentinel KQL) suit teams standardized on one platform.
- To retarget: keep the Sigma prompt's structure and source-grounding, swap the Sigma YAML fields for the target format's syntax, and swap the validator for that format's linter.
