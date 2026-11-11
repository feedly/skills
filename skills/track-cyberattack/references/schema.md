# Reference A. The attack tracker (`tracker.json`)

Read this at Step 3, before the first `add`.

`tracker.json` is one JSON object at the top of the working directory. Each key is a collection: an array of row objects. `summary` has one row. IDs are stable across runs: never renumber, never delete, only append. `tracker_tool.py add` refuses unknown collections and unknown fields, so the field names below are exact.

## How to write rows

Never write `tracker.json` by hand. Create it once, then add rows from small files in `work/rows/`:

```
python3 work/scripts/tracker_tool.py init tracker.json --attack "Harbor Ledger breach"
python3 work/scripts/tracker_tool.py add tracker.json work/rows/01-sources-ledger.json
python3 work/scripts/tracker_tool.py set tracker.json ttps M02 confidence Low
```

A rows file is either `{"collection": "ledger", "rows": [ ... ]}` or several collections at once, `{"sources": [ ... ], "ledger": [ ... ]}`. `summary` takes one object. `add` merges by ID: a row with an existing ID updates only the fields it gives. Pass `--replace` to overwrite whole rows. If a rows file is not valid JSON, `add` names the line and column and changes nothing; fix that small file and run it again. ID fields (`source_ids`, `claim_ids`, `basis`, `superseded_by`, `relay_of`, `event_ids`, `closed_by`) are space separated; a list is also accepted. `data_types` takes a list or a semicolon-separated string.

`set` changes one field of one row (`set tracker.json summary - status Contained` for the summary). Every `add` and `set` also refreshes `summary.newest_source_date`, so you never type it. `migrate` brings an older tracker up to the current schema (it gives technique rows without one a `ttp_id`).

## Collections

Required fields are in bold. `check` reports an empty required field as an ERROR.

