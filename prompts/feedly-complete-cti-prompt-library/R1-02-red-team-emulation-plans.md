# Red team emulation plans

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Cyberattack Prompts

## What this prompt does
Converts threat intelligence into an executable Adversary Emulation Report that red teams can use to simulate real adversary behavior, bridging the gap between reading about an attack and emulating it with specific TTPs, tools, and commands. It is built for red team operators planning emulation exercises, purple teams coordinating validation, and CTI analysts supporting threat-informed defense. Output includes emulation steps, detection opportunities, purple team collaboration points, and mitigations.

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
Read the provided [data] and generate a structured Adversary Emulation Report to support Red Team operations. The goal is to simulate realistic threat actor behavior based on recent tradecraft observed in the wild.
</task>

<output_format>
## 1. Summary of Threat Activity
1. Threat Actor (if known)
2. Campaign or Attack Name (if applicable)
3. Targeted Sectors/Industries
4. Reported Objective (e.g., data exfiltration, ransomware deployment, espionage)
5. MITRE ATT&CK Tactics & Techniques
6. Tools, Malware, or Frameworks Used
7. Relevant CVEs (if exploitation was part of initial access or lateral movement)

## 2. Attack Procedures (Emulation Steps)
For each procedure, provide the following details:
1. Step Name (short title of the simulated attack phase)
2. Tactic (MITRE ATT&CK Tactic, e.g., Initial Access, Persistence)
3. Technique ID & Name (MITRE ATT&CK Technique, e.g., T1566.001 Spearphishing Attachment)
4. Procedure Description (technical detail of how the technique was used, including commands, payloads, or LOLBins; highlight novel chaining techniques if observed)
5. Emulation Plan (exact steps to emulate this behavior with tools such as manual commands, Cobalt Strike, Brute Ratel, Mythic, Atomic Red Team, or Caldera; include preconditions and payload examples)
6. Environment Considerations (infrastructure or configurations required, e.g., phishing server, domain controller, PowerShell remoting)

## 3. Detection Opportunities
1. Log Sources & Event IDs
2. Telemetry Requirements
3. Known Sigma Rules or Detection Samples
4. Blind spots or evasions observed

## 4. Purple Team Collaboration Opportunities
1. Techniques that benefit from validation
2. Coordinated tests to measure fidelity, tune detections, or validate response
3. Suggested KPIs (dwell time, detection latency, alert-to-investigation timing)

## 5. Mitigations and Hardening
1. High-level mitigations aligned to MITRE M-codes (e.g., M1047, Audit PowerShell logging)
</output_format>

<guidelines>
1. Ensure emulation steps reflect observed tradecraft from the [data]
2. Prioritize fidelity and align with MITRE ATT&CK standards
3. Avoid vague descriptions; use real payloads, delivery methods, and sources
4. Include specific tool commands and configuration details
5. Focus on actionable procedures that can be executed
6. Include citations to source material
7. Fill sections with details from the provided data ONLY. If information for any part of the report is not available in the source material, explicitly state 'Not available in provided reports' rather than filling gaps with generic knowledge
</guidelines>
```

## Notes
- Run the emulation procedures using tools like Cobalt Strike or Atomic Red Team to validate detection coverage.
- Identify detection gaps by comparing the emulation steps against your log sources and existing detection rules.
- Share the detection opportunities section with your SOC to tune existing detections or create new ones.
