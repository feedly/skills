# Reference B. Rubrics

Read this at Step 3 (grading sources) and keep it open through Step 11.

## B1. Admiralty grading

Grade the source and the claim separately. A usually reliable vendor reporting an uncorroborated claim is B3, not B1.

| Reliability (source) | Typical use | Credibility (claim) |
|---|---|---|
| A Completely reliable | Government advisory with a track record | 1 Confirmed by independent sources |
| B Usually reliable | Established vendor research, the victim's own statement, major outlets with original reporting | 2 Probably true |
| C Fairly reliable | News relaying others, smaller research shops | 3 Possibly true |
| D Not usually reliable | Aggregators, rewrites, blogs without sourcing | 4 Doubtful |
| E Unreliable | Known bad track record | 5 Improbable |
| F Cannot be judged | Machine-extracted feeds, first-seen sources, actor statements | 6 Cannot be judged |

Grade each source on its own record. If every source in a run gets the same grade, look again; `check` warns when that happens.

## B2. Claim status

| Status | Rule | `corroboration` says |
|---|---|---|
| Confirmed | Two or more independent originators, or the victim or an authority speaking about its own actions in a source you read (`first_party` true). See B3.5 for a victim statement known only through an outlet. | The originators by name, or "first-party: <who>" |
| Reported | One credible originator. Most early facts sit here, as do statements that favour their speaker (B3.7) and allegations made before a conviction (B3.8). | "single originator: <who>" |
| Actor-asserted | The actor said it about itself (a leak-site post, a claim of responsibility, a ransom note). It confirms only that the actor made the claim. Write the claim as what the actor says. | "actor: <who>, via <source>" |
| Assessed | Your analytic judgment. Needs an ICD 203 term, a confidence level and `basis`, within the caps in B6. | Leave empty; fill `basis` |
| Superseded | Replaced by later reporting. Keep it, with `superseded_by`. | Keep what it had |
| Unknown | A gap that matters, stated as a claim ("the initial access vector has not been disclosed"). Name only what is in scope; presuppose no attack type. | Leave empty |

An event, a victim tier or a judgment is never stronger than the claims behind it.

## B3. Corroboration is counted by originator, not by publisher

Grade each claim by how well it is corroborated, never by who printed it.