| Collection | Fields |
|---|---|
| `summary` | **`attack`**, **`status`** (Active, Contained, Concluded, or a short phrase), `mode` (full or quick), `case_type` (incident, campaign, actor, law-enforcement), **`iteration`**, `created` (first run, never changes), **`as_of`** (ISO UTC), `newest_source_date` (kept by the helper), **`tlp`**, `language` (en, es, fr, de, pt), `feedly_id`, **`attack_version`**, **`bluf`** (the summary, bottom line), **`leadership`**, **`exposure`**, **`takeaway`**, `org_context` (sector, region and key technology), `audience` (cti, soc, hunt or leadership; sets the order of Action rows and the hand-over emphasis), `audience_team` (the team the user typed through Other, in their wording; empty otherwise), `relevance`, **`scope`**, **`attribution_statement`**, `actor`, `actor_likelihood`, `actor_confidence`, `glance_victim`, `glance_type`, `glance_window`, `glance_access`, `glance_impact`, `glance_attribution`, `soc_note`, `validation`, `cause_confirmed` (true or false: whether the victim or an authority has confirmed a cyberattack as the cause; when false, the bottom line, leadership summary and `glance_type` say "suspected" or "reportedly") |
| `changes` | **`change_id`**, `iteration`, **`kind`** (New, Revised, Superseded, Closed gap, Removed), **`item`**, `before`, `after`, `claim_ids`. Empty on the first run; `diff` writes it. |
| `headlines` | **`metric`** (a short key, such as dwell), **`label`** (the caption shown under the number), **`kind`** (span_days, span_hours, span_minutes, figure), `from_event`, `from_field` (when or end), `to_event`, `to_field`, `figure_id`, `unit` |
| `sources` | **`source_id`**, **`title`**, **`publisher`**, **`date`** (ISO date; "undated" only for a failed source with no date anywhere), `url` (http or https only), **`type`** (use "reference" for background pages such as ATT&CK, which do not count as incident reporting), **`position`** (Primary, Secondary), **`originator`** (one name), `relay_of`, `first_party` (victim, victim-relayed, authority, actor or empty), `interest` (independent, victim, actor, vendor, government), **`retrieval`** (read, excerpts, summarised, snippet, failed), `spot_check` ("3/3 matched", "2/3 matched" or "not run"; excerpts only), `language`, **`reliability`** (A to F), `notes` |
| `ledger` | **`claim_id`**, **`topic`**, **`claim`**, `quote`, `quote_source`, `line` (the line of the quote in `work/sources/<quote_source>.txt`), **`status`** (Confirmed, Reported, Actor-asserted, Assessed, Superseded, Unknown), **`credibility`** (1 to 6), **`source_ids`**, `corroboration`, `event_date`, `first_party` (true or false), `superseded_by`, `basis`, `incident`, `said_by` (who made the statement: "Harbor Ledger", "Metro Police"; separate two speakers with a semicolon), `contrary` (key judgments only: the claim IDs and one line on the strongest contrary signal) |
| `timeline` | **`event_id`**, **`when`**, `end`, **`precision`** (exact, approx, day, month), **`lane`**, **`event_type`**, **`event`**, **`status`**, **`claim_ids`**, `disclosed`, `incident`, `time_line` (where the time of day comes from when it is not in the cited quote, as `S01:19`) |
| `figures` | **`figure_id`**, **`label`**, **`value`**, `unit`, **`status`**, **`claim_id`**, `note` (the method and its caveats) |
| `victims` | **`victim_id`**, **`victim`**, **`role`** (compromised party, affected party (cause not confirmed), downstream installer, credential exposure, possible pathway), `sector`, `country`, **`tier`**, `impact`, `data_types` (PII, credentials, payment, health, intellectual property, OT or engineering data, none reported), **`count_method`**, **`claim_ids`**, `incident` |
| `ttps` | **`ttp_id`** (M01), **`technique_id`**, **`name`**, `domain` (enterprise or ics; ics is inferred for T0xxx), **`tactic`**, **`phase`**, `incident`, **`how_used`**, **`occurrence`**, **`confidence`** (High, Medium, Low), `event_ids`, **`claim_ids`**, `check` |
| `attribution` | **`row_id`**, **`kind`** (Statement, Signal, Hypothesis, Diamond), **`party`**, **`position`**, `likelihood`, `confidence`, `for_signals`, `against_signals` (both cite Signal row IDs or claim IDs; the old names `Evidence`, `for_evidence` and `against_evidence` are renamed on `add`), `limits`, `claim_ids` |
| `conflicts` | **`conflict_id`**, **`topic`**, **`position_a`**, **`position_b`**, **`resolution`**, **`claim_ids`** |
| `gaps` | **`item_id`**, **`kind`** (Gap, Watch, Action), **`item`**, `why`, **`next_step`**, `owner`, `status` (Open, Closed), `closed_by` (the claim that answers it), `blocking` (true for a Gap whose missing originator holds up a key fact), `claim_ids`, `source_ids` |
| `scope` | **`scope_id`**, **`kind`** (Name, Incident, Out of scope), **`value`**, `note` |
| `software` | **`software_id`**, **`software`**, **`version`**, **`role`**, **`how`**, `cve`, `affected_versions`, `fixed_version`, `advisory_source`, **`claim_ids`** |
| `killchain` | **`stage_id`**, **`order`**, **`stage`**, **`observed`** (Observed, Reported, Not observed), **`tactic`**, `techniques`, `process`, `action`, `logs`, `parent`, `artefacts`, `network`, `detections`, `hunt`, `sourced_fields`, `claim_ids` |

**ID prefixes.** S sources, C claims, A key judgments (ledger rows with topic Key judgment), E events, F figures, V victims, M techniques, H attribution rows, K conflicts, G gaps, W watch items, R actions, N names, I incidents, X out of scope, D changes, P software, Q kill chain stages. Use two digits at least (C01, not C1), so the dashboard and report can link them.

