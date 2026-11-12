#!/usr/bin/env python3
"""Regression tests for tracker_tool.py, built on a fictional case (Harbor Ledger, FerryGate, Crimson Ferry).

  python3 tests/run_tests.py            run every test in a temporary folder; exit 1 on any failure

Each test starts from tests/fixture/rows.json and the saved extracts in tests/fixture/sources, changes one thing,
and checks what `check`, `diff`, `navigator` or `html` says. Add a test whenever a review finds a rule that
`check` should have caught.
"""
import copy, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
TOOL = os.path.join(SKILL, "scripts", "tracker_tool.py")
ROWS = json.load(open(os.path.join(HERE, "fixture", "rows.json"), encoding="utf-8"))
results = []


def run(*args, cwd):
    r = subprocess.run([sys.executable, TOOL, *args], cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def case(mutate=None):
    """A fresh working folder holding tracker.json built from the fixture, with an optional change applied."""
    d = tempfile.mkdtemp(prefix="tc-test-")
    shutil.copytree(os.path.join(HERE, "fixture", "sources"), os.path.join(d, "work", "sources"))
    rows = copy.deepcopy(ROWS)
    if mutate:
        mutate(rows)
    json.dump(rows, open(os.path.join(d, "rows.json"), "w"), ensure_ascii=False)
    run("init", "tracker.json", "--attack", rows["summary"]["attack"], cwd=d)
    code, out = run("add", "tracker.json", "rows.json", cwd=d)
    assert code == 0, out
    return d


def check(d, path="tracker.json"):
    return run("check", path, cwd=d)[1]


def test(name, ok, detail=""):
    results.append((name, ok, detail))


def row(rows, coll, key, value):
    return next(r for r in rows[coll] if r.get(key) == value)


# 0. the fixture itself is clean
out = check(case())
test("baseline: fixture passes with 0 errors", "0 errors" in out, out[-300:])

# quote verification
test("a paraphrased quote in a summarised file reports NOT CHECKED, not an error",
     "1 NOT CHECKED" in out and "C12" not in "".join(l for l in out.splitlines() if l.startswith("ERROR")), out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "C03").update(line=5)))
test("a quote on the wrong line is an error", "C03: quote is on line 4" in out, out[-300:])

# first-party rules
def actor_confirms(r):
    r["sources"].append({"source_id": "S09", "title": "Crimson Ferry statement", "publisher": "Crimson Ferry", "date": "2026-10-24",
                         "type": "actor statement", "position": "Primary", "originator": "Crimson Ferry", "first_party": "actor",
                         "interest": "actor", "retrieval": "read", "reliability": "F"})
    r["ledger"].append({"claim_id": "C20", "topic": "Impact", "claim": "Crimson Ferry says it took 40 GB of data.", "status": "Confirmed",
                        "credibility": 2, "source_ids": "S09", "corroboration": "first-party: Crimson Ferry", "first_party": True})
out = check(case(actor_confirms))
test("an actor's claim about itself cannot be Confirmed", "C20: an actor speaking about itself cannot confirm" in out, out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "C10").update(
    status="Confirmed", credibility=1, first_party=True, corroboration="first-party: Metro Police (S06)",
    claim="Metro Police arrested a man on 29 October in connection with the intrusion; he is an alleged participant.")))
test("an authority's statement about its own action can be Confirmed alone",
     "C10: Confirmed rests on one originator" not in out and "C10: an actor" not in out, out[-300:])
def relayed_technical(r):
    r["ledger"].append({"claim_id": "C21", "topic": "Initial access", "claim": "Harbor Ledger told reporters a FerryGate flaw was the way in.",
                        "quote": "Harbor Ledger said customer names and email addresses were copied.", "quote_source": "S03", "line": 2,
                        "status": "Confirmed", "credibility": 2, "source_ids": "S03", "corroboration": "first-party (relayed): Harbor Ledger", "first_party": True})
out = check(case(relayed_technical))
test("a relayed victim statement cannot confirm root cause", "C21: a relayed victim statement can confirm only" in out, out[-300:])

# confidence caps
out = check(case(lambda r: row(r, "ledger", "claim_id", "A01").update(
    claim="Crimson Ferry is very likely responsible for the breach (high confidence).")))
