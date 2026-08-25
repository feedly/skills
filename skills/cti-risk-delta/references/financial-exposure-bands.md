# Financial exposure bands

This file translates one OWASP factor, Financial Damage, into money bands
sized to the organization. It is a lookup, not a loss model. Follow it
exactly.

## 1. What the band is

Financial Damage is already a money scale in OWASP wording: less than the
cost to fix the vulnerability 1, minor effect on annual profit 3,
significant effect on annual profit 7, bankruptcy 9. Those four anchors get
currency ranges from one of two places, in this order of preference: the
organization's own loss bands, where it already has them, or the table in
item 2a, applied to the currency and annual profit bracket the user gives in
item 2. The skill reports which band the threat sat in before CTI action and
which band it sits in after. It does not price the threat and it does not
build a loss estimate.

### 1a. Read the OWASP wording literally

The wording decides what the band means. Two of the four anchors are
expressed as an effect on annual profit. So the band is the effect on annual
profit this organization would expect if this threat were realised. It is
conditional on the threat happening. It is not a per event cost, it is not
an expected annual loss, and no likelihood, frequency or probability is
applied to it anywhere. Use the phrase "if realised" every time the band
appears above the appendix, and never the phrase "per year" or "one
occurrence".

## 2. Getting the bands

If the organization's own loss bands were supplied at Step 0, use them and
skip to item 2b. An organization's own published bands always beat a derived
set. If they were not supplied, and the org context does not contain them,
derive the bands from the organization's annual profit. Ask these two
questions once, both in the same batch, using the multiple-choice question
tool, immediately before Round 2. They do not count toward the four
questions in a round. Do not ask either of them twice.

**Question 1, currency:**

"What currency does your organization report in?"

Offer the three currencies most plausible for the user's country or region
as the options, for example US dollar, euro, pound sterling. Let the tool
add its own Other for anything else. Do not supply an Other of your own.

**Question 2, annual profit:**

"Roughly what is your organization's annual profit? I use this to size the
OWASP money anchors to your organization. I do not need an exact figure and
I am not going to price the threat."

- under 10M
- 10M to under 100M
- 100M to under 1B
- 1B and above

Write the option labels in the currency chosen at question 1. Let the tool
add its own Other.

### 2a. The band table

Turn the answer into four bands using this table and nothing else. Read the
row. Do not recalculate it. The figures are numerals applied in the currency
the user chose. Never convert a figure between currencies and never apply an
exchange rate.

| Bracket selected | Working figure | less than the cost to fix [1] | minor effect on annual profit [3] | significant effect on annual profit [7] | bankruptcy [9] |
|---|---|---|---|---|---|
| under 10M | 1M | under 10k | 10k to under 100k | 100k to under 1M | 1M and above |
| 10M to under 100M | 10M | under 100k | 100k to under 1M | 1M to under 10M | 10M and above |
| 100M to under 1B | 100M | under 1M | 1M to under 10M | 10M to under 100M | 100M and above |
| 1B and above | 1B | under 10M | 10M to under 100M | 100M to under 1B | 1B and above |

The working figure is the floor of the bracket the user selected, so the
bands are the most conservative that bracket supports. Each boundary is one
percent, ten percent and one hundred percent of the working figure, which is
why every row is the same shape moved by one decade.

Three things about this ladder have to be stated in Appendix F rather than
left for the reader to work out:

- The significant band closes at one hundred percent of the working figure,
  because a loss that consumes a full year of profit is where the OWASP
  wording stops calling the effect significant. The bankruptcy band is open
  ended above that.
- "Less than the cost to fix the vulnerability" is not a share of profit in
  OWASP's wording. One percent of the working figure is used as a proxy so
  that all four anchors sit on one scale. Say that plainly. Do not imply
  OWASP defined it that way.
- The bands are an order of magnitude wide because the OWASP scale has four
  rungs and movement is capped at one option. Precision beyond one
  significant figure would be false precision.

Four things can come back through Other, and each has a fixed response:

- **An exact profit figure.** Use it in place of the bracket floor and apply
  the same ladder: under one percent, one to under ten percent, ten to under
  one hundred percent, then the figure itself and above. Round every
  boundary to one significant figure.
- **No profit figure exists**, for example a public body, a charity or a
  pre-profit company. Accept annual operating budget or annual revenue,
  apply the same ladder, and name in Appendix F which figure the bands were
  derived from. Never silently treat revenue as profit.
