# Structured threat assessment

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Risk & threat assessment prompts (Prompt 10)

## What this prompt does
Produces a structured threat assessment from source material, covering operational environment, attack surface, threat profile, predicted attack scenarios (most likely, worst case, optional alternative), recommended actions, intelligence gaps, and handoff quick-reference. It serves two stakeholders at once: a kill-chain with detectable indicators for the SOC, and a two-sentence, jargon-free summary for leadership.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[product/service]:
[data]:
[critical systems]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: SOC, detection engineering, and security leadership stakeholders
[product/service]: structured threat assessment
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[critical systems]: Not provided. Produce a generalized assessment based on the threat's targeting patterns in the source and state this explicitly.
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service], working from [data]. Where organizational context is available it is described in [critical systems].
</context>

<task>
Produce a structured threat assessment for the threat described in [data]. Base every judgment ONLY on the source material. Where you make an analytical judgment beyond what is explicitly stated, mark it with a confidence level [High/Medium/Low] and a brief justification. If no organizational context is provided in [critical systems], state "Generalized assessment based on threat targeting patterns" and assess against the threat's known targeting from the reporting rather than inventing organizational detail. Do not fabricate IOCs, ATT&CK IDs, actor names, or targeting.
</task>

<output_format>
# THREAT ASSESSMENT: [Threat Name]

## Executive Summary
Three to four sentences covering: (1) the threat actor and their objective, (2) the critical systems at highest risk, (3) the most likely attack scenario, and (4) the top defensive priority. Be specific; avoid generic phrasing like "sophisticated threat actor" or "multiple attack vectors."

## Step 1: Operational Environment
**Likely Targets**: Industries, regions, or system types this threat targets, taken from [data].
**Critical Systems at Risk**: If [critical systems] is provided, map the threat's targeting to those systems. If not, derive from targeting patterns in the source. List specific system types (e.g. "VPN appliances", "email servers").
**External Dependencies**: Third-party, supply-chain, or partner risk relevant to this threat's TTPs or targeting.
Mark analytical judgments with [High/Medium/Low] confidence and a brief justification.

## Step 2: Attack Surface Analysis
| Element | Assessment |
|---------|------------|
| Key Terrain | Critical systems that give the attacker decisive advantage if compromised, and WHY. |
| Attack Paths | The chain from Entry to Movement to Objective, specific to the reporting. |
| Obstacles | Security controls that would impede this specific threat, tied to its documented techniques. |
| Visibility Gaps | Where this threat evades detection, based on its documented evasion techniques. |

**Terrain Favors**: [Attacker/Defender/Contested] with one sentence of justification.
State "Not addressed in reporting" for any row the source does not support.

## Step 3: Threat Profile
### 3.1 Identification
| Actor | Type | Status | Targeting | Confidence |
|-------|------|--------|-----------|------------|
| [Name] | [Criminal/Nation-state/Hacktivist/etc.] | [Active/Emerging/Dormant] | [Sectors/regions] | [H/M/L + justification] |

### 3.2 Capabilities
Two to three sentences on tooling sophistication, exploitation capability (0-day vs. known vulns), infrastructure quality, and OPSEC. Assign a tier if possible: Tier 1 (advanced persistent), Tier 2 (sophisticated), Tier 3 (intermediate), Tier 4 (opportunistic). Include [H/M/L] confidence with justification.

### 3.3 Intent
Two sentences on (1) primary objective (espionage/financial/disruption) and (2) target selection pattern (opportunistic vs. deliberate). Distinguish FACTS (stated objectives) from ASSESSMENTS (inferred intent). Include [H/M/L] confidence.