test("a judgment resting on one originator is capped at low confidence", "A01: its basis rests on one originator" in out, out[-300:])
def secondary_basis(r):
    row(r, "ledger", "claim_id", "A02").update(basis="C12", source_ids="S08",
        claim="Customer contact details were very likely stolen at scale (high confidence).")
out = check(case(secondary_basis))
test("Reported claims from Secondary sources cap a judgment at likely", "A02: every claim in its basis is Reported from Secondary" in out, out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "C10").update(claim="Metro Police charged a man with the intrusion.")))
test("an allegation needs the word alleged", "C10: put the word 'alleged'" in out, out[-300:])

# diff covers every collection and continues change IDs
d = case()
old = json.load(open(os.path.join(d, "tracker.json")))
old["changes"] = [{"change_id": "D07", "iteration": 1, "kind": "New", "item": "earlier change"}]
json.dump(old, open(os.path.join(d, "tracker.prev.json"), "w"))
upd = {"summary": {"iteration": 2, "status": "Concluded"},
       "sources": [{"source_id": "S10", "title": "Update", "publisher": "Harbor Ledger", "date": "2026-11-04", "type": "victim statement",
                    "position": "Primary", "originator": "Harbor Ledger", "first_party": "victim", "interest": "victim", "retrieval": "read", "reliability": "B"}],
       "ledger": [{"claim_id": "C04", "claim": "The intruders copied the names and email addresses of customers from the server."},
                  {"claim_id": "C22", "topic": "Impact", "claim": "Harbor Ledger says 12,000 customers were affected.", "status": "Reported",
                   "credibility": 2, "source_ids": "S10", "corroboration": "single originator: Harbor Ledger (S10)"}],
       "victims": [{"victim_id": "V02", "victim": "A FerryGate customer in Belgium", "role": "downstream installer", "tier": "Reported",
                    "count_method": "S04, as of 25 October 2026", "claim_ids": "C07"}],
       "ttps": [{"ttp_id": "M04", "technique_id": "T1657", "name": "Financial Theft", "tactic": "impact", "phase": "Post-compromise",
                 "how_used": "No theft reported; placeholder for the test.", "occurrence": "Assessed", "confidence": "Low", "claim_ids": "C04"}],
       "timeline": [{"event_id": "E08", "when": "2026-11-04", "precision": "day", "lane": "Victim and response", "event_type": "notification",
                     "event": "Harbor Ledger notifies affected customers by email", "status": "Reported", "claim_ids": "C22"}],
       "figures": [{"figure_id": "F01", "label": "Customers affected", "value": 12000, "status": "Reported", "claim_id": "C22", "note": "Victim count"}],
       "gaps": [{"item_id": "G01", "status": "Closed", "closed_by": "C22"}]}
json.dump(upd, open(os.path.join(d, "upd.json"), "w"))
run("add", "tracker.json", "upd.json", cwd=d)
code, out = run("diff", "tracker.prev.json", "tracker.json", cwd=d)
ch = json.loads(out)["changes"]
kinds = {(c["kind"], c["item"].split(":")[0]) for c in ch}
want = {("New", "Source S10"), ("New", "Claim C22"), ("New", "Victim V02"), ("New", "Technique T1657 Financial Theft (impact)"),
        ("New", "Event E08 (2026-11-04)"), ("New", "Figure F01"), ("Closed gap", "Gap G01"), ("Revised", "Claim C04 reworded"),
        ("Revised", "Summary status")}
test("diff reports new rows in every collection, rewordings and closed gaps", want <= kinds, f"missing {want - kinds}")
test("change IDs continue from the highest existing ID", ch and ch[0]["change_id"] == "D08", ch[0]["change_id"] if ch else "none")
out = check(d)
test("a closed gap needs closed_by, and a valid one passes", "G01: a Closed gap" not in out, out[-300:])

# stale reporting
out = check(case(lambda r: r["summary"].update(as_of="2027-12-01T00:00:00Z")))
test("a tracker whose newest source is a year old warns", "is 397 days older than as_of" in out, out[-400:])
d = case()
test("newest_source_date ignores reference pages", json.load(open(os.path.join(d, "tracker.json")))["summary"][0]["newest_source_date"] == "2026-10-30")