1. **Primary** means the publisher is the originator and published it itself: the victim's own notice, the vendor's own advisory, the researcher's own write-up, the agency's own release.
2. **Secondary** is everything else, including a news story that relays a vendor blog, a repost, a translation, and a leaked or scraped copy of someone else's document. Set `originator` to the original author and `relay_of` to the source it repeats, if you have it. A source has one originator; name any others in `notes`.
3. A relay never adds corroboration. Twenty stories that repeat one vendor blog are one originator. `check` follows `relay_of` to count originators. When you judge that two sources share one originator, start `corroboration` with "single originator:", and `check` takes that as your decision. **Count speakers, not outlets.** Three wire services quoting one Harbor Ledger statement are one speaker. Put the speaker in the claim's `said_by`; `check` warns when a Confirmed claim has one speaker, unless that speaker is first-party and was read in the original.
4. **Upgrade** a Reported claim to Confirmed when a second independent originator supports it, and write both names in `corroboration`. **Demote** a Confirmed claim to Reported when its support turns out to be one originator.
5. **First-party.** Mark a source `first_party` victim when the victim speaks about itself, authority when a government body, regulator or law enforcement agency speaks about its own action (an advisory it issued, an arrest it made), and actor when the attacker speaks. A victim or authority statement read in the original can confirm a claim about the speaker's own actions alone. A victim statement known only through an outlet is `victim-relayed` and Secondary. It stays Reported unless all three of these hold: (a) the `quote_source` is the `victim-relayed` source and it is verified (`read`, or `excerpts` with a passing spot-check); (b) the cited line holds the victim's own words inside quotation marks; (c) the claim is about the victim's own action (suspending withdrawals, the number of stores closed, a password reset it ordered), never root cause, technique or attribution. When they hold, the claim can be Confirmed with `first_party` true. `check` tests (a) and (b) and flags technical topics; the audit tests (c). A statement that favours the victim stays Reported (B3.7). An actor statement is never confirmation; label the claim Actor-asserted.
6. **Quotes are checked against saved lines.** A quote must sit on the `line` it cites in `work/sources/Sxx.txt`. Four retrieval values carry quotes. `read` is the page's own text. `excerpts` is sentences the fetch tool copied on request. `check` matches each quote to its saved line, but the saved line is the tool's copy, so this shows the quote matches the copy, not the live page. An `excerpts` source is verified only when its `spot_check` says every checked line matched. `summarised` is a summary: its quotes are NOT CHECKED, and every line the tool reworded starts with `~ `. A quote from a `~` line is a paraphrase and supports nothing above Reported. `snippet` is a search-result snippet. **A Confirmed claim needs a verified supporting source (`read`, or `excerpts` with a passing spot-check), or two independent originators.** One unchecked `excerpts` source is never enough on its own. Two summarised originators that agree make a strong Reported claim, never a Confirmed one. `summary.validation` says how many quotes were NOT CHECKED. A source you could not read (`retrieval` failed) supports no claim. Log it as a Gap with `source_ids`.
7. **Interest.** Record each source's `interest`: independent, victim, actor, vendor (a vendor with a product interest in the story) or government. A first-party statement that favours the speaker ("no customer data was affected", "the incident is contained") stays Reported until an independent originator supports it.
8. **Allegations.** An allegation by police or prosecutors before a conviction is recorded as Reported, with the word "alleged" in the claim, never Confirmed. The arrest itself, stated by the police, is the authority's own action and can be Confirmed. Never name the suspect (hard rule 7).
9. **Named originators must be read.** When a source attributes a fact to someone you have not read ("according to the FBI"), go after that originator once on its own domain. If you still cannot read it, or get only a summary of it, add a Gap with `blocking` true; any judgment resting on it is capped at low confidence (B6).

## B4. Victim tiers

Confirmed (victim statement, regulatory filing such as an SEC 8-K Item 1.05, breach notice); Claimed (leak site or actor post: never confirmation); Reported (one credible source); Assessed (your inference, such as a pathway through a dependency); Unknown (none confirmed yet).

## B5. Technique occurrence

| Occurrence | Rule |
|---|---|
| Observed | Seen in in-the-wild telemetry or in a real artefact from an incident. |
| Reported | A source says it happened against a real target, without showing the artefact or telemetry. |
| Capability | The code or the vulnerability can do it, and nobody has seen it used against a real target. A discoverer's or vendor's own proof-of-concept or lab reproduction is Capability, not Observed. |
| Assessed | Inferred, such as how the attacker probably found a leaked key. |

**Technique confidence.** A technique row's confidence follows the originators behind its cited claims. High needs two or more originators. Medium needs two or more, or an Observed occurrence. Anything else is Low. An Assessed row states its inference in `how_used` with an ICD 203 term. `check` warns on both.

## B6. ICD 203 estimative language and its caps

Every judgment carries one likelihood term and one confidence level. Never put a number in place of the term.

| Likelihood term | Rough meaning |
|---|---|
| almost no chance | 1 to 5 percent |
| very unlikely | 5 to 20 percent |
| unlikely | 20 to 45 percent |
| roughly even chance | 45 to 55 percent |
| likely | 55 to 80 percent |
| very likely | 80 to 95 percent |
| almost certain | 95 to 99 percent |

Confidence is low, moderate or high. It describes the quality of the sourcing and reasoning, not the likelihood. A "likely" judgment can rest on low confidence.

**Caps.** `check` warns when a key judgment breaks one of the first four; the audit checks the fifth.

| If the judgment's basis | Then the judgment is capped at |
|---|---|
| is made only of Reported claims from Secondary sources | "likely" (or "unlikely"), moderate confidence |
| rests on one originator, however many claims it cites | low confidence |
| rests only on the absence of reporting (Unknown claims) | low confidence, and the judgment says it rests on the absence of reporting |
| includes a claim behind a blocking gap | low confidence |
| rests on an actor's own claim | Actor-asserted support never lifts a judgment above "roughly even chance" on its own |