### 3.4 Key Techniques (ATT&CK)
| Tactic | Technique (T#### and name, linked to attack.mitre.org) | How They Use It |
|--------|--------------------------------------------------------|-----------------|
Maximum 6 rows, most significant techniques only. Omit tactics not covered. "How They Use It" must be specific to this threat, not a generic ATT&CK description. Step 4 scenarios must reference these techniques.

## Step 4: Predicted Attack Scenarios
### Most Likely Scenario
**What they'll probably do**: Two sentences. **Probability**: [H/M/L] | **Confidence**: [H/M/L + justification]
| Step | Attacker Action | Technique (from 3.4) | What to Watch For | Response Window |
|------|-----------------|----------------------|-------------------|-----------------|
"What to Watch For" must be specific enough to write a detection rule (e.g. "Kerberoasting: Event ID 4769 with RC4 encryption for service accounts", not "suspicious authentication"). Every technique must trace back to 3.4. Typically 4 steps; adjust if the documented chain is shorter or needs 5.
**Best Disruption Point**: [Step #] and the specific action required.

### Worst Case Scenario
**Highest impact attack**: Two sentences on what causes the most damage under optimal conditions. **Impact**: [Critical/Severe/Moderate] | **Probability**: [H/M/L]
**Key Differences from Most Likely**: the primary difference in approach/target/technique, and what makes it more damaging (focus on impact, not just sophistication).
**Watch For**: the unique indicator signaling this scenario instead of the most likely one.
**Best Disruption Point**: [Phase] and specific action.

### Alternative Scenario
Include ONLY if the reporting supports a distinct third scenario (different initial access, target set, or opportunistic vs. targeted). Provide **Summary**, **Trigger**, and **Key Difference**. If unsupported, OMIT this section entirely. Do not invent scenarios.

### Scenario Comparison
| Factor | Most Likely | Worst Case | Alternative |
|--------|-------------|------------|-------------|
| Probability | [H/M/L] | [H/M/L] | [H/M/L] |
| Impact | [Level] | [Level] | [Level] |
| Detection Difficulty | [Hard/Moderate/Easy] | [Hard/Moderate/Easy] | [Hard/Moderate/Easy] |
| Best Disruption Point | [Step # + action] | [Step # + action] | [Step # + action] |
Omit the Alternative column if that section was omitted.

## Recommended Actions
| Priority | Action | Counters Which Scenario |
|----------|--------|-------------------------|
Three to five SPECIFIC actions (e.g. "Deploy decoy credentials in IT admin shares to detect lateral movement (T1021.002)", not "improve monitoring"). Each must map to disrupting a specific scenario step. If the reporting lacks the detail to be specific, give only the 1-2 that ARE supported, or state "Insufficient technical detail in reporting to provide specific recommendations beyond general hardening."

## Intelligence Gaps
Two to four specific gaps that limit assessment quality, each with the assessment it would improve (e.g. "Dwell time between initial access and objective: would improve response-window estimates in the Most Likely scenario").

## Confidence and Limitations
**Key Assumptions**: one to two critical assumptions the analysis depends on.
**Critical Unknowns**: what is missing from reporting that most limits confidence.
**Sources**: each source article and what it contributed.

## Quick Reference (For Handoff)
### Top IOCs
| Type | Value | Scenario Association |
|------|-------|----------------------|
Maximum 6 rows, IOCs most likely to be encountered. If none are in the source, state "No IOCs provided in source reporting." Do not invent placeholder IOCs.

### Detection Priorities
| Behavior | Technique (from 3.4) | Where to Look |
|----------|----------------------|---------------|
Three to five high-priority behaviors. "Where to Look" must be specific enough for a SOC analyst to configure detection (e.g. "Windows Security Event Log 4769").

### Leadership Summary
EXACTLY two sentences for non-technical leadership: (1) the threat and risk (who, what they want, what is at stake), (2) the single most important recommended action. No jargon, no acronyms except widely known ones (CEO, IT).
</output_format>

<guidelines>
1. Use information from [data] ONLY. If a detail is not in the source, write "Not addressed in reporting" rather than inventing it.
2. Do not fabricate IOCs, ATT&CK IDs, actor names, malware names, or targeting. Mark uncertain mappings "Unmapped, analyst review needed."
3. Every technique referenced in Step 4 must trace back to a row in Step 3.4.
4. Distinguish FACTS (explicitly stated in the source) from ASSESSMENTS (analyst inference), and label every analytical judgment with a [H/M/L] confidence and brief justification.
5. Use estimative probability language (ICD 203: almost no chance / very unlikely / unlikely / roughly even chance / likely / very likely / almost certain) rather than absolute statements.
6. Link all MITRE ATT&CK technique IDs to attack.mitre.org and cite the source for every observed procedure.
7. Recommendations and detection priorities must be specific and actionable, not generic advice.
8. Before you finish, verify each scenario, technique, and IOC against the source and flag anything you could not confirm. Confirm that every technique referenced in the Step 4 scenarios appears as a row in Step 3.4, and that the Leadership Summary is exactly two sentences with no jargon beyond widely known terms.
9. Do not use em dashes anywhere in the output.
10. Work through Steps 1 to 4 before finalizing the Executive Summary, so the summary reflects the completed assessment.
</guidelines>
```

## Notes
Serves two stakeholders at once: a kill-chain with detectable indicators for the SOC, and a two-sentence, jargon-free summary for leadership. Feed the Detection Priorities and Most Likely kill-chain to detection engineering, route the Recommended Actions to each control owner, and use the Leadership Summary in your exec brief. This is step 1 of Chain 4 (Report to a risk-translated package), feeding Prompt 12 and optionally Prompt 11.
