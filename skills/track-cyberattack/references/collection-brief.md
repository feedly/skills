# Reference G. The collection subagent brief

Read this at Step 3, and in update mode. Fill the angle-bracket fields and launch one subagent with it. Do not paste the rubrics; the subagent reads them itself.

---

You are collecting sources for an attack tracker on one cyberattack or campaign.

- Attack and scope: <attack name, aliases from the alias table in their original spelling, case type, scope statement, and any incidents in scope>
- Time window: <window>. Newest reporting already held: <summary.newest_source_date, or "none" on a first run>.
- Allowed sources: <web search, Feedly tools, the user's files: list only what the user allowed>
- Page-text tool: <the tool name, such as the built-in browser's `get_page_text` or Claude in Chrome, when the user allowed browser use at Step 1; otherwise "none">
- Leads already held: <the Step 1 entity and look-alike results from the main thread, each with its URL or Feedly ID; the path of any Feedly result saved to disk, such as a `search_threat_intelligence` file; and any link the user gave that was blocked; otherwise "none">
- Skill folder: <path to this skill>. Working directory: <path>. Save files in `work/sources/`.

**0. Save the leads first.** Before you search or fetch anything, turn each lead above into a source. From a saved Feedly file, save each article it holds as its own `Sxx.txt` with `retrieval: read`. Save a main-thread entity or look-alike result with the search or Feedly call it came from as its title line, so any domain, URL or IP it names sits in a saved extract. Never let a lead reach a fact without a saved source behind it.

**Source priority.** Search and fetch in this order. Move down a tier only when the tier above is exhausted or unreachable:

1. **The victim and national authorities.** The victim's own statements, national CERTs and CSIRTs, government cyber security agencies (CISA, NCSC UK, BSI, CERT-FR, ACSC and peers), law enforcement and regulators.
2. **Established CTI vendors and technical vendor reports.** Threat research teams with a public track record (for example Mandiant, Microsoft Threat Intelligence, Palo Alto Unit 42, Cisco Talos, CrowdStrike, ESET, Kaspersky GReAT, Check Point Research, Recorded Future Insikt Group, Sophos X-Ops, SentinelLabs, Proofpoint, Huntress), plus the affected product's vendor advisory and the CVE record.
3. **Cyber news media.** Specialist outlets with their own reporting (for example BleepingComputer, The Record, SecurityWeek, Dark Reading, The Register, CyberScoop, Help Net Security).
4. **High-quality general news media.** Wire services and newspapers of record (for example Reuters, AP, Bloomberg, the Financial Times, the BBC), and local outlets with first-hand access, in the local language.

Treat blogs, aggregators and social media posts as leads only, and chase the originator they name. The tier sets the order of collection, not the grade. Grade every source by Rubrics B1 and B3 in step 4, whatever its tier. With Feedly, apply the same order when you choose which articles to read with `get_article`.

**1. Search.** Use standard search mode first; use extended mode only when standard results are thin. Search for each of these separately, in the source priority order:

- tier 1, the victim's own statements (newsroom, press releases, breach notices, status pages, investor relations);
- tier 1, regulator and law enforcement material: national CERT or CSIRT advisories, government cyber security agencies such as CISA, the UK NCSC and BSI, the FBI and IC3, police and prosecutor releases, and regulatory filings such as an SEC 8-K Item 1.05. For any agency or vendor in `<skill folder>/references/originator-urls.md`, fetch its index page from that table first and open the matching entry; search the agency's own site only if that fails;
- tier 2, technical reports from established CTI vendors on the attack, the actor or the malware, on the vendor's own research blog;
- tier 2, the vendor advisory for any exploited product, and the CVE record;
- tier 3 and then tier 4, only for what tiers 1 and 2 do not cover: the outlet that first reported each claim, and local outlets with first-hand access, in the local language;
- the most recent period explicitly: search for reporting from the last 30 days, and from after the newest reporting already held, so a current date never sits on old reporting;
- for an actor or law enforcement case, every incident the actor claimed or was reported for, so each one can be listed as in or out of scope.

Before you fetch a search result, check the date the result shows. Skip any page dated outside the time window. Skip outlets that only relay a source you already have. Never open a leak site or link to one.

**2. Fetch at most 12 pages, in source priority order.** Spend the first five fetches only on tier 1 and tier 2 originator pages: the victim's newsroom or notice, the agency, CERT or police page, the vendor advisory, and the CTI vendor's own research blog. Spend the rest on any remaining tier 2 reports, then tier 3 cyber news media, then tier 4 general news media, always choosing outlets with first-hand reporting over relays. When a page names an originator you have not read ("according to the police", "the FBI said"), add that originator to your list and try it.

For the five originator pages, use the page-text tool named above when there is one; it returns the page's own text, so save it with `retrieval: read`. For every other page, and for originator pages when there is no page-text tool, give the fetch tool exactly this prompt:

> Return the date, the author, and up to 15 sentences from the article copied exactly, each under 125 characters, that bear on the attack. Copy them; do not reword them.

Save what comes back with `retrieval: excerpts`. If the tool returns a summary instead of copied sentences, save it with `retrieval: summarised` (step 3). Never ask for "the full text of the article"; the fetch tool will not reproduce a whole news article and returns a summary that looks like quotation.

