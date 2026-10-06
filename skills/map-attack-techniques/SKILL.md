---
name: "map-attack-techniques"
description: "Maps a threat report's narrative behaviour to current MITRE ATT&CK Enterprise and ICS techniques, with verbatim evidence, occurrence status and confidence for every mapping, after offering recommended defaults or a few setup questions; outputs markdown, Word, one Navigator layer per ATT&CK domain, and optional STIX; with the Feedly MCP server connected, optionally compares the mapping with the actor's Feedly Threat Graph profile."
---

# Map ATT&CK Techniques

Takes the narrative description of adversary behaviour in a report, the
prose that says what the actor did rather than any ATT&CK table the vendor
published, and maps it to current MITRE ATT&CK techniques and
sub-techniques. Enterprise is the default domain. ICS is used for behaviour
against operational technology (OT), and Mobile for behaviour on mobile
devices.

Every mapping carries verbatim supporting quotes with locations, an
occurrence status (was it observed, reported, assessed, or only a
capability?), and a confidence rating that follows a written rubric. The
skill checks the current ATT&CK version at run time and reports, check by
check, what was and was not validated.

**Outputs.** By default: one markdown file, one Word document, and one or
more ATT&CK Navigator layers (JSON, layer format 4.5). There is one layer
per ATT&CK domain the mapping uses, and one per source if the user asks for
that. A STIX 2.1 bundle is optional. The user can drop any format at intake.
With the Feedly MCP server connected, Step 8 can add a Feedly context file
(markdown) and one comparison Navigator layer per domain. These are
companion files. They never change the mapping.

**Package contents.**

- `scripts/attack_tool.py`: version check, ID lookup, quote check, layer
  build and validation, Feedly comparison layer, STIX export. Standard library only. Commands below
  give its path relative to this skill's folder: call it by its full path
  and keep your working files in your own working directory.
- `references/output-format.md`: templates for sections 0 to 5, the
  written threat intelligence report and its writing standards, and the
  Feedly context file (section F).
- `references/mappings-schema.md`: the mappings file the script reads, and
  `feedly-context.json` (section F).
- `references/layer-rules.md`: what the layer contains, and rules for
  building one by hand when no shell is available, including the Feedly
  comparison layer (section F).

**Dependencies.** Python 3 for the script. The Word document needs a docx
capability (the docx skill, python-docx or the docx npm package). If none is
available, say so in one line, deliver the other formats, and offer the
markdown file for conversion. Never skip the Word document without saying so.
The first lookup downloads and caches the STIX bundle for each domain used
(Enterprise about 55 MB, ICS about 4 MB). Global options (`--offline`,
`--attack-version X.Y`, `--bundle PATH`) can go before or after the
subcommand.

**Feedly MCP server (optional).** Needed only for Step 8. If it is not
connected, the skill runs Steps 0 to 7 in full and does not mention
Feedly, unless the user asked for Feedly context. In that case, say in
one line that the server is not connected and link the setup guide:
https://docs.feedly.com/article/822-setting-up-the-feedly-mcp-server-in-claude

If the server is connected, always say so in the Step 7 closing summary,
whether or not Step 8 runs. Never skip Step 8 silently or only hint at the
reason. When Step 8 cannot run because the source names no actor, malware
or campaign (8.1), the closing summary must contain this exact line:
"Feedly is connected. Step 8 was skipped because the source names no
actor, malware or campaign."

## Workflow

Eight steps, Step 0 to Step 7, in order, plus the optional Step 8 when the
Feedly MCP server is connected. Stop and wait for the user at the
end of Step 0 (only if source material is missing) and Step 1. Show no
mappings before Step 3 is finished.

### Step 0. Confirm the source material

The skill maps only what the source describes. Confirm you have it: a pasted
report, an attached file (PDF, DOCX, HTML, text) or a URL. Read all of it.

- If nothing is provided, ask for it. Do not map from a threat actor name or
  from training knowledge. Use web search only if the user tells you to, and
  then treat the pages you find as the source and cite them.
- Remind the user once, in one line, to sanitize before sharing: victim
  names, internal hostnames and internal IPs replaced with placeholders, and
  nothing above TLP:GREEN unless its handling terms allow it.