# timeline date checks
out = check(case(lambda r: row(r, "timeline", "event_id", "E01").update(status="Confirmed")))
test("an event cannot be stronger than its claims", "E01: status Confirmed is stronger" in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E04").update(precision="exact")))
test("exact precision needs a time of day", "E04: precision exact needs a time of day" in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E04").update(when="2026-11-10")))
test("an event dated after every source that reports it warns", "E04: dated 2026-11-10, after every source" in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E07").update(when="2026-10-30")))
test("an event dated on its only source's publication day warns", "E07: its date equals the publication date" in out, out[-300:])

# link schemes
out = check(case(lambda r: row(r, "sources", "source_id", "S02").update(url="javascript:alert(1)")))
test("a javascript: URL is an error", "S02: url must start with http" in out, out[-300:])

# technique rows by ttp_id, set, and migrate
d = case()
json.dump({"ttps": [{"ttp_id": "M01", "incident": "I01"}]}, open(os.path.join(d, "p.json"), "w"))
run("add", "tracker.json", "p.json", cwd=d)
test("patching a technique row by ttp_id adds no stub rows", len(json.load(open(os.path.join(d, "tracker.json")))["ttps"]) == 3)
code, out = run("set", "tracker.json", "ttps", "M02", "confidence", "High", cwd=d)
test("set changes one field", code == 0 and json.load(open(os.path.join(d, "tracker.json")))["ttps"][1]["confidence"] == "High", out)
t = json.load(open(os.path.join(d, "tracker.json")))
for r in t["ttps"]:
    r.pop("ttp_id")
json.dump(t, open(os.path.join(d, "old.json"), "w"))
code, out = run("migrate", "old.json", cwd=d)
test("migrate gives old technique rows a ttp_id", all(r.get("ttp_id") for r in json.load(open(os.path.join(d, "old.json")))["ttps"]), out)

# one originator per source
def two_names(r):
    row(r, "sources", "source_id", "S04").update(originator="Northlight Research; Saltmarsh Analytics")
out = check(case(two_names))
test("a source counts as one originator, and ';' gets a warning", "S04: originator holds several names" in out
     and "Reported but 2 originators" not in out, out[-300:])

# the pinned ATT&CK map, ICS
out = check(case(lambda r: r["ttps"].append({"ttp_id": "M09", "technique_id": "T1999", "name": "Made up", "tactic": "execution", "phase": "x",
                                              "how_used": "x", "occurrence": "Reported", "confidence": "Low", "claim_ids": "C07"})))
test("a made-up technique ID fails", "M09: T1999 is not a technique" in out, out[-300:])
out = check(case(lambda r: r["ttps"].append({"ttp_id": "M09", "technique_id": "T1078", "name": "Valid Accounts", "tactic": "lateral-movement", "phase": "x",
                                              "how_used": "x", "occurrence": "Reported", "confidence": "Low", "claim_ids": "C07"})))
test("T1078 under lateral-movement fails", "M09: T1078 Valid Accounts does not carry tactic lateral-movement" in out, out[-300:])
d = case(lambda r: r["ttps"].append({"ttp_id": "M09", "technique_id": "T0831", "name": "Manipulation of Control", "domain": "ics", "tactic": "impact",
                                     "phase": "Impact", "how_used": "It is unlikely the actor changed set points (low confidence).", "occurrence": "Assessed", "confidence": "Low", "claim_ids": "C07"}))
out = check(d)
code, nav = run("navigator", "tracker.json", "nav.json", cwd=d)
test("an ICS technique passes and gets its own Navigator layer",
     "M09" not in out and os.path.exists(os.path.join(d, "nav-ics.json")), out[-200:] + nav)

# people, presupposition, self-serving statements, data types
out = check(case(lambda r: row(r, "victims", "victim_id", "V01").update(impact="Data of a 15-year-old customer was copied")))
test("detail about a minor warns", "people: possible detail about a person under 18" in out, out[-300:])
out = check(case(lambda r: r["summary"].update(glance_type="Ransomware attack on a file transfer server")))
test("a glance field naming an unsupported attack type warns", "'ransomware' appears" in out, out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "C05").update(status="Confirmed", credibility=2, first_party=True,
                                                                         corroboration="first-party: Harbor Ledger (S01)")))
test("a self-serving victim statement stays Reported", "C05: a victim statement that favours the victim" in out, out[-300:])
out = check(case(lambda r: row(r, "victims", "victim_id", "V01").update(data_types=["PII", "crypto wallets"])))
test("an unknown data type is an error", "V01: data type 'crypto wallets'" in out, out[-300:])
out = check(case(lambda r: row(r, "victims", "victim_id", "V01").update(data_types=["health"])))
test("a data type the claims do not name warns", "V01: data type 'health' does not appear" in out, out[-300:])

# the standalone page and the response metrics
d = case()
code, out = run("html", "tracker.json", "page.html", cwd=d)
page = open(os.path.join(d, "page.html"), encoding="utf-8").read() if code == 0 else ""
test("html writes one page with the data, the template and the runtime",
     'id="tracker-data"' in page and "dash.calc('summary'" in page and "window.dash" in page, out)
run("publish", "tracker.json", "pub", cwd=d)
pub = json.load(open(os.path.join(d, "pub", "tracker-data.json")))
names = [m["metric"] for m in pub["ir_metrics"]]
test("publish computes dwell time, time to contain and time to disclose",
     names == ["Dwell time", "Time to contain", "Time to disclose"], str(names))
test("publish adds ATT&CK reference mitigations", "M1051" in pub["ttps"][0].get("mitigations", ""))

# quotes you can trust
def edit_source(d, sid, fn):
    p = os.path.join(d, "work", "sources", f"{sid}.txt")
    lines = open(p, encoding="utf-8").read().splitlines()
    open(p, "w", encoding="utf-8").write("\n".join(fn(lines)) + "\n")


d = case()
edit_source(d, "S08", lambda ls: [ls[0]] + ["~ " + x for x in ls[1:]] + ["~ The attackers stole the contact details of every customer."])
out = check(d)
test("a quote from a '~' line counts as paraphrase", "of which 1 paraphrase" in out, out[-300:])
d = case(lambda r: row(r, "sources", "source_id", "S04").update(retrieval="excerpts"))
out = check(d)
test("excerpts are a retrieval value and their quotes are checked",
     "0 errors" in out and "3 from excerpts, 0 of those spot-checked" in out, out[-300:])
out = check(case(lambda r: row(r, "sources", "source_id", "S01").update(retrieval="summarised")))
test("Confirmed with no verified source and one originator fails",
     "ERROR C02: Confirmed needs a verified source or two independent originators" in out, out[-300:])
out = check(case(lambda r: r["ledger"].append({"claim_id": "C20", "topic": "Impact", "claim": "The flaw affects FerryGate 9.0 to 9.4.1.",
     "status": "Confirmed", "credibility": 2, "source_ids": "S02 S04", "said_by": "Northlight Research",
     "corroboration": "FerryGate Systems (S02); Northlight Research (S04)"})))
test("a Confirmed claim with one speaker warns", "C20: Confirmed, but every source relays one speaker" in out, out[-300:])
relayed = {"claim_id": "C21", "topic": "Impact", "claim": "Harbor Ledger says customer names and email addresses were copied.",
           "quote": "Harbor Ledger said customer names and email addresses were copied.", "quote_source": "S03", "line": 2,
           "status": "Confirmed", "credibility": 2, "source_ids": "S03", "first_party": True,
           "corroboration": "first-party: Harbor Ledger, relayed by S03"}
out = check(case(lambda r: r["ledger"].append(dict(relayed))))
test("a relayed victim claim needs the victim's words in quotation marks", "line 2 of S03 holds no quotation marks" in out, out[-300:])
d = case(lambda r: r["ledger"].append(dict(relayed)))
edit_source(d, "S03", lambda ls: [ls[0], 'Harbor Ledger said "customer names and email addresses were copied."'])
out = check(d)
test("a quoted relay passes the mechanical test", "C21: Confirmed on a relayed" not in out, out[-300:])
out = check(case(lambda r: (r["ledger"].append(dict(relayed)), row(r, "sources", "source_id", "S03").update(retrieval="summarised"))))
test("a relay that was only summarised cannot confirm", "with a verified source" in out, out[-300:])

# excerpts need a spot-check (or a second originator) before they confirm
out = check(case(lambda r: row(r, "sources", "source_id", "S01").update(retrieval="excerpts")))
test("one originator and one unchecked excerpts source cannot confirm",
     "ERROR C02: Confirmed needs a verified source" in out and "ERROR C11: Confirmed on a first-party statement needs that "
     "statement verified" in out, out[-400:])
out = check(case(lambda r: row(r, "sources", "source_id", "S01").update(retrieval="excerpts", spot_check="3/3 matched")))
test("the same claim passes once its excerpts pass a spot-check",
     "C02: Confirmed" not in out and "C11: Confirmed" not in out and "0 errors" in out, out[-400:])
out = check(case(lambda r: (row(r, "sources", "source_id", "S01").update(retrieval="excerpts"),
                            row(r, "sources", "source_id", "S04").update(retrieval="excerpts"))))
test("two independent excerpts originators confirm without a spot-check", "C01: Confirmed" not in out, out[-400:])
d = case(lambda r: (r["ledger"].append(dict(relayed)), row(r, "sources", "source_id", "S03").update(retrieval="excerpts")))
edit_source(d, "S03", lambda ls: [ls[0], 'Harbor Ledger said "customer names and email addresses were copied."'])
out = check(d)
test("a relayed victim quote from unchecked excerpts fails Rubric B3.5",
     "C21: Confirmed on a relayed victim statement needs quote_source to be the victim-relayed source, with a verified "
     "source" in out, out[-400:])
out = check(case(lambda r: row(r, "sources", "source_id", "S02").update(spot_check="all good")))
test("spot_check on a read source, or in a bad shape, warns",
     "S02: spot_check is set but retrieval is read" in out and "S02: spot_check 'all good' must look like" in out, out[-400:])

# a summary of an originator's own page is a blocking gap
police_relay = {"source_id": "S10", "title": "Arrest made in Harbor Ledger case", "publisher": "Coastal Times",
                "date": "2026-10-30", "type": "news", "position": "Secondary", "originator": "Metro Police",
                "interest": "independent", "retrieval": "read", "reliability": "B", "relay_of": "S06"}
def police_summary(r, gap=False, kj=False):
    row(r, "sources", "source_id", "S06").update(retrieval="summarised")
    r["sources"].append(dict(police_relay))
    if gap:
        r["gaps"].append({"item_id": "G09", "kind": "Gap", "item": "The Metro Police release came back only as a summary",
                          "why": "The arrest details rest on it", "next_step": "Retry on next update", "status": "Open",
                          "blocking": True, "source_ids": "S06", "claim_ids": "C10"})
    if kj:
        r["ledger"].append({"claim_id": "A09", "topic": "Key judgment", "status": "Assessed", "credibility": 3, "basis": "C10",
                            "claim": "It is likely that the arrested man took part in the intrusion (moderate confidence)."})
out = check(case(police_summary))
test("an originator known only from a summary raises the not-read warning",
     "originator 'Metro Police' (named by S10) was read only as a summary (S06)" in out, out[-400:])
out = check(case(lambda r: police_summary(r, gap=True)))
test("the warning goes quiet once a blocking Gap names the originator", "originator 'Metro Police'" not in out, out[-400:])
out = check(case(lambda r: police_summary(r, gap=True, kj=True)))
test("a judgment resting on that blocking gap is capped at low confidence",
     "A09: its basis includes a claim behind a blocking gap" in out, out[-400:])

# audience
out = check(case(lambda r: r["summary"].update(audience="board")))
test("audience: an unknown audience value warns", "summary: audience must be one of" in out, out[-300:])
out = check(case(lambda r: r["summary"].update(audience="soc")))
test("audience: a known audience value passes", "summary: audience" not in out, out[-300:])
out = check(case(lambda r: r["summary"].update(audience="hunt")))
test("audience: hunt passes", "summary: audience" not in out, out[-300:])
out = check(case(lambda r: r["summary"].update(audience="executives")))
test("audience: executives is not an audience value", "summary: audience must be one of" in out, out[-300:])
out = check(case(lambda r: r["summary"].update(audience="cti", audience_team="Fraud")))
test("audience: a typed team in audience_team is accepted", "audience_team" not in out, out[-300:])

# presupposition
out = check(case(lambda r: r["summary"].update(cause_confirmed="false")))
test("cause_confirmed false needs a hedged bottom line", "cause_confirmed is false, so bluf" in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E02").update(claim_ids="C02")))
test("an access event resting only on detection warns", "E02: an initial-access event cites only detection" in out, out[-300:])
out = check(case(lambda r: row(r, "victims", "victim_id", "V01").update(claim_ids="C05", data_types=["none reported"])))
test("'compromised party' needs a claim that the victim was attacked", "V01: role 'compromised party'" in out, out[-300:])
out = check(case(lambda r: row(r, "victims", "victim_id", "V01").update(role="affected party (cause not confirmed)", claim_ids="C05",
                                                                        data_types=["none reported"])))
test("'affected party' needs no attack claim", "V01: role" not in out, out[-300:])
out = check(case(lambda r: (r["scope"].append({"scope_id": "I09", "kind": "Incident", "value": "Look-alike domains"}),
                            r["ledger"].append({"claim_id": "C22", "topic": "Scope", "claim": "No source links the look-alike domains to the breach.",
                                                "status": "Unknown", "credibility": 6, "source_ids": "S04", "incident": "I09"}))))
test("an Incident backed only by Unknown claims warns", "I09: every claim behind this Incident" in out, out[-300:])
neg = "It is unlikely that further FerryGate victims will emerge in the coming weeks (moderate confidence)."
out = check(case(lambda r: row(r, "ledger", "claim_id", "A02").update(claim=neg)))
test("a negative judgment without contrary warns", "A02: a negative judgment" in out, out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "A02").update(claim=neg, contrary="C06: the flaw needs no credentials")))
test("contrary silences it", "A02: a negative judgment" not in out, out[-300:])

