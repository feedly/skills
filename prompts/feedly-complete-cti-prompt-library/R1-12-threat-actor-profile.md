# Threat actor profile

**Source report:** CTI Prompt Library (Volume 1)
**Source URL:** https://feedly.com/ti-essentials/posts/cyber-threat-intel-prompt-library
**Section / workflow:** Intelligence Product Prompts

## What this prompt does
Builds comprehensive profiles of threat actors including their motivations, targets, and tradecraft so defenders can understand relevant threats proactively, and provides IOCs and TTP analysis that can be immediately operationalized for detection and hunting. It serves CTI analysts tracking actors relevant to their sector, geography, or tech stack; security operations teams responding to suspected intrusions; and threat hunting teams building hunts. Output is a full actor profile with targeting, TTPs, attribution, IoCs, risk assessment, and recommendations.

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
Generate a comprehensive Threat Actor Profile about [Threat Actor Name] using the [data].
</task>

<output_format>
## 1. Title
Threat Actor Profile: [Threat Actor Name]

## 2. Executive Summary
High-level overview of the threat actor and relevance to your organization.

## 3. Threat Actor Overview
1. Background and history
2. Known aliases and affiliations
3. Motivation and objectives
4. Estimated capabilities and resources

## 4. Targeting and Victimology
1. Geographic regions targeted
2. Industries and sectors targeted
3. Types of organizations targeted
4. Selection criteria and patterns

## 5. Tactics, Techniques, and Procedures (TTPs)
1. Attack vectors and initial access methods
2. Malware and tools used
3. Infrastructure characteristics
4. Operational security measures
5. MITRE ATT&CK mapping

## 6. Attribution and Campaign Linking
1. Evidence linking to known campaigns or incidents
2. Confidence level in attribution
3. Connections to other threat groups or nation-states

## 7. Indicators of Compromise (IoCs)
1. Malicious IPs and domains
2. File hashes
3. YARA rules (if available)
4. Other detection artifacts

## 8. Risk Assessment
1. Potential impact to your organization
2. Likelihood of targeting based on sector and geography
3. Financial and reputational risk considerations

## 9. Recommendations
1. Detection and monitoring recommendations
2. Prevention and hardening measures
3. Response and containment guidance
</output_format>

<guidelines>
1. Build comprehensive profiles based on available intelligence
2. Include IOCs and TTPs that can be operationalized immediately
3. Assess relevance to the specified industry and region
4. Provide confidence levels for attribution claims
5. Balance depth with actionability for defenders
6. Include citations to source material
</guidelines>
```

## Notes
- Use the IOCs section to hunt for evidence of the threat actor in your environment.
- Implement the recommendations to improve defenses against the actor's known TTPs.
