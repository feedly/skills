---
name: "track-cyberattack"
description: "Takes a named cyberattack or campaign (a breach, intrusion campaign, supply-chain compromise, threat actor or law enforcement action) and turns it into an attack tracker dashboard in Claude, with a Word report, a Word executive brief, a STIX 2.1 bundle and ATT&CK Navigator layers, plus a standalone HTML page on request. Every fact enters a claims ledger as a graded, cited claim, and the timeline, victims, MITRE ATT&CK techniques, SOC kill chain, attribution, gaps and actions are built from that ledger. Use it when someone names an attack and asks to track it, follow it, build a timeline, find out who was hit or who is behind it, or consolidate reporting on it. Also use it to update an existing tracker (update the tracker, what's new on X, any developments, refresh the dashboard, what changed since last week) and for a fast read (quick brief on X), which skips the files. A full run takes about 15 to 30 minutes."
---

# Track a Cyberattack

This skill builds and maintains an attack tracker dashboard on one named cyberattack or campaign. Every fact enters a claims ledger as a graded claim, and every other section is built from that ledger, so each conclusion traces back to a saved extract, a source and a confidence level. Re-running it on the same attack updates the dashboard and leads with what changed, because early reporting on a live incident is often revised.

## Before you run

- **Claude features used.** Artifacts with the Dashboard type, one subagent for collection and one for the audit, file and shell tools, the question tool, and `SendUserFile`. Each has a fallback (see Compatibility).
- **Web access.** The skill runs web searches and reads public web pages to collect sources. It never opens a leak site. Say "no web" to work only from what you attach.
- **Feedly.** Optional. With the Feedly Threat Graph MCP server connected (it needs a Feedly Threat Intelligence plan), Feedly is the first collection source. Say "skip Feedly" to leave it out.
- **Time and usage.** A full run takes 15 to 30 minutes and about 20 turns; an update about 15 turns; a quick brief about 8. Most usage goes on collection.
- **Build tools.** Python 3.9 or later. Node with the docx package for the Word report and executive brief, Graphviz for the attack-chain image, and matplotlib for PNG images (without it, images are drawn as SVG). `preflight` says what is missing; the run carries on without it.
- **Companion skills (optional).** map-attack-techniques, create-sigma-rule, create-cql-query and ioc-extract-enrich, offered at the end when installed.

## The run at a glance

Load order: if the user said skip Feedly, no Feedly or web only, make no Feedly tool search or call for the rest of the run. Otherwise: this skill, then the Feedly check, then the look-alike search, then the question card, then collection.

| Step | In short | Stop when |
|---|---|---|
| 0 | Set up and pick the mode | Tools copied into `work/`, preflight run, mode chosen |
| 1 | Disambiguate and ask once | The user answered, or defaults taken |
| 2 | Write the scope | Case type, scope and incident rows saved |
| 3 | Collect and grade sources | Subagent JSON received, originators chased, sources saved |
| 4 | Write the rows | All rows files written in one turn and added, no `add` errors |
| 5 | Correlate and grade corroboration | Conflicts saved, statuses upgraded or demoted |
| 6 | Timeline | Every dated claim is on the timeline or explained |
| 7 | Victims | Victim rows saved, with data exposed |
| 8 | Techniques | Technique rows saved and checked against the pinned ATT&CK map |
| 9 | Attribution | Statement, signal or hypothesis, and Diamond rows saved |
| 10 | SOC hand-off | Software and kill chain rows saved, or `soc_note` |
| 11 | Judgments, relevance, gaps, actions | Summary filled |
| 12 | Validate | `check` has 0 errors and the audit passed |
| 13 | Build | Every output built and verified |
| 14 | Hand over | Outputs shown, narrative written |

Do not start a step until the previous step's stop condition holds. Show no findings to the user before Step 4 is done.

## Outputs

A full run delivers these, all built from one file, `tracker.json`, so no two outputs can disagree. Deliverables go in `out/`; everything the run uses for itself goes in `work/`.

| Output | Purpose |
|---|---|
| Tracker dashboard (Claude artifact) | The main deliverable. Eight tabs: Overview, Timeline, Victims, TTPs and attack chain, Kill chain (SOC), Attribution, Claims and sources, Gaps and actions. Claim, source and event IDs are links; technique IDs open ATT&CK. Re-runs update the same dashboard. |
| `out/<attack>-report.docx` | The same content as a Word report, for editing, filing or a ticket. |
| `out/<attack>-exec-brief.docx` | One or two pages for leadership, in Word: page one of the report plus the top actions, with no ledger or technique tables. |
| `out/<attack>-stix.json` | STIX 2.1 bundle for a TIP: a report holding the campaign, actors, techniques, CVEs, sectors, and a note for every claim, event and gap. No indicator objects. |
| `out/<attack>-navigator.json` | ATT&CK Navigator layer of the Enterprise techniques, coloured by occurrence. An ICS layer (`-navigator-ics.json`) comes too when ICS techniques are mapped. |
| `out/<attack>-dashboard.html` (on request, or as the fallback) | The same dashboard as one standalone page that opens offline in any browser, for a team wiki, an intranet or a TLP:AMBER+STRICT or TLP:RED attack. |

`tracker.json` stays at the top of the working directory and is not handed over. It holds the short verbatim quotes that back each claim, and update runs build on it.

Need a PDF? Open the Word report or executive brief and save it as PDF from Word.

A quick brief (see "Quick brief mode") delivers a reply in the conversation instead of files.

If a capability is missing (no Artifact tool, no Node), say so in one line and deliver the rest. Never drop an output silently.

## Glossary