- **The user does not know, would rather not say, or asks to skip.** Omit
  the financial exposure section and Appendix F per item 9, move on without
  comment, and do not ask again.
- **The user volunteers the organization's own bands.** Use those instead of
  the derived set and record the source under item 4.

### 2b. Check the band set before you use it

Where the bands came from the user directly or from org context, confirm
that every band carries an explicit currency, that the four increase
monotonically, and that they do not overlap. If any check fails, quote the
bands back in one line, ask the user once to confirm or correct, and if that
is not resolved report scores only. That single clarification is not a
second ask under item 2. Bands read from the item 2a table are ordered, non
overlapping and single currency by construction, so record that in Appendix
F and check only that the currency from question 1 carried through to every
band.

Print the four bands in one line before Round 2, so the user can see what
they are about to answer against. Do not ask a separate question to confirm
them. The Round 2 Financial Damage question carries the same bands in its
option labels under item 3, and answering it is the confirmation.

## 3. Carry the bands into the Financial Damage question

Whether the bands were supplied or derived, carry them into the Round 2
Financial Damage question. Each option label keeps its OWASP score and gains
the matching band, for example "significant effect on annual profit [7], 1M
to under 10M". The user is then answering in money sized to their
organization, which is the point of collecting the currency and the profit
bracket at all.

### 3a. When the band may be reported

The band may only be reported where the user answered the Financial Damage
question directly against those banded option labels. If Financial Damage
was estimated, inferred from org context, or answered before the bands
existed, omit the financial exposure section and Appendix F and record why
in Appendix E. Bands supplied or derived after that question has been
answered are accepted only if you re-put the one question with banded labels
and the user re-confirms. That re-put is not a second ask under item 2.

## 4. Record where the bands came from

Record the source as one of: published risk appetite or ERM framework,
finance or risk team provided, derived from the annual profit bracket the
user selected using the item 2a table, analyst estimate. An analyst estimate
is reported as such, and the financial exposure section states in one clause
that the bands are unvalidated. A derived set is reported as such, and the
financial exposure section states in one clause that the bands are sized
from the profit figure the user gave and are not the organization's own
published bands.

## 5. Open ended bands

An open ended band cannot be reported as a figure. Where the bands were
supplied, print the open ended one as the user gave it and add the clause
"upper bound not stated by the organization". Where they were derived, the
bankruptcy band is open ended by construction, so print it as the working
figure and above and add the clause "open ended, no upper bound is defined".
In neither case substitute a representative number of your own, and do not
ask again.

## 6. What you may never do to a band

Read the before band and the residual band off the Financial Damage row in
Appendix A. Nothing else feeds them. Never do any of the following:

- multiply or divide a band by a score, likelihood, frequency, probability,
  count of events or count of actions
- annualise, or report any figure per year
- collapse a band to a single point figure
- average, interpolate between, or blend bands
- derive a band from any factor other than Financial Damage
- call the difference between the two bands savings, cost avoided, loss
  prevented, value delivered, ROI or return

A band is the effect on annual profit this organization would expect if this
threat were realised at the level the user selected. It is not probability
weighted, and it is not money the organization now has.

## 7. When Financial Damage did not move

If Financial Damage did not move, say so in one line and give the unchanged
band. This is the common case and it is not a failure. Most CTI action moves
Opportunity and Intrusion Detection, which are likelihood factors and carry
no money. Report that honestly rather than reaching for a different number
or implying the band moved.

Two branches need exact wording:

- Where a Rule 7 finding under the mitigation rules concerns Financial
  Damage, write "Financial Damage did not move down, and [N] action(s) were
  found to increase it, see Appendix A", because the clamp must never be
  reported as stability.
- Where no factor moved at all, write "Financial Damage did not move, and no
  other factor moved either".

### 7a. When it did move

Where the band did move, state how many actions moved Financial Damage, and
add the clause "movement is capped at one band".

## 8. Attribute jointly

One sentence naming the teams that implemented the actions, and stating that
CTI supplied the intelligence and the decision it changed. Never present the
movement as CTI's alone.

## 9. When there are no bands at all

If no bands were supplied and the user declined to give a currency or a
profit bracket, omit the financial exposure section and Appendix F entirely
and add one line to Appendix E naming what would be needed to produce them.
Do not substitute an industry benchmark, a published breach cost average, a
figure inferred from the organization's sector or headcount, or any figure
the user did not give you.