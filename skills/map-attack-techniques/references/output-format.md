# Output format

Title: `ATT&CK Technique Mapping: [source title]`, then the "Sections
included" line (for example "Sections included: 0, 1, 2, 3, 4, threat
intelligence report"). Section numbers are fixed (0 to 5). Leave out a
section the user did not choose, but never renumber. The written threat
intelligence report, when chosen, comes after the last numbered section,
starts on a new page in the Word document, and is not numbered (see the
end of this file).

Column definitions used in every table that has these columns:

- **Occurrence** (how the source knows it happened)
- **Confidence** (how well the quoted evidence fits the technique's ATT&CK definition)

Write the bracketed definition into the column header itself, exactly as
above, in section 1 and in the technique summary table of the written
report.

## 0. Version and Source Verification (always)

| Source | URL | Version reported | Release date | Checked (date and method) |
|---|---|---|---|---|
| ATT&CK Version History page | https://attack.mitre.org/resources/versions/ | | | live fetch / NOT CHECKED |
| attack-stix-data collection index | https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/index.json | | | |

**Version used for this mapping:** [domain(s), version and release date]
**Verification status:** [Verified against both sources / Sources disagree, see note / History page NOT CHECKED / NOT VERIFIED]
**Navigator:** layer format 4.5, built for Navigator [version]
**Source publication date(s):** [date per source; recorded separately from the ATT&CK version]
**Source reliability (optional):** [Admiralty grade, for example B2, only when the user gives one; otherwise leave this line out. Also set `sources[].reliability` so the layer carries it.]

**Validation checks** (copied from the script's report, one line per check):

| Check | Result |
|---|---|
| Mapping records (quotes, locators, occurrence) | PASS / FAIL |
| Local layer structure | PASS / FAIL |
| ATT&CK content against the pinned bundle | PASS / FAIL / NOT CHECKED |
| Quote verification against source text | PASS / FAIL / NOT CHECKED |
| Source ID reconciliation | PASS / FAIL / NOT APPLICABLE |
| Full Navigator layer schema | NOT CHECKED |
| Navigator application import | NOT CHECKED |

## 1. Mapping Summary (always)

| # | Domain | Tactic | Technique ID and Name (linked) | Sub-technique (if mapped) | Procedure as described in source (1 to 2 sentences) | Occurrence (how the source knows it happened) | Confidence (how well the quoted evidence fits the technique's ATT&CK definition) |
|---|---|---|---|---|---|---|---|

Order the rows by domain (Enterprise, then ICS, then Mobile), then by tactic
in matrix order (from `tactics --domain D`), then by confidence (High,
Moderate, Low), then by where the behaviour first appears in the source.
Number the rows after sorting. The `ref` in the mappings file and the
3.X numbering use the same numbers.

Below the table, one line of counts: mappings by confidence and by
occurrence status. If a confidence threshold removed mappings, add one line
pointing to section 5.

This table is the only coverage view in the report. Do not add a separate
per-tactic coverage table.

## 2. Source ID Reconciliation (always)

If the source cites no IDs, write one line, "The source cites 0 ATT&CK IDs",
and go to 2.1.

Otherwise, one row per distinct cited ID, each exactly once. Then a count
line: "N IDs cited; N reconciled."

| ID as cited in source | Where cited | Status | ID used in this mapping | Reason |
|---|---|---|---|---|

Status is one of:

- Current, retained
- Renamed
- Revoked (replaced by ...)
- Deprecated
- Merged
- Refined to sub-technique
- Generalised to parent
- Not supported by the narrative
- Not in the matrix the source claims (for example, an ICS ID in a report
  that says it uses Enterprise)
- Profile claim, not incident claim (the ID is in an actor profile or
  background section, not the incident narrative)

Never emit a revoked or deprecated ID in section 1, section 3 or any layer.

### 2.1 Source Issues (always; "None found" if none)

Short bullet list of problems in the source that affect the mapping, such
as:

- the matrix it says it uses and the IDs it cites disagree
- it uses different verbs for the same event ("utilized" in one place,
  "deployed" in another)
- the executive summary claims more than the technical sections show
- a cited technique was created in ATT&CK after the source's publication
  date
- its own ATT&CK table contradicts its narrative

## 3. Mapping Detail (always; parts vary)

One block per row in section 1.

### 3.X [Technique ID] [Technique Name] ([Domain], [Tactic])

**3.X.1 Evidence (always).** Every supporting quote, verbatim, in quotation
marks, each with its locator. Number them when there is more than one. The
layer and STIX notes carry the same quotes.

**3.X.2 Rationale (if chosen).** Full:
1. Which element of the quoted behaviour triggers this technique.
2. Why this technique rather than the nearest alternatives, naming each one.
3. Sub-technique justification, or a statement that the source does not
   describe the variant and the mapping stops at the parent.
4. Domain choice, if the behaviour is near the IT and OT boundary.

Short: one sentence covering point 1 and, where relevant, point 3. With
"Short for High, full for Moderate and Low", use Short on High rows only.

**3.X.3 Occurrence (always).** Observed / Reported / Source-assessed /
Capability only, with one sentence saying how the source knows it. For
capability only, state plainly that execution against a victim was not
established.

**3.X.4 Confidence (always).** High / Moderate / Low and the reason, in the
terms of the rubric (decision rule R3). For High, state that the High check
passed.

**3.X.5 Candidate Alternatives Not Selected (if chosen).** For every
mapping, whatever its confidence: each technique considered, linked, with a
one-line reason. "None considered" only if none were. This must agree with
point 2 of the rationale.

At the end of section 3, the consolidated table:

| Mapping # | Technique selected | Candidate not selected | Why it was not selected |
|---|---|---|---|

## 4. Behaviours Not Mapped (if chosen)

| Behaviour described in source (verbatim or close paraphrase) | Locator | Why it was not mapped | What the source would need to say to map it |
|---|---|---|---|

Reasons (use these words):

- no corresponding technique in the domain
- too vague to attribute
- tool named without behaviour
- appears only in mitigations or recommendations
- different campaign or background
- actor profile claim, not incident evidence
- model inference only (R1)
- out of the domains mapped

The last column tells the source author, or the analyst writing the next
report, what wording would have made the behaviour mappable. This makes the
section a quality check on the report's writing.

An empty table on a long report usually means behaviours were forced onto
techniques. If it is empty, say why in one line.

## 5. Below-Threshold Decision Log (only when a threshold removed mappings)

Mappings removed by the confidence threshold keep their full record here,
numbered B1, B2 and so on: the same blocks as section 3 (evidence,
rationale, occurrence, confidence, alternatives), plus one line on what the
source would need to say to raise the rating. They are not in section 1 or
the layer, but the reasoning is not lost.

## Written threat intelligence report (default; unnumbered; left out only if the user asks)

The report is written to be read, forwarded or pasted into an email on its
own. It goes after the last numbered section.

**Layout rules.**

- Word document: insert a page break before the report title so the
  report starts on its own page. Use the Title style (or Heading 1) for the
  report title and Heading 2 for its subheadings. Use heading styles with
  no list numbering attached, so nothing like "6." or "6.1" appears.
- Markdown: put a horizontal rule (`---`) before the report title, use `#`
  for the report title and `##` for its subheadings.
- No numbers in any heading of the report. Subheadings are plain words:
  "Bottom Line Up Front", "Attack Narrative", "Technique Summary",
  "Detection and Hunting Implications", "Confidence and Limitations",
  "Sources". Do not refer to the report as "section 6" or by any number
  anywhere in the outputs.
- Inside the report, do not point to numbered sections of the mapping
  ("see 3.4"). Name the mapping document instead ("see the full mapping in
  [slug]-attack-mapping"), so the report still reads correctly when pasted
  elsewhere.

**Report title.** Write a real headline, as a finished threat intelligence
report would carry. It names the actor, malware or campaign (as the source
names it), the main behaviour in plain words, and the target sector or
region when the source gives one. Title case, no more than about 14 words,
no "TTP report", "mapping" or "ATT&CK" in the title. Examples of the shape:

- "APT29 Phishes European Diplomats and Abuses Cloud Tokens for Persistent Mailbox Access"
- "Atomic macOS Stealer Spreads Through Fake Software Updates to Steal Browser Credentials"
- "Unattributed Actor Tampers with Water Utility PLCs After VPN Compromise"

If the source names no actor, describe the activity ("Unattributed
Actor", "Ransomware Affiliate"). Never add an attribution the source does
not make.

Directly under the title, one plain line: "[date] | Prepared for
[stakeholders] | Based on [source title], published [date] | ATT&CK
[version]". Add the source's TLP marking at the start of the line only
when the source states one.

### Bottom Line Up Front

Three to five sentences: what the adversary does, in behavioural terms, and
what it means for [stakeholders] in [sector] in [country or region].

### Attack Narrative

The intrusion in kill chain order, in prose, with the technique ID inline
at each step, for example "the actor gained access through spearphishing
attachments (T1566.001)". Written for an analyst who has not read the
source, citing the source at each step. Say "the code can" for
capability-only behaviour, never "the actor did".

### Technique Summary

Section 1 reproduced, with the same column headers (including the bracketed
definitions of Occurrence and Confidence), so the report reads on its own.

### Detection and Hunting Implications

| Technique | What to look for behaviourally | Telemetry that would carry it | Notes (including how diagnostic the technique is) |
|---|---|---|---|

Behavioural pointers only. No detection rules, and no field names, command
lines or artefacts that are not in the source.

### Confidence and Limitations

1. Overall confidence in the mapping set and what drives it.
2. What the source does not say that would change the mapping.
3. Single source or corroborated, and how that affects reliance.
4. ATT&CK version used, the date of the version check, and the source
   publication date.

### Sources

Every source document with URL and publication date.

### Writing standards for the report

- Spell out every acronym and malware short name on first use, with the
  short form in brackets, for example "Atomic macOS Stealer (AMOS)". Do this
  separately in the BLUF and in the body.
- BLUF first; state the judgement, then the evidence.
- Estimative language must match the ratings. Use "we assess with high
  confidence" only for High mappings. Do not say "likely" about a behaviour
  rated Low.
- Separate fact from judgement: "the source reports" or "the source
  assesses" for the source's claims, "we assess" for yours.
- Active voice, short sentences, one idea per sentence.
- Dates as "2 October 2026". Times with a time zone.
- No em dashes in your own prose.
- No heading numbers, and no references to numbered mapping sections.
- Re-read the report against this list before delivery.

## F. Feedly context file (Step 8 only)

A separate companion file, written only when Step 8 runs. It never changes
sections 0 to 5 or the written report. The "F." numbering is internal to
this file and does not continue the mapping's numbering.

```markdown
# [Report title]: Feedly context

Companion to [slug]-attack-mapping.md. Feedly Threat Graph data,
queried [date] for [window]. This file does not change the mapping.

## F.0 Scope
| Entity (as in source) | Locator | Source attribution | Feedly entity | Match basis | Window |
|---|---|---|---|---|---|

Not found in Feedly: [list or "none"]. Not comparable (deprecated or
unknown IDs): [list or "none"].

## F.1 Summary
Two to four sentences: counts per group, the most notable "New for this
entity" techniques, and the most reported "Not in this report"
techniques. Estimative language only for the source's own claims.

## F.2 Corroborated
| Mapping # | Technique | Confidence (from mapping) | Feedly articles (N) | Example articles |
|---|---|---|---|---|

## F.3 New for this entity
| Mapping # | Technique | Confidence | Occurrence | Note |
|---|---|---|---|---|

## F.4 Reported elsewhere, not in this report
| Technique | Tactic | Feedly articles (N) | Most recent | Example articles | Section 4 match |
|---|---|---|---|---|---|

[N] further techniques reported in a single article are not listed.

## F.5 Method and limits
Window, deduplication applied (source and republications removed,
same-publisher campaign reporting counted once), parent-level matches,
revoked IDs replaced, and the R6 reminder.
```

Technique IDs are hyperlinked to attack.mitre.org. Article titles are
hyperlinked to the article. "Section 4 match" refers to section 4,
Behaviours Not Mapped, of the mapping document.
