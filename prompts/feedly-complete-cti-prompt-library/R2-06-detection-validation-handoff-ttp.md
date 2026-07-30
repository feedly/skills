# Detection, validation, and handoff (TTP to deployable detection)

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Detection engineering prompts (Prompt 5), contributed by Omar Aboelrous, DFIR Analyst at a cybersecurity vendor

## What this prompt does
For every adversary TTP evidenced in the source, produces a self-contained detection, validation, and handoff package. Each package detects (drafts portable Sigma logic plus required telemetry), validates (specifies how to safely trigger the behavior and confirm the rule fires, with evasions and false positives documented), and hands off (gives the receiving team everything needed to deploy and tune without re-deriving the analysis).

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
[job role]: Detection Engineer
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: SOC and detection engineering stakeholders
[product/service]: Detection, validation, and handoff package
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with [product/service].
</context>

<task>
Work directly from [data]. For every adversary TTP evidenced in the source, produce a self-contained detection, validation, and handoff package. Each package must do three things: (1) DETECT, draft portable detection logic as a Sigma rule plus the exact telemetry it depends on; (2) VALIDATE, specify how to safely trigger the behavior and confirm the rule fires, with known evasions and false-positive sources documented up front; and (3) HAND OFF, give the receiving team everything needed to deploy and tune it without re-deriving the analysis. This prompt is standalone: it does not assume any prior detection-engineering output. If [data] already contains detection rules (Sigma, YARA, KQL, SPL, Snort), incorporate and validate them rather than rewriting from scratch, and say so. Build detections ONLY for TTPs actually evidenced in [data]. Do not summarize the threat.
</task>

<output_format>
## 1. TTP Detection Summary
| # | Tactic | Technique ID and Name (linked to attack.mitre.org) | Procedure Observed (1-2 sentences from source) | Data Source Required | Detection Confidence (High/Med/Low) |
|---|--------|----------------------------------------------------|-------------------------------------------------|----------------------|-------------------------------------|

Detection Confidence reflects how reliably this behavior can be detected as described. High = behavior is specific and high-signal. Med = detectable but noisy or config-dependent. Low = weak signal, likely high false positives, or requires telemetry rarely available.

## 2. Detection, Validation, and Handoff Packages
Produce one numbered package per TTP. Repeat the full structure below for each.

### 2.X [Technique ID] [Technique Name]

#### 2.X.1 Detection Rationale
1. Procedure as observed in [data] (with citation)
2. What specific behavior or artifact the detection targets
3. Why this is the chosen detection point in the kill chain (versus other observable stages)

#### 2.X.2 Telemetry and Required Fields
| Log Source | Specific Event or Channel (e.g., Sysmon Event ID 1, Windows Security 4688, EDR process telemetry) | Required Fields | Field Availability Notes |
|------------|----------------------------------------------------------------------------------------------------|-----------------|--------------------------|

State explicitly if the required telemetry is commonly absent by default (for example command-line logging, Sysmon, PowerShell ScriptBlock logging) and what must be enabled.

#### 2.X.3 Draft Detection Logic (Sigma)
Provide a syntactically valid Sigma rule in a code block. Include: title, id (leave as a placeholder UUID), status (experimental), description, references (cite source), author placeholder, date, logsource, detection (selection plus condition), falsepositives, level, and ATT&CK tags. Logic must be grounded ONLY in behavior evidenced in the source. Do not invent field values, hashes, IPs, or command lines not present in or directly inferable from [data]. If [data] already contained a rule for this behavior, reproduce it exactly first, then provide the Sigma version and note any gaps between them.

#### 2.X.4 SIEM Portability Notes
| Platform | Translation Note |
|----------|------------------|
| Splunk (SPL) | Key field mappings and index considerations |
| Elastic (ES\|QL or EQL) | Field name equivalents (for example process.command_line) |
| Microsoft Sentinel (KQL) | Table mapping (for example DeviceProcessEvents) |
Note non-portable elements (for example regex behavior, field normalization differences). Mark "Not applicable" where the data source does not exist on a platform. These are pointers for the receiving team, not full conversions.

#### 2.X.5 Known Evasions and Limitations
1. Documented or plausible evasions for this detection logic (for example LOLBin substitution, obfuscation, parent-process spoofing)
2. Coverage gaps (what variants of the technique this rule will NOT catch)
3. Brittleness factors (hardcoded strings, environment-specific paths)

#### 2.X.6 False Positive Sources and Tuning
| Likely FP Source | Tuning Guidance |
|------------------|-----------------|

#### 2.X.7 Validation Test
1. Atomic Red Team reference (test number or name) if a corresponding atomic exists. State "No direct Atomic Red Team mapping identified" if not. Do not fabricate a test ID.
2. Manual reproduction steps (commands and preconditions) to safely trigger the behavior in a test environment
3. Expected telemetry on success (what the analyst should see if the detection fires correctly)
4. Pass or fail criteria (the specific signal that confirms the rule fired, and what a miss looks like)

## 3. Handoff and Deployment Prioritization
| Technique | Detection Confidence | Telemetry Readiness (Available/Needs Enablement/Unavailable) | Validation Status (Test defined/No atomic mapping) | Relevance to [sector name] and [country/region] | Priority (1-High/2-Med/3-Low) | Suggested Owner |
|-----------|----------------------|---------------------------------------------------------------|----------------------------------------------------|-------------------------------------------------|-------------------------------|-----------------|

## 4. Detection Gaps
1. TTPs in [data] that cannot be reliably detected with commonly available telemetry
2. Required data sources not typically collected that would close these gaps
3. Recommended compensating controls or hunt hypotheses where detection is not feasible
</output_format>

<guidelines>
1. Build detections ONLY for TTPs evidenced in [data]. Do not pad the output with generic detections for the technique class that are not supported by the observed procedure.
2. Do not fabricate IOCs, field values, command lines, hashes, or Atomic Red Team test IDs. Where a specific detail is not in the source, write "Not available in provided reports" and build the logic at the behavioral level instead of inventing artifacts.
3. Sigma rules must be syntactically valid and behavior-focused. Prefer durable behavioral logic over brittle atomic IOCs, and note explicitly when a rule is IOC-based and therefore short-lived.
4. Treat detection and validation as one unit of work. A package is not complete until it states how the receiving team confirms the rule fires and what a false negative looks like.
5. Distinguish what is directly evidenced in the source from what is analyst-inferred tradecraft. Label inferred evasions and FP sources as such rather than presenting them as reported fact.
6. Be honest about telemetry assumptions. If a detection depends on logging that is off by default, say so in section 2.X.2 rather than assuming it is present.
7. Sigma is AI-generated and the SIEM portability notes are pointers, not validated conversions. Flag both for review by a detection engineer before deployment. Mark inside each Sigma rule, as a comment, any selection field or value that is analyst-inferred rather than directly evidenced in the source, so a reviewer can see which conditions are grounded and which are assumptions.
8. Prioritize techniques and tuning relevant to the specified industry and region, but produce packages for all evidenced TTPs.
9. Link all MITRE ATT&CK technique IDs to attack.mitre.org and include inline citations to the source material for every observed procedure.
10. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
Hand to detection engineering to run the validation tests in a controlled environment, tune against the documented false-positive sources before alerting, and feed Detection Gaps to whoever owns telemetry-onboarding.
