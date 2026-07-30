# Hunt lead feasibility and coverage assessment

**Source report:** CTI Prompt Library (Volume 2)
**Source URL:** https://feedly.com/ti-essentials/posts/cti-prompt-library-volume-2
**Section / workflow:** Threat hunting prompts (Prompt 7), contributed by Nathan Hoffman, Security Data Engineer

## What this prompt does
For each hunt lead in the source (which can be the output of the hunt lead extraction prompt or a list you provide), assesses how feasible it is to run the hunt given your logging, controls, existing detections, and analyst capacity. It helps a hunt lead or manager decide which leads to assign, defer, or escalate before committing analyst time, and identifies logging/control gaps to close first.

## Prompt
```
<variables>
[job role]:
[sector name]:
[country/region]:
[stakeholder team names]:
[product/service]:
[data]:
[stack summary]:
[analyst capacity]:
** Note about default_behavior **
If no value is provided for a variable (left blank after colon), use these defaults:
[job role]: Threat Intelligence Analyst
[sector name]: cross-industry
[country/region]: global
[stakeholder team names]: threat hunting team
[product/service]: hunt lead feasibility and coverage assessment
[data]: the reports pasted below. If none are provided, ask the analyst for source material, or use web search when the analyst directs you to, rather than drawing on general training knowledge
[stack summary]: Not provided. List the data sources each lead would require and mark coverage as "unknown, confirm against your stack."
[analyst capacity]: Not provided. Give effort estimates only and skip the resourcing recommendation.
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service]. Our logging sources, detection tooling, and key controls are described in [stack summary]. Our available hunting resource is described in [analyst capacity]. The output will be used to decide which leads to hunt now, which to defer, and which need a logging or control gap closed first.
</context>

<task>
For each hunt lead in the [data] (this can be the output of the hunt lead extraction prompt or a list you provide), assess how feasible it is to run the hunt given our logging, controls, existing detections, and analyst capacity. The goal is to help a hunt lead or manager decide which leads to assign, defer, or escalate before committing analyst time.
</task>

<output_format>
## 1. Feasibility Assessment Table
| Lead ID | Hunt Lead | Required data sources | Logging or control gaps (against [stack summary]) | Existing detection coverage (Covered / Partial / None / Unknown) | Complexity (Low / Med / High) | Estimated effort (analyst-hours or S/M/L) | Effort rationale (one line) | Skills required | Recommended disposition (Hunt now / Defer / Close gap first / Convert to detection) | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
Always print the complete table. If this is a re-run or revision, re-emit every row, not only the rows that changed.
## 2. Logging and Control Gap Notes
For each lead that cannot be hunted today, name the specific missing data source or control and what would need to change to make the hunt possible.
## 3. Existing Detection Evaluation
For each lead already covered by a detection, state whether the coverage looks sufficient or needs tuning, and recommend converting any lead that is fully covered into a maintained detection rather than a repeat hunt.
## 4. Resourcing Recommendation
Map the "Hunt now" leads against [analyst capacity]. Suggest a sequence, separate quick wins from larger efforts, and note any lead that needs a skill the team does not currently have.
## 5. Assumptions and Intelligence Gaps
List the assumptions you made and any information that would change the assessment if provided.
## 6. Validation Status
State that effort and coverage estimates depend entirely on the supplied [stack summary] and [analyst capacity], that coverage marked Unknown was not assumed, and what a human should confirm before resourcing.
</output_format>

<guidelines>
1. Ground the gap analysis in [stack summary]. If it is not provided, list the data sources each lead requires and mark coverage as "unknown, confirm against your stack." Do not invent data.
2. Be specific about gaps. "No PowerShell ScriptBlock logging (Event ID 4104) enabled on workstations" is useful; "logging could be improved" is not.
3. Do not recommend tooling the team does not already have unless you flag it explicitly as a gap-closing recommendation with an effort estimate.
4. Every complexity and effort estimate must carry a one-line rationale tied to the data sources, query difficulty, or environment scope the hunt requires.
5. Use estimative probability language rather than absolutes, and assign a confidence level to every row.
6. For existing detection coverage, do not assume coverage that is not described in [stack summary]. Mark it "Unknown" rather than guessing.
7. Do not fabricate data sources, detection names, or control names. Use only what is in [data] and [stack summary].
8. Cite the source for each lead.
9. Before you finish, verify each assessment against [data] and [stack summary], confirm the full table was emitted, confirm no coverage was assumed beyond what the stack states, and flag anything you could not confirm.
10. Do not use em dashes anywhere in the output.
</guidelines>
```

## Notes
The gap analysis is highly dependent on the data provided in the "Stack summary" variable. The more data provided, the better the output quality. Share the "Hunt now" leads with your threat hunters, route "Close gap first" leads to whoever owns logging with the specific gap attached, and convert fully covered leads into maintained detections. This is step 2 of Chain 2 (Report to prioritized, feasible hunt).
