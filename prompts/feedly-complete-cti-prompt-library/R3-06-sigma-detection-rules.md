# Draft Sigma detection rules for the SOC

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 5: Creating detection rules, hunt hypotheses, and briefs, Step 1: Draft detection rules for the SOC

## What this prompt does
This prompt turns the validated TTPs and IOCs from earlier workflows into Sigma detection rules (one per detectable behavior or indicator set) following the SigmaHQ specification, with a unique UUID, a short title, a precise logsource, ATT&CK tags, known false positives, and an experimental status until validated.

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
[stakeholder team names]: security operations center
[data]: the validated TTPs and IOCs provided below
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to give the [stakeholder team names] Sigma rules they can validate and deploy.
</context>

<task>
Using the validated TTPs and IOCs in [data], draft Sigma detection rules, one per detectable behavior or indicator set, following the SigmaHQ specification.
</task>

<output_format>
For each rule, a Sigma YAML block with these fields in order:
- title: short, no "Detects" prefix
- id: a randomly generated UUIDv4
- status: experimental
- description: why the rule exists and when it triggers, without a "Detects" or "This rule will" prefix
- references: the source report URL or citation
- author: [job role]
- date: today's date in YYYY-MM-DD
- tags: the relevant attack.<tactic> and attack.<technique-id> values
- logsource: category, product, and service as applicable
- detection: named selection group(s) and a condition
- falsepositives: known benign scenarios
- level: informational, low, medium, high, or critical
</output_format>

<guidelines>
1. Base every rule on [data]; do not invent indicators or behaviors.
2. Prefer field-based detection over keyword matching where the report supports it, since field-based logic performs better in most SIEMs and static IOCs age quickly.
3. Keep the title short and avoid "Detects when ..."; write the description without "Detects" or "This rule will".
4. Tag each rule with the mapped ATT&CK tactic and technique IDs (for example attack.initial_access and attack.t1566).
5. Set status to experimental; every rule must be validated and tuned before deployment.
6. List realistic false positives, and note the log source and fields each rule depends on.
7. Return the rules only.
</guidelines>
```

## Notes
- Validate every rule with pySigma or sigma-cli before it goes near production detection. Do not push unparsed LLM-drafted rules to the SOC.
- Sigma is SIEM-agnostic; to target YARA, Suricata, KQL, or SPL instead, use the adapter prompt (file 05) and swap in the matching validator.
- Example of the expected Sigma structure (illustrative, generate a fresh UUIDv4 and validate before use):

```yaml
title: Encoded PowerShell Command Execution
id: 2b9f1c9e-0000-4a00-9a00-000000000000
status: experimental
description: Detects PowerShell launched with an encoded command, per the source report
references:
  - https://vendor.example/report
author: CTI team
date: 2026/01/01
tags:
  - attack.execution
  - attack.t1059.001
logsource:
  product: windows
  category: process_creation
detection:
  selection:
    Image|endswith: '\powershell.exe'
    CommandLine|contains: '-enc'
  condition: selection
falsepositives:
  - Legitimate administrative scripts
level: medium
```

