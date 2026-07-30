# Visual attack flow

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Cyberattack Prompts

## What this prompt does
Creates a one-page workflow diagram that makes complex attack chains immediately understandable, aligning each stage with MITRE ATT&CK T-Codes to standardize how the team discusses and tracks adversary techniques. It suits CTI analysts creating briefings for technical teams or executives, and threat hunters or detection engineers visualizing attack paths to find defensive gaps. Output includes a stage-by-stage analysis, a summary table, and a visual diagram (React/HTML/SVG, Mermaid, generated image, or ASCII fallback).

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
Analyze the [data] and create a workflow diagram illustrating the attack chain from initial access to objective completion.
</task>

<output_format>
## 1. Attack Workflow Analysis

### 1.1 Attack Chain Overview
For each identified attack stage, provide:
1. Stage Number & Name (e.g., Stage 1: Initial Access)
2. MITRE ATT&CK T-Code (e.g., T1566.001)
3. Technique Summary (2-3 sentence description of what occurred)
4. Indicators of Compromise (IOCs): file hashes (MD5/SHA256), IP addresses/domains, file paths/registry keys, other artifacts
5. Transition (how this stage connects to the next)

### 1.2 Attack Flow Summary Table
| Stage | T-Code | Technique Name | Key IOC(s) |
|-------|--------|----------------|------------|
| 1     | TXXXX  | Name           | IOC        |

## 2. Attack Workflow Diagram
Generate a visual diagram of the attack workflow using one of these formats:

Option A, Interactive/Code-Based Diagram:
Create a React component, HTML/SVG, or JavaScript-based flowchart showing the attack progression.

Option B, Mermaid Diagram:
```mermaid
For example: graph LR
    A[Initial Access] --> B[Execution]
    B --> C[Persistence]
    C --> D[Privilege Escalation]
    D --> E[Lateral Movement]
    E --> F[Exfiltration/Impact]

Option C, Generated Image:
Use image generation tools to create a visual flowchart of the attack stages.

Option D, ASCII Diagram (Fallback):
For example:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ T1566.001   │───▶│ T1059.001   │───▶│ T1053.005   │
└─────────────┘    └─────────────┘    └─────────────┘
The diagram MUST include:

1. Sequential flow showing attack progression (left-to-right or top-to-bottom)
2. Each node contains: T-Code, Technique Name, and at least one key IOC
3. Arrows or connectors showing stage transitions
4. Clear visual separation between stages
5. Color coding if supported (e.g., red for initial access, orange for execution)

## 3. Formatting Requirements

1. One-page equivalent layout (concise, scannable)
2. T-Codes linked to attack.mitre.org where possible
3. IOCs formatted for direct ingestion into SIEM/detection tools following STIX best practices
</output_format>

<guidelines>
1. Identify each attack stage and align it with MITRE ATT&CK T-Codes
2. Include T-Code, summary, and IOCs in each node
3. Ensure a clear, one-page layout for readability
4. Do not skip the visualization; select whichever option the platform supports
5. Prioritize actionable intelligence relevant to the specified industry
6. Include citations to source material
</guidelines>
```

## Notes
- Include the diagram in threat reports or incident summaries to show stakeholders exactly how an attack unfolded.
- Use the mapped T-Codes and IOCs to prioritize which stages of the attack kill chain need improved detection or response.
- Combine with MITRE D3FEND to uncover defense gaps and opportunities for improvement.