**Spot-check the excerpts.** When a page-text tool is named above, spot-check up to five `excerpts` sources after the originator fetches, starting with the ones that carry the most facts. Read the page with the page-text tool, compare three of its saved lines with the page text, and set `spot_check` to "3/3 matched" (or "2/3 matched" and so on). If any line does not match, change the source's `retrieval` to `summarised` and start every line that did not match with `~ `. Save nothing else from the page-text read. With no page-text tool, set `spot_check` to "not run".

**Blocked pages.** If a page returns a block for legal reasons (SITE_BLOCKED or similar), do not retry it and do not route around it with curl, caches, mirrors or archives. When Feedly is allowed, search for the article with `search_articles` on its exact title and, if Feedly has indexed it, read it with `get_article`. Otherwise save the search snippet with `retrieval: snippet` and list the page in `gaps`.

If an authoritative page will not load for any other reason (a government advisory, the victim's notice, the vendor advisory), try a second route before giving up: its index page in `originator-urls.md`, a search for its exact title, the same document on the publisher's other pages or an official mirror, or coverage that quotes it. If it still cannot be read, register it with `retrieval` "failed" and say why in `notes`. Do not use it to support any fact. When you have only a search snippet, set `retrieval` to "snippet". Never fetch a page twice in this run once it has come back summarised or failed. List a summarised originator page in `tried_originators` with the result "summarised".

Use one more fetch to confirm the current MITRE ATT&CK version: https://attack.mitre.org/resources/versions/ (the row marked current), or https://attack.mitre.org/resources/updates/ if that fails. Return it as `attack_version`, or "not verified" if both fail.

**3. Save each source** as `work/sources/S01.txt`, `work/sources/S02.txt` and so on. The first line holds the title, publisher, date and URL, then `retrieval: read`, `retrieval: excerpts`, `retrieval: summarised`, `retrieval: snippet` or `retrieval: failed`. After that, one sentence per line:

- **read and excerpts:** copy each sentence verbatim. Never rewrite a sentence.
- **summarised:** keep any sentence the tool returned inside quotation marks exactly as given, in double quotes. Start every line the tool reworded with `~ ` (a tilde and a space), so nobody can cite a paraphrase as a quote.

Write the files yourself; do not return them in full.

**Dates.** If a page shows only a weekday or a relative date ("Tuesday 19:56", "two days ago"), take the date from the search result or the URL, and say so in `notes`. If a failed source has no date anywhere, set `date` to "undated". Never guess a date.

While saving, protect people. Replace the name of anyone who is not an official spokesperson or a public figure with their role in square brackets, for example [a store manager] or [the arrested man]. This includes people arrested or charged but not convicted. Never save the name, age, school, town or any other detail that could identify a person under 18.

**4. Grade and tag each source.** Read sections B1 and B3 of `<skill folder>/references/rubrics.md` before you grade. Set `originator` to the one party that first reported the content; put any other names in `notes`. Mark a relay as Secondary and set `relay_of` to the source ID it repeats. A leaked, scraped or reposted copy of someone else's document is Secondary, with the original author as originator. Set `first_party` to "victim" when the victim speaks about itself, "authority" when a government body, regulator or law enforcement agency speaks about its own action, "actor" when the attacker speaks, and "victim-relayed" for a victim statement you know only through an outlet; otherwise leave it empty. Set `interest` to independent, victim, actor, vendor (a vendor with a product interest in the story) or government.

**5. Return only JSON**, in this shape:

```json
{"attack_version": "v20.1",
 "sources": [{"source_id": "S01", "title": "", "publisher": "", "date": "", "url": "", "type": "", "position": "",
              "originator": "", "relay_of": "", "first_party": "", "interest": "", "retrieval": "excerpts", "spot_check": "", "language": "",
              "reliability": "", "notes": ""}],
 "facts": [{"fact": "", "quote": "", "source_id": "S01", "line": 2, "said_by": "", "event_date": "", "first_party": false}],
 "tried_originators": [{"originator": "", "page": "", "result": "read as S03, or why it failed: X post, paywall, 404, bot wall"}],
 "conflicts": [{"topic": "", "positions": [{"source_id": "S01", "position": ""}]}],
 "dated_events": [{"when": "", "what": "", "source_id": "S01", "line": 2}],
 "out_of_scope_context": [{"when": "", "what": "", "source_id": "S01", "line": 2}],
 "gaps": [""]}
```

A fact may say only what its saved line says: no detail from memory, from a summary or from another line. Each `quote` is one sentence copied exactly from the saved file, and `line` is its line number there (line 1 is the title line). Never quote a line that starts with `~`. `said_by` names who made the statement ("Harbor Ledger", "Metro Police", "Reuters" for the outlet's own reporting), because three outlets relaying one spokesperson are one speaker.

List every dated event the sources give, including when the attack was detected, when it was disclosed, when customers were notified, when any advisory came out and any law enforcement action, even if it seems minor; the timeline is built from this list. Give each event's own date, not the date of the article that reports it. A time in a live page's update heading is when the update was posted; say so in `what`.

List in `out_of_scope_context` each incident you meet that falls outside the scope (an earlier wave, a same-week attack no source links), so it can still appear as labelled context.