# bottom line, roles, judgments, techniques, times and wording
out = check(case(lambda r: row(r, "ttps", "ttp_id", "M02").update(confidence="High")))
test("High on one originator warns", "M02: confidence High needs two or more originators" in out, out[-300:])
out = check(case(lambda r: row(r, "ttps", "ttp_id", "M02").update(occurrence="Assessed")))
test("an Assessed technique needs an ICD 203 term", "M02: an Assessed technique" in out, out[-300:])
d = case(lambda r: r["timeline"].append({"event_id": "E09", "when": "2026-10-21T10:05-04:00", "precision": "exact", "lane": "Victim and response",
                                         "event_type": "other", "event": "Harbor Ledger staff log the alert in the ticket system",
                                         "status": "Confirmed", "claim_ids": "C02"}))
when = next(e["when"] for e in json.load(open(os.path.join(d, "tracker.json")))["timeline"] if e["event_id"] == "E09")
test("add converts an offset time to UTC", when == "2026-10-21T14:05Z", when)
out = check(case(lambda r: row(r, "sources", "source_id", "S02").update(date="undated")))
test("'undated' is only for a failed source", "S02: date 'undated' is only for a failed source" in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E04").update(when="2026-10-22T09:00Z", precision="exact")))
test("an exact time with no time in the cited quotes warns", "E04: precision exact, but no time of day" in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E04").update(when="2026-10-22T09:00Z", precision="exact", time_line="S01:2")))
test("time_line points check at the line with the time", "E04: precision exact" not in out, out[-300:])
out = check(case(lambda r: row(r, "gaps", "item_id", "R01").update(next_step="Search IIS logs for POSTs to unknown .aspx files.")))
test("an Action with no claim ID and no prefix warns", "R01: next_step puts unsourced steps first" in out, out[-300:])
long = ("Customer names and email addresses were copied from the server by the intruders during the week before the "
        "company noticed anything unusual on the file transfer appliance it runs.")
out = check(case(lambda r: row(r, "victims", "victim_id", "V01").update(impact=long)))
test("a sentence over 25 words warns", "victims has 1 row(s) with a sentence over 25 words: V01" in out, out[-300:])
out = check(case(lambda r: r["ledger"].append({"claim_id": "C23", "topic": "Context", "claim": "Northlight suspected attacks on other FerryGate servers that week.",
                                               "status": "Reported", "credibility": 3, "source_ids": "S04", "corroboration": "single originator: Northlight Research (S04)"})))
test("'suspected attacks' with no person does not ask for 'alleged'", "C23: put the word 'alleged'" not in out, out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "C12").update(claim="A news digest says the attackers stole contact details, but the page was not read in full.")))
test("'was not read' is not a 'this is not' construction", "'this is not' construction" not in out, out[-300:])
out = check(case(lambda r: row(r, "ledger", "claim_id", "C13").update(claim="This is not a ransomware case, and no source reports any encryption.")))
test("'this is not' still warns", "'this is not' construction" in out, out[-300:])
out = check(case(lambda r: row(r, "software", "software_id", "P01").update(version="Not reported")))
test("'Not reported' is accepted as a version", "P01: version" not in out, out[-300:])
out = check(case(lambda r: r["timeline"].append({"event_id": "E08", "when": "2026-10-20", "precision": "day", "lane": "Context",
                                                 "event_type": "context", "event": "FerryGate Systems publishes advisory FG-2026-07",
                                                 "status": "Reported", "claim_ids": "C06"})))
