# CTI Risk Rating and Residual Risk Prompt: OWASP Scoring Before and After CTI Action

**Why this prompt matters.** CTI teams get asked what their work changed, and the answer tends to be scattered across tickets, detections, and briefings that nobody ever scored. This prompt rates a threat against your organization using the OWASP Risk Rating Methodology, then rates it again counting only the mitigations your team has taken or formally committed to. The before and after sit side by side in one table. Where you can give a reporting currency and a rough annual profit bracket, it also reports the OWASP Financial Damage anchor as a money band sized to your organization, which is usually the part that survives into a board pack.

**Who benefits.** CTI analysts and team leads who need to show what actioned intelligence removed from the risk picture, rather than how many reports they published last quarter; CISOs who need a defensible before and after rating, and a money band that holds up when someone in finance asks where the figure came from.

**How to action the output.** Take the BLUF and the risk rating table into your stakeholder or board reporting as the record of what CTI changed on this threat. Where a financial exposure band is present, use it to say which band the threat sits in now, and say plainly that it is the effect on annual profit if the threat is realised, conditional on it happening, with no likelihood applied. If someone in the room multiplies it by the likelihood score, that is not a number this method produced. Where the bands were sized from a profit bracket rather than lifted from your own risk appetite framework, say so, and treat closing that gap with your risk team as the follow up, because their bands will carry more weight than a derived set. Hand Appendix D to the named owners as the next set of asks, and re-run the prompt when a planned action lands or a new one gets committed.

---

Copy everything below into your AI assistant, fill in the variables, and attach or paste your source report(s).

