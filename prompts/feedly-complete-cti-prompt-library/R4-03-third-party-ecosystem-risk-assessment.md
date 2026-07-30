# Third-party and ecosystem risk assessment

**Source report:** Accelerating BFSI CTI Workflows with Prompt-Driven Threat Intelligence
**Source URL:** https://feedly.com/ti-essentials/posts/accelerating-banking-financial-services-and-insurance-cti-workflows-with-prompt-driven
**Section / workflow:** Section 2: Enrich, assess relevance and impact, Prompt 3

## What this prompt does
Takes a third-party incident report and assesses downstream effects for a financial institution. Because a vulnerability or outage at a core banking vendor, payment processor, or cloud platform can cascade across every institution sharing that infrastructure, it maps exposed institutional services, customer-facing impact, concentration risk, and regulatory notification implications.

## Prompt
```
<variables>
[job role]:
[country/region]:
[stakeholder team names]:

** Note about default_behavior **
If no value is provided for a variable (left blank after colon),
use these defaults:
[job role]: CTI Analyst
[country/region]: Global
[stakeholder team names]: Risk, Operations, and Compliance Teams
</variables>

<context>
I'm a [job role] at a financial institution in [country/region].
I need to assess the downstream exposure of a third-party
provider incident, identifying which institutional services
are affected, what the customer-facing impact is, and whether
concentration risk across shared infrastructure amplifies
the threat beyond this single provider incident for
[stakeholder team names].
</context>

<task>
Using the provider incident report or alert pasted below,
which may be a vendor notification, sector alert,
open-source intel report, or internal monitoring alert,
produce a third-party and ecosystem risk assessment.

Assess which institutional services are exposed, map
customer-facing impact, identify concentration risk across
shared providers, and flag any regulatory notification
implications triggered by the provider incident.

If the incident report is sparse or early-stage, document
what is known, flag what is unconfirmed, and recommend
monitoring actions while the incident develops.

State "Not available in source material" for any field
where information is absent, do not fill gaps with
assumptions.

Before using this prompt, confirm the intelligence has
been sanitized in accordance with your institution's
data handling and TLP compliance requirements.

[PASTE INCIDENT REPORT, VENDOR NOTIFICATION, PUBLIC URL
OR INDUSTRY ALERT HERE]
</task>

<output_format>
## Third-Party and Ecosystem Risk Assessment

### 1. Incident Summary, Read First
| Field | Detail |
|-------|--------|
| Provider / vendor affected | |
| Incident type | Outage / Vulnerability / Breach / Ransomware / Other |
| Incident status | Confirmed / Developing / Unconfirmed |
| Source of this report | Vendor notification / Open-source report / Internal |
| Immediate action required | Yes / No, summarize in one line |

### 2. Institutional Service Exposure
| Service | Provider Dependency | Exposure Level | Current Status |
|---------|--------------------|--------------------|----------------|
| | Direct / Indirect | Confirmed / Probable / Possible | Affected / Monitoring / Unaffected |

### 3. Customer-Facing Impact
| Impact Area | Assessment | Confirmed / Estimated |
|-------------|------------|----------------------|
| Transaction processing | | |
| Account access | | |
| Payment authorization | | |
| Customer notifications required | | |

### 4. Concentration Risk
- Does this provider support multiple critical services
  at this institution? Yes / No / Unknown
- Are other institutions likely affected by the same
  incident? Yes / No / Unknown
- Is there a single-provider dependency that amplifies
  exposure beyond this incident? Yes / No / Unknown
- Concentration risk assessment:

### 5. Regulatory and Notification Flags
- Does this third-party incident trigger this institution's
  own regulatory notification obligations?
  Yes / No / Requires Review
- Basis for determination:
- Recommended compliance team action:

### 6. Monitoring and Response Actions
| Action | Owner | Priority | Timeline |
|--------|-------|----------|----------|
| | CTI / Risk / Operations / Compliance | Immediate / 24hr / 72hr | |

### 7. Intelligence Gaps
- What information from the provider would materially
  change this assessment?
- Recommended monitoring sources while incident develops: Add URLs for the sources.
</output_format>

<guidelines>
1. If the incident report is early-stage or sparse, do not wait for complete information, document what is known, flag gaps, and recommend interim monitoring actions.
2. Concentration risk must be assessed even when a single provider is named, shared infrastructure in BFSI means one incident can affect multiple institutions simultaneously.
3. Regulatory notification flags must consider the institution's own obligations, not just the provider's, a third-party breach may trigger your reporting requirements independently.
4. Customer-facing impact should be assessed separately from technical service exposure, operational teams need to know what customers will experience, not just which systems are affected.
5. Ensure response action timelines are based on industry best practices and standards, not AI generated/based on AI judgement.
6. Do not use em dashes anywhere in the output. Use a comma, colon, or period instead.
</guidelines>
```

## Notes
How to action the output: use the service exposure mapping to brief operations and risk teams on what is immediately at risk before the provider issues formal guidance; use the concentration risk section to identify whether other providers or services share the same vulnerability; use the regulatory flags to determine whether a third-party incident triggers your institution's own notification obligations.