test("a Context event skips the report-date warning", "E08: its date equals" not in out, out[-300:])
out = check(case(lambda r: row(r, "timeline", "event_id", "E03").update(event_type="other")))
test("a missing detection event still warns", "no detection event" in out, out[-300:])
out = check(case(lambda r: (row(r, "timeline", "event_id", "E03").update(event_type="other"),
                            r["gaps"].append({"item_id": "G09", "kind": "Gap", "item": "When the victim detected the intrusion",
                                              "why": "Sets dwell time", "next_step": "Watch for an updated notice", "status": "Open"}))))
test("a detection Gap silences it", "no detection event" not in out, out[-300:])
out = check(case(lambda r: row(r, "killchain", "stage_id", "Q01").update(network="Analyst guidance: block evil[.]example[.]net")))
test("a defanged indicator in no saved extract warns", "indicators: 1 defanged value(s)" in out and "evil[.]example[.]net" in out, out[-300:])
d = case(lambda r: row(r, "killchain", "stage_id", "Q01").update(network="Analyst guidance: block evil[.]example[.]net"))
edit_source(d, "S04", lambda ls: ls + ["The web shell beaconed to evil.example.net."])
out = check(d)
test("an indicator found in a saved extract passes", "indicators:" not in out, out[-300:])

# tooling
code, out = run("attack", "valid", "accounts", "--domain", "ics", cwd=HERE)
test("attack looks techniques up in the pinned map", code == 0 and "T0859" in out and "Valid Accounts" in out, out)
d = case()
run("publish", "tracker.json", "pub", cwd=d)
meta = json.load(open(os.path.join(d, "pub", "dash-meta.json")))
index = json.load(open(os.path.join(d, "pub", "dash-index.json")))
test("publish writes the dashboard batch documents",
     meta.get("title", "").endswith("Attack Tracker") and "dash.calc('summary'" in index.get("text", ""), str(meta))