- **Information.** What the tracker holds: claims collected from reporting, each one cited and graded. Information becomes intelligence only when an analyst takes it through the full intelligence life cycle, including analysis. The skill calls its output information or claims, never intelligence and never evidence.
- **Claim.** One atomic fact in the ledger, in your own words, with an ID such as C07. Key judgments are ledger rows with IDs such as A02.
- **Claims ledger.** The ledger table of claims and key judgments.
- **Signal.** An attribution row that records one indicator of who is behind the attack (shared code, infrastructure overlap, a claim of responsibility), what it shows and its limits.
- **Saved extract.** The text of a source saved in `work/sources/Sxx.txt`, one sentence per line. A claim cites the line its fact comes from, and says only what that line says.
- **Originator.** Who first reported a piece of information. Corroboration is counted by originator, never by article. A source has exactly one originator.
- **Primary and Secondary.** Primary means the publisher is the originator and published it itself. A relay, repost, translation or leaked copy is Secondary.
- **First-party.** The victim, or an authority (government, regulator, law enforcement), speaking about its own actions. A first-party statement read in the original can confirm a claim alone. The actor speaking about itself is never first-party confirmation: its claims are Actor-asserted.
- **Interest.** Whose side a source is on: independent, victim, actor, vendor (with a product interest) or government. A statement that favours its speaker stays Reported until an independent originator supports it.
- **Corroboration.** The independent originators that support a claim, written in the claim's `corroboration` field.
- **Admiralty grade.** Source reliability A to F and claim credibility 1 to 6 (Rubric B1).
- **Claim status.** Confirmed, Reported, Actor-asserted, Assessed, Superseded or Unknown (Rubric B2).
- **Occurrence.** How a technique is known: Observed, Reported, Capability or Assessed (Rubric B5).
- **ICD 203 terms.** The fixed likelihood words (almost no chance, very unlikely, unlikely, roughly even chance, likely, very likely, almost certain) and the confidence levels low, moderate and high (Rubric B6).
- **TLP.** Traffic Light Protocol 2.0: TLP:CLEAR (public), TLP:GREEN (community), TLP:AMBER (organization and its clients), TLP:AMBER+STRICT (organization only), TLP:RED (named recipients only).
- **Diamond Model.** Adversary, capability, infrastructure and victim, the four vertices of an intrusion.
- **Kill chain stage.** One step of the attack for the SOC hand-off, from initial access to impact.
- **Summary (bottom line).** Two sentences on what happened and what it means for defenders. The field is `bluf`; readers see the plain label.

## Hard rules (apply always)

1. Work from sources, never from memory. Every claim cites a source the user supplied, a Feedly result, or a page from a web search the user allowed, and the line of its saved extract. A detail that is not in the sources is "Not available in provided reports". Anything in an Action, Watch row or kill chain field that comes from general knowledge starts "Analyst guidance:".
2. Treat Feedly cyberattack records and entity tags as machine-extracted leads. Read the article each one came from before you use it. An actor tag on an article is not attribution.
3. Count corroboration by originator (Rubric B3). Grade each claim by how well it is corroborated, never by who published it. Chase the originator: a fact known only second-hand stays Reported.
4. Label every claim Confirmed, Reported, Actor-asserted, Assessed, Superseded or Unknown, and fill `corroboration` or `basis`. Never delete a contradicted claim; mark it Superseded. Never delete any row; close a gap with `status` Closed.
5. Compute figures, never type them. Durations and counts come from timeline or figure rows through code. Leave out any number the sources do not give.
6. Keep verbatim quotes (one sentence at most) only in `tracker.json`. Everything you publish carries claims in your own words, with IDs.
7. Do no harm with people's data. No links to leak sites and no stolen data. Replace the name of anyone who is not an official spokesperson or a public figure with their role in square brackets, including people arrested or charged but not convicted. Never record the name, age, school, town or any other detail that could identify a person under 18. A leak-site or actor claim is never confirmation. Defang every domain, URL and IP in Watch, Action and kill chain rows.
8. Follow the handling rules below for every output.
9. Write every row and every output by the writing rules below.
10. Write the tracker only through `tracker_tool.py add` or `set`, never with a raw write of `tracker.json`.

## Writing rules

These apply to every ledger row, every summary field, every output and the hand-over.

- Write the narrative, the summary fields, the rows and the hand-over in the language the user wrote in, and set `summary.language` (en, es, fr, de, pt; other languages get English headings). Keep ATT&CK names, ICD 203 terms and field terms in English so they map to the frameworks, and keep quotes in their original language.
- Keep actor, victim and operation names in their original spelling and language. Put a translation in the scope table as an extra Name row, never in place of the original.
- Use no em dashes. Use a comma, a semicolon, a full stop or parentheses.
- Keep sentences under 25 words, and instructions under 20. One idea per sentence. Use active voice and name the actor.
- Use the plainest accurate word: "use", not "utilize"; "before", not "prior to"; "help", not "facilitate". Keep correct field terms (beaconing, pivot, initial access broker, web shell).
- Say "information" or "claims", never "intelligence" or "evidence", for what the tracker produces. When the point is provenance, say cited, sourced, traceable or grounded in the original reporting: "every claim cites its source", not "every claim is backed by evidence". Keep "evidence" only inside a quote, in a statement you attribute ("the victim says it found no evidence of data theft"), or for forensic artefacts from incident response. "Proof of exploit" stays as it is. Keep "intelligence" only in proper names and field terms (Feedly Threat Intelligence, cyber threat intelligence, the intelligence life cycle).
- Use one term for one thing through the whole tracker. If you call the group "the actor", do not switch to "the adversary".
- Put every judgment in ICD 203 terms with a confidence level. Never replace the term with a number. Keep facts and assessments apart.
- Keep a negative finding negative. "No exfiltration was reported" is not "no data was taken".
- A detection date is never an access date. If a source gives only when the victim detected the intrusion, the initial-access event is undated and says "access start undisclosed".
- A figure in the summary that rests on one originator names that originator: "Reuters reports more than 100 shops".
- Presuppose nothing. An Unknown claim or a `glance_` field names only what is in scope, without assuming the attack type or a cause: write "Payload: not reported" unless a source says ransomware was used, and never imply a causal link the sources do not make.
- State a verification caveat once, where the claim first appears, then let the status label carry it. Do not repeat "this has not been independently verified" through the text.
- Say what something is. Do not write "this is not X" or "it is not X, it is Y". Do not use sentence fragments for effect, rhetorical questions, emojis or hype words.
- Avoid absolute words (always, never, all, none) in analysis unless a source states them.
- Put conditions before actions: "If FerryGate is internet-facing, upgrade to 9.4.2."
- Every action says exactly how: where to look, which log or event ID, which query, what to look for. When the how is not in the sources, start it "Analyst guidance:".

`tracker_tool.py check` scans every text field for em dashes, loose uses of "evidence", "this is not" constructions, sentences over 25 words, repeated verification caveats, presupposed attack types and possible detail about minors.

## Handling and sanitization

- At Step 0, tell the user once, in one line, that the run will use web search (unless they ruled it out), and remind them to sanitize what they share (internal hostnames, internal IPs, victim names they are not cleared to share).
- Default to TLP:CLEAR when every source is public. If the user supplies non-public material, ask which mark applies before publishing anything.
- Never publish a dashboard that holds TLP:AMBER+STRICT or TLP:RED material. Build the standalone HTML page (`tracker_tool.py html`) instead and send it as a file.
- The TLP mark goes on every output: the dashboard header, the Word report and brief headers, the HTML page, and every STIX object.