- Save a plain-text copy of each source in the working directory
  (`source-1.txt` and so on). The script checks every quote against it.
- Note: the number of sources; the source's publication date; whether it
  cites ATT&CK IDs and how many (count each distinct ID); which matrix it
  says it uses; and whether it describes OT assets (PLCs, HMIs, engineering
  workstations, safety systems, field devices, the physical process).

### Step 1. Intake

Ask only what the user has not already answered. Use the multiple-choice
question tool when it exists; it allows at most three questions per call and
adds its own "Other" option, so never supply one. If there is no
multiple-choice tool, send one plain-text message that lists every question
below as a numbered list with the recommended answer marked, and accept
"defaults" as a reply.

**Round 0 (one question, always first unless already answered):**
"Run with the recommended defaults, or choose the options?"
- Use recommended defaults (Recommended): no more questions; the run
  finishes without input.
- Let me choose

If the user picks defaults, or said "use defaults", "just run it" or similar,
skip to the end of this step. Apply the defaults table and list the defaults
in one line. Read the paragraph on implied answers below first.

**Round 1 (three questions):**

1. "How much rationale do you want behind each technique?"
   - Full rationale (Recommended): the four-point rationale in 3.X.2.
   - Short for High, full for Moderate and Low: keeps long reports short.
   - Short rationale: one sentence per technique.
   - No rationale: evidence, occurrence and confidence only.
2. "Do you want the candidate techniques considered but not selected?"
   (3.X.5 and the consolidated table)
   - Yes (Recommended)
   - No
3. "Do you want the table of behaviours in the report that were not
   mapped?" (section 4)
   - Yes (Recommended): the main check that behaviours were not forced onto
     techniques.
   - No

**Round 2 (three questions):**

4. "Do you want a written threat intelligence report on top of the mapping
   tables?" (a titled, unnumbered report on its own page, ready to paste
   into an email)
   - Yes, add the written report (Recommended)
   - No, mapping tables only
5. "Which mappings should be included in the report and the layer?"
   - All confidence levels (Recommended)
   - Moderate and High only
   - High only
6. "Which output files do you want?"
   - Markdown, Word and Navigator layer (Recommended)
   - Word and Navigator layer (no markdown file)
   - Navigator layer only
   - All three plus a STIX 2.1 bundle
   Any other combination comes through "Other". There is one Navigator
   layer per ATT&CK domain used.

**Round 3 (only when there is more than one source):**

7. "You gave me more than one source. How should the Navigator layer be
   built?"
   - One combined layer (Recommended): comments name the source of each
     quote.
   - One layer per source
   - Both

**Round 4 (only if the user chose "Let me choose" and kept the written
report):** in one plain-text message, ask for the user's role, sector,
country or region, the teams the report is for, and the layer name. Show
the defaults and accept "defaults". On the defaults path, do not ask:
write the report with the default audience values below.

**Implied answers.** The written report is produced by default. If the
user gives an audience, role, sector, region or stakeholders anywhere in
the request, use what they gave, default the rest, and say so in the
one-line summary. Leave the report out only when the user says so (for
example "mapping tables only" or "no report"), or picks "No" at Q4.

If the user mentions Feedly, the Threat Graph, or asks how this report
compares with other reporting on the actor, they want Step 8. Plan to run
it after Step 7 and say so in the one-line summary. Step 8 still shows its
routing plan for approval before it queries anything. Do not add an intake
question for Step 8; the defaults path must still finish without input.

Do not ask about the parent of a mapped sub-technique (always uncoloured and
only expanded), about the ATT&CK domain (decided by the rules in Step 3), or
about any other optional section.

**Defaults:**

| Setting | Default |
|---|---|
| Rationale | Full |
| Candidates not selected (3.X.5) | Yes |
| Behaviours not mapped (section 4) | Yes |
| Written threat intelligence report | Yes (left out only if the user asks) |
| Minimum confidence | All |
| Output files | Markdown, Word, Navigator layer(s) |
| STIX bundle | No |
| Parent of sub-technique in layer | Not coloured, only expanded (fixed) |
| Source ID reconciliation (section 2) | Always; states "0 IDs cited" when none |
| Below-threshold decision log (section 5) | Yes whenever a threshold removes a mapping |
| Multiple sources | One combined layer |
| Job role | Threat Intelligence Analyst |
| Sector | cross-industry |
| Country or region | global |
| Stakeholders | detection engineering and threat hunting stakeholders |
| Layer name | "[Actor or report title] TTP Mapping" |

