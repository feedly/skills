---
name: cti-risk-delta
description: Rates a threat against the OWASP Risk Rating Methodology, then rates it again counting only the mitigations the CTI team has taken or formally committed to, and shows the before and after side by side with a financial exposure band sized to the organization. Use this skill whenever the user wants to score or rate a threat, measure risk before and after CTI action, show residual risk, quantify what actioned intelligence removed from the risk picture, produce a risk reduction or risk delta assessment, or says things like "what did our CTI work actually change", "rate this threat for my org", "score this report with OWASP", "show the risk reduction from these mitigations", or hands over a threat report and asks what the risk is to their organization. Also use it when a CISO or board needs a defensible before and after rating with a money band behind it. Produces the assessment as markdown and as a Word document.
---

# CTI Risk Delta: OWASP rating before and after CTI action

CTI teams get asked what impact their work had, and the answer is usually
spread across tickets, detections and briefings rather than sitting in a
number. This skill takes a threat, rates it against the OWASP Risk Rating
Methodology, then rates it again counting only the mitigations the team has
taken or formally committed to, and puts the two side by side. Where the
user gives a reporting currency and a rough annual profit bracket, it also
reports the OWASP Financial Damage anchor as a money band sized to their
organization.

Treat the CTI team as the subject of the measurement, not just the author of
the report.

Read `references/owasp-factors.md` before scoring anything. Read
`references/financial-exposure-bands.md` before asking the currency and
profit questions. Read `references/mitigation-rules.md` before re-scoring.
The scoring reads those anchors every run, which is what makes a factor
scored a seven in January still a seven in August.

## Workflow

Eight steps, Step 0 to Step 7, in order. Do not skip ahead and do not produce the final output
until Step 6. Stop and wait for the user at the end of Steps 0, 3 and 5. No
score previews before Step 4, and no residual figures before Step 6.

### Step 0. Intake

The skill needs a small amount of context the threat reporting cannot carry.
Ask only for what the user has not already given you, using the
multiple-choice question tool where the answer is a choice and plain text
where it is not. If the user has already supplied all of it in their
request, skip this step entirely and say nothing about it.

- Their role. Default: Threat Intelligence Analyst.
- Their sector. Default: cross-industry.
- Their country or region. This sets the currency options later. Default:
  global.
- Who the assessment is for. Default: security leadership.
- Org context: internet-facing assets, key controls, detection coverage,
  business dependencies. Default: not provided, in which case assume no
  organizational detail and take everything from the Step 3 questions.
- Whether the organization has its own financial impact bands, one per OWASP
  Financial Damage anchor, each with an explicit currency. Default: not
  provided, in which case derive them at Step 3.

Also confirm you have the source reporting. If the user has not attached or
pasted a threat report, ask for it. Do not proceed on a threat name alone.

### Step 1. Identify the risk

From the source reporting only, state what the threat is, who is behind it
or "Unattributed", the vulnerability or weakness it exploits, the attack
method, and what it targets. Two or three sentences. If the reporting covers
several distinct risks, name them, ask the user which one to rate, and rate
one at a time.

### Step 2. Score the six factors the reporting can answer

Score Skill Level, Motive, Size, Ease of Discovery, Ease of Exploit and
Awareness from the reporting, using the scales in
`references/owasp-factors.md`. Cite the evidence for each. Where the
reporting does not support a factor, say so and carry it into Step 3 as a
question rather than guessing.

### Step 3. Ask for the remaining factors

Ten factors depend on the organization, not the threat, so the reporting
cannot answer them. Ask only for the ones you cannot already score from the
reporting or the org context, following the question rules below. Do not
proceed until every factor has a score.

### Step 4. Produce the rating before CTI action

Calculate likelihood, technical impact and business impact per the scoring
arithmetic in `references/owasp-factors.md`, read the severity off the OWASP
matrix, and present it in three lines or fewer. Then move straight to Step
5. Do not write the full report yet.

### Step 5. Capture mitigation, then extend it

**5a.** Lock the Step 4 scores as the "before CTI action" baseline. From
here on, no factor moves unless a specific named action moves it.

**5b.** Ask the user this question, using the multiple-choice question tool,
with these options exactly:

"Does your CTI team have existing mitigations in place or mitigations
planned?"

1. Yes, I will provide them.
2. No, can you recommend a list of mitigations/actions we can take?
3. Yes, I will provide them, but can you also recommend additional
   mitigations that can be taken?

The question tool appends its own "Other" option, so supply only options 1
to 3 and let the tool add the fourth. Never show "Other" twice.

If the user picks 1 or 3, reply with a single short request asking them to
type in the details, or drop in a file, covering the actions the CTI team
has taken or the recommendations that have been acted on, and who owns each.
Name the kinds of thing that count, in one line: intelligence shared with
SecOps, detections written, IOCs blocked, hunts run, patching driven,
advisories issued, tabletop or playbook work, briefings that changed a
decision. Wait for their input. If they attach or reference a file, read it
and pull the actions, owners and status out of it. Then ask about status
only for the actions where it is still unclear, using the 5c question
format.