## Feedly decision tree

Run this once, at Step 0. Never stop the run because Feedly is missing or failing.

1. Did the user say "skip Feedly", "no Feedly", "web only" or similar? Make no Feedly tool search and no Feedly call for the rest of the run, including org profiles. Go to step 4.
2. Load the Feedly Threat Graph tools with one tool search, in the same turn as loading this skill. Are `search_cyber_attacks` and `search_threat_intelligence` present?
   - Yes: Feedly is the primary collection source. Go to step 3.
   - No: if the user asked for Feedly by name, say in one line that it is not connected and link https://docs.feedly.com/article/822-setting-up-the-feedly-mcp-server-in-claude. Go to step 4.
3. If a Feedly call fails (authentication, plan limits, timeouts), say so in one line and carry on with the other sources. Do not retry the same call.
4. Without Feedly, use the user's material and web search. If the user has supplied nothing and has not allowed web search, ask for sources or permission in the Step 1 question card. That is the only point where a missing source stops the run.

## Decision cheat sheet

| If | Then |
|---|---|
| The victim or an authority states its own action, and the original is verified (read, or excerpted with a passing spot-check) | It can be Confirmed alone; set `first_party` true and name the speaker in `corroboration` |
| A victim statement is known only through a news outlet | Reported, unless the outlet was read, or excerpted with a passing spot-check, the cited line holds the victim's words in quotation marks, and the claim is the victim's own action (Rubric B3.5) |
| The actor speaks about itself | Actor-asserted; it shows only that the claim was made |
| A claim has two independent originators | Confirmed, credibility 1 or 2 |
| A claim has one originator, however many articles repeat it | Reported |
| A statement favours its speaker ("no customer data was affected") | Reported until an independent originator supports it |
| Police or prosecutors allege something before a conviction | Reported, with "alleged" in the claim |
| A source repeats another, or is a leaked or reposted copy | Secondary, `relay_of` set, adds no corroboration |
| A source names an originator you have not read ("according to the police") | One targeted search for it on its own domain; if that fails, a blocking Gap, and any judgment resting on it is low confidence |
| An authoritative page will not load | `retrieval` failed, a Gap row with `source_ids`, retry on the next update |
| Only a summary of a page could be fetched | `retrieval` summarised; reworded lines start `~ `; its quotes are NOT CHECKED, cannot support Confirmed, and are counted in `validation`. Never re-fetch it in this run; log a Gap, with `blocking` true when it is an originator's own page; retry on the next update |
| The fetch tool copied sentences on request | `retrieval` excerpts; quotes are matched to the saved line; with the browser allowed, up to five are spot-checked against the real page (`spot_check`) |
| A Confirmed claim has no verified source and only one originator | Reported (Rubric B3.6) |
| Several outlets relay one speaker | One speaker in `said_by`; Reported unless that speaker is first-party and read in the original |
| A link the user gave is blocked | No retry and no workaround; with Feedly, `search_articles` on the exact title then `get_article`; otherwise a snippet plus a Gap |
| Look-alike domains or other activity no source links to the attack | An Out of scope row plus a Watch row, never an Incident |
| Only an actor or leak site names a victim | Victim tier Claimed |
| A technique is shown only in a lab or proof-of-concept | Occurrence Capability |
| The sources name two or more credible actors | Hypothesis rows with likelihood, confidence and signals both ways, plus Signal rows for the consistency matrix |
| The sources name one actor, or none | Signal rows with their limits, no Hypothesis rows |
| A kill chain field is not in the sources | Starts "Analyst guidance:"; a stage with no host says "N/A (no host stage)" for process and parent |
| No CVE is reported | A claim saying so; no patch target |
| A campaign has several incidents | Incident rows in `scope`, and `incident` (the scope ID) on events, victims and techniques |
| The case is an actor or a law enforcement action | `case_type` actor or law-enforcement; list every incident; the SOC hand-off may be skipped with `soc_note` |
| The user wants speed | Quick brief mode |

## Workflow

**Turn budget: about 20 turns for a first full run, about 15 for an update, about 8 for a quick brief.** Every turn re-reads the whole context. Make independent tool calls in parallel in one turn, never spend a turn only on a task-list update, and do not re-read a file you just wrote. Write all the rows files in one turn and `add` them in the next. Small models write one rows file per turn (see Compatibility).

**Task list.** Create these items in one turn, alongside the first real work: Set up; Collect; Ledger and analysis; Validate; Build; Hand over. Hand over is always the last item. Update an item only in a turn that is already doing other work.

**Unattended runs.** In a scheduled or unattended run, take the defaults in the Step 1 table, ask nothing, and state at the top of the hand-over which reading you took.

### Step 0. Set up and pick the mode

1. If the user said skip Feedly, no Feedly or web only, make no Feedly tool search or call for the rest of the run.
2. Create `work/` and `out/`. Copy `scripts/` and `assets/` from this skill's folder into `work/`, then run `python3 work/scripts/tracker_tool.py preflight`. It checks Python, the ATT&CK map, matplotlib, Graphviz, and Node with the docx package, and prints one fix command. Run the fix command if the environment allows installs. Otherwise carry on and say in the hand-over what was skipped.
3. Pick the mode:
   - **Update mode** if the user gives a tracker dashboard link, attaches a `tracker.json`, or says "update", "refresh", "what changed" or "what's new". Read `references/update-mode.md` and follow it instead of Steps 1 to 3.
   - **Quick brief** if the user asks for something quick, brief or fast, or only wants the headline. See "Quick brief mode".
   - **Full run** otherwise.
