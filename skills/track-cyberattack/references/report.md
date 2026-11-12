# Reference D. The Word report and executive brief

Read this at Step 13 only if a build command fails or you need to change the layout.

`scripts/build_report.js` builds `out/<attack>-report.docx` from `tracker.json` and the images in `work/diagrams/`. With `--exec` it builds the executive brief, also in Word. It never writes quotes. Then `tracker_tool.py verify-docx` checks the report. Neither file gets a PDF copy.

```
python3 work/scripts/render_diagrams.py tracker.json work/diagrams
node work/scripts/build_report.js tracker.json work/diagrams out/<attack>-report.docx
node work/scripts/build_report.js tracker.json work/diagrams out/<attack>-exec-brief.docx --exec
python3 work/scripts/tracker_tool.py verify-docx out/<attack>-report.docx --tracker tracker.json --images 4
```

## Layout

US Letter, 1-inch margins, Arial. The TLP mark and attack name are in the header of every page, with page numbers in the footer. Headings follow `summary.language` (English, Spanish, French, German or Portuguese); table headers, ATT&CK names and ICD 203 terms stay in English.

Page one is the leadership page and has no page breaks: title and status line (with the newest source date), **Summary (bottom line)**, **Relevance to us** (only when an org context was given), **For leadership**, **Key judgments** (numbered, each with its basis), **Attack at a glance** (victim, attack type, window, initial access, impact, attribution status, from the `glance_` fields), **Response metrics** (when the timeline holds the events) and **What changed since the last update** (update runs only, the latest iteration's rows).

Every chapter after that starts on a new page, and headings stay with the content under them:

1. **Timeline**: the timeline image, then the events table.
2. **Victims**: victims table with data exposed, then figures with their method notes.
3. **Attack chain and TTPs**: the ATT&CK version line, the attack-chain image, the ATT&CK matrix image (Enterprise and ICS), the technique table with links to attack.mitre.org and the events each technique appears in, then **ATT&CK reference mitigations**, labelled as coming from the knowledge base and not the reporting.
4. **Kill chain for SOC hand-off** (when `software` or `killchain` has rows, or `soc_note` when it was skipped): the software table, the patch-target line or CVE table, then one block per stage with every field.
5. **Attribution**: the statement, competing hypotheses and the consistency matrix (with two or more Hypothesis rows), attribution signals and their limits, the Diamond Model image and table, and who has said what.
6. **Relevance and recommended actions**: the exposure question, actions, indicators to watch, information gaps with their status.
7. **Claims and sources**: where sources disagree, the source register with interest and retrieval (bookmarked), scope and validation status.
8. **Appendix: claims ledger**: every claim, bookmarked by ID.

Every Cxx, Axx and Sxx in the report is an internal link to its bookmark, so the report works without the dashboard.

## Executive brief

One or two pages for leadership, from the same data: page one of the report (without basis links or the change log), then **Top actions** (up to five open Action rows: what, how and owner) and the exposure question. No timeline, ledger, technique or source tables, and IDs are plain text because the brief has no appendix. Hand it over as `out/<attack>-exec-brief.docx`.

## Rules

- Never put Mermaid, Graphviz or any other diagram source into the Word file. `verify-docx` fails on diagram text.
- Images are embedded at natural size or smaller, never enlarged, and kept to about two thirds of a page.
- Without matplotlib, `render_diagrams.py` writes the timeline, matrix and Diamond as SVG. `build_report.js` embeds SVG with a PNG fallback made by rsvg-convert, ImageMagick or Inkscape when one is installed, or a blank fallback otherwise. Word 2016 or later shows the SVG.
- If `build_report.js` fails, read its error and fix the data or the script. If Node or the docx package is missing and a docx skill is available, build the same layout with it. Otherwise say in one line that the Word report was skipped and why.
