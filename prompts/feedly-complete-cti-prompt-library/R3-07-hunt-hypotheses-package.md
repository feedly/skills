# Generate a threat hunt hypotheses package

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 5: Creating detection rules, hunt hypotheses, and briefs, Step 2: Generate the hunt package for the threat hunting team

## What this prompt does
This prompt converts the validated ATT&CK mapping into threat hunt hypotheses the hunting team can run. For each procedure it documents the patterns to look for and the log sources / Event IDs, then adds a short prioritization note on which hypotheses matter most for your environment and which data sources you may be missing.

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
[stakeholder team names]: threat hunting team
[data]: the validated ATT&CK mapping provided below
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to give the [stakeholder team names] a set of hunt hypotheses they can run.
</context>

<task>
For each procedure in [data], document it as a threat hunt hypothesis with the detail below.
</task>

<output_format>
| Procedure | Description (patterns to look for) | Log sources and Event IDs |
|-----------|------------------------------------|---------------------------|

Then a short prioritization note: which hypotheses are highest priority for our environment, and which data sources we may be missing.
</output_format>

<guidelines>
1. Provide detailed, actionable technical patterns for each procedure; avoid generic descriptions.
2. Base every hypothesis on [data]. If a procedure is not described, do not include it.
3. Prioritize hypotheses relevant to the specified industry and region.
4. Return Markdown only.
5. Where a log source or Event ID is not supported by the source, mark it "to confirm" rather than guessing, and state "Not available in provided reports" for any element the source does not support.
</guidelines>
```