After the questions, summarize the choices in one line and move on.

### Step 2. Verify the current ATT&CK version

Do this before any mapping. Use two sources, because they fail differently.

1. Run `python3 scripts/attack_tool.py version`. It reads the
   attack-stix-data collection index (the machine source that tooling,
   including the Navigator, downloads from) for Enterprise, ICS and Mobile,
   and reports the current Navigator release. Without a shell, fetch
   https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/index.json
   and read the highest version of each collection.
2. Fetch https://attack.mitre.org/resources/versions/ itself with a live
   fetch tool and read the current version and release date. A search
   result snippet does not count: snippets have been a full minor version
   out of date. If you cannot fetch the page, record it as NOT CHECKED.
3. Re-run `version --history-version X.Y` with the version from the page.
   Follow the decision it prints:
   - Versions agree: "Verified against both sources".
   - History page is higher than the index: no bundle exists yet for that
     version. Map and validate against the index version, state the
     discrepancy, and say the newer version's content was NOT CHECKED.
     Never label the mapping with a version you could not validate against.
   - Index is higher: map against the index version and note that the page
     lags.
4. If you cannot reach either source, stop. Say that you could not verify
   the version, name the latest version you know and your knowledge cutoff,
   warn that the matrix has likely changed since, and ask the user to enable
   web access or confirm a version. A mapping made against an unverified
   matrix is not a deliverable. If they confirm one, carry on with section 0
   marked NOT VERIFIED and every output labelled draft. Set
   `verification_status` to "NOT VERIFIED" and run the script with
   `--attack-version X.Y` (add `--offline` if there is no network). The
   layer then carries a DRAFT status line.

Record the source's publication date next to the ATT&CK version in
section 0. They are different facts. A technique created in ATT&CK after the
source's publication date is a Source Issue (the report may have been revised
without a new date), not a reason to drop the mapping.

### Step 3. Map the behaviour

Work through the narrative prose in kill chain order, applying the decision
rules below. For every behaviour: decide whether it can be mapped at all,
choose the domain and technique, collect every supporting quote, set the
occurrence status, rate confidence, and record each alternative you
considered. Do this even if the user did not ask to see rationale or
alternatives. The intake controls what is printed, not how carefully you map.

Verify every ID before writing it anywhere:
`python3 scripts/attack_tool.py lookup T#### T####.### ...` (T0### IDs
resolve against ICS automatically; use `--domain mobile` for Mobile). It
returns the name, tactics, status (current, revoked with replacement, or
deprecated), the ATT&CK creation date, and how many groups, campaigns and
software use the technique. Use `tactics --domain D` for tactic names and
matrix order. Without a shell, open each technique page on attack.mitre.org.
Do not emit an ID you could not verify.

Run every ID the source cites through `lookup` for section 2, and confirm
the reason for each change against https://attack.mitre.org/resources/updates/.

### Step 4. Build the Navigator layer(s) and run the checks

Write `mappings.json` (schema in `references/mappings-schema.md`) with one
entry per mapping, including mappings below the confidence threshold (the
script filters them). Include `source_cited_ids`, the `reconciliation` list
and `text_path` for each source. Then, for each domain present:

```
python3 scripts/attack_tool.py verify-quotes mappings.json
python3 scripts/attack_tool.py build-layer mappings.json --domain enterprise -o <slug>-enterprise-navigator-layer.json
python3 scripts/attack_tool.py build-layer mappings.json --domain ics -o <slug>-ics-navigator-layer.json
python3 scripts/attack_tool.py validate <slug>-enterprise-navigator-layer.json
```

Drop `--domain` when only one domain is used, and name the file
`<slug>-navigator-layer.json`. `build-layer` prints a named check report and
writes nothing if any check FAILS:

