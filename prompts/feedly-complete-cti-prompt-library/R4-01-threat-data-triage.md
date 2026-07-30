# Threat data/information triage

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 1: Detect and triage, Prompt 1

## What this prompt does
Applies a consistent BFSI-specific relevance filter to any incoming threat data and information, producing scalable outputs that meet compliance requirements. It leads with prioritization and immediate actions, and conditionally generates a full audit record depending on the disposition assigned.

## Prompt
```
<variables>
[job role]:
[country/region]:
[stakeholder team names]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: CTI Analyst
[country/region]: Global
[stakeholder team names]: SOC and Fraud Teams
</variables>

<context>
I'm a [job role] at a financial institution in [country/region]. My goal is to triage the threat data/information below and provide [stakeholder team names] with an assessment of what action is required.
</context>

<task>
Review the threat data/information pasted below and produce a structured triage assessment. Lead with prioritization and immediate actions.

If the signal is sparse, for example, a single IP, domain, or hash with no additional context, note what is known, identify what enrichment is needed before a priority decision can be made, and recommend an interim prioritization.

Apply the following documentation rule based on prioritization:

- Immediate Escalation or Elevated: produce full triage assessment AND audit record
- Enrich Before Decision: produce triage assessment only. Add a note that the audit record should be completed after enrichment confirms priority
- Monitor or Close: produce triage assessment only with one-line closure rationale. No audit record required.

Before using this prompt, confirm the threat data/information has been sanitized in accordance with your institution's data handling and TLP compliance requirements.

[PASTE SANITIZED THREAT DATA/INFORMATION HERE]
</task>

<output_format>
## Triage Assessment

### 1. Prioritization and Immediate Actions
- Priority: Immediate Escalation / Elevated /
  Enrich Before Decision / Monitor or Close
- Owners: SOC / Fraud / CTI / Risk
- Immediate containment actions (if applicable):
  - Block: [IOCs to block now]
  - Monitor: [what to watch in parallel]
  - Notify: [who needs to know immediately]

### 2. Threat Data/Information Summary
What was received, from what source, and what it describes.

### 3. BFSI Relevance
- Infrastructure potentially affected: payment rails (ACH, RTP, SWIFT), card networks, core banking, identity and authentication systems, or none identified
- Relevance determination: Confirmed / Possible / Not Relevant
- Rationale

---
## Audit Record
(Generated only for Immediate Escalation or Elevated dispositions. Omitted for Enrich Before Decision and Monitor or Close.)

### A. Relevance Assessment for Compliance Review
Plain language summary of why this threat data/information is relevant to BFSI infrastructure, written for a compliance or audit reviewer without CTI expertise.

### B. Priority Decision Rationale
- Priority assigned:
- Basis for this decision:
- What information, if available, would have
  changed this decision:

### C. Actions Taken
- Containment actions initiated:
- Teams notified and at what time: [Analyst to record exact notification times and names before filing]
- Analyst completing this record: [Analyst to add name and timestamp before filing]
- Follow-up actions assigned and to whom:

### D. Analyst Confidence
- Confidence level: High / Medium / Low
- Known gaps or unknowns at time of decision:

### E. Compliance Flags
- Does this threat data/information involve potential regulatory
  notification obligations? Yes / No / Requires Review
- Basis for determination:
- Any steps skipped or overridden and reason:
</output_format>

<guidelines>
1. If the signal is sparse, do not inflate confidence, document what is unknown and recommend enrichment before escalation. All outputs must be validated against source material before filing.
2. In the audit record, write all rationale in plain language that a compliance reviewer can evaluate without CTI expertise
3. Flag potential regulatory notification obligations automatically for any escalated signal involving payment infrastructure or customer data exposure
4. Do not use em dashes anywhere in the output. Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: block or monitor the IOCs identified in the containment actions; route the relevant threat data to the correct team based on the disposition; if escalated, carry the triage assessment into Section 2 as the starting point for enrichment.