```
<variables>
Fill in the bracketed variables. If left blank, the default behavior applies.

[job role] - Your role. Default: Threat Intelligence Analyst.
[sector name] - Your industry. Default: cross-industry.
[country/region] - Your operating geography. Default: global.
[stakeholder team names] - Who this assessment is for. Default: security leadership.
[product/service] - The deliverable you are producing. Default: OWASP risk rating and residual risk assessment.
[data] - The threat report(s) to assess. Paste or attach the full source material. Default: access your own dataset.
[org context] - A short description of your relevant environment: internet-facing assets, key controls, detection coverage, business dependencies. Default: not provided, so assume no organizational detail. Everything needed about the organization comes from the questions in Step 3.
[loss bands] - Your organization's own financial impact bands, one per OWASP Financial Damage anchor, each with an explicit currency. Default: not provided, so derive them from the two questions in <financial_exposure_band> item 2 and the table in item 2a. If the user declines to give a currency or a profit bracket, omit the financial exposure section and Appendix F entirely.
</variables>

<context>
I'm a [job role] in the [sector name] industry, in [country/region]. My goal is to provide [stakeholder team names] team(s) with a [product/service], working from the threat reporting in [data]. Known organizational context is in [org context]. My organization's own financial impact bands, if I have them, are in [loss bands].

The output is used to show what the risk associated with this threat was before the CTI team acted on it, and what it is after. Treat the CTI team as the subject of the measurement, not just the author.
</context>

<task>
Rate the threat described in [data] using the OWASP Risk Rating Methodology, then rate it again after the mitigating actions the CTI team has taken or has committed to take.

Work in six steps, in order. Do not skip ahead and do not produce the final output until Step 6.

Step 1. Identify the risk. From [data] only, state what the threat is, who is behind it (or "Unattributed"), the vulnerability or weakness it exploits, the attack method, and what it targets. Two or three sentences. If the reporting covers several distinct risks, name them, ask the user which one to rate, and rate one at a time.

Step 2. Score the six factors the reporting can answer. Score Skill Level, Motive, Size, Ease of Discovery, Ease of Exploit, and Awareness from [data] using the scales in <owasp_factors>. Cite the evidence for each. Where the reporting does not support a factor, say so and carry it into Step 3 as a question rather than guessing.

Step 3. Ask the user for the remaining factors, up to ten of them. These depend on the organization, not the threat, so the reporting cannot answer them. Ask only for the ones you cannot already score from [data] or [org context]. Follow <question_rules> exactly, and do not proceed until every factor has a score. Capture the currency and the annual profit bracket before Round 2, and size the loss bands from them, as described in <financial_exposure_band>.

Step 4. Produce the risk rating before CTI action. Calculate Likelihood and Impact per <scoring_rules>, read the severity off the OWASP matrix, and present it in three lines or fewer. Then move straight to Step 5. Do not write the full report yet.

Step 5. Capture mitigation, then extend it.

5a. Lock the Step 4 scores as the "before CTI action" baseline. From here on, no factor moves unless a specific named action moves it.

5b. Ask the user this question, using the multiple-choice tool, with these options exactly:

"Does your CTI team have existing mitigations in place or mitigations planned?"
1. Yes, I will provide them.
2. No, can you recommend a list of mitigations/actions we can take?
3. Yes, I will provide them, but can you also recommend additional mitigations that can be taken?
4. Other

If the multiple-choice tool appends its own "Other" option, supply only options 1 to 3 and let the tool add the fourth. Never show "Other" twice.

If the user picks 1 or 3, reply with a single short request asking them to type in the details, or drop in a file, covering the actions the CTI team has taken or the recommendations that have been acted on, and who owns each. Name the kinds of thing that count, in one line: intelligence shared with SecOps, detections written, IOCs blocked, hunts run, patching driven, advisories issued, tabletop or playbook work, briefings that changed a decision. Wait for their input. If they attach or reference a file, read it and pull the actions, owners and status out of it. Then ask about status only for the actions where it is still unclear, using the 5c question format.

If the user picks 2, go straight to 5c.

If the user picks 4, ask one plain-text follow-up to find out what they mean, then route to whichever of 1, 2 or 3 fits.

5c. Ask which actions have been taken or will be taken.

If the user picked 2 or 3, first propose additional actions the CTI team could take or drive with other security stakeholders. Each must name the OWASP factor it would move, the stakeholder who owns it, and the expected score change. Ground every one in this specific threat, not generic hardening. Cap the list at eight.

At least one proposed action must target a business impact factor: Financial Damage, Reputation Damage, Non-compliance or Privacy Violation. Severity is read from business impact, so a list that only moves likelihood and technical impact factors cannot change the severity word no matter how much work the team does. If no credible action against this specific threat moves a business impact factor, say so in one line rather than inventing one.

If loss bands are in play, whether supplied or derived, state explicitly whether any credible action against this specific threat moves Financial Damage. If none does, write that in one line and expect the band not to move. Never propose a Financial Damage action solely to make the band move.

Then ask about each action, using the multiple-choice tool, one question per action, batched four questions to a round. Phrase each one as a question about that specific action, not as a rating exercise:

"Has your team done this, or will it? [name the action]"
- Already taken [counts toward residual risk]
- Planned and committed, give the target date [counts toward residual risk]
- Not planned [does not count]

Let the tool add its own "Other" option. Do not supply one.

A commitment with no date does not count. If the user picks the second option without a date, treat it as undated and record it in Appendix D as "committed, no date given". Do not ask again and do not describe it as Not planned, because that is not what the user said.

Ask the same question about any action the user listed at 5b whose status is unclear. Do not ask about an action whose status the user has already given you.

Step 6. Produce the final output in <output_format>. Re-score under <mitigation_rules> to produce the residual rating.
</task>

<owasp_factors>
Every factor is scored 0 to 9 using these options exactly. Do not invent intermediate values and do not interpolate.

LIKELIHOOD, threat agent factors
Skill Level: no technical skills 1 | some technical skills 3 | advanced computer user 5 | network and programming skills 6 | security penetration skills 9
Motive: low or no reward 1 | possible reward 4 | high reward 9
Opportunity: full access or expensive resources required 0 | special access or resources required 4 | some access or resources required 7 | no access or resources required 9
Size: developers 2 | system administrators 2 | intranet users 4 | partners 5 | authenticated users 6 | anonymous internet users 9

LIKELIHOOD, vulnerability factors
Ease of Discovery: practically impossible 1 | difficult 3 | easy 7 | automated tools available 9
Ease of Exploit: theoretical 1 | difficult 3 | easy 5 | automated tools available 9
Awareness: unknown 1 | hidden 4 | obvious 6 | public knowledge 9
Intrusion Detection: active detection in application 1 | logged and reviewed 3 | logged without review 8 | not logged 9

IMPACT, technical factors
Loss of Confidentiality: minimal non-sensitive data disclosed 2 | minimal critical data disclosed 6 | extensive non-sensitive data disclosed 6 | extensive critical data disclosed 7 | all data disclosed 9
Loss of Integrity: minimal slightly corrupt data 1 | minimal seriously corrupt data 3 | extensive slightly corrupt data 5 | extensive seriously corrupt data 7 | all data totally corrupt 9
Loss of Availability: minimal secondary services interrupted 1 | minimal primary services interrupted 5 | extensive secondary services interrupted 5 | extensive primary services interrupted 7 | all services completely lost 9
Loss of Accountability: fully traceable 1 | possibly traceable 7 | completely anonymous 9

IMPACT, business factors
Financial Damage: less than the cost to fix the vulnerability 1 | minor effect on annual profit 3 | significant effect on annual profit 7 | bankruptcy 9
Reputation Damage: minimal damage 1 | loss of major accounts 4 | loss of goodwill 5 | brand damage 9
Non-compliance: minor violation 2 | clear violation 5 | high profile violation 7
Privacy Violation: one individual 3 | hundreds of people 5 | thousands of people 7 | millions of people 9
</owasp_factors>

<financial_exposure_band>
This block translates one OWASP factor into money bands sized to the organization. It is a lookup, not a loss model. Follow it exactly.

1. Financial Damage is already a money scale in OWASP wording: less than the cost to fix the vulnerability 1, minor effect on annual profit 3, significant effect on annual profit 7, bankruptcy 9. Those four anchors get currency ranges from one of two places, in this order of preference: [loss bands], where the organization already has its own, or the table in item 2a, applied to the currency and annual profit bracket the user gives in item 2. The prompt reports which band the threat sat in before CTI action and which band it sits in after. It does not price the threat and it does not build a loss estimate.

1a. Read the OWASP wording literally, because it decides what the band means. Two of the four anchors are expressed as an effect on annual profit. So the band is the effect on annual profit this organization would expect if this threat were realised. It is conditional on the threat happening. It is not a per event cost, it is not an expected annual loss, and no likelihood, frequency or probability is applied to it anywhere. Use the phrase "if realised" every time the band appears above the appendix, and never the phrase "per year" or "one occurrence".

2. If [loss bands] is provided, use it and skip to item 2b. An organization's own published bands always beat a derived set. If it is not provided, and [org context] does not contain it, derive the bands from the organization's annual profit. Ask these two questions once, both in the same batch, using the multiple-choice tool, immediately before Round 2 of <question_rules>. They do not count toward the four questions in a round. Do not ask either of them twice.

   Question 1, currency:

   "What currency does your organization report in?"

   Offer the three currencies most plausible for [country/region] as the options, for example US dollar, euro, pound sterling. Let the tool add its own Other for anything else. Do not supply an Other of your own.

   Question 2, annual profit:

   "Roughly what is your organization's annual profit? I use this to size the OWASP money anchors to your organization. I do not need an exact figure and I am not going to price the threat."

   - under 10M
   - 10M to under 100M
   - 100M to under 1B
   - 1B and above

   Write the option labels in the currency chosen at question 1. Let the tool add its own Other.

2a. Turn the answer into four bands using this table and nothing else. Read the row. Do not recalculate it. The figures are numerals applied in the currency the user chose. Never convert a figure between currencies and never apply an exchange rate.

   | Bracket selected | Working figure | less than the cost to fix [1] | minor effect on annual profit [3] | significant effect on annual profit [7] | bankruptcy [9] |
   |---|---|---|---|---|---|
   | under 10M | 1M | under 10k | 10k to under 100k | 100k to under 1M | 1M and above |
   | 10M to under 100M | 10M | under 100k | 100k to under 1M | 1M to under 10M | 10M and above |
   | 100M to under 1B | 100M | under 1M | 1M to under 10M | 10M to under 100M | 100M and above |
   | 1B and above | 1B | under 10M | 10M to under 100M | 100M to under 1B | 1B and above |

   The working figure is the floor of the bracket the user selected, so the bands are the most conservative that bracket supports. Each boundary is one percent, ten percent and one hundred percent of the working figure, which is why every row is the same shape moved by one decade.

   Three things about this ladder have to be stated in Appendix F rather than left for the reader to work out:
   - The significant band closes at one hundred percent of the working figure, because a loss that consumes a full year of profit is where the OWASP wording stops calling the effect significant. The bankruptcy band is open ended above that.
   - "Less than the cost to fix the vulnerability" is not a share of profit in OWASP's wording. One percent of the working figure is used as a proxy so that all four anchors sit on one scale. Say that plainly. Do not imply OWASP defined it that way.
   - The bands are an order of magnitude wide because the OWASP scale has four rungs and movement is capped at one option. Precision beyond one significant figure would be false precision.

   Four things can come back through Other, and each has a fixed response:
   - An exact profit figure. Use it in place of the bracket floor and apply the same ladder: under one percent, one to under ten percent, ten to under one hundred percent, then the figure itself and above. Round every boundary to one significant figure.
   - No profit figure exists, for example a public body, a charity or a pre-profit company. Accept annual operating budget or annual revenue, apply the same ladder, and name in Appendix F which figure the bands were derived from. Never silently treat revenue as profit.
   - The user does not know, would rather not say, or asks to skip. Omit the financial exposure section and Appendix F per item 9, move on without comment, and do not ask again.
   - The user volunteers the organization's own bands. Use those instead of the derived set and record the source under item 4.

2b. Check the band set before you use it. Where the bands came from [loss bands], [org context] or the user directly, confirm that every band carries an explicit currency, that the four increase monotonically, and that they do not overlap. If any check fails, quote the bands back in one line, ask the user once to confirm or correct, and if that is not resolved report scores only. That single clarification is not a second ask under item 2. Bands read from the item 2a table are ordered, non overlapping and single currency by construction, so record that in Appendix F and check only that the currency from question 1 carried through to every band.

   Print the four bands in one line before Round 2, so the user can see what they are about to answer against. Do not ask a separate question to confirm them. The Round 2 Financial Damage question carries the same bands in its option labels under item 3, and answering it is the confirmation.

3. Whether the bands were supplied or derived, carry them into the Round 2 Financial Damage question. Each option label keeps its OWASP score and gains the matching band, for example "significant effect on annual profit [7], 1M to under 10M". The user is then answering in money sized to their organization, which is the point of collecting the currency and the profit bracket at all.

3a. The band may only be reported where the user answered the Financial Damage question directly against those banded option labels. If Financial Damage was estimated, inferred from [org context], or answered before the bands existed, omit the financial exposure section and Appendix F and record why in Appendix E. Bands supplied or derived after that question has been answered are accepted only if you re-put the one question with banded labels and the user re-confirms. That re-put is not a second ask under item 2.

4. Record where the bands came from, as one of: published risk appetite or ERM framework, finance or risk team provided, derived from the annual profit bracket the user selected using the item 2a table, analyst estimate. An analyst estimate is reported as such, and the financial exposure section states in one clause that the bands are unvalidated. A derived set is reported as such, and the financial exposure section states in one clause that the bands are sized from the profit figure the user gave and are not the organization's own published bands.

5. An open ended band cannot be reported as a figure. Where the bands were supplied, print the open ended one as the user gave it and add the clause "upper bound not stated by the organization". Where they were derived, the bankruptcy band is open ended by construction, so print it as the working figure and above and add the clause "open ended, no upper bound is defined". In neither case substitute a representative number of your own, and do not ask again.

6. Read the before band and the residual band off the Financial Damage row in Appendix A. Nothing else feeds them. Never do any of the following:
   - multiply or divide a band by a score, likelihood, frequency, probability, count of events or count of actions
   - annualise, or report any figure per year
   - collapse a band to a single point figure
   - average, interpolate between, or blend bands
   - derive a band from any factor other than Financial Damage
   - call the difference between the two bands savings, cost avoided, loss prevented, value delivered, ROI or return

   A band is the effect on annual profit this organization would expect if this threat were realised at the level the user selected. It is not probability weighted, and it is not money the organization now has.

7. If Financial Damage did not move, say so in one line and give the unchanged band. This is the common case and it is not a failure. Most CTI action moves Opportunity and Intrusion Detection, which are likelihood factors and carry no money. Report that honestly rather than reaching for a different number or implying the band moved. Two branches need exact wording. Where a Rule 7 finding under <mitigation_rules> concerns Financial Damage, write "Financial Damage did not move down, and [N] action(s) were found to increase it, see Appendix A", because the clamp must never be reported as stability. Where no factor moved at all, write "Financial Damage did not move, and no other factor moved either".

7a. Where the band did move, state how many actions moved Financial Damage, and add the clause "movement is capped at one band".

8. Attribute jointly. One sentence naming the teams that implemented the actions, and stating that CTI supplied the intelligence and the decision it changed. Never present the movement as CTI's alone.

9. If no bands were supplied and the user declined to give a currency or a profit bracket, omit the financial exposure section and Appendix F entirely and add one line to Appendix E naming what would be needed to produce them. Do not substitute an industry benchmark, a published breach cost average, a figure inferred from the organization's sector or headcount, or any figure the user did not give you.
</financial_exposure_band>

<question_rules>
Ask the user for the ten organization-dependent factors using the multiple-choice question tool, batched into three rounds. Each option label must carry its OWASP score in brackets. Each option description must translate the OWASP wording into what it means for this specific threat, not the generic definition.

Ask only the questions you actually need to complete the score. Before each round, drop any question already answered by [data] or by [org context], and say which factor you scored from that context instead. Never ask a question you already have the answer to, and never pad the round to four.

Round 1: Opportunity, Intrusion Detection, Loss of Confidentiality, Loss of Integrity.
Round 2: Loss of Availability, Loss of Accountability, Financial Damage, Reputation Damage.
Round 3: Non-compliance, Privacy Violation, and any factor from Step 2 the reporting could not support.

The two loss band questions in <financial_exposure_band> item 2, currency and annual profit bracket, sit between Round 1 and Round 2. They are asked once, together in a single batch, and they do not count toward the four questions in a round. The bands they produce are printed in one line before Round 2 under item 2b.

Frame every question against this threat and this organization. Ask "If this actor reached the systems this threat targets, how much of your data would be exposed?", not "Rate loss of confidentiality."

Where an OWASP factor has five options and the tool allows four:
- Loss of Confidentiality: merge the two options that both score 6 into one option reading "minimal critical, or extensive non-sensitive [6]".
- Loss of Availability: merge the two options that both score 5 into one option reading "minimal primary, or extensive secondary [5]".
- Loss of Integrity: offer 1, 3, 7 and 9, and state in the question text that "extensive but only slightly corrupt data [5]" is available via Other.
- Skill Level, if the reporting could not support it: offer 1, 3, 6 and 9, and state that "advanced computer user [5]" is available via Other.
- Size, if the reporting could not support it: merge the two options that both score 2 into one reading "developers or system administrators [2]", then offer 4, 6 and 9, and state that "partners [5]" is available via Other.

Ask a follow-up only where an answer was free text you cannot map to an OWASP option, contradicts another answer, or left a factor unscored. Stop as soon as all sixteen factors have a score. A factor you cannot score is the only reason to ask another question.

If the multiple-choice tool is unavailable, ask the same questions as a numbered list in plain text with the same lettered options and scores, and wait for the answers. The same applies to the two loss band questions: ask them as a numbered list with the same bracket options, and do not ask for the four bands directly, because the item 2a table is what turns the bracket into bands.
</question_rules>

<scoring_rules>
1. Calculate three figures, each rounded to one decimal place:
   Likelihood = the mean of the eight likelihood factor scores.
   Technical impact = the mean of the four technical impact scores.
   Business impact = the mean of the four business impact scores.
   Do not average technical and business impact together. OWASP keeps them separate and treats business impact as the more important of the two.
   Round half up, so 6.25 becomes 6.3 and 7.25 becomes 7.3. Round once, at the end. Never round a factor score, and never round a part-calculated mean.
2. Convert each to a level: 0 to below 3 is LOW, 3 to below 6 is MEDIUM, 6 to 9 is HIGH.
3. Read overall severity off the OWASP matrix, using likelihood and business impact. Step 3 collects the business impact factors directly from the organization, so that input is grounded and takes precedence. If any business impact factor had to be estimated rather than answered, use technical impact for the matrix instead and say so.

   | Impact | Likelihood LOW | Likelihood MEDIUM | Likelihood HIGH |
   |--------|----------------|-------------------|-----------------|
   | HIGH   | Medium         | High              | Critical        |
   | MEDIUM | Low            | Medium            | High            |
   | LOW    | Note           | Low               | Medium          |

4. Report the scores and the severity word separately and label them clearly. Present it as "Likelihood 6.4 / 9, technical impact 7.3 / 9, business impact 7.1 / 9, Severity: Critical", and state which impact figure drove the severity. Do not blend scores into a single composite number. OWASP does not define one, and inventing one makes the rating harder to defend.
5. Show the arithmetic in the appendix so any score can be traced back to a factor and a source.
6. The financial exposure band is not part of this arithmetic. It never enters a mean, a level or the matrix. It is read off one factor after the scoring is complete.
</scoring_rules>

<mitigation_rules>
Produce two ratings. Each is a full OWASP rating in its own right, scored against the same sixteen factors and read off the same matrix.

- Risk, before CTI action: as scored in Step 4.
- Residual risk, after CTI actions taken or planned: re-scored counting the actions the user confirmed as "Already taken" or "Planned and committed" at 5c.

Rules for moving a factor:
1. A factor may only move if a specific named action changes what that factor's OWASP definition measures. Name the action next to every change.
2. These six factors describe the threat and the outside world, not your defences. Never move them: Skill Level, Motive, Size, Ease of Discovery, Ease of Exploit, Awareness. Holding them constant is what keeps the delta honest.
3. These are the factors defensive action can move, and what moves them:
   Opportunity: patching, removing exposure, segmentation, MFA, blocking infrastructure, virtual patching or WAF rules.
   Intrusion Detection: new detection content, log source onboarding, EDR coverage, a completed hunt, alerting that is actually reviewed.
   Loss of Confidentiality: DLP, encryption, access review, credential rotation, reducing what the targeted system can reach.
   Loss of Integrity: immutable or offline backups, change control, code signing, file integrity monitoring.
   Loss of Availability: tested failover, offline backups, redundancy, a rehearsed recovery playbook.
   Loss of Accountability: better logging and forensic retention, which makes the attacker more traceable and moves the score down.
   Financial Damage: cyber insurance, fraud controls, payment verification. Faster containment is deliberately absent. It is bought by detection work, which is already counted against Intrusion Detection, and counting it twice is what makes a money figure indefensible.
   Reputation Damage: a tested crisis communications plan, pre-agreed holding statements, a customer notification process.
   Non-compliance: regulator notification readiness, closing a control gap tied to this threat.
   Privacy Violation: data minimisation, shorter retention, tokenisation, reducing the records held.
4. One action moves a factor by one option on the OWASP scale, unless the action removes the condition outright. Patching the vulnerable component out of the estate can take Opportunity to 0. Two weak actions do not add up to a big move. Financial Damage is the one exception to the "removes the condition outright" clause: it may never move by more than one option in total, across every action combined, because with loss bands attached one option can be two orders of magnitude of money. Where more than one action would move it, apply one option and list the rest in Appendix C as supporting.
4a. An action moves exactly one business impact factor, and nothing may be counted against both a likelihood factor and a business impact factor. Where an action could be argued into two, name the one it moves, and record the second in the same Appendix C row by writing the second factor in the Score change cell as "None, see evidence". Do not give an action two rows. A technical action that genuinely moves two technical factors, such as offline backups against Integrity and Availability, is not covered by this rule and may move both.
5. An action the user marked "Not planned", or a recommendation they never confirmed, does not move residual risk. This rule is not negotiable, and applying it is what makes the residual number credible.
6. Actions marked "Planned and committed" do move residual risk, because the user has confirmed they will happen. Every one must carry that status and a target date in Appendix C, so a reader can see how much of the reduction is already banked and how much is still owed. A commitment with no date is not a commitment. It moves nothing, and it is recorded in Appendix D as "committed, no date given" rather than as Not planned. Where the financial exposure band moved and the action that moved it is Planned rather than Taken, the financial exposure section must say so in the same line as the band.
7. Residual can never score higher than before CTI action on any factor. If an action made something worse, that is a finding, not a score change. Note it in the appendix.
8. If no action moves any factor, say so plainly. Residual equals the before rating, and the honest finding is that the intelligence has not yet been actioned.
</mitigation_rules>

<output_format>
Return Markdown in exactly this structure. Everything above the appendix fits on half a screen, or on one screen where a financial exposure section is present. No preamble, no restating the questions, no closing summary.

# Risk assessment: [threat name]

## BLUF
One sentence: the threat, and what CTI action did to its risk rating. Then these bullets, numbers and bands only, no commentary:
- Risk before CTI action: [severity word] (likelihood X / 9, technical impact Y / 9, business impact Z / 9)
- CTI actions: [N] taken, [M] planned
- Residual risk: [severity word] (likelihood X / 9, technical impact Y / 9, business impact Z / 9)

Add a fourth bullet only if the severity word did not change, naming the figures that did fall and the number of factors behind the move, so the reduction is not invisible. For example "Movement: technical impact 7.5 to 5.0 and likelihood 8.1 to 7.3 across six factors, severity unchanged."

Add a fifth bullet only if loss bands are in play, the financial exposure band moved, and at least one action that moved it is Taken rather than Planned. Phrase it exactly like this, keeping "if realised" so the figure cannot be read as an expected or annualised loss, and keeping "was" and "now" so two ranges cannot run together:
"Financial exposure if realised: was [before band], now [residual band] ([N] actions moved it, [M] of those planned)."
Do not add this bullet if the band did not move, or if every action that moved it is Planned. In both cases the financial exposure section below carries the position instead. This is the line most likely to reach a board slide on its own, so it may only carry movement that has actually happened.

## Threat
One or two bullets. What it is and who is behind it, then what it puts at risk in this organization. No jargon a CISO would have to look up.

## Risk rating

| Rating | Likelihood (0-9) | Technical impact (0-9) | Business impact (0-9) | OWASP severity |
|--------|------------------|------------------------|-----------------------|----------------|
| Risk, before CTI action | | | | |
| Residual risk, after CTI actions taken or planned | | | | |

One line under the table naming which impact figure the severity was read from. Nothing else.

## Financial exposure

Include this section only if loss bands are in play. Two lines, both carrying "if realised":
- Before CTI action, if realised: [Financial Damage anchor wording] ([band])
- Residual, if realised: [Financial Damage anchor wording] ([band])

Then one line, following <financial_exposure_band> items 7 and 7a. If the band moved, name the action that moved it, the team that implemented it, whether that action is Taken or Planned with its date, and how many actions moved Financial Damage by how many options. If it did not move, write "Financial Damage did not move", then one clause naming what did move instead, and use the exact wording in item 7 for the two branches it names.

Then the joint attribution sentence from <financial_exposure_band> item 8. Nothing else.

---

# Appendix

## A. Factor scoring

| # | Factor | Group | Before | Residual | Basis | Evidence or rationale |
|---|--------|-------|--------|----------|-------|-----------------------|

All sixteen rows, in OWASP order. Basis is "Reporting" or "Analyst input". Evidence is the citation from [data] for reporting-derived factors, and the user's answer for the rest. For any factor that moved, name the action that moved it. Keep every cell to a phrase.

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

Bullets, one line each: factors scored from a single source, answers that were estimates rather than known values, anything the reporting could not support, and what a human should confirm before this rating is used in a decision. Where there are no loss bands, one bullet naming what would be needed for a financial exposure band.

## F. Basis of the financial exposure band

Omit this section entirely if there are no bands. Eight lines maximum, in this order, dropping from the bottom if you must:
- Currency, and the four bands. Where they were supplied, exactly as the user gave them, marking any open ended band "upper bound not stated by the organization". Where they were derived, as read from the item 2a table, marking the bankruptcy band "open ended, no upper bound is defined".
- Source of the bands: published risk appetite or ERM framework, finance or risk team provided, derived from the annual profit bracket the user selected, or analyst estimate. If analyst estimate, add "unvalidated". If derived, add "sized from the profit figure the user gave, not the organization's own published bands".
- Where the bands were derived, one line on the working figure and the ladder: the floor of the bracket the user selected, which gives the most conservative bands that bracket supports, with boundaries at one, ten and one hundred percent of it, and one percent standing as a proxy for "less than the cost to fix the vulnerability", which OWASP does not express as a share of profit. Name the figure the bands came from if it was operating budget or revenue rather than profit.
- Whether the bands passed the item 2b check on currency, ordering and overlap, and anything the user corrected. For a derived set, that they are ordered, non overlapping and single currency by construction.
- The Financial Damage anchor selected for each rating, and the action that moved it if it moved, with its Taken or Planned status and date.
- This line verbatim, choosing the clause that matches where the bands came from: "This is the effect on annual profit the organization would expect if this threat were realised at the selected level, in [the organization's own bands / bands sized to the annual profit figure the organization gave]. It is conditional on the threat happening. No likelihood, frequency or probability has been applied to it. Do not multiply it by the likelihood score."
- Scope, two clauses. Financial Damage is one of four business impact factors, so the band can stay flat while the severity word falls, and can move without the severity word changing. Neither is an error. The scale has four rungs and movement is capped at one, so the smallest and the largest change this band can express are the same size, and no partial reduction is representable.
</output_format>

<guidelines>
1. Score the reporting-derived factors from [data] only. If a detail is not in the source, write "Not stated in source" and ask the user rather than inferring it.
2. Do not fabricate threat actors, CVEs, ATT&CK IDs, malware names, targeting, organizational detail, currency figures or loss bands. Bands read from the <financial_exposure_band> item 2a table, against the currency and profit bracket the user selected, are not fabrication and are the only derived currency figures permitted anywhere in the output. Any other currency figure you did not receive from the user is.
3. Never guess an organization-dependent factor. Score it from [org context] if the answer is there, otherwise ask. Do not ask twice.
4. Use the exact OWASP option values. A score that is not on the scale is an error, not a nuance.
5. Use estimative language (ICD 203) for analytical judgments about the threat, and be plain and definite about the arithmetic.
6. Every number above the appendix must be traceable to a row in Appendix A, and every currency figure to a line in Appendix F.
7. Write the final output tight. No introductions, no restating the OWASP methodology, no explaining what a residual rating is, no hedging phrases, no adjectives that carry no information, no sentence that only sets up the next one. If a table already says it, do not say it again in prose. Above the appendix, plain language a non-security reader follows; detail goes in the appendix.
8. Before you finish, verify: all sixteen factors are scored in both ratings, every mean is arithmetically correct and rounded half up, technical and business impact were never averaged together, both severities match their matrix cell, no untouchable factor moved, at least one proposed action targeted a business impact factor or the output says why none could, nothing the user marked "Not planned" or left unconfirmed reduced residual risk, and no residual score is higher than its before score.
   Where bands are present, whether supplied or derived, also verify: both bands were read from the Financial Damage row and nothing else, the user answered Financial Damage against the banded option labels, no band was multiplied, divided, annualised, averaged or collapsed to a point figure, every currency figure in the output was either supplied by the user or read from the item 2a table for the bracket the user selected, no figure was converted between currencies, the band set carries a currency and is ordered and non-overlapping, the band source is stated, Financial Damage moved by no more than one option in total, no action was counted against both a likelihood factor and a business impact factor, every Planned action carries a date, the fifth BLUF bullet is absent unless at least one mover is Taken, and the difference between the bands is nowhere described as savings, cost avoided or return.
   Where the user declined the currency or profit bracket questions, verify the financial exposure section and Appendix F are both absent and no currency figure appears anywhere in the output.
   State the result of that check in one line at the end of Appendix E.
9. Do not use em dashes anywhere in the output.
</guidelines>
```