| Check | Meaning |
|---|---|
| Mapping records | every mapping has quotes, a locator for each quote, and a valid occurrence status |
| Local layer structure | a subset of the Navigator 4.5 format, checked locally |
| ATT&CK content | ID, name and tactic match the pinned STIX bundle for that domain; NOT CHECKED offline |
| Quote verification | each quote is at least four words and appears word for word, on word boundaries, in the saved source text; NOT CHECKED without text |
| Source ID reconciliation | every cited ID has exactly one disposition, worded as a section 2 status |
| Full Navigator layer schema | always NOT CHECKED by this tool |
| Navigator application import | always NOT CHECKED; the user confirms by importing |

Quote verification and ATT&CK content cover the domain being built.
Reconciliation always covers the whole file. Fix the mapping, not the check,
and re-run until nothing FAILS. Report the
statuses exactly as printed. Never describe a layer as "validated" or
"conforms" when any line says NOT CHECKED. Instead say which checks passed
and which were not run. The script also prints counts: direct mappings,
coloured entries, and parent display entries. Parent entries are only there
so the Navigator can expand a sub-technique. They are not mapped procedures,
and must never be counted as such.

If the user asked for STIX, run
`python3 scripts/attack_tool.py export-stix mappings.json -o <slug>-stix.json`
and state that the bundle was not run through a STIX validator.

If no shell is available, build the layer by hand to
`references/layer-rules.md`, check it line by line, and mark every check
that needs the script as NOT CHECKED.

### Step 5. Write the mapping in markdown

Follow `references/output-format.md`. Keep the section numbers fixed (0 to 5)
even when a section is left out, so "section 4" means the same thing on
every run. Section 2 (Source ID Reconciliation) always comes before
section 3 (Mapping Detail). There is no coverage snapshot section: the
section 1 summary table is the coverage view. The written threat
intelligence report (included by default) goes after the last numbered section, has
its own headline title and unnumbered subheadings, and never refers to
numbered mapping sections. Put a one-line "Sections included" note under
the title. Save as `<slug>-attack-mapping.md`. Write it even if the user did not ask for the
markdown file, because the Word document is built from it. Deliver it only if
the user asked for it.

### Step 6. Build the Word document

Read the docx skill's SKILL.md (or use python-docx or the docx npm package),
then build `<slug>-attack-mapping.docx` with the same content and section
order and no additions. Tables stay tables, and technique IDs stay
hyperlinked. The section 1 column headers keep their bracketed
definitions of Occurrence and Confidence. If the written threat
intelligence report is included, insert a page break before its title,
use the Title style (or Heading 1) for the title and Heading 2 for its
subheadings, and use heading styles with no list numbering attached, so
the report can be copied into an email without "6." or "6.1" prefixes.
If no docx capability exists, say so (see Dependencies).

### Step 7. Self-check, then deliver

Before sending anything, check:

- Every ID anywhere in the report text (sections 1, 2, 3 and 5, and the
  written report) is current, its name matches, and its tactic is one it sits under in the
  version mapped. The script checks this for the layer only; apply the same
  result to the report.
- Every ID in sections 1 and 3 matches the layer(s), and the layer quotes
  match section 3 (all quotes, not only the first).
- Every High mapping passed the High check below.
- Every cited source ID appears exactly once in section 2, or section 2
  says "The source cites 0 ATT&CK IDs."
- Section 1 column headers carry the bracketed definitions of Occurrence
  and Confidence.
- Unless the user left it out, the written report exists and meets the writing
  standards in `references/output-format.md` (a headline title, no heading
  numbers, its own page in the Word document, acronyms spelled out on first
  use, BLUF first, estimative language matching the confidence levels).
- Quoted text is untouched (see the em dash rule).

Send the files the user chose. Then, in no more than six lines:

- The ATT&CK version or versions mapped and the verification status.
- Counts: direct mappings by confidence and by occurrence status;
  behaviours not mapped; and, per layer, coloured entries and parent
  display entries.
- The check report in one line: which checks passed and which were not run.
- How to import: at https://mitre-attack.github.io/attack-navigator/, choose "Open Existing Layer", then
  "Upload from local", and select the JSON file. Import an ICS layer into
  the ICS matrix. If the Navigator's matrix is newer, it offers to upgrade
  the layer, which is safe to accept.