4. Run the Feedly decision tree. Load `ArtifactData` in the same tool search as the Feedly tools, so the dashboard needs no load later.
5. Check the tool list for a page-text tool (the built-in browser's `get_page_text` or Claude in Chrome). If one is present, the Step 1 card asks whether it may be used.
6. If a link the user gave is blocked (SITE_BLOCKED or similar), do not retry it or route around it. Pass it to the collection brief as a lead; with Feedly the subagent finds it with `search_articles` on its exact title and reads it with `get_article`, and otherwise it becomes a snippet plus a Gap.
7. In one line, say that the run will search and read public web pages (unless the user ruled it out) and remind the user to sanitize what they share.

### Step 1. Disambiguate, then ask once

Attack names are messy. Vendor campaign names, victim-named incidents, actor names and malware names get used interchangeably, and one victim can suffer two incidents in a year.

1. In the same turn as loading the skill, build an alias table and search for look-alikes (one or two standard web searches, or `search_cyber_attacks` and `search_entities` when Feedly is connected). Make the alias search, the look-alike search and, with Feedly, `list_org_profiles` in that one turn, since none depends on another. Keep every result: the main thread passes them to the collection brief as leads. Keep every name in its original spelling and language; a translation is an extra alias, never a replacement.
2. Ask everything in one `AskUserQuestion` call. Never split the card across turns, and never send `Audience` without `Org context`. Ask only what the user has not already answered, by these rules:

   - **Always ask `Audience` and `Org context`**, in the same call, unless the user already answered them in the request. They are the last two questions on the card.
   - **Put the permission questions that apply first**, in this order: `Incident`, then `Sources` or `Browser`.
   - **When `Sources` and `Browser` both apply, merge them into one `Sources` question** (see "Merged Sources options"), so the card never holds more than four questions and `Org context` is never cut.
   - **`TLP` and `Window` take their defaults** unless the user raised them. Name the defaults in the hand-over.
   - **Check the card before you send it.** It must hold both `Audience` and `Org context`, unless the user already answered one. If either is missing, add it before the call.

| Header | Question | Default |
|---|---|---|
| `Incident` | Which incident? (only when Step 1.1 found more than one) | The most recent incident that matches the name |
| `Sources` | Which sources may I use? (only when Feedly is absent and the user supplied none) | Web search plus anything you attach |
| `Browser` | May I use your browser to read agency and vendor pages in full? (only when Step 0 found a page-text tool) | Yes, for up to five originator pages |
| `Audience` | Which team should we tailor the attack tracker (dashboard) to? | CTI |
| `Org context` | What organizational context should I tailor the outputs to? | A saved profile from the project or Claude's memory, otherwise none |
| `TLP` | Which handling mark? | TLP:CLEAR when every source is public |
| `Window` | Which time window? | From the earliest substantiated activity to today |

   For `Incident`, `Sources`, `Browser`, `TLP` and `Window`, list the default first and label it "(Recommended)". `Audience` and `Org context` have no recommended option: they depend on the reader, so give every option equal weight and use the default only when the question is cut or the run is unattended.

   When the look-alike search finds activity that no source links to the attack (look-alike domains, a same-week phishing wave), the `Incident` question offers it as "Track it as a watch lead (Recommended)", never as part of the attack.

   **Audience options.** Offer these four teams, in this order, with these labels and descriptions. The question's own "Other" option lets the user type any other team. Every option still gets every output; the answer sets `summary.audience` and changes only the order and emphasis described in Steps 11 and 14.

   | Label | Description | `summary.audience` |
   |---|---|---|
   | CTI | Analytic depth first; findings lead with attribution, corroboration and open gaps | cti |
   | SOC and detections | Detection actions first; findings lead with techniques and the kill chain | soc |
   | Threat Hunting | Hunt hypotheses first; findings lead with behaviors, kill chain gaps and pivots | hunt |
   | Security Leadership | Exposure and decisions first; the hand-over leads with the executive brief | leadership |

   When the user types another team through "Other" (for example Fraud or Vulnerability Management), save their wording in `summary.audience_team` and tailor from the closest of the four teams in `summary.audience`. Name their team in the hand-over, and say in one line which of the four shaped the order. If they choose Other but type nothing, take CTI.

   **Merged Sources options.** When `Sources` and `Browser` both apply, ask "Which sources may I use?" with these options, in this order: "Web search and your browser (Recommended)", with the description "Web search, anything you attach, and your browser for up to five agency and vendor pages"; "Web search only", with the description "Web search and anything you attach; no browser"; and "Only what I attach", with the description "No web search and no browser".

   **Org context options.** Take the first three that apply from this list, in this order, then add "No org context" as the last option. Never drop the question. When none of the first five applies, offer "Victim's sector" with the description "The victim's sector and region, once collection finds them", plus "No org context".

   1. **The saved profile**, when the project or Claude's memory holds the organization's sector, region and technology. Label it with the organization's short name; the description gives the sector, region and key technology.
   2. **A Feedly org profile**, when Feedly is connected. Call `list_org_profiles` with `types: ["companyInfo", "text"]` in Step 1.1 and offer the profile whose sector best matches the victim's. Label it with the profile name; the description gives its sector and region.
   3. **The victim's sector**, when Step 1.1 found it. Label "Victim's sector"; the description names the sector and region (for example "Retail organizations in the UK"). The relevance then speaks to the victim's peers.
   4. **The affected technology**, when Step 1.1 found an affected product. Label "Runs <product>" (for example "Runs FerryGate"); the description says the relevance and actions fit any organization running it, in any sector.
   5. **A second Feedly org profile**, when one matches and a slot is still free.
   6. **No org context.** Label "No org context"; the description says the tracker stays general and the relevance section is left out.

   Put this sentence at the end of the question text: "Or choose Other and type your sector, region, and/or key technology, for example: Financial services, US." Save the answer in `summary.org_context` as sector, region and technology; for "Runs <product>", save "Any organization running <product>". If the user chooses Other but types nothing, take no org context and say so in the hand-over.

   Every question needs a `header` of 12 characters or fewer (use the ones above), two to four options, and `multiSelect` false. If the tool errors or is not available, send the same questions as one numbered list with the default marked for every question except `Audience` and `Org context`, and accept "defaults" as a reply.

   The card holds at most four questions: `Incident`, one `Sources` or `Browser` question, `Audience` and `Org context`. Take the default for `TLP` and `Window`, and say so in the hand-over. The outputs are fixed; do not offer an outputs menu.

3. Stop and wait for the answer. Then `init` the tracker: `python3 work/scripts/tracker_tool.py init tracker.json --attack "<name>"`.

### Step 2. Scope

1. Set `summary.case_type`: incident (one breach), campaign (several incidents under one name), actor (a group and what it has done) or law-enforcement (an arrest, takedown or indictment). Set `summary.language` to the user's language.
2. Write a scope statement: what is in scope, and what is deliberately out (earlier incidents at the same victim, same-week attacks that no source links). Out-of-scope items may appear only as labelled context.
3. Add `scope` rows: one Name row per alias, in its original spelling, with any translation as its own Name row; one Out of scope row per exclusion; and one Incident row per distinct incident (a mass-exploitation wave, a specific breach, a researcher's live-exploitation study). For an actor or law enforcement case, list every incident the actor claimed or was reported for as an Incident or Out of scope row, so nothing is silently missed. Tag later events, victims and techniques with `incident`, using the scope ID (I01). Activity no source links to the attack goes in as an Out of scope row plus a Watch row; it becomes an Incident row only when a source makes the link. Each `out_of_scope_context` entry the subagent returns becomes an Out of scope row.
4. Save the org context, if given, in `summary.org_context`, and the audience in `summary.audience` (cti, soc, hunt or leadership), plus any team the user typed through Other in `summary.audience_team`.

### Step 3. Collect and grade the sources

**Collection always runs in one subagent.** Invoking this skill is the user's request to use a subagent for collection. In the launch turn, read `references/collection-brief.md`, `references/schema.md`, `references/rubrics.md` and `references/soc-handoff.md` together (small models: see Compatibility), fill the brief, and launch it with the `Agent` tool (`subagent_type: "general-purpose"`, `model: "sonnet"`). Fill `Leads already held` with every Step 1 result and the path of any Feedly result saved to disk, and `Page-text tool` with the tool the user allowed. The subagent reads the rubrics itself; do not paste them. If the harness has no subagent tool, follow the same brief in the main thread and keep only the fields it returns.

**Source priority.** Collection searches and fetches sources in this order, and moves down a tier only when the tier above is exhausted or unreachable:

1. **The victim and national authorities.** The victim's own statements, national CERTs and CSIRTs, government cyber security agencies (CISA, NCSC UK, BSI, CERT-FR, ACSC and peers), law enforcement and regulators.
2. **Established CTI vendors and technical vendor reports.** Threat research teams with a public track record (for example Mandiant, Microsoft Threat Intelligence, Palo Alto Unit 42, Cisco Talos, CrowdStrike, ESET, Kaspersky GReAT, Check Point Research, Recorded Future Insikt Group, Sophos X-Ops, SentinelLabs, Proofpoint, Huntress), plus the affected product's vendor advisory and the CVE record.
3. **Cyber news media.** Specialist outlets with their own reporting (for example BleepingComputer, The Record, SecurityWeek, Dark Reading, The Register, CyberScoop, Help Net Security).
4. **High-quality general news media.** Wire services and newspapers of record (for example Reuters, AP, Bloomberg, the Financial Times, the BBC), and local outlets with first-hand access, in the local language.

Blogs, aggregators and social media posts are leads only: chase the originator they name. The tier sets the order of collection, not the grade. Grade every source by Rubrics B1 and B3, and count corroboration by originator, whatever its tier. A tier 3 or tier 4 outlet with first-hand reporting is still an originator.

The brief spends the first five fetches on tier 1 and tier 2 originator pages (the victim's newsroom, the agency or CERT page, the vendor advisory, the named research firm's own blog) and only then on news. It also confirms the current ATT&CK version, so the main thread needs no fetch for it. The main thread runs web search only for the Step 1 look-alike check and the originator round below.

When the subagent returns:

1. Review its grades against `references/rubrics.md` (B1 and B3) and change any you disagree with. Check every Primary label: a relay, repost or leaked copy is Secondary.
2. Read its `tried_originators` list. If any source names an originator nobody read (for example "according to the police" or "the FBI said"), run one targeted round before Step 4: fetch its index page from `references/originator-urls.md`, or search the exact title on the originator's own domain, then fetch it and save it like the others. Never re-fetch a page in this run once it came back summarised or failed. When that page is a named originator's own page, add a Gap row with `blocking` true naming the originator; otherwise add an ordinary Gap. Update mode retries both. If it still fails, add a Gap row with `blocking` true naming that originator, and cap any key judgment that rests on it at low confidence.
3. Use the subagent's JSON; open a saved extract only to check a quote.

Useful Feedly calls, for the brief:

| Need | Tool |
|---|---|
| Cited synthesis across articles (try this first) | `search_threat_intelligence` |
| The attack record and its cited articles | `search_cyber_attacks` or `get_trending_cyber_attacks` |
| Full text of a cited article | `get_article`. The ID is the part after the last `_` in a `feedly.com/i/entry/...` link. |
| More articles | `search_articles` with entity IDs from `search_entities`, or keywords |
| Actor or malware background | `get_threat_actor_info`, `get_threat_actor_relationships`, `get_malware_info` |
| Existing detections | `get_detection_rules_for_entity` |

### Step 4. Write the claims ledger and the rows

Steps 4 to 11 say what goes in each rows file; they are one writing pass, not separate turns. Write the rows files in one turn, in parallel: sources and ledger; the analysis rows (conflicts, timeline, victims, techniques, attribution, software and kill chain); and judgments, gaps and summary. Then run one `add` loop and `check` in the next turn. Do not draft the ledger in your reasoning first. Fix anything `check` raises with `add` or `set`.

For the ledger:

- `claim`: your paraphrase, one fact per row. A fact may say only what its saved line says. A detail the subagent reports that is not on a saved line does not enter the ledger.
- `quote`, `quote_source` and `line`: one verbatim sentence at most, from the saved extract, and its line number there.
- `status` (Rubric B2), Admiralty `credibility` 1 to 6, and `corroboration` naming the originators.
- `said_by`: the speaker, from the subagent's fact. Several outlets carrying one speaker are one speaker.
- Never quote a line that starts `~`; it is the fetch tool's paraphrase.
- `event_date`: when it happened, not when it was reported.
- `first_party`: true only when a cited source is the victim or an authority speaking about its own actions (Rubric B3.5).
- On each source, `interest` (independent, victim, actor, vendor or government) and exactly one `originator`; put any other names in `notes`.

Everything after this step is built only from ledger rows. If you need a fact that is not in the ledger, add the claim first.

### Step 5. Correlate and grade corroboration

1. Add a `conflicts` row wherever sources disagree (times, counts, root cause, names), with the resolution you use and why.
2. When later reporting replaces a claim (a revised root cause, a corrected count, a retraction), mark the old claim Superseded with `superseded_by`. Keep it; the change is information the reader needs.
3. Walk the ledger once against Rubric B3. Upgrade a Reported claim to Confirmed when a second independent originator supports it. Demote a Confirmed claim to Reported when its support is one originator, and to Actor-asserted when only the actor said it. When you decide two outlets share one originator, start `corroboration` with "single originator:". Fill every `corroboration` field.
4. Trace every Feedly record item and entity tag to an originating article before you use it.

### Step 6. Timeline

Build `timeline` rows. Each event has `when` (and `end` for a window), `precision` (exact, approx, day or month), a `lane`, an `event_type`, `status` and `claim_ids`.

- Include every event type the sources give: earliest activity, initial access, attacker actions, detection, containment, disclosure, customer notification, first public reporting, government advisories and law enforcement action. A run with only the earliest activity is incomplete. For a law enforcement case, centre the timeline on the action and the incidents behind it.
- Every ledger claim with an `event_date` becomes an event, unless it is not an event (then clear its `event_date`). `check` lists the dated claims missing from the timeline.
- Write each `event` as who did what: "Harbor Ledger detects unusual activity on the appliance", not "Detection".
- Date the event, not the report. `check` warns when an event's date is later than every source that reports it, or equals its only source's publication date for anything other than a disclosure, report, advisory or claim.
- An event takes the status of the strongest claim behind it, never a stronger one.
- Use `exact` only when a cited quote or the source gives the time of day; never invent a time. Otherwise use `day`.
- `disclosed` is when the world learned of it, which is often days later.
- A detection date is never an access date. If the sources give only detection, the initial-access event is undated and says "access start undisclosed"; `check` warns when an access event cites only detection quotes.
- A time may carry its source's offset (`2026-11-04T09:50-05:00`); `add` converts it to UTC. A time from a live page's update heading is when the update was posted: write "update posted HH:MM", give it a disclosure or notification type, and set `time_line` to the heading line (`S01:19`).

### Step 7. Victims

Build `victims` rows with a tier (Rubric B4), role (compromised party, affected party (cause not confirmed), downstream installer, credential exposure, possible pathway), sector, country, impact, `data_types` and `count_method`. Counts say how they were counted and as of when. Separate the upstream victim from the one-to-many spread. A download, a scan hit or a leak-site listing is not a confirmed victim. Use "compromised party" only when a cited claim has the victim or an authority saying the victim was attacked; until then the role is "affected party (cause not confirmed)". Use "possible pathway" only when a cited claim names the pathway.

`data_types` lists the kinds of data the sources say were exposed: PII, credentials, payment, health, intellectual property, OT or engineering data, or none reported. Each one must appear in the victim's cited claims; never infer a data type the sources do not name.

### Step 8. Techniques

1. Take the ATT&CK version the collection subagent confirmed, and save it in `summary.attack_version`. If the subagent could not reach the versions page, use the bundled version, `v20.1 (not verified at run time)`. `check` validates every technique ID and tactic against the map in `work/scripts/attack_v20.json` (Enterprise and ICS v20.1, which match v20.0); a new ATT&CK release means replacing that one file. Never place a technique from memory. In the turn you write the technique rows, run `python3 work/scripts/tracker_tool.py attack <keyword> [--domain ics]` for the case's key behaviours; it prints the matching IDs, names and tactics from the pinned map. ICS v20.1 has no Default Credentials technique; use T0859 Valid Accounts.
2. Give each row a stable `ttp_id` (M01, M02). Use the current tactic shortnames: reconnaissance, resource-development, initial-access, execution, persistence, privilege-escalation, stealth, defense-impairment, credential-access, discovery, lateral-movement, collection, command-and-control, exfiltration, impact. Never use the retired defense-evasion. Disabling or degrading defenses is defense-impairment; hiding and blending in is stealth. A technique sits only under a tactic it carries in ATT&CK (T1078 is never lateral-movement).
3. For attacks on industrial control systems, map with ATT&CK for ICS: set `domain` ics and use its tactics (inhibit-response-function, impair-process-control, impact and others). T0831 Manipulation of Control is an ICS technique, not an Unmapped row.
4. For unauthenticated exploitation of a public-facing service, use T1190 for the vector and T1059.* for the command execution that follows. T1203 is for a user opening malicious content on a client, not server-side RCE. Use T1211 or T1212 only when that is the exploit's actual effect.
5. For theft of money or crypto assets, map the outcome to T1657 Financial Theft. Map a change of wallet control (pre-signed authorizations, a sweeper contract, a changed signer) to T1098 Account Manipulation as Reported, and say in `how_used` that the mapping is by analogy.
6. Give each row a `phase` so the chain reads in order (for example Upstream, Downstream, Post-compromise), an `incident` when the campaign has several, and `event_ids` for the timeline events it appears in. Set `occurrence` (Rubric B5) and High, Medium or Low confidence. High needs two or more originators; Medium needs two or more, or an Observed occurrence. Assessed rows state the inference in `how_used` with an ICD 203 term. Describe how this attacker used the technique, not the generic ATT&CK text.
7. If no technique fits, use `Unmapped` with tactic `unmapped` and write "analyst review needed" in `check`.
8. Keep this section tied to defender decisions. The dashboard and report add ATT&CK reference mitigations from the bundled map, labelled so no one reads them as sourced. For a full multi-domain mapping with a verbatim quote per technique, offer the map-attack-techniques skill if it is installed.

### Step 9. Attribution

Let the structure fit the incident. Build `attribution` rows of these kinds:

1. **Statement**: every party that has published analysis, and what it will and will not claim.
2. **Signal**: each attribution signal in the reporting (shared code, infrastructure overlap, a claim of responsibility, a government statement), what it shows, and its `limits`.
3. **Hypothesis**: only when the sources name two or more credible candidates. Each has an ICD 203 `likelihood`, a `confidence`, and `for_signals` and `against_signals` that cite the Signal row IDs (H02) or the claim IDs behind them. The dashboard and report then draw a consistency matrix of signals against hypotheses. Never invent alternatives to fill the table; one Hypothesis row fails `check`.
4. **Diamond**: one row each for Adversary, Capability, Infrastructure and Victim. The dashboard and report draw them as a diamond.

For ransomware and extortion, separate the roles (developer, affiliate, initial access broker). An actor's claim of responsibility is Actor-asserted, not attribution. A suspect named by police is alleged until convicted. Write `summary.attribution_statement` as one or two sentences an executive can repeat. When an actor is named, fill `summary.actor`, `actor_likelihood` and `actor_confidence` so the STIX bundle carries the attribution.

### Step 10. SOC hand-off

Build the `software` and `killchain` rows from `references/soc-handoff.md`, which you read at Step 3. Every sourced field traces to a claim; every other field starts "Analyst guidance:". A stage with no host (an on-chain transfer, a change to a physical process) says "N/A (no host stage)" for process and parent. Name the log streams, say which must be turned on first, and defang everything.

For an actor or law enforcement case with no technical reporting, skip the rows and write one line in `summary.soc_note` saying why, instead of a table of "Not available".

### Step 11. Judgments, relevance, gaps and actions

1. Write three to six **key judgments** as ledger rows with topic `Key judgment`, status Assessed, an ICD 203 term and a confidence level in the text, and `basis` listing the claims they rest on. Respect the caps in Rubric B6: a basis of Reported claims from Secondary sources caps the judgment at "likely" with moderate confidence; a basis resting on one originator, on the absence of reporting, or on a blocking gap caps confidence at low. Fill `contrary` (claim IDs and one line) with the strongest contrary signal in the sources; it is required for any judgment that says "unlikely", "rather than" or "no".
2. Fill `summary`: the bottom line (`bluf`, two sentences), a leadership summary of exactly two jargon-free sentences, the exposure question marked `[ANALYST CONFIRMS]`, a one-sentence takeaway, and the six `glance_` fields (presuppose nothing). If the newest incident reporting is more than 30 days older than today, say in the bottom line how old the reporting is. Set `cause_confirmed` to true only when the victim or an authority has said it was a cyberattack; while it is false, the bottom line, leadership summary and `glance_type` say "suspected" or "reportedly". A recommendation in the bottom line needs no "Analyst guidance:" prefix when it cites the Action rows it summarises: "rotate passwords, tokens and API keys (R02, R03)".
3. If an org context was given, write `summary.relevance`: two or three sentences on why this attack does or does not matter to that sector, region and technology, citing claims. Tailor the actions to the same context. When the org context names a region with a breach-notification regime (GDPR, NIS2, a national rule), add one Gap or Action row that points to the regulator's own guidance; never give legal advice or a deadline as fact.
4. Fill `gaps` with three kinds of row. A Gap says what we do not know, why it matters and what would close it; set `status` Open, and `blocking` true when a key fact rests on an originator nobody could read. A Watch row is an early sign the attack is moving again. An Action says exactly how: what to search for, where, and with which query or log source. Put the sourced steps first, each with its claim ID in brackets, then "Analyst guidance:" and the rest. Order the Action rows by `summary.audience`: detections first for soc, hunt hypotheses with their queries and log sources first for hunt, collection first for cti, and decisions an owner can sign off (patch, isolate, notify) first for leadership. Any part of a Watch or Action that is not in the sources starts "Analyst guidance:".
5. Fold behavioural detection into Watch and Action rows: anomalous request shapes, a web server spawning a shell, suspicious egress, file paths, markers and headers, each tied to its claims. Offer, without running them, create-sigma-rule or create-cql-query to turn those rows into detections, and ioc-extract-enrich for network indicators, if those skills are installed.
6. Choose four to six `headlines`. `metric` is a short key and `label` is the caption under the number. Each is a duration computed from two timeline events, or a figure from the figures table. Lead with the one nearest the outcome. Dwell time, time to contain, time to disclose and time to notify are computed for you whenever both events exist, so headlines can cover other spans.

### Step 12. Validate

1. Run `python3 work/scripts/tracker_tool.py check tracker.json --sources work/sources`. Fix every ERROR through `add` or `set`. Resolve every WARN or explain it in `summary.validation`. `check` validates references, labels, dates and formats, and matches quotes to their saved lines. It does not verify that a claim is supported by its source; the audit does that, so a clean `check` is not a clean tracker.
2. Audit the draft as a separate pass, by a subagent given `work/sources/` and `tracker.json` but not your reasoning. It checks for unsupported or overstated claims, wrong ATT&CK IDs or tactics, confidence the sources do not carry, and anything published that should not be. It works through the QA checklist below and returns Pass, Pass with fixes, or Do not publish, with its findings. It also writes every fix as `add`-ready rows (merged by ID) to `work/rows/audit-fixes.json`, and writes nothing else; it never touches `tracker.json`. Give it these intentional conventions, so it does not raise them as findings: `exposure` keeps `[ANALYST CONFIRMS]`; a software `version` is "Any" or "Not reported" when no source states one; an Out of scope row may cite a search result; text starting "Analyst guidance:" is unsourced by design. Review the fixes file, edit what you disagree with, and run one `add`. Do not build until every High-severity item is fixed.
3. Record what was and was not verified in `summary.validation` (one or two sentences), including the quote count `check` prints (verified, and NOT CHECKED from summarised retrieval).

**Analyst QA checklist.**

- **QA1. Confidence consistency.** When a key judgment restates an attribution hypothesis or the summary actor, the likelihood term and the confidence level match. No judgment breaks a Rubric B6 cap.
- **QA2. Retraction handling.** A retracted claim cites the source that reports the retraction and is dated to the retraction. The original claim is Superseded with `superseded_by`.
- **QA3. Negative findings and presupposition.** A "no confirmed compromise" or similar judgment names, in one line, the strongest contrary signal in the sources. No Unknown claim, `glance_` field or judgment assumes an attack type, payload or cause the sources do not state.
- **QA4. Attribution signals are sourced.** Every signal, for and against entry traces to a source, claim or Signal row ID.
- **QA5. Root-cause citation.** The root cause cites the originator whose technical mapping you follow (usually the CNA or the vendor advisory).
- **QA6. Occurrence and confidence calibration.** No technique is Observed on a demonstration alone, and no judgment is more confident than single-source, scanning-only or chatter-based reporting supports.
- **QA7. SOC rows.** Sourced fields trace to claims, everything else is labelled analyst guidance, versions appear only where a source states them, and network values are defanged.
- **QA8. Corroboration.** No claim is Confirmed on one originator unless the victim or an authority said it about its own actions and the original was verified (read, or excerpted with a passing spot-check). No actor claim is Confirmed. No self-serving statement or pre-conviction allegation is Confirmed. No Primary source is a relay or leaked copy. Every named originator was read or is a blocking gap.
- **QA9. Writing.** Each caveat is stated once, there are no "this is not" constructions, the attribution structure fits the sources (no manufactured hypotheses), and "evidence" appears only in a quote, a reported statement or a forensic sense. The tracker's own output is called information or claims, never intelligence.
- **QA10. People.** No private individual is named (role in square brackets instead), no suspect is named before conviction, and nothing could identify a person under 18.
- **QA11. Dates.** Event dates are event dates, not report dates; precision matches what the source gives; and the newest source date is stated when it trails the as-of date.

### Step 13. Build the outputs

Run the file builds in one shell command, in this order, and send nothing to the user yet:

```
python3 work/scripts/tracker_tool.py publish tracker.json work/published && \
python3 work/scripts/tracker_tool.py stix tracker.json out/<attack>-stix.json && \
python3 work/scripts/tracker_tool.py navigator tracker.json out/<attack>-navigator.json && \
python3 work/scripts/render_diagrams.py tracker.json work/diagrams && \
node work/scripts/build_report.js tracker.json work/diagrams out/<attack>-report.docx && \
node work/scripts/build_report.js tracker.json work/diagrams out/<attack>-exec-brief.docx --exec && \
python3 work/scripts/tracker_tool.py verify-docx out/<attack>-report.docx --tracker tracker.json --images 4
```

Use a short file-safe form of the attack name for `<attack>`. `--images` is the number of images the report should have: timeline, attack chain, ATT&CK matrix and Diamond Model, less any section with no rows. If a command fails, read `references/report.md` or `references/stix.md`, fix the cause, and run the rest. A missing image or a skipped Word file is reported in one line, never hidden. A diagram that shows as text fails `verify-docx` and is a High finding.

Then build the dashboard last, following `references/dashboard.md` (four tool calls on a first run). For TLP:AMBER+STRICT or TLP:RED, or when the harness has no Artifact tool or Dashboard type, run `python3 work/scripts/tracker_tool.py html tracker.json out/<attack>-dashboard.html` instead and send that file.

### Step 14. Hand over

In the final turn, make these tool calls back to back, with no text before or between them:

1. `Artifact` with `action: "open"` and the dashboard `url`, so the dashboard card sits at the end of the conversation. If the dashboard `check` document did not appear at Step 13, read it again in this same turn (Reference C).
2. One `SendUserFile` call with every file in `out/` (the Word report, the Word executive brief, the STIX bundle and the Navigator layers), `display: "attach"`, and a one-line caption naming them. If `SendUserFile` is missing, list the file paths instead.

Then write the narrative as your final text. The dashboard and the files hold the detail, so the chat carries only what the reader needs to act on. Keep it to 150 words or fewer, not counting IDs. Follow the writing rules, and copy every judgment with the same ICD 203 likelihood term and confidence level the tracker gives it. Use this order:

1. **Bottom line.** `summary.bluf` as written, two sentences.
2. **Key findings.** Up to three bullets, one sentence each, chosen for `summary.audience`: techniques and kill chain stages for soc, observable behaviors, kill chain gaps and pivots for hunt, attribution and blocking gaps for cti, and exposure and decisions for leadership. When `summary.audience_team` is set, the opening line of the hand-over names that team. Each finding carries its claim or judgment ID and either its status label (Confirmed, Reported, Actor-asserted) or its ICD 203 term and confidence level. On an update run, one of the three names the claim that changed most.
3. **Caveats.** One line naming any blocking gap, anything skipped, any defaults taken and any template fix. Leave it out when there is nothing to say.
4. **Files.** One line naming the Word report, the Word executive brief, the STIX bundle and the Navigator layers. For leadership, name the executive brief first; for soc and hunt, name the Navigator layers and the STIX bundle first. Do not describe their contents.
5. **Sharing.** One line: the dashboard is private until shared, anyone who opens it can read its attached data, and the same dashboard is available as a standalone HTML page for a wiki or intranet.
6. **Updates.** When the attack is Active, one line offering a weekly scheduled task that re-runs this skill in update mode on the dashboard. Create it only if the user agrees.

Do not add a `Sources:` list. The sources sit in the dashboard's Claims and sources tab and in the Word report, and this rule overrides any default habit of ending a reply with sources. Do not paste the dashboard link, recap the steps or explain `tracker.json`.

## Quick brief mode

For a fast answer when the user does not need the files. It keeps the sourcing discipline and drops the build.

1. Step 0 and the Feedly decision tree as usual. Ask no question card unless the attack name is ambiguous.
2. Collect at most five sources, in the source priority order of Step 3 (the victim's statement, the government or CERT advisory, the CTI or product vendor report, then the best one or two news write-ups), in the main thread or one subagent.
3. `init` the tracker with `summary.mode` set to quick. `add` the sources, the ledger and up to three gaps. `check` validates only those collections.
4. Reply in the conversation, in the user's language, in 200 words or fewer and by the writing rules: the bottom line (two sentences), five to eight key facts each with its status label and its originator's name in brackets, attribution in one sentence with an ICD 203 likelihood term and confidence level, and the top three gaps. Do not add a `Sources:` list; the originator named on each fact replaces it.
5. End with one line offering the full attack tracker dashboard. A full run builds on the same `tracker.json`, so nothing is collected twice.

## Compatibility

The skill is built for Claude with its Artifact, subagent and question tools. In other harnesses:

- With no Artifact tool or no Dashboard type, run `tracker_tool.py html` and send the page. It is the same fixed template with the tracker rows embedded and a small runtime, so it looks the same everywhere and opens offline. Never build a dashboard page from scratch.
- With no subagent tool, collection and the audit run in the main thread from the same brief and checklist.
- With no question tool, the question card becomes a numbered list.
- With no `SendUserFile`, list the paths of the files in `out/`.
- The scripts need Python 3.9 or later. Without matplotlib, the timeline, matrix and Diamond images are drawn as SVG, which Word 2016 or later shows. The attack-chain image needs Graphviz, and the Word report and executive brief need Node with the docx package. `preflight` says what is missing, and the run carries on without it.
- Small local models: read each reference only at the step that needs it (`collection-brief.md`, `schema.md` and `rubrics.md` at Step 3, `soc-handoff.md` at Step 10). Write one rows file per turn and run `add` after each, instead of writing them all in one turn. Expect about twice the turns.

## Files in this skill

| File | Read or run it |
|---|---|
| `references/schema.md` | Step 3 (read with the brief): every collection, field and ID prefix, with examples |
| `references/rubrics.md` | Steps 3 to 11: Admiralty grades, claim status, corroboration, victim tiers, occurrence, ICD 203 and its caps |
| `references/collection-brief.md` | Step 3: the subagent brief |
| `references/originator-urls.md` | Step 3: agency, CERT and OT vendor index pages to fetch before searching |
| `references/soc-handoff.md` | Step 3 (read with the schema), or Step 10 on small models: software and kill chain rows |
| `references/dashboard.md` | Step 13: the dashboard procedure and the HTML page |
| `references/report.md` | Step 13, on failure: the Word report and executive brief layout |
| `references/stix.md` | Step 13, on failure: what the STIX bundle and Navigator layers hold, and validation results |
| `references/update-mode.md` | Step 0, in update mode |
| `scripts/tracker_tool.py` | preflight, init, add, set, migrate, check, attack, publish, html, diff, stix, navigator, verify-docx |
| `scripts/attack_v20.json` | The pinned ATT&CK Enterprise and ICS map: techniques, tactics and reference mitigations |
| `scripts/render_diagrams.py` | Timeline, attack chain, ATT&CK matrix and Diamond Model images |
| `scripts/build_report.js` | The Word report and, with `--exec`, the executive brief |
| `assets/dashboard-index.html` | The fixed dashboard page |
| `assets/standalone-runtime.js` | The runtime `tracker_tool.py html` puts into the standalone page |
| `tests/run_tests.py` | Regression tests for the helper on a fictional case; run them after any change to the scripts |