If the user picks 2, go straight to 5c.

If the user picks 4, ask one plain-text follow-up to find out what they
mean, then route to whichever of 1, 2 or 3 fits.

**5c.** Ask which actions have been taken or will be taken.

If the user picked 2 or 3, first propose additional actions the CTI team
could take or drive with other security stakeholders. Each must name the
OWASP factor it would move, the stakeholder who owns it, and the expected
score change. Ground every one in this specific threat, not generic
hardening. Cap the list at eight.

At least one proposed action must target a business impact factor: Financial
Damage, Reputation Damage, Non-compliance or Privacy Violation. Severity is
read from business impact, so a list that only moves likelihood and
technical impact factors cannot change the severity word no matter how much
work the team does. If no credible action against this specific threat moves
a business impact factor, say so in one line rather than inventing one.

If loss bands are in play, whether supplied or derived, state explicitly
whether any credible action against this specific threat moves Financial
Damage. If none does, write that in one line and expect the band not to
move. Never propose a Financial Damage action solely to make the band move.

Then ask about each action, using the multiple-choice question tool, one
question per action, batched four questions to a round. Phrase each one as a
question about that specific action, not as a rating exercise:

"Has your team done this, or will it? [name the action]"

- Already taken [counts toward residual risk]
- Planned and committed, give the target date [counts toward residual risk]
- Not planned [does not count]

Let the tool add its own "Other" option. Do not supply one.

A commitment with no date does not count. If the user picks the second
option without a date, treat it as undated and record it in Appendix D as
"committed, no date given". Do not ask again and do not describe it as Not
planned, because that is not what the user said.

Ask the same question about any action the user listed at 5b whose status is
unclear. Do not ask about an action whose status the user has already given
you.

### Step 6. Produce the final output

Re-score under `references/mitigation-rules.md` to produce the residual
rating, then write the assessment in the output format below, using
`assets/assessment-template.md` as the skeleton. Save it as a markdown file
and send it to the user.

### Step 7. Build the Word document

Read the docx skill's SKILL.md, then build the same assessment as a .docx
and send that too. Same content, same section order, no additions. Tables
stay tables. Send both files.

## Question rules

Ask for the organization-dependent factors using the multiple-choice
question tool, batched into three rounds. Each option label must carry its
OWASP score in brackets. Each option description must translate the OWASP
wording into what it means for this specific threat, not the generic
definition.

Ask only the questions you actually need to complete the score. Before each
round, drop any question already answered by the reporting or by the org
context, and say which factor you scored from that context instead. Never
ask a question you already have the answer to, and never pad the round to
four.

- **Round 1:** Opportunity, Intrusion Detection, Loss of Confidentiality,
  Loss of Integrity.
- **Round 2:** Loss of Availability, Loss of Accountability, Financial
  Damage, Reputation Damage.
- **Round 3:** Non-compliance, Privacy Violation, and any factor from Step 2
  the reporting could not support.

The two loss band questions in `references/financial-exposure-bands.md` item
2, currency and annual profit bracket, sit between Round 1 and Round 2. They
are asked once, together in a single batch, and they do not count toward the
four questions in a round. The bands they produce are printed in one line
before Round 2 under item 2b.

Frame every question against this threat and this organization. Ask "If this
actor reached the systems this threat targets, how much of your data would
be exposed?", not "Rate loss of confidentiality."

Where an OWASP factor has five options and the tool allows four, use the
merges listed at the end of `references/owasp-factors.md`.

Ask a follow-up only where an answer was free text you cannot map to an
OWASP option, contradicts another answer, or left a factor unscored. Stop as
soon as all sixteen factors have a score. A factor you cannot score is the
only reason to ask another question.

If the multiple-choice question tool is unavailable, ask the same questions
as a numbered list in plain text with the same lettered options and scores,
and wait for the answers. This applies to Step 0 and Step 5 as well as the
three rounds. It also applies to the two loss band questions: ask them as a
numbered list with the same bracket options, and do not ask for the four
bands directly, because the item 2a table is what turns the bracket into
bands.

## Output format

Return Markdown in exactly the structure in `assets/assessment-template.md`.
Everything above the appendix fits on half a screen, or on one screen where
a financial exposure section is present. No preamble, no restating the
questions, no closing summary.

The details the template compresses:

1. **BLUF.** One sentence on the threat and what CTI action did to its risk
   rating, then three bullets carrying numbers and bands only, no commentary.
2. **Fourth BLUF bullet**, only if the severity word did not change, naming
   the figures that did fall and the number of factors behind the move, so
   the reduction is not invisible.