# information, not evidence: attribution Signal rows, old names, loose wording
def old_signal(r):
    a = next(x for x in r["attribution"] if x["kind"] == "Signal")
    a["kind"] = "Evidence"
    a["for_evidence"] = "C07"


d = case(old_signal)
t = json.load(open(os.path.join(d, "tracker.json"), encoding="utf-8"))
sig = [a for a in t["attribution"] if a.get("kind") == "Signal"]
test("add renames an Evidence row to Signal and for_evidence to for_signals",
     sig and sig[0].get("for_signals") == "C07" and "for_evidence" not in sig[0], str(sig[:1]))
t["attribution"][0]["kind"] = "Evidence"
t["attribution"][0]["against_evidence"] = "C08"
json.dump(t, open(os.path.join(d, "tracker.json"), "w"), ensure_ascii=False)
code, out = run("migrate", "tracker.json", cwd=d)
t = json.load(open(os.path.join(d, "tracker.json"), encoding="utf-8"))
test("migrate renames Evidence attribution rows in an existing tracker",
     code == 0 and "renamed from Evidence to Signal" in out and t["attribution"][0]["kind"] == "Signal"
     and t["attribution"][0].get("against_signals") == "C08", out)
out = check(case(lambda r: row(r, "gaps", "item_id", r["gaps"][0]["item_id"]).update(
    why="Every action here is backed by evidence from the vendor.")))
test("'evidence' in our own words warns", "use(s) of 'evidence' in our own words" in out, out[-400:])
out = check(case(lambda r: row(r, "gaps", "item_id", r["gaps"][0]["item_id"]).update(
    why="Harbor Ledger said it found no evidence of data theft; forensic evidence may change that.")))
test("attributed speech and forensic evidence pass", "in our own words" not in out, out[-400:])
tpl = open(os.path.join(SKILL, "assets", "dashboard-index.html"), encoding="utf-8").read()
test("the dashboard template says Claims and sources and Signal, never Evidence as a label",
     "Claims and sources" in tpl and "attr_signals" in tpl and ">Evidence" not in tpl and "'Evidence'" not in tpl.replace("r.kind === 'Evidence'", ""))

failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"\n     {detail}"))
print(f"{len(results) - len(failed)} of {len(results)} passed")
sys.exit(1 if failed else 0)