- A reminder that each mapping is a model-made claim to accept, amend or
  reject before the output leaves the team. Mention that the layer's
  "generated by" metadata field says this, and that the user can edit it
  before distributing the layer outside the team.
- If the Feedly MCP server is connected, one line that states it is
  connected and what happens next. Check 8.1 first, before writing this
  line:
  - The source names at least one actor, malware family or campaign, and
    Step 8 was not already requested: "Feedly is connected." followed by
    an offer to compare the mapping with the Threat Graph profiles of the
    actors and malware the report names.
  - The source names none: "Feedly is connected. Step 8 was skipped
    because the source names no actor, malware or campaign." Write it
    exactly like this. Do not replace it with a vaguer phrase such as
    "nothing to run against".

### Step 8. Actor context from Feedly (optional)

Run this step only when the Feedly MCP server is connected and the user
asked for it, accepted the offer in Step 7, or implied it at intake. It
reads the finished mapping and adds context. It never edits sections 0 to
5, the written report, the main layer(s) or the STIX bundle, and nothing it
finds may change eligibility, confidence or occurrence status (R6).

**8.1 Pick the entities.** List the threat actors, malware families and
campaigns that the source names as responsible for, or used in, the
mapped activity. Take them from the source text only, with a locator for
each. Record the source's attribution strength next to each entity:
attributed by the source, attributed by a third party the source cites, or
suspected or tentative. If the source names none, skip the step and say so
in one line, worded exactly: "Feedly is connected. Step 8 was skipped
because the source names no actor, malware or campaign." This applies
whether Step 8 was requested or only offered. Do not choose an actor
yourself to make the step run (R1, R6).

**8.2 Resolve each entity in Feedly.** Search the Threat Graph for each
name and its aliases in the source. Accept a Feedly entity only when its
name or alias matches. If two or more entities match, or the match depends
on an alias the source does not use, list the candidates in the routing
plan and let the analyst choose. If nothing matches, record "not found in
Feedly" and continue with the other entities.

**8.3 Show the routing plan and wait.** In one message, show a table with
these columns: entity as named in the source, Feedly entity, match basis,
source attribution strength, time window, and the Feedly tool each query
goes to. The default time window is the last 12 months to the run date. If
the source is older than 12 months, offer a window that ends at its
publication date as a second option. Wait for approval. The analyst can
drop entities, change the window or correct a match.

Route each need to the Feedly MCP tool whose description covers it. Read
the server's tool list at run time and name the actual tool in the routing
plan; do not guess a tool name.

| Need | Feedly MCP tool |
|---|---|
| Resolve an actor, malware or campaign name and aliases | the server's entity search or lookup tool |
| Technique profile for an entity in a time window | the server's entity profile or TTP tool |
| Articles reporting a technique for an entity | the server's article search tool, filtered by entity and technique |

If no tool on the server covers a need, say which one in the routing plan
and run the rest of the step without it.

**8.4 Pull the technique profiles.** For each approved entity, get its
ATT&CK technique profile for the window: each technique ID, the number of
distinct articles reporting it, and up to five article links (title,
publisher, date), most recent first. Then:

- Run every Feedly technique ID through `attack_tool.py lookup`. If an ID
  is revoked, use the replacement and note "Feedly ID T#### revoked;
  shown as T####". If an ID is deprecated or not found, list it under
  "Not comparable" in F.0 and leave it out of the comparison.
- Remove the source itself from the article lists and counts, and any
  republication of it (same title or same body under another publisher).
  A report cannot corroborate itself.
- Count articles from the same publisher about the same campaign as one.

**8.5 Compare.** Compare at technique level, using the mapping's
confidence threshold. Compare a parent technique in Feedly with any of
its sub-techniques in the mapping, and the reverse, as a "parent-level
match" and say so. Put every technique in exactly one group:

