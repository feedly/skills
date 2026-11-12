# Reference C. The dashboard

Read this at Step 13, after the files are built.

The dashboard page is a fixed template, `assets/dashboard-index.html`. Never generate dashboard HTML. The template reads one dataset, `tracker`, which is `work/published/tracker-rows.json`: every collection flattened to rows with a `collection` column, quotes removed, plus the rows the helper adds (response metrics, the tactic order, technique URLs and ATT&CK reference mitigations). Everything attack-specific comes from the data, so the same page works for any attack.

## What the template shows

| Tab | Contents |
|---|---|
| Header | Title, status, iteration, as-of date, newest source date (flagged when it is more than 30 days older), TLP, a link to the source conflicts, and the summary (bottom line) |
| Overview | Headline tiles; key judgments; leadership card (leadership, relevance to us when an org context was given, exposure, takeaway); response metrics; what changed in the latest iteration (a first-run note until `changes` has rows); where sources disagree |
| Timeline | Swim-lane chart with an all-dates view and a busiest-day view; full events table. Selecting an event row or a dot opens the event's claims in full, with their status and source links. |
| Victims | Bars by tier; bars by data exposed; figures with method notes; victims table |
| TTPs and attack chain | Chain by phase, and by incident when the campaign has several; ATT&CK matrix view with ICS columns after Enterprise ones; full techniques table with events and ATT&CK reference mitigations. Every technique ID opens its ATT&CK page. Legends list only the values present. |
| Kill chain (SOC) | Software and versions with the patch-target line; the kill chain table with a "Copy table for SOC (tab-separated)" button. Shows `soc_note` instead when the hand-over was skipped; hides when there is neither. |
| Attribution | Statement; attribution signals and their limits; competing hypotheses and the consistency matrix (only with two or more Hypothesis rows); the Diamond Model drawn as a diamond; who has said what |
| Claims and sources | Ledger tiles (the conflicts tile jumps to the conflicts table); source register with interest and retrieval status (links only for http and https URLs); searchable ledger with corroboration and basis; scope; names and incidents |
| Gaps and actions | Actions, watch list, information gaps. Closed gaps stay, greyed, with the claim that closed them; blocking gaps say so. |

Every claim ID (Cxx, Axx) and source ID (Sxx) in any table is a link that opens the Claims and sources tab at that row and highlights it, clearing the ledger search if it hid the row. Every event ID (Exx) opens that event on the Timeline tab. Every table sits in a wrapper that scrolls sideways, so nothing runs past its card on a narrow screen.

## First run (four tool calls)

`ArtifactData` is loaded at Step 0, in the same tool search as the Feedly tools, and `tracker_tool.py publish` has already written the two fixed documents, so no Python turn is needed here.

1. List the Artifact types (`scope: "types"`). If a Dashboard type is listed, create from it with the title `<attack> Attack Tracker` and `auto_open: "after_first_write"`.
2. Upload `work/published/tracker-rows.json` once as an asset on the new dashboard (`Artifact` publish with `asset: true`).
3. In one `ArtifactData` batch, write three documents:
   - `dash/meta`: the contents of `work/published/dash-meta.json` (`{title}`).
   - `datasets/tracker`: inline, because it needs the asset URL: `{title: "<attack> attack tracker", description: "<one sentence>. Analyst-graded by the track-cyberattack skill from public reporting, so it is a file, not a live query", source: {kind: "file", url: "<asset url as returned>", name: "tracker-rows.json", format: "json"}, updated: {at, by: "track-cyberattack, iteration N"}, schedule: "Updates on each re-run of the tracker in update mode", staleAfterHours: 168}`.
   - `files/index.html`: the contents of `work/published/dash-index.json` (`{text: <assets/dashboard-index.html, unchanged>}`).
4. Read `data/users/me` doc `check` once, straight after the batch. A document without `failed` means it passed. If no document comes back, the type writes it after the page first loads, so make the second read in the Step 14 hand-over turn, in parallel with `Artifact` open and `SendUserFile`, and report the result there. Only when the second read also finds nothing, treat it as a pass and say in the hand-over that the check result was not available.

Do not read the Dashboard type's reference files, and do not edit the template, unless `check` reports `failed`. Then read only the file the failure points to, fix the template copy, and write it once more. Report any template fix in the hand-over, so the user can apply it to their own copy of the skill.

## Update runs

Upload the new `tracker-rows.json`, then make one pinned `update` of `datasets/tracker` that changes `source.url`, `source.name` and `updated`. Never rewrite `files/index.html`, unless `migrate` renamed attribution rows: then write the current template once, so the new tabs, labels and columns appear, and say so in the hand-over. The change log shows the latest iteration's rows by itself.

## The standalone HTML page

`python3 work/scripts/tracker_tool.py html tracker.json out/<attack>-dashboard.html` writes one self-contained page: the same template, the same published rows embedded as JSON, and `assets/standalone-runtime.js`, which supplies the design tokens (light and dark), the Dashboard runtime calls the template makes, and a small stand-in for D3 when the copy from cdnjs cannot load. The page opens offline in any browser, on a team wiki or an intranet, and shows the same tabs. It carries the TLP mark at the top and offers the rows as a JSON download. It stores nothing and fetches nothing except, when online, D3 itself.

Use it:

- **when there is no Artifact tool or no Dashboard type** (Claude Code on another provider, ChatGPT, a local model): send the page as the dashboard;
- **for TLP:AMBER+STRICT or TLP:RED material**: never publish a dashboard; send the page as a file;
- **on request** in any run, for publishing outside claude.ai. Offer it in one line in the hand-over.

Say in one line which of these applied. Never build a dashboard page from scratch: a model-built page loses the layout, the links and the labels.

Do not render or browse the dashboard to check it; the type's `check` document is the check. For the standalone page, `tests/run_tests.py` covers the build.