3. **Fifth BLUF bullet**, only if loss bands are in play, the band moved,
   and at least one action that moved it is Taken rather than Planned.
   Phrase it exactly as the template gives it, keeping "if realised" so the
   figure cannot be read as an expected or annualised loss, and keeping
   "was" and "now" so two ranges cannot run together. This is the line most
   likely to reach a board slide on its own, so it may only carry movement
   that has actually happened.
4. **Financial exposure section.** Two lines, both carrying "if realised".
   Then one line following items 7 and 7a of the bands reference: if the
   band moved, name the action that moved it, the team that implemented it,
   whether that action is Taken or Planned with its date, and how many
   actions moved Financial Damage by how many options. If it did not move,
   write "Financial Damage did not move", then one clause naming what did
   move instead, using the exact wording in item 7 for the two branches it
   names. Then the joint attribution sentence from item 8. Nothing else.
5. **Appendix A** carries all sixteen rows in OWASP order, with Basis as
   "Reporting" or "Analyst input", and the action named against any factor
   that moved.
6. **Appendix F** carries this line verbatim, choosing the clause that
   matches where the bands came from: "This is the effect on annual profit
   the organization would expect if this threat were realised at the
   selected level, in [the organization's own bands / bands sized to the
   annual profit figure the organization gave]. It is conditional on the
   threat happening. No likelihood, frequency or probability has been
   applied to it. Do not multiply it by the likelihood score." Its scope
   clause states that Financial Damage is one of four business impact
   factors, so the band can stay flat while the severity word falls, and can
   move without the severity word changing, and that neither is an error;
   and that the scale has four rungs with movement capped at one, so the
   smallest and the largest change this band can express are the same size,
   and no partial reduction is representable.

## Guidelines

1. Score the reporting-derived factors from the source reporting only. If a
   detail is not in the source, write "Not stated in source" and ask the
   user rather than inferring it.
2. Do not fabricate threat actors, CVEs, ATT&CK IDs, malware names,
   targeting, organizational detail, currency figures or loss bands. Bands
   read from the item 2a table, against the currency and profit bracket the
   user selected, are not fabrication and are the only derived currency
   figures permitted anywhere in the output. Any other currency figure you
   did not receive from the user is.
3. Never guess an organization-dependent factor. Score it from org context
   if the answer is there, otherwise ask. Do not ask twice.
4. Use the exact OWASP option values. A score that is not on the scale is an
   error, not a nuance.
5. Use estimative language (ICD 203) for analytical judgments about the
   threat, and be plain and definite about the arithmetic.
6. Every number above the appendix must be traceable to a row in Appendix A,
   and every currency figure to a line in Appendix F.
7. Write the final output tight. No introductions, no restating the OWASP
   methodology, no explaining what a residual rating is, no hedging phrases,
   no adjectives that carry no information, no sentence that only sets up
   the next one. If a table already says it, do not say it again in prose.
   Above the appendix, plain language a non-security reader follows; detail
   goes in the appendix.
8. Do not use em dashes anywhere in the output.

## Verification before you finish

Verify: all sixteen factors are scored in both ratings, every mean is
arithmetically correct and rounded half up, technical and business impact
were never averaged together, both severities match their matrix cell, no
untouchable factor moved, at least one proposed action targeted a business
impact factor or the output says why none could, nothing the user marked
"Not planned" or left unconfirmed reduced residual risk, and no residual
score is higher than its before score.

Where bands are present, whether supplied or derived, also verify: both
bands were read from the Financial Damage row and nothing else, the user
answered Financial Damage against the banded option labels, no band was
multiplied, divided, annualised, averaged or collapsed to a point figure,
every currency figure in the output was either supplied by the user or read
from the item 2a table for the bracket the user selected, no figure was
converted between currencies, the band set carries a currency and is ordered
and non-overlapping, the band source is stated, Financial Damage moved by no
more than one option in total, no action was counted against both a
likelihood factor and a business impact factor, every Planned action carries
a date, the fifth BLUF bullet is absent unless at least one mover is Taken,
and the difference between the bands is nowhere described as savings, cost
avoided or return.

Where the user declined the currency or profit bracket questions, verify the
financial exposure section and Appendix F are both absent and no currency
figure appears anywhere in the output.

State the result of that check in one line at the end of Appendix E.

## How to action the output

Take the BLUF and the risk rating table into stakeholder or board reporting
as the record of what CTI changed on this threat. Where a financial exposure
band is present, use it to say which band the threat sits in now, and say
plainly that it is the effect on annual profit if the threat is realised,
conditional on it happening, with no likelihood applied. If someone in the
room multiplies it by the likelihood score, that is not a number this method
produced. Where the bands were sized from a profit bracket rather than
lifted from the organization's own risk appetite framework, say so, and
treat closing that gap with the risk team as the follow up, because their
bands will carry more weight than a derived set. Hand Appendix D to the
named owners as the next set of asks, and re-run the skill when a planned
action lands or a new one gets committed.