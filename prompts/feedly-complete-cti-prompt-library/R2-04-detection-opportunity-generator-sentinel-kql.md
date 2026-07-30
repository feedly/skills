# Detection opportunity generator (Microsoft Sentinel and KQL)

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Detection engineering prompts (Prompt 3), contributed by Jack Alexander, Intelligence & Detection Engineering Manager at Quorum Cyber

## What this prompt does
Creates a report identifying detection opportunities for Microsoft Sentinel. It works through each attack procedure in the source, matches each detection to the telemetry that actually records the behavior, names exact tables and key fields, and produces up to five KQL detection samples with time-bounded joins, ATT&CK tags, false-positive tuning notes, and schema-verification flags.

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
[job role]: Cyber Detection Engineer
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: technical security stakeholders
[product/service]: Detection Engineering Report
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with [product/service].
</context>

<task>
Create a report identifying detection opportunities for Microsoft Sentinel. Go through the [data] and for each attack procedure, document the information specified below.
</task>

<telemetry_guidelines>
- Match each detection to the telemetry that actually records the behavior. Process creation tables (DeviceProcessEvents) only capture what appears on a command line. In-memory, reflective, or fileless techniques (for example reflective .NET assembly loading, process injection, or AMSI-visible script execution) usually leave nothing on the command line, so detect them with DeviceImageLoadEvents, DeviceEvents (including AmsiScan or reflective-load action types), or module-load telemetry instead.
- For each detection, name the exact table and the key fields it depends on, and add one sentence explaining why that telemetry captures the behavior.
- Every join MUST be time-bounded: filter both sides to the same lookback window and constrain the join on a time proximity (for example a 1h bin or a between-timestamps condition), so the query cannot fan out across unrelated events.
- Any table name, column, or ActionType value that you are not certain exists in the current Microsoft Defender / Sentinel schema must be written followed by "(verify against schema)". Do not present an unverified field as definitely correct.
- Do not rely on a single brittle string match where a more robust field or behavioral condition is available.
</telemetry_guidelines>

<output_format>
## Detection Opportunities
1. Log Sources & Event IDs (bulleted list)
2. Telemetry Requirements (bulleted list with one sentence of explanation each)
3. Detection opportunities (written in KQL) (create a maximum of 5 detection samples and match to priority number from table). For each KQL sample, add three short lines beneath it: "ATT&CK:" with the technique ID and name, "Likely false positives / tuning:" with the main benign cause and how to tune it, and "Schema notes:" listing any field marked for verification.
## Detection Hypotheses Table
Create a table with the following columns:
| Log Source / Table | Detection Opportunity | ATT&CK Technique | Priority Number | Likely False Positives | Reference |
|---|---|---|---|---|---|
## Validation Status
State that all KQL is AI-generated and untested, list the specific fields or ActionType values that need schema confirmation, and note that each query must be run in the target tenant before deployment.
</output_format>

<guidelines>
1. Provide detailed technical information for each procedure, grounded only in the [data].
2. Include only actionable detection opportunities; avoid generic or ambiguous logic.
3. Focus on specific search patterns and detection logic, and prioritize hypotheses relevant to the specified industry and region.
4. Include citations to source material.
5. Create a maximum of 5 detection opportunities in total.
6. KQL is AI-generated; never claim a query is tested, and require validation in the environment before deployment.
7. Before you finish, verify that every join is time-bounded and that every table and field name either is standard or is tagged "(verify against schema)". Flag any field you are unsure of. Prefer durable behavioral logic over hard-coded IOCs: if a detection relies only on report-specific IPs, domains, or hashes, label it as short-lived and add a behavioral complement where one is feasible.
8. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Have detection engineering validate each KQL sample against your own data, confirm any field tagged "verify against schema" exists in your tenant, tune for false positives, and route the telemetry gaps to whoever owns logging. This is step 1 of Chain 1 (Report to Sentinel detection), with output optionally feeding Prompt 4 (SPL converter).

Example of the expected KQL shape (illustrative, validate before use):

```kql
DeviceProcessEvents
| where Timestamp > ago(7d)
| where FileName in~ ("powershell.exe", "pwsh.exe")
| where ProcessCommandLine has_any ("-enc", "FromBase64String")
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine
// ATT&CK: T1059.001
// Likely false positives / tuning: administrative scripts using encoded commands
// Schema notes: DeviceProcessEvents (Defender XDR)
```
