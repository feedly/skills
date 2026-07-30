# Build prioritized control-gap recommendations

**Source report:** How to Automate Common CTI Workflows
**Source URL:** https://feedly.com/ti-essentials/posts/how-to-automate-common-cti-workflows
**Section / workflow:** Workflow 4: Scoping the threat to your assets and controls, Step 6: Build prioritized recommendations

## What this prompt does
This prompt turns the exposed-products and control-gap list (produced by the n8n CMDB-scoping workbook earlier in Workflow 4) into first-pass, prioritized recommendations the analyst can refine. For each gap it gives the in-scope technique it addresses, the affected product, the recommended countermeasure (D3FEND, NIST CSF, or CIS), and a first-pass priority, skipping any control already marked implemented.

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
[stakeholder team names]: security operations and engineering
[data]: the exposed-products and gap list provided below
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to give [stakeholder team names] prioritized recommendations to close the control gaps for products we confirmed we run, with our existing controls taken into account.
</context>

<task>
Using the exposed-products and gap list in [data], draft prioritized recommendations to close the gaps. For each gap, give the in-scope technique it addresses, the affected product, the recommended countermeasure, and a first-pass priority.
</task>

<output_format>
| Exposed product | In-scope technique | Gap | Recommended countermeasure (D3FEND, NIST CSF, or CIS) | First-pass priority | Owning team | Notes |
|-----------------|--------------------|-----|-------------------------------------------------------|---------------------|-------------|-------|
</output_format>

<guidelines>
1. Recommend only against gaps present in [data]; do not introduce controls for techniques not listed or for products not confirmed in scope.
2. Skip any countermeasure already marked as implemented.
3. First-pass priority and the owning team are suggestions for the analyst to confirm against business criticality and implementation effort. Mark effort estimates as [ANALYST CONFIRMS].
4. Use estimative language. Avoid absolute claims about effectiveness.
5. Return Markdown only.
</guidelines>
```

## Notes
- This is the second resource for Workflow 4; the first is an n8n workbook (a JSON scaffold, not a prompt) that cross-references your CMDB and looks up D3FEND controls to produce the gap list this prompt consumes.
- The analyst still prioritizes gaps against business criticality and real implementation cost. Route each confirmed recommendation to the owning team, ideally via scoped tickets raised through the Workflow 5 automation.
