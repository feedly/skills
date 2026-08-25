# Risk assessment: [threat name]

## BLUF

One sentence: the threat, and what CTI action did to its risk rating. Then these bullets, numbers and bands only, no commentary:

- Risk before CTI action: [severity word] (likelihood X / 9, technical impact Y / 9, business impact Z / 9)
- CTI actions: [N] taken, [M] planned
- Residual risk: [severity word] (likelihood X / 9, technical impact Y / 9, business impact Z / 9)

<!--
Fourth bullet, only if the severity word did not change. Name the figures that
did fall and the number of factors behind the move, so the reduction is not
invisible. For example:
- Movement: technical impact 7.5 to 5.0 and likelihood 8.1 to 7.3 across six factors, severity unchanged.

Fifth bullet, only if loss bands are in play, the financial exposure band moved,
and at least one action that moved it is Taken rather than Planned. Phrase it
exactly like this, keeping "if realised" and keeping "was" and "now":
- Financial exposure if realised: was [before band], now [residual band] ([N] actions moved it, [M] of those planned).
Do not add this bullet if the band did not move, or if every action that moved
it is Planned.
-->

## Threat

One or two bullets. What it is and who is behind it, then what it puts at risk in this organization. No jargon a CISO would have to look up.

## Risk rating

| Rating | Likelihood (0-9) | Technical impact (0-9) | Business impact (0-9) | OWASP severity |
|--------|------------------|------------------------|-----------------------|----------------|
| Risk, before CTI action | | | | |
| Residual risk, after CTI actions taken or planned | | | | |

One line under the table naming which impact figure the severity was read from. Nothing else.

## Financial exposure

<!-- Include this section only if loss bands are in play. -->

- Before CTI action, if realised: [Financial Damage anchor wording] ([band])
- Residual, if realised: [Financial Damage anchor wording] ([band])

Then one line, following items 7 and 7a of `references/financial-exposure-bands.md`. Then the joint attribution sentence from item 8. Nothing else.

---

# Appendix

## A. Factor scoring

| # | Factor | Group | Before | Residual | Basis | Evidence or rationale |
|---|--------|-------|--------|----------|-------|-----------------------|

All sixteen rows, in OWASP order. Basis is "Reporting" or "Analyst input". Evidence is the citation from the source reporting for reporting-derived factors, and the user's answer for the rest. For any factor that moved, name the action that moved it. Keep every cell to a phrase.

## B. Calculation

For both ratings, show likelihood as the sum of its eight factor scores over eight, technical impact as the sum of its four over four, and business impact as the sum of its four over four. State the level each figure converts to, and the matrix cell the severity came from.

## C. Actions counted in residual risk

| # | Action | Owner | Status | Factor moved | Score change |
|---|--------|-------|--------|--------------|--------------|

Status is Taken or Planned. Include actions the user reported that moved no factor, with "None" in the factor column and a short reason.

## D. Actions not counted

| # | Action or recommendation | Suggested owner | Factor it would move | Expected change |
|---|--------------------------|-----------------|----------------------|-----------------|

Everything the user marked "Not planned", never confirmed, or committed without a date. Mark the last of those "committed, no date given" and say in the same row that it moved nothing for that reason. Only actions specific to this threat. Omit the section if there are none.

## E. Assumptions and validation status

Bullets, one line each: factors scored from a single source, answers that were estimates rather than known values, anything the reporting could not support, and what a human should confirm before this rating is used in a decision. Where there are no loss bands, one bullet naming what would be needed for a financial exposure band. Last line is the result of the final verification check.

## F. Basis of the financial exposure band

<!-- Omit this section entirely if there are no bands. Eight lines maximum, in this order, dropping from the bottom if you must. -->

- Currency, and the four bands.
- Source of the bands.
- Where the bands were derived, one line on the working figure and the ladder.
- Whether the bands passed the item 2b check on currency, ordering and overlap.
- The Financial Damage anchor selected for each rating, and the action that moved it if it moved, with its Taken or Planned status and date.
- The verbatim conditionality line from item 6 of the output format section in SKILL.md.
- Scope, two clauses.