**Incident tags.** `incident` on events, victims, techniques and claims takes the incident's scope ID (I01). The incident's name is also accepted, but the ID is preferred.

**Times.** `when` and `end` take an ISO date, or a date and time. A time may carry its source's offset (`2026-11-04T09:50-05:00`); `add` converts it to UTC (`2026-11-04T14:50Z`), so never convert by hand. A time taken from a live page's update heading is when the update was posted: write the event as "update posted HH:MM", give it a disclosure or notification type, and point `time_line` at the heading line.

**Actions.** In an Action's `next_step`, put the sourced steps first, each with its claim ID in brackets, then "Analyst guidance:" and the rest. A step with no claim ID starts "Analyst guidance:".

**Lanes.** Attacker; Victim and response; Disclosure; Government and law enforcement; Context.

**Event types.** earliest-activity, initial-access, attacker-action, detection, containment, disclosure, notification, public-report, claim, advisory, law-enforcement, remediation, context, other. The response metrics use earliest-activity (or initial-access), detection, containment, disclosure and notification, so give those types wherever they apply.

**What the helper adds when it publishes.** `publish` and `html` add, without changing `tracker.json`: `newest_source_date` on the summary; on each technique its `domain`, its ATT&CK URL and its ATT&CK reference mitigations; an `ir_metrics` collection (dwell time, time to contain, time to disclose and time to notify, each from the earliest event of the two types, left out when either is missing); and a `tactics` collection with the pinned tactic order.

**Summary fields the outputs need.** The dashboard reads `attack`, `status`, `iteration`, `as_of`, `newest_source_date`, `tlp`, `bluf`, `leadership`, `exposure`, `takeaway`, `relevance`, `attribution_statement`, `scope`, `soc_note`, `validation` and `attack_version`. The Word report and executive brief also read `language` and the six `glance_` fields. The STIX bundle reads `actor`, `actor_likelihood` and `actor_confidence` when an actor has been named.

## Examples

Two or three rows per collection are enough to show the shape. These come from the test case in `tests/fixture/rows.json`, where every collection has a full example.

```json
{"sources": [
  {"source_id": "S01", "title": "Notice of a security incident", "publisher": "Harbor Ledger", "date": "2026-10-23",
   "url": "https://example.com/notice", "type": "victim statement", "position": "Primary", "originator": "Harbor Ledger",
   "first_party": "victim", "interest": "victim", "retrieval": "read", "reliability": "B"},
  {"source_id": "S03", "title": "Payments firm hit by appliance flaw", "publisher": "Example Tech News", "date": "2026-10-24",
   "type": "news", "position": "Secondary", "originator": "Harbor Ledger", "relay_of": "S01", "interest": "independent",
   "retrieval": "read", "reliability": "C", "notes": "Relays S01."},
  {"source_id": "S05", "title": "Joint advisory on FerryGate exploitation", "publisher": "National CERT", "date": "2026-10-31",
   "type": "government advisory", "position": "Primary", "originator": "National CERT", "interest": "government",
   "retrieval": "failed", "reliability": "A", "notes": "Page would not load; logged as G02."}],
 "ledger": [
  {"claim_id": "C01", "topic": "Initial access", "claim": "The intruders exploited CVE-2026-41234 in the FerryGate server on 14 October 2026.",
   "quote": "Attackers exploited a vulnerability in our FerryGate file transfer server on 14 October.", "quote_source": "S01", "line": 3,
   "status": "Confirmed", "credibility": 1, "source_ids": "S01 S04",
   "corroboration": "Harbor Ledger (S01); Northlight Research (S04)", "event_date": "2026-10-14", "first_party": true},
  {"claim_id": "C05", "topic": "Impact", "claim": "Harbor Ledger says no payment card data was affected.",
   "quote": "No payment card data was affected.", "quote_source": "S01", "line": 6, "status": "Reported", "credibility": 3,
   "source_ids": "S01", "corroboration": "single originator: Harbor Ledger (S01), a statement that favours the victim",
   "said_by": "Harbor Ledger"},
  {"claim_id": "C14", "topic": "Attribution", "claim": "Crimson Ferry says it acted alone.", "status": "Actor-asserted",
   "credibility": 5, "source_ids": "S04", "corroboration": "actor: Crimson Ferry, via S04"},
  {"claim_id": "A01", "topic": "Key judgment", "claim": "Crimson Ferry is roughly even chance to be responsible for the breach (low confidence), resting on one researcher's attribution and the actor's own leak-site listing.",
   "status": "Assessed", "credibility": 4, "source_ids": "S04", "basis": "C07 C08",
   "contrary": "C14: the actor's own post says it acted alone, which fits but does not prove the attribution"}],
 "timeline": [
  {"event_id": "E02", "when": "2026-10-14", "precision": "day", "lane": "Attacker", "event_type": "initial-access",
   "event": "Intruders exploit CVE-2026-41234 on Harbor Ledger's FerryGate server", "status": "Confirmed", "claim_ids": "C01",
   "disclosed": "2026-10-23"},
  {"event_id": "E03", "when": "2026-10-21T14:05Z", "precision": "exact", "lane": "Victim and response", "event_type": "detection",
   "event": "Harbor Ledger detects unusual activity on the FerryGate server", "status": "Confirmed", "claim_ids": "C02"}],
 "victims": [
  {"victim_id": "V01", "victim": "Harbor Ledger", "role": "compromised party", "sector": "Financial services", "country": "Netherlands",
   "tier": "Confirmed", "impact": "Customer contact details copied", "data_types": ["PII"],
   "count_method": "Victim statement S01, as of 23 October 2026", "claim_ids": "C01 C04"}],
 "ttps": [
  {"ttp_id": "M01", "technique_id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "initial-access",
   "phase": "Initial access", "how_used": "Exploited CVE-2026-41234 on the internet-facing FerryGate server.",
   "occurrence": "Reported", "confidence": "High", "event_ids": "E02", "claim_ids": "C01"},
  {"ttp_id": "M04", "technique_id": "T0831", "name": "Manipulation of Control", "domain": "ics", "tactic": "impact",
   "phase": "Impact", "how_used": "Changed refrigeration set points through the vendor's remote portal.",
   "occurrence": "Reported", "confidence": "Medium", "claim_ids": "C15"}],
 "attribution": [
  {"row_id": "H02", "kind": "Signal", "party": "Leak-site listing", "position": "Crimson Ferry listed the victim on 22 October (C08).",
   "limits": "An actor's own claim, known only through S04.", "claim_ids": "C08"},
  {"row_id": "H07", "kind": "Hypothesis", "party": "Crimson Ferry", "position": "The group named by S04.",
   "likelihood": "roughly even chance", "confidence": "low", "for_signals": "H02 C07", "against_signals": ""},
  {"row_id": "H03", "kind": "Diamond", "party": "Adversary", "position": "Crimson Ferry (named by S04; not confirmed)."}],
 "gaps": [
  {"item_id": "G01", "kind": "Gap", "item": "How many customers were affected", "why": "Sets the notification scale",
   "next_step": "Watch for a regulator filing or an updated notice", "status": "Closed", "closed_by": "C22"},
  {"item_id": "G03", "kind": "Gap", "item": "The Metro Police release named in S03 could not be found", "why": "The arrest date rests on a relay",
   "next_step": "Search the police newsroom for the release title on the next update", "status": "Open", "blocking": true,
   "claim_ids": "C10"},
  {"item_id": "R02", "kind": "Action", "item": "Hunt for the IIS worker spawning a shell", "why": "Matches the execution step",
   "next_step": "Analyst guidance: query EDR process telemetry for w3wp.exe with a cmd.exe or powershell.exe child in the last 30 days",
   "owner": "SOC"}]
}
```

For `software` and `killchain` rows, see `references/soc-handoff.md`.