| Group | Meaning | How to describe it |
|---|---|---|
| Corroborated | In this mapping and in the Feedly profile | "Also reported for [entity] in N other articles." This supports the fit to the actor. It does not raise the mapping's confidence. |
| New for this entity | In this mapping, not in the Feedly profile for the window | "Not in Feedly's [entity] profile for [window]." Possible new tradecraft, a coverage gap in Feedly, or an attribution question. Do not decide which. |
| Not in this report | In the Feedly profile, not in this mapping | "Reported for [entity] elsewhere; not observed in this source." A hunting lead or a visibility question. Never a mapping, never "missed". |

For "Not in this report", show only techniques reported in at least two
distinct articles in the window, sorted by article count, top 25 per
entity. List the rest as a count only. If a technique in this group
matches a behaviour in section 4 (behaviours not mapped), say so and give
the section 4 row: it may be worth a second look at the source, but the
section 4 decision stands.

If the source's attribution of an entity is suspected or tentative, put
this above that entity's results: "The source's attribution of this
activity to [entity] is tentative, so this comparison is too."

**8.6 Write the outputs.** Write `<slug>-feedly-context.md` to the template
in `references/output-format.md` (section F). If the analyst wants the
comparison layer, write `feedly-context.json` (schema in
`references/mappings-schema.md`, section F) and run:

```
python3 scripts/attack_tool.py build-comparison-layer mappings.json feedly-context.json --domain enterprise -o <slug>-enterprise-feedly-comparison-layer.json
python3 scripts/attack_tool.py validate <slug>-enterprise-feedly-comparison-layer.json
```

Build one comparison layer per domain present. Without a shell, build it by
hand to `references/layer-rules.md` (section F) and mark the checks that
need the script NOT CHECKED.

**8.7 Deliver.** Send the files. Then, in no more than four lines: the
entities and window queried; counts per group per entity; the checks run
on the comparison layer; and a reminder that Feedly profiles are built
from aggregated reporting, change over time, and are dated in the file.

## Decision rules

### R1. Eligibility comes before confidence

A behaviour can be mapped only if the source describes it: an action, the
thing acted on, and enough detail to match a technique definition.
Eligibility is a yes or no decision made first. Confidence is set
afterwards and only expresses how sure you are in reading behaviour the
source describes. A Low rating never makes an ineligible behaviour
eligible.

These are not eligible on their own, and go to section 4 with the reason:

- A tool or file being present ("mimikatz.exe was recovered") when the
  source does not say it ran or what it did.
- The actor's reputation, other reporting about the actor, or what the actor
  "typically" does.
- Your own inference that something "probably" happened.
- Behaviour named only in mitigations, recommendations or hunting
  suggestions.
- Behaviour from a different campaign or historical background section.
- Anything added to make a tactic look covered. Do not pad a tactic to make
  coverage look complete.
- IDs listed in an actor profile, as opposed to the incident narrative.

The source author's own analytic judgement ("investigators assess that
credentials were dumped") is eligible, with occurrence status
source-assessed. A model-made hypothesis is not, whatever confidence it
would get.

### R2. Occurrence status (separate from confidence)

Every mapping records how the source knows the behaviour happened:

| Status | Use when |
|---|---|
| Observed | the source author saw it (telemetry, forensics, logs, malware analysis of a sample from the incident) |
| Reported | the source relays a third party's observation (a victim, partner or other vendor) |
| Source-assessed | the source author judges it happened without direct observation |
| Capability only | the source describes what code, a tool or a kit can do, but not that it ran against a victim |

Capability-only behaviour is eligible when the source describes the
behaviour itself (for example, code analysis of an exfiltration module). It
must never be described as completed activity anywhere in the outputs. If
the executive summary of the source claims more than its technical sections
show, map to the technical evidence and record the gap under Source Issues.

### R3. Confidence rubric (ICD 203 terms: High, Moderate, Low)

Confidence measures how well the quoted behaviour fits the selected
technique's ATT&CK definition. It does not measure whether the event
happened (that is occurrence).

| Rating | All of these hold |
|---|---|
| High | The quote states the action and its object explicitly. It meets the technique's definition as written on attack.mitre.org, including any conditions the definition sets (for example, T1110.004 requires credentials from unrelated breaches). No considered alternative stays defensible on this evidence. If a sub-technique is chosen, the quote names the variant. |
| Moderate | The behaviour is described, but either one other technique stays defensible, or a definitional condition is likely met but not stated. |
| Low | The behaviour is described, but thinly. Several techniques stay defensible, or the description matches the technique only in part. |

**High check.** Before marking a mapping High, answer each line yes or no
in your working notes: action and object stated? definition conditions met?
alternatives ruled out by the quote itself? sub-technique variant named (if
used)? ID, name and tactic verified? Any "no" makes it Moderate. Rate the
same evidence the same way across reports: if two quotes are equally
explicit, they get the same rating.

The script accepts "medium" as an alias, but all outputs say "Moderate".

### R4. Domain choice: Enterprise, ICS or both

- Map to the domain of the asset the behaviour acts on. Behaviour against
  PLCs, HMIs, engineering workstations, safety systems, field devices or the
  physical process goes to ICS. IT-side behaviour goes to Enterprise.
  Behaviour on mobile devices goes to Mobile.
- Do not push OT behaviour into Enterprise approximations, or the
  Enterprise layer misrepresents an OT report. If an OT behaviour has no
  ICS technique, put it in section 4.
- One behaviour gets one domain by default. Record the other domain's
  equivalent as a candidate not selected, with the reason "cross-domain
  equivalent". Map in both domains only when the source describes distinct
  activity in each environment. In that case link the two rows with
  `paired_with` and say why.
- If a source's own IDs come from a different matrix from the one it says it
  uses, record the mismatch under Source Issues and give those IDs the
  section 2 status "not in the matrix the source claims".

### R5. Mapping discipline

1. Work from the narrative prose. Treat any ATT&CK table in the source as a
   claim to check, not input to copy. Map the prose first, then reconcile in
   section 2. Vendor tables go stale and are often drafted against an older
   matrix.
2. Quotes are verbatim, in quotation marks, with a locator (section, page,
   heading or paragraph). Give every passage that supports a mapping; the
   layer, the document and the STIX notes carry all of them. Mark an
   omission with "[...]". Never rewrite, trim mid-word or reword a quote. If
   you cannot quote it, you cannot map it.
3. Prefer the parent technique when the source does not describe the
   sub-technique variant. A confident sub-technique from a thin sentence is
   worse than an honest parent mapping.
4. Where two techniques are defensible, map the stronger one and record the
   other as a candidate not selected. Where the source supports both, map
   both as separate rows and say why.
5. List every alternative you considered for every mapping, whatever its
   confidence. Write "None considered" only when there were none. Never write
   "None, unambiguous" next to a rationale that names rejected alternatives.
6. If one behaviour sits under two tactics for the same technique, make one
   row per tactic.
7. Map against the version verified in Step 2 only. The matrix changes about
   twice a year: in v19, Defense Evasion was split into Stealth and Defense
   Impairment, and T1562 Impair Defenses was merged into T1685. A mapping
   made against a remembered version is unreliable however confident it
   reads.
8. Link every technique ID to attack.mitre.org and cite the source for
   every procedure, quote and claim.
9. Usage counts from `lookup` measure how diagnostic a technique is. A
   technique used by few groups says more about the actor than one used by
   dozens. Use them only in the written report's analysis, never to change
   eligibility or confidence.
10. No em dashes in your own prose. Quoted source text is exempt: keep the
    source's punctuation exactly, em dashes included.

### R6. Feedly context is kept apart from the mapping

1. Nothing from Feedly enters sections 0 to 5, the written report, the main
   layer(s) or the STIX bundle. Do not add, remove, re-rate or re-word a
   mapping because of Feedly.
2. Every Feedly claim is labelled "Feedly Threat Graph" and links to its
   articles. Never present Feedly content as coming from the source.
3. "Not in this report" techniques are never described as missed, likely,
   probable or expected in this incident. They are things reported
   elsewhere, to hunt for or ask about.
4. Feedly's profile is aggregated reporting, not ground truth. "New for
   this entity" can mean new tradecraft, a gap in Feedly's coverage, or
   misattribution. Name the possibilities and do not pick one.
5. Record the query date and time window everywhere a Feedly count
   appears. Profiles change.
6. No em dashes in your own prose (as R5.10). Article titles are quoted as
   published.