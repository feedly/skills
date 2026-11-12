#!/usr/bin/env python3
"""track-cyberattack helper. Standard library only (stix2 is used for an extra check if installed).

  preflight                                  check the build tools and print one fix command
  init      tracker.json --attack NAME       create an empty attack tracker
  add       tracker.json ROWS.json           validate rows and merge them into the tracker (safe write)
  set       tracker.json COLL ID FIELD VALUE change one field of one row (ID '-' for summary)
  migrate   tracker.json                     bring an older tracker up to the current schema
  check     tracker.json [--sources DIR]     validate references, labels, dates, quotes and writing rules
  attack    KEYWORD... [--domain ics]        look techniques up in the pinned ATT&CK map (IDs, names, tactics)
  publish   tracker.json OUTDIR              write tracker-data.json, tracker-rows.json (no quotes) and the
                                             dashboard batch documents dash-meta.json and dash-index.json
  html      tracker.json OUT.html            write the dashboard as one standalone page that opens offline
  diff      old.json new.json                print 'changes' rows for an update run
  stix      tracker.json OUT.json            write and validate the STIX 2.1 bundle
  navigator tracker.json OUT.json            write one ATT&CK Navigator layer per domain
  verify-docx REPORT.docx --tracker tracker.json [--images N]
                                             confirm the report has its images, bookmarks and no diagram code

check validates references, labels, formats and the rules below. It does not verify that a claim is supported
by its source; the Step 12 audit does that.
"""
import json, os, re, shutil, subprocess, sys, tempfile, uuid, zipfile, importlib.util
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- schema
FIELDS = {
    "summary": ["attack", "status", "mode", "case_type", "iteration", "created", "as_of", "newest_source_date",
                "tlp", "language", "feedly_id", "attack_version", "bluf", "leadership", "exposure", "takeaway",
                "org_context", "relevance", "scope", "attribution_statement", "actor", "actor_likelihood",
                "actor_confidence", "glance_victim", "glance_type", "glance_window", "glance_access",
                "glance_impact", "glance_attribution", "soc_note", "validation", "cause_confirmed", "audience",
                "audience_team"],
    "changes": ["change_id", "iteration", "kind", "item", "before", "after", "claim_ids"],
    "headlines": ["metric", "label", "kind", "from_event", "from_field", "to_event", "to_field", "figure_id", "unit"],
    "sources": ["source_id", "title", "publisher", "date", "url", "type", "position", "originator", "relay_of",
                "first_party", "interest", "retrieval", "spot_check", "language", "reliability", "notes"],
    "ledger": ["claim_id", "topic", "claim", "quote", "quote_source", "line", "status", "credibility", "source_ids",
               "corroboration", "event_date", "first_party", "superseded_by", "basis", "incident", "said_by",
               "contrary"],
    "timeline": ["event_id", "when", "end", "precision", "lane", "event_type", "event", "status", "claim_ids",
                 "disclosed", "incident", "time_line"],
    "figures": ["figure_id", "label", "value", "unit", "status", "claim_id", "note"],
    "victims": ["victim_id", "victim", "role", "sector", "country", "tier", "impact", "data_types", "count_method",
                "claim_ids", "incident"],
    "ttps": ["ttp_id", "technique_id", "name", "domain", "tactic", "phase", "incident", "how_used", "occurrence",
             "confidence", "event_ids", "claim_ids", "check"],
    "attribution": ["row_id", "kind", "party", "position", "likelihood", "confidence", "for_signals",
                    "against_signals", "limits", "claim_ids"],
    "conflicts": ["conflict_id", "topic", "position_a", "position_b", "resolution", "claim_ids"],
    "gaps": ["item_id", "kind", "item", "why", "next_step", "owner", "status", "closed_by", "blocking", "claim_ids",
             "source_ids"],
    "scope": ["scope_id", "kind", "value", "note"],
    "software": ["software_id", "software", "version", "role", "how", "cve", "affected_versions", "fixed_version",
                 "advisory_source", "claim_ids"],
    "killchain": ["stage_id", "order", "stage", "observed", "tactic", "techniques", "process", "action", "logs",
                  "parent", "artefacts", "network", "detections", "hunt", "sourced_fields", "claim_ids"],
}
COLLECTIONS = list(FIELDS)
KEYS = {"changes": ("change_id",), "headlines": ("metric",), "sources": ("source_id",), "ledger": ("claim_id",),
        "timeline": ("event_id",), "figures": ("figure_id",), "victims": ("victim_id",), "ttps": ("ttp_id",),
        "attribution": ("row_id",), "conflicts": ("conflict_id",), "gaps": ("item_id",), "scope": ("scope_id",),
        "software": ("software_id",), "killchain": ("stage_id",)}
REQUIRED = {
    "sources": ["source_id", "title", "publisher", "date", "type", "position", "originator", "reliability", "retrieval"],
    "ledger": ["claim_id", "topic", "claim", "status", "credibility", "source_ids"],
    "timeline": ["event_id", "when", "precision", "lane", "event_type", "event", "status", "claim_ids"],
    "figures": ["figure_id", "label", "value", "status", "claim_id"],
    "victims": ["victim_id", "victim", "role", "tier", "count_method", "claim_ids"],
    "ttps": ["ttp_id", "technique_id", "name", "tactic", "phase", "how_used", "occurrence", "confidence", "claim_ids"],
    "attribution": ["row_id", "kind", "party", "position"],
    "conflicts": ["conflict_id", "topic", "position_a", "position_b", "resolution", "claim_ids"],
    "gaps": ["item_id", "kind", "item", "next_step"],
    "scope": ["scope_id", "kind", "value"],
    "software": ["software_id", "software", "version", "role", "how", "claim_ids"],
    "killchain": ["stage_id", "order", "stage", "observed", "tactic"],
    "headlines": ["metric", "label", "kind"],
    "changes": ["change_id", "kind", "item"],
}
SUMMARY_REQUIRED = ["attack", "status", "iteration", "as_of", "tlp", "attack_version", "bluf", "leadership",
                    "exposure", "takeaway", "scope", "attribution_statement"]
QUICK_SUMMARY_REQUIRED = ["attack", "status", "as_of", "bluf"]
PRIVATE = {"quote", "quote_source", "line"}
ID_FIELDS = {"claim_ids", "source_ids", "basis", "superseded_by", "relay_of", "sourced_fields", "event_ids",
             "closed_by"}
LIST_FIELDS = {"data_types"}

CLAIM_STATUS = {"Confirmed", "Reported", "Actor-asserted", "Assessed", "Superseded", "Unknown"}
STATUS_RANK = {"Confirmed": 4, "Reported": 3, "Actor-asserted": 2, "Assessed": 2, "Unknown": 1, "Superseded": 0}
TIERS = {"Confirmed", "Claimed", "Reported", "Assessed", "Unknown"}
OCCURRENCE = {"Observed", "Reported", "Capability", "Assessed"}
TTP_CONF = {"High", "Medium", "Low"}
POSITION = {"Primary", "Secondary"}
RELIABILITY = set("ABCDEF")
RETRIEVAL = {"read", "excerpts", "summarised", "snippet", "failed"}
VERBATIM = {"read", "excerpts"}
SPOT_CHECK = re.compile(r"^(\d+)/(\d+) matched$")
AUDIENCES = {"cti", "soc", "hunt", "leadership"}


def verified(src):
    """A source is verified when it was read in full, or its excerpts passed a spot-check against the live page."""
    r = s((src or {}).get("retrieval"))
    if r == "read":
        return True
    m = SPOT_CHECK.match(s((src or {}).get("spot_check")))
    return r == "excerpts" and bool(m) and m.group(1) == m.group(2) and int(m.group(1)) > 0
SRC_FIRST_PARTY = {"", "victim", "victim-relayed", "authority", "actor"}
CONFIRMING_PARTIES = {"victim", "authority"}
INTEREST = {"independent", "victim", "actor", "vendor", "government"}
DATA_TYPES = {"pii": "PII", "credentials": "credentials", "payment": "payment", "health": "health",
              "intellectual property": "intellectual property", "ot or engineering data": "OT or engineering data",
              "none reported": "none reported"}
DATA_TYPE_WORDS = {
    "PII": r"personal|pii|name|address|e-?mail|phone|social security|date of birth|passport|identit|employee data|customer data",
    "credentials": r"credential|password|token|key|secret|login|session|cookie|hash",
    "payment": r"payment|card|bank|iban|account number|financial|billing",
    "health": r"health|medical|patient|clinical|prescription|insurance claim",
    "intellectual property": r"source code|intellectual property|proprietary|design|blueprint|trade secret|research",
    "OT or engineering data": r"engineering|\bot\b|scada|plc|ics|drawing|schematic|control system|configuration",
    "none reported": r".",
}
CASE_TYPES = {"incident", "campaign", "actor", "law-enforcement"}
GAP_STATUS = {"Open", "Closed"}
LANES = {"Attacker", "Victim and response", "Disclosure", "Government and law enforcement", "Context"}
PRECISION = {"exact", "approx", "day", "month"}
EVENT_TYPES = {"earliest-activity", "initial-access", "attacker-action", "detection", "containment", "disclosure",
               "notification", "public-report", "claim", "advisory", "law-enforcement", "remediation", "context",
               "other"}
REPORT_DATE_TYPES = {"disclosure", "public-report", "advisory", "claim"}
ATTR_KINDS = {"Statement", "Hypothesis", "Signal", "Diamond"}
# The tracker produces information, not evidence (evidence is chain-of-custody DFIR material), so the old
# "Evidence" names for attribution signals are mapped to the current ones on add and migrate.
LEGACY_ATTR_FIELDS = {"for_evidence": "for_signals", "against_evidence": "against_signals"}
LEGACY_ATTR_KINDS = {"Evidence": "Signal"}
# "evidence" in our own words, outside attributed speech. Quotes and reported statements may keep the source's word.
LOOSE_EVIDENCE = re.compile(r"\bevidence\b", re.I)
SPEECH = re.compile(r"\b(says?|said|stat(es|ed)|report(s|ed)|told|found|claim(s|ed)|according to|announced|wrote)\b",
                    re.I)
EVIDENCE_OK = re.compile(r"\bforensic evidence\b|\bproof of exploit\b", re.I)
DIAMOND = {"Adversary", "Capability", "Infrastructure", "Victim"}
GAP_KINDS = {"Gap", "Watch", "Action"}
SCOPE_KINDS = {"Name", "Incident", "Out of scope"}
CHANGE_KINDS = {"New", "Revised", "Superseded", "Closed gap", "Removed"}
HEADLINE_KINDS = {"span_days", "span_hours", "span_minutes", "figure"}
KC_OBSERVED = {"Observed", "Reported", "Not observed"}
KC_FREE = {"stage_id", "order", "stage", "observed", "tactic", "techniques", "sourced_fields", "claim_ids"}
TLP = {"TLP:CLEAR", "TLP:GREEN", "TLP:AMBER", "TLP:AMBER+STRICT", "TLP:RED"}
ICD_TERMS = ["almost no chance", "very unlikely", "unlikely", "roughly even chance", "likely", "very likely",
             "almost certain"]
ICD = r"\b(almost no chance|very unlikely|unlikely|roughly even chance|very likely|likely|almost certain(ly)?)\b"
CONF_LEVELS = {"low", "moderate", "high"}
CONF_RANK = {"low": 0, "moderate": 1, "high": 2}
UNSOURCED_PREFIXES = ("Analyst guidance:", "Not available in provided reports", "N/A (no host stage)")
GENERIC_EVENT = re.compile(r"^(event|activity|update|incident|attack|report(ed)?|disclosure|detection|"
                           r"claim|advisory|notification|response)\b[\w\s]{0,12}$", re.I)
UNDEFANGED = re.compile(r"\bhttps?://|\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
NOT_X = re.compile(r"\b(this|it)\s+(is|was)\s+not\b|\bis not [^.;,]{1,40}, (it|this|that) is\b|"
                   r"\b(is|was|are|were) not (?!only\b)[^.;,]{1,40},? but\b", re.I)
CAVEAT = re.compile(r"\bnot\s+(been\s+)?(independently\s+)?(verified|confirmed)\b|\bunverified\b", re.I)
CVE = re.compile(r"^CVE-\d{4}-\d{4,}$")
TIME_OF_DAY = re.compile(r"\b\d{1,2}[:.h]\d{2}\b|\b\d{1,2}\s?(am|pm|a\.m\.|p\.m\.)\b|\b(UTC|GMT|CET|CEST|EST|EDT|PST|"
                         r"PDT|BST)\b|\bmidnight\b|\bnoon\b", re.I)
MINOR = re.compile(r"\b(1[0-7]|[1-9])[- ]years?[- ]old\b|\b(aged?|age of) (1[0-7]|[1-9])\b|\bteen(age(r|d)?)?s?\b|"
                   r"\bjuvenile\b|\ba minor\b|\bminors\b|\bschool ?(boy|girl|pupil|student)s?\b|\bpupils?\b", re.I)
PERSON = re.compile(r"\b(a|an|the|one|two|three|four|five|several|\d+)\s+(\w+\s+)?suspects?\b|\bsuspects? (was|were|is|are|has|have)\b|"
                    r"\b(arrested|detained|charged|indicted|defendants?|men|women|man|woman|teenagers?|"
                    r"individuals?|person|people|nationals?|citizens?)\b", re.I)
ALLEGATION = re.compile(r"\b(charged|accused|suspect(s|ed)?|indicted|on suspicion|allegedly|alleged)\b", re.I)
CONVICTION = re.compile(r"\b(convicted|pleaded guilty|pled guilty|found guilty|sentenced)\b", re.I)
SELF_SERVING = re.compile(r"\bno (evidence|indication|sign)s?\b|\bno (customer|client|personal|sensitive|payment|user|"
                          r"patient|financial)\b|\bnot (been )?(affected|impacted|compromised|accessed)\b|"
                          r"\bunaffected\b|\b(limited|contained|isolated|confined) to\b|\bfully (restored|contained)\b",
                          re.I)
TECHNICAL_TOPIC = re.compile(r"initial access|root cause|technique|ttp|attribution|malware|vulnerab|cve|exploit|"
                             r"infrastructure|tooling|payload", re.I)
ABSENCE = re.compile(r"\b(absence|no evidence|no reporting|not (been )?reported|no source|not disclosed|has not been|no report)",
                     re.I)
HEDGE = re.compile(r"\b(suspect(ed)?|reported(ly)?|alleged(ly)?|claimed|possible|possibly|apparent(ly)?|"
                   r"unconfirmed|not (yet )?confirmed)\b", re.I)
KJ_NEGATIVE = re.compile(r"\brather than\b|\bunlikely\b|\balmost no chance\b|\bno (evidence|indication|sign|"
                         r"confirmed|link|connection|compromise)\b|\bnot (been )?(linked|connected|confirmed|compromised)\b",
                         re.I)
ACCESS_VERB = re.compile(r"\b(access(ed)?|broke|breach(ed)?|gain(ed)?|exploit(ed)?|enter(ed)?|intru(ded|sion)|"
                         r"compromis(e|ed)|infiltrat)", re.I)
ATTACKED = re.compile(r"\b(attack(ed)?|cyber-?attack|breach(ed)?|compromis(e|ed)|hack(ed|ing)?|intrusion|ransomware|"
                      r"unauthori[sz]ed (access|activity)|malicious)", re.I)
PATHWAY = re.compile(r"\b(pathway|route|vector|through|via|supplier|vendor|provider|third[- ]party|contractor|"
                     r"integrator|managed service)\b", re.I)
DEFANGED = re.compile(r"\b[\w-]+(?:\[\.\][\w-]+)+(?:/[^\s,;)]*)?|hxxps?\[?:\]?//[^\s,;)]+|\b\d{1,3}(?:\[\.\]\d{1,3}){3}\b")
MACHINE_SOURCE = re.compile(r"machine|extracted|feedly (record|entity|tag)|entity tag|cyber ?attack record", re.I)
LONG_SKIP = {"url", "quote", "quote_source", "title", "hunt", "detections", "logs", "artefacts", "network", "process",
             "parent", "techniques", "sourced_fields", "claim_ids", "source_ids", "basis", "event_ids", "relay_of",
             "superseded_by", "closed_by", "corroboration", "as_of", "created", "when", "end"}
PRESUPPOSED = ["ransomware", "wiper", "exfiltrat", "encrypt", "phishing", "zero-day", "supply chain", "insider",
               "extortion"]

TLP_DEFS = {
    "TLP:CLEAR": ("94868c89-83c2-464b-929b-a1a8aa3c8487", "clear"),
    "TLP:GREEN": ("bab4a63c-aed9-4cf5-a766-dfca5abac2bb", "green"),
    "TLP:AMBER": ("55d920b0-5e8b-4f79-9ee9-91f868d9b421", "amber"),
    "TLP:AMBER+STRICT": ("939a9414-2ddd-4d32-a0cd-375ea402b003", "amber+strict"),
    "TLP:RED": ("e828b379-4e03-4974-9ac4-e53a884c97c1", "red"),
}
TLP_EXT = "extension-definition--60a3c5c5-0d10-413e-aab3-9e08dde9e88d"
STIX_NS = uuid.UUID("4b7c8f0e-2d6a-5b1e-9c3f-7a1d2e8b6c40")
ICD_TO_STIX = {"almost no chance": 5, "very unlikely": 15, "unlikely": 30, "roughly even chance": 50,
               "likely": 70, "very likely": 85, "almost certain": 95}


# ---------------------------------------------------------------- the pinned ATT&CK map
def _load_attack():
    p = os.path.join(HERE, "attack_v20.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


ATTACK = _load_attack()
_FALLBACK_TACTICS = ["reconnaissance", "resource-development", "initial-access", "execution", "persistence",
                     "privilege-escalation", "stealth", "defense-impairment", "credential-access", "discovery",
                     "lateral-movement", "collection", "command-and-control", "exfiltration", "impact"]
TACTICS = (ATTACK["enterprise"]["tactic_order"] if ATTACK else _FALLBACK_TACTICS) + ["unmapped"]
ICS_TACTICS = (ATTACK["ics"]["tactic_order"] if ATTACK else []) + ["unmapped"]
DOMAIN_TACTICS = {"enterprise": TACTICS, "ics": ICS_TACTICS}
ALL_TACTICS = list(dict.fromkeys(TACTICS + ICS_TACTICS))
PINNED_VERSION = ATTACK["attack_version"] if ATTACK else "v20.0"


def ttp_domain(r):
    d = s(r.get("domain")).lower()
    if d:
        return d
    return "ics" if re.fullmatch(r"T0\d{3}(\.\d{3})?", s(r.get("technique_id"))) else "enterprise"


def attack_tech(domain, tid):
    if not ATTACK or domain not in ("enterprise", "ics"):
        return None
    return ATTACK[domain]["techniques"].get(tid)


def attack_url(tid):
    return "https://attack.mitre.org/techniques/" + tid.replace(".", "/") + "/"


def mitigations_for(domain, tid):
    """ATT&CK reference mitigations for a technique: [(id, name)]. Sub-techniques inherit none of their own extras."""
    t = attack_tech(domain, tid)
    if not t:
        return []
    names = ATTACK[domain]["mitigations"]
    return [(m, names.get(m, "")) for m in t.get("mitigations", [])]


# ---------------------------------------------------------------- helpers
def s(v):
    """Field value as a stripped string."""
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else ""
    if isinstance(v, list):
        return " ".join(str(x) for x in v).strip()
    return str(v).strip()


def ids(v):
    return s(v).replace(",", " ").split()


def truthy(v):
    return s(v).lower() in ("true", "yes", "1")


def norm(text):
    """Fold smart punctuation, whitespace and case so quote matching ignores typography."""
    text = (text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2013", "-").replace("\u2014", "-").replace("\u00a0", " "))
    return re.sub(r"\s+", " ", text).strip().lower()


def iso(v):
    v = s(v)
    if re.fullmatch(r"\d{4}-\d{2}", v):
        v += "-01"
    d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    return d.astimezone(timezone.utc).replace(tzinfo=None) if d.tzinfo else d


def day(v):
    try:
        return iso(v).date()
    except (ValueError, TypeError):
        return None


def split_list(v):
    if isinstance(v, list):
        return [s(x) for x in v if s(x)]
    return [x.strip() for x in re.split(r"[;,]", s(v)) if x.strip()]


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR {path} is not valid JSON: {e.msg} at line {e.lineno}, column {e.colno}. "
                 f"Fix that file; nothing was changed.")
    except FileNotFoundError:
        sys.exit(f"ERROR {path} not found")


def save(path, data):
    """Atomic write with a one-step backup, so a failed write can never corrupt the tracker."""
    text = json.dumps(data, indent=1, ensure_ascii=False)
    json.loads(text)
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tracker-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    if os.path.exists(path):
        shutil.copyfile(path, path + ".bak")
    os.replace(tmp, path)


def summary_row(t):
    rows = t.get("summary") or [{}]
    return rows[0] if isinstance(rows, list) else rows


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_reference(src):
    return "reference" in s(src.get("type")).lower()


def newest_source_date(t):
    """Newest publication date among sources that report on the incident (reference pages and failed reads excluded)."""
    best = None
    for x in t.get("sources", []):
        if s(x.get("retrieval")) == "failed" or is_reference(x):
            continue
        d = day(x.get("date"))
        if d and (best is None or d > best):
            best = d
    return best.isoformat() if best else ""


def next_id(rows, field, prefix):
    n = 0
    for r in rows:
        m = re.fullmatch(prefix + r"(\d+)", s(r.get(field)))
        if m:
            n = max(n, int(m.group(1)))
    return n


def legacy_attr(r):
    """Rename old attribution fields and kinds in one row; return True if anything changed."""
    changed = False
    for old, new in LEGACY_ATTR_FIELDS.items():
        if old in r:
            if not s(r.get(new)):
                r[new] = r[old]
            del r[old]
            changed = True
    if s(r.get("kind")) in LEGACY_ATTR_KINDS:
        r["kind"] = LEGACY_ATTR_KINDS[s(r.get("kind"))]
        changed = True
    return changed


def migrate_rows(t):
    """Upgrade an older tracker to the current schema: give technique rows a stable ttp_id and open gaps a status."""
    notes = []
    ttps = t.get("ttps") or []
    n = next_id(ttps, "ttp_id", "M")
    for r in ttps:
        if not s(r.get("ttp_id")):
            n += 1
            r["ttp_id"] = f"M{n:02d}"
            notes.append(f"ttps: {s(r.get('technique_id'))} ({s(r.get('phase'))}) is now {r['ttp_id']}")
    for a in t.get("attribution") or []:
        if isinstance(a, dict) and legacy_attr(a):
            notes.append(f"attribution: {s(a.get('row_id'))} renamed from Evidence to Signal")
    for g in t.get("gaps") or []:
        if s(g.get("kind")) == "Gap" and not s(g.get("status")):
            g["status"] = "Open"
    for name in FIELDS:
        t.setdefault(name, [] if name != "summary" else [{}])
    return notes


# ---------------------------------------------------------------- init / add / set / migrate
def cmd_init(path, attack, force=False):
    if os.path.exists(path) and not force:
        sys.exit(f"ERROR {path} exists. Use it, or pass --force to start over.")
    t = {c: [] for c in COLLECTIONS}
    ts = now_iso()
    t["summary"] = [{"attack": attack, "status": "Active", "mode": "full", "case_type": "incident", "iteration": 1,
                     "created": ts, "as_of": ts, "tlp": "TLP:CLEAR", "language": "en"}]
    save(path, t)
    print(f"created {path} for '{attack}'")


def _rowkey(name, row):
    return tuple(s(row.get(k)) for k in KEYS[name])


def utc_when(v):
    """Convert a timestamp with an offset ('2026-11-04T09:50-05:00') to UTC ('2026-11-04T14:50Z'); leave others alone."""
    v = s(v)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?[+-]\d{2}:?\d{2}", v):
        return v
    if re.search(r"[+-]\d{4}$", v):
        v = v[:-2] + ":" + v[-2:]
    d = datetime.fromisoformat(v).astimezone(timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%SZ" if d.second else "%Y-%m-%dT%H:%MZ")


def _normalise_row(r, name=None):
    if name == "timeline":
        for k in ("when", "end"):
            if k in r:
                try:
                    r[k] = utc_when(r[k])
                except ValueError:
                    pass
    for k in list(r):
        if k in ID_FIELDS and isinstance(r[k], list):
            r[k] = " ".join(str(x) for x in r[k])
        if k in LIST_FIELDS and isinstance(r[k], list):
            r[k] = "; ".join(str(x) for x in r[k])


def _after_write(t):
    """Fields the helper keeps for the analyst, so nobody types them."""
    nd = newest_source_date(t)
    if nd:
        summary_row(t)["newest_source_date"] = nd


def cmd_add(path, rows_path, replace=False):
    t = load(path)
    incoming = load(rows_path)
    if isinstance(incoming, dict) and "collection" in incoming:
        incoming = {incoming["collection"]: incoming.get("rows", [])}
    if not isinstance(incoming, dict):
        sys.exit('ERROR rows file must be {"collection": NAME, "rows": [...]} or {NAME: [...], ...}')
    problems, counts = [], {}
    for name, rows in incoming.items():
        if name not in FIELDS:
            problems.append(f"unknown collection '{name}'. Allowed: {', '.join(COLLECTIONS)}")
            continue
        if name == "summary" and isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            problems.append(f"{name}: rows must be a list")
            continue
        for i, r in enumerate(rows):
            if not isinstance(r, dict):
                problems.append(f"{name}[{i}]: each row must be an object")
                continue
            if name == "attribution":
                legacy_attr(r)
            bad = [k for k in r if k not in FIELDS[name]]
            if bad:
                problems.append(f"{name}[{i}]: unknown field(s) {', '.join(bad)}. Allowed: {', '.join(FIELDS[name])}")
            _normalise_row(r, name)
            if name != "summary" and not all(s(r.get(k)) for k in KEYS[name]):
                hint = " (technique rows are keyed by ttp_id, prefix M)" if name == "ttps" else ""
                problems.append(f"{name}[{i}]: missing key field {', '.join(KEYS[name])}{hint}")
    if problems:
        for p in problems:
            print("ERROR", p)
        sys.exit(f"{len(problems)} problem(s); nothing was changed.")
    notes = migrate_rows(t)
    for name, rows in incoming.items():
        if name == "summary":
            rows = [rows] if isinstance(rows, dict) else rows
            cur = summary_row(t)
            for r in rows:
                cur.update(r)
            t["summary"] = [cur]
            counts[name] = len(rows)
            continue
        t.setdefault(name, [])
        index = {_rowkey(name, r): i for i, r in enumerate(t[name])}
        for r in rows:
            k = _rowkey(name, r)
            if k in index and not replace:
                t[name][index[k]].update(r)
            elif k in index:
                t[name][index[k]] = r
            else:
                index[k] = len(t[name])
                t[name].append(r)
        counts[name] = len(rows)
    _after_write(t)
    save(path, t)
    for n in notes:
        print("MIGRATED", n)
    print("merged " + ", ".join(f"{n} {c}" for n, c in counts.items()) + f" into {path}")


def cmd_set(path, coll, rid, field, value):
    t = load(path)
    if coll not in FIELDS:
        sys.exit(f"ERROR unknown collection '{coll}'. Allowed: {', '.join(COLLECTIONS)}")
    if field not in FIELDS[coll]:
        sys.exit(f"ERROR unknown field '{field}' for {coll}. Allowed: {', '.join(FIELDS[coll])}")
    if field in KEYS.get(coll, ()):
        sys.exit("ERROR the ID field cannot be changed; IDs are stable across runs")
    migrate_rows(t)
    if coll == "summary":
        row = summary_row(t)
        t["summary"] = [row]
    else:
        row = next((r for r in t.get(coll, []) if s(r.get(KEYS[coll][0])) == rid), None)
        if row is None:
            sys.exit(f"ERROR {coll} has no row {rid}; use add to create it")
    old = row.get(field)
    row[field] = value
    _normalise_row(row, coll)
    _after_write(t)
    save(path, t)
    print(f"set {coll} {rid if coll != 'summary' else ''} {field}: '{s(old)[:60]}' -> '{s(value)[:60]}'".replace("  ", " "))


def cmd_migrate(path):
    t = load(path)
    notes = migrate_rows(t)
    _after_write(t)
    save(path, t)
    for n in notes:
        print("MIGRATED", n)
    print(f"{path} is on the current schema ({len(notes)} row(s) migrated)")


# ---------------------------------------------------------------- check
def originators(srcs, sid, seen=None):
    """The originator of a source, following relay_of to the first reporter. One source has one originator."""
    seen = seen or set()
    src = srcs.get(sid)
    if not src or sid in seen:
        return {sid}
    seen.add(sid)
    if s(src.get("relay_of")):
        out = set()
        for r in ids(src.get("relay_of")):
            out |= originators(srcs, r, seen)
        return out
    return {(s(src.get("originator")) or sid).lower()}


def first_parties(srcs, sid, seen=None):
    """First-party labels reachable from a source, following relays (a relay of a victim notice is victim-relayed)."""
    seen = seen or set()
    src = srcs.get(sid)
    if not src or sid in seen:
        return set()
    seen.add(sid)
    out = {s(src.get("first_party"))} - {""}
    for r in ids(src.get("relay_of")):
        for fp in first_parties(srcs, r, seen):
            # a relay of the victim or an authority can no longer confirm alone; a relay of the actor stays the actor
            out.add({"victim": "victim-relayed", "authority": "authority-relayed"}.get(fp, fp))
    return out


def _same_party(a, b):
    a, b = a.lower().strip(), b.lower().strip()
    return bool(a and b) and (a in b or b in a)


def read_saved(src_dir, sid):
    p = os.path.join(src_dir, f"{sid}.txt")
    if not os.path.exists(p):
        return p, None
    with open(p, encoding="utf-8", errors="ignore") as fh:
        return p, fh.read().splitlines()


def is_summarised(src, lines):
    head = (lines[0] if lines else "").lower()
    return s(src.get("retrieval")) == "summarised" or bool(re.search(r"retrieval:\s*\"?summari[sz]ed", head))


def judgment_parts(text):
    m = re.search(ICD, text, re.I)
    term = m.group(1).lower() if m else ""
    if term == "almost certainly":
        term = "almost certain"
    c = re.search(r"\b(low|moderate|high) confidence\b", text, re.I)
    return term, (c.group(1).lower() if c else "")


def check(t, src_dir=None):
    err, warn, info = [], [], []
    summ = summary_row(t)
    quick = s(summ.get("mode")).lower() == "quick"
    for c in COLLECTIONS:
        if c not in t:
            (warn if quick or c in ("changes", "headlines", "software", "killchain") else err).append(
                f"missing collection {c} (an empty list is fine)")
    for f in (QUICK_SUMMARY_REQUIRED if quick else SUMMARY_REQUIRED):
        if not s(summ.get(f)):
            err.append(f"summary: {f} is empty")
    if not quick and not s(summ.get("validation")):
        warn.append("summary: validation is empty (fill it after the audit)")
    if s(summ.get("tlp")) and s(summ.get("tlp")) not in TLP:
        err.append(f"summary: tlp '{summ.get('tlp')}' must be one of {', '.join(sorted(TLP))}")
    if s(summ.get("case_type")) and s(summ.get("case_type")) not in CASE_TYPES:
        err.append(f"summary: case_type must be one of {', '.join(sorted(CASE_TYPES))}")
    av = s(summ.get("attack_version"))
    if av and "not verified" in av.lower():
        warn.append("summary: attack_version was not verified at run time; say so in the validation status")
    if av and ATTACK:
        major = re.search(r"v?(\d+)", av)
        if major and major.group(1) != re.search(r"v?(\d+)", PINNED_VERSION).group(1):
            warn.append(f"summary: attack_version {av} differs from the bundled map ({PINNED_VERSION}); replace "
                        f"scripts/attack_v20.json with the current version's map before trusting the technique check")
    if s(summ.get("org_context")) and not s(summ.get("relevance")):
        warn.append("summary: org_context is set but relevance is empty")
    if s(summ.get("audience")) and s(summ.get("audience")).lower() not in AUDIENCES:
        warn.append(f"summary: audience must be one of {', '.join(sorted(AUDIENCES))}, or empty")

    for name, req in REQUIRED.items():
        if quick and name not in ("sources", "ledger", "gaps"):
            continue
        for row in t.get(name, []):
            rid = next((s(row.get(k)) for k in KEYS.get(name, ()) if s(row.get(k))), "?")
            if name == "ttps" and rid == "?":
                rid = s(row.get("technique_id")) or "?"
            missing = [f for f in req if not s(row.get(f))]
            if missing:
                hint = " (run migrate to give old technique rows a ttp_id)" if "ttp_id" in missing else ""
                err.append(f"{name} {rid}: empty required field(s) {', '.join(missing)}{hint}")

    srcs = {s(x.get("source_id")): x for x in t.get("sources", [])}
    claims = {s(c.get("claim_id")): c for c in t.get("ledger", [])}
    events = {s(e.get("event_id")): e for e in t.get("timeline", [])}
    gaps = t.get("gaps", [])
    gap_text = " ".join(" ".join(s(v) for v in g.values()) for g in gaps)
    blocking_text = " ".join(" ".join(s(v) for v in g.values()) for g in gaps if truthy(g.get("blocking")))
    saved = {}
    if src_dir and os.path.isdir(src_dir):
        for sid in srcs:
            saved[sid] = read_saved(src_dir, sid)

    # newest reporting behind the date on the tracker
    nd = newest_source_date(t)
    if nd and s(summ.get("newest_source_date")) != nd:
        warn.append(f"summary: newest_source_date should be {nd}; run any add or set to refresh it")
    if nd and s(summ.get("as_of")):
        try:
            lag = (iso(summ.get("as_of")).date() - day(nd)).days
            if lag > 30:
                warn.append(f"summary: the newest incident reporting ({nd}) is {lag} days older than as_of. Search the "
                            f"most recent period explicitly, and say in the BLUF how old the reporting is.")
        except (ValueError, TypeError):
            pass

    # sources
    no_interest = []
    for sid, x in srcs.items():
        if s(x.get("position")) and s(x.get("position")) not in POSITION:
            err.append(f"{sid}: position must be Primary or Secondary")
        if s(x.get("reliability")) and s(x.get("reliability")) not in RELIABILITY:
            err.append(f"{sid}: reliability must be A to F")
        if s(x.get("retrieval")) and s(x.get("retrieval")) not in RETRIEVAL:
            err.append(f"{sid}: retrieval must be read, excerpts, summarised, snippet or failed")
        sc = s(x.get("spot_check"))
        if sc and s(x.get("retrieval")) != "excerpts":
            warn.append(f"{sid}: spot_check is set but retrieval is {s(x.get('retrieval')) or 'empty'}; only an excerpts "
                        f"source is spot-checked")
        if sc and sc != "not run" and not SPOT_CHECK.match(sc):
            warn.append(f"{sid}: spot_check '{sc}' must look like '3/3 matched', '2/3 matched' or 'not run'")
        dt = s(x.get("date"))
        if dt.lower() == "undated":
            if s(x.get("retrieval")) != "failed":
                warn.append(f"{sid}: date 'undated' is only for a failed source; take the date from the search result "
                            f"or the URL and say so in notes")
        elif dt and not day(dt):
            warn.append(f"{sid}: date '{dt}' is not an ISO date (YYYY-MM-DD, or YYYY-MM)")
        if s(x.get("first_party")) not in SRC_FIRST_PARTY:
            err.append(f"{sid}: first_party must be victim, victim-relayed, authority, actor or empty")
        if s(x.get("interest")) and s(x.get("interest")) not in INTEREST:
            err.append(f"{sid}: interest must be one of {', '.join(sorted(INTEREST))}")
        if not s(x.get("interest")):
            no_interest.append(sid)
        url = s(x.get("url"))
        if url and not re.match(r"^https?://", url, re.I):
            err.append(f"{sid}: url must start with http:// or https:// (got '{url[:40]}')")
        if ";" in s(x.get("originator")):
            warn.append(f"{sid}: originator holds several names; keep one originator and put the others in notes")
        for r in ids(x.get("relay_of")):
            if r not in srcs:
                err.append(f"{sid}: relay_of unknown source {r}")
        if s(x.get("relay_of")) and s(x.get("position")) == "Primary":
            err.append(f"{sid}: a source that relays another is Secondary, not Primary")
        pub, org = s(x.get("publisher")), s(x.get("originator"))
        if s(x.get("position")) == "Primary" and pub and org and not _same_party(pub, org):
            warn.append(f"{sid}: Primary but the originator ({org}) is not the publisher ({pub}). A republished, "
                        f"leaked or relayed copy is Secondary.")
        if s(x.get("first_party")) == "victim-relayed" and s(x.get("position")) == "Primary":
            err.append(f"{sid}: a victim statement known only through another outlet is Secondary")
        if s(x.get("retrieval")) == "failed" and sid not in gap_text:
            err.append(f"{sid}: retrieval failed; log it as a Gap row (source_ids {sid}) with 'retry on next update'")
    if no_interest and srcs:
        warn.append(f"sources: interest is empty for {' '.join(no_interest[:10])}{' ...' if len(no_interest) > 10 else ''} "
                    f"(independent, victim, actor, vendor or government)")
    if len(srcs) >= 4 and len({s(x.get("reliability")) for x in srcs.values()}) == 1:
        warn.append("sources: every source has the same reliability grade; grade each source on its own record")

    # named originators that nobody read (the police release, the FBI alert, the victim's own notice)
    read_parties = [s(x.get(f)) for x in srcs.values() if s(x.get("retrieval")) in ("read", "excerpts")
                    and not s(x.get("relay_of")) for f in ("publisher", "originator")]
    summary_only = {sid: x for sid, x in srcs.items() if s(x.get("retrieval")) == "summarised"
                    and not s(x.get("relay_of"))}
    unread = {}
    for sid, x in srcs.items():
        org = s(x.get("originator"))
        if not org or _same_party(org, s(x.get("publisher"))):
            continue
        if any(_same_party(org, p) for p in read_parties):
            continue
        unread.setdefault(org, []).append(sid)
    for org, via in unread.items():
        if org.lower() in blocking_text.lower():
            continue
        summ_ids = [sid for sid, x in summary_only.items()
                    if any(_same_party(org, s(x.get(f))) for f in ("publisher", "originator"))]
        if summ_ids:
            warn.append(f"originator '{org}' (named by {' '.join(via)}) was read only as a summary "
                        f"({' '.join(summ_ids)}). Do not re-fetch it in this run; add a Gap row with blocking true naming "
                        f"'{org}', cap any key judgment resting on it at low confidence, and retry it on the next update.")
            continue
        warn.append(f"originator '{org}' (named by {' '.join(via)}) was not read. Run one targeted search for the "
                    f"exact title on its own domain, then fetch it; if that fails, add a Gap row with blocking true "
                    f"and cap any key judgment resting on it at low confidence.")

    # ledger
    creds, quote_ok, quote_nc, no_line, unbacked, paraphrase = set(), 0, 0, [], [], []
    for cid, c in claims.items():
        st = s(c.get("status"))
        text = s(c.get("claim"))
        if st not in CLAIM_STATUS:
            err.append(f"{cid}: status '{st}' must be one of {', '.join(sorted(CLAIM_STATUS))}")
        cr = s(c.get("credibility"))
        if cr not in {"1", "2", "3", "4", "5", "6"}:
            err.append(f"{cid}: credibility must be 1 to 6")
        creds.add(cr)
        cited = ids(c.get("source_ids"))
        for sid in cited:
            if sid not in srcs:
                err.append(f"{cid}: unknown source {sid}")
            elif s(srcs[sid].get("retrieval")) == "failed":
                err.append(f"{cid}: cites {sid}, which could not be read; a failed source cannot support a claim")
        for r in ids(c.get("basis")) + ids(c.get("superseded_by")):
            if r not in claims:
                err.append(f"{cid}: refers to unknown claim {r}")
        if st == "Superseded" and not s(c.get("superseded_by")):
            err.append(f"{cid}: Superseded without superseded_by")
        if st in ("Confirmed", "Reported", "Actor-asserted") and not s(c.get("corroboration")):
            err.append(f"{cid}: {st} needs corroboration (name the independent originators, or 'first-party: <who>', "
                       f"or 'single originator: <who>', or 'actor: <who>')")
        if st == "Assessed" and not s(c.get("basis")):
            err.append(f"{cid}: Assessed needs basis (the claim IDs it rests on)")
        if s(c.get("topic")) == "Key judgment":
            if not cid.startswith("A"):
                warn.append(f"{cid}: key judgments use the A prefix")
            if not re.search(ICD, text, re.I):
                err.append(f"{cid}: key judgment has no ICD 203 likelihood term")
            if not re.search(r"\b(low|moderate|high) confidence\b", text, re.I):
                err.append(f"{cid}: key judgment has no confidence level")
            if KJ_NEGATIVE.search(text) and not s(c.get("contrary")):
                warn.append(f"{cid}: a negative judgment ('{KJ_NEGATIVE.search(text).group(0).strip()}') needs contrary: "
                            f"the claim IDs and one line on the strongest contrary signal (QA3)")
        for r in re.findall(r"\b[CA]\d{2,}\b", s(c.get("contrary"))):
            if r not in claims:
                err.append(f"{cid}: contrary cites unknown claim {r}")
        claim_fp = truthy(c.get("first_party"))
        origins, fps = set(), set()
        for sid in cited:
            origins |= originators(srcs, sid)
            fps |= first_parties(srcs, sid)
        n_err = len(err)
        any_verified = any(verified(srcs.get(x)) for x in cited)
        if st == "Confirmed" and len(origins) < 2:
            if claim_fp and fps & CONFIRMING_PARTIES:
                if any_verified and not any(verified(srcs.get(x)) and s(srcs.get(x, {}).get("first_party")) in
                                            CONFIRMING_PARTIES for x in cited):
                    err.append(f"{cid}: Confirmed on a first-party statement needs that statement verified (read, or "
                               f"excerpts with a passing spot-check) (Rubric B3.6). Relabel Reported.")
            elif claim_fp and "victim-relayed" in fps:
                qsrc = srcs.get(s(c.get("quote_source")), {})
                if not s(c.get("quote")):
                    err.append(f"{cid}: Confirmed on a relayed victim statement needs the victim's verbatim words "
                               f"in quote (Rubric B3.5)")
                elif "victim-relayed" not in first_parties(srcs, s(c.get("quote_source"))) or not verified(qsrc):
                    err.append(f"{cid}: Confirmed on a relayed victim statement needs quote_source to be the "
                               f"victim-relayed source, with a verified source (read, or excerpts with a passing "
                               f"spot-check) (Rubric B3.5)")
                elif src_dir and s(c.get("line")).isdigit():
                    _, qlines = read_saved(src_dir, s(c.get("quote_source")))
                    n = int(s(c.get("line")))
                    if qlines and 1 <= n <= len(qlines) and not re.search(r"[\"\u201c\u201d\u00ab\u00bb\u201e]", qlines[n - 1]):
                        err.append(f"{cid}: Confirmed on a relayed victim statement, but line {n} of "
                                   f"{s(c.get('quote_source'))} holds no quotation marks; the victim's own words must be "
                                   f"quoted (Rubric B3.5)")
                if TECHNICAL_TOPIC.search(s(c.get("topic")) + " " + text):
                    err.append(f"{cid}: a relayed victim statement can confirm only the victim's own actions, never "
                               f"root cause, techniques or attribution; relabel Reported")
            elif "actor" in fps:
                err.append(f"{cid}: an actor speaking about itself cannot confirm a claim; label it Actor-asserted")
            else:
                err.append(f"{cid}: Confirmed rests on one originator ({', '.join(sorted(origins)) or 'none'}). Relabel "
                           f"Reported, or set first_party if the victim or an authority said it about its own actions.")
        if claim_fp and not fps:
            warn.append(f"{cid}: first_party is set but no cited source is marked first_party")
        if st == "Actor-asserted" and "actor" not in fps:
            warn.append(f"{cid}: Actor-asserted but no cited source is marked first_party actor")
        if st == "Reported" and len(origins) >= 2 and not s(c.get("corroboration")).lower().startswith("single originator:"):
            warn.append(f"{cid}: Reported but {len(origins)} originators support it; if they are independent, "
                        f"upgrade to Confirmed (or start corroboration with 'single originator:' to record your decision)")
        if st == "Confirmed" and cited and not any_verified and len(origins) < 2 and len(err) == n_err:
            err.append(f"{cid}: Confirmed needs a verified source or two independent originators (Rubric B3.6). "
                       f"Relabel Reported.")
        speakers = [x.strip() for x in s(c.get("said_by")).split(";") if x.strip()]
        if st == "Confirmed" and len(speakers) == 1 and not (claim_fp and fps & CONFIRMING_PARTIES) and \
                not (claim_fp and "victim-relayed" in fps):
            warn.append(f"{cid}: Confirmed, but every source relays one speaker ({speakers[0]}); count speakers, not "
                        f"outlets (Rubric B3.3). Relabel Reported unless that speaker is first-party and read.")
        if st == "Confirmed" and cr in {"3", "4", "5", "6"}:
            warn.append(f"{cid}: Confirmed with credibility {cr}; Confirmed claims are usually 1 or 2")
        if st == "Confirmed" and len(origins) < 2 and fps <= {"victim", "victim-relayed"} and SELF_SERVING.search(text):
            warn.append(f"{cid}: a victim statement that favours the victim ('{SELF_SERVING.search(text).group(0)}') "
                        f"stays Reported until an independent originator supports it (Rubric B3.7)")
        if ALLEGATION.search(text) and PERSON.search(text) and not CONVICTION.search(text):
            if st == "Confirmed":
                warn.append(f"{cid}: an allegation made before a conviction is recorded as Reported, never Confirmed")
            if not re.search(r"\balleg", text, re.I):
                warn.append(f"{cid}: put the word 'alleged' in a claim about a suspect who has not been convicted")
        # quotes and saved lines
        q, qs, ln = s(c.get("quote")), s(c.get("quote_source")), s(c.get("line"))
        if q and qs and qs not in cited:
            warn.append(f"{cid}: quote_source {qs} is not among its source_ids")
        if st in ("Confirmed", "Reported", "Actor-asserted") and not q and not ln and src_dir:
            unbacked.append(cid)
        if q and src_dir:
            p, lines = saved.get(qs, (os.path.join(src_dir, f"{qs}.txt"), None)) if qs in saved else read_saved(src_dir, qs)
            if lines is None:
                warn.append(f"{cid}: no saved text {p}")
            elif any(norm(q) in norm(l) for l in lines if l.lstrip().startswith("~")):
                quote_nc += 1
                paraphrase.append(cid)
                if st == "Confirmed":
                    warn.append(f"{cid}: its quote comes from a '~' line, which is the fetch tool's paraphrase "
                                f"(NOT CHECKED); it cannot support Confirmed")
            elif is_summarised(srcs.get(qs, {}), lines):
                quote_nc += 1
            else:
                hits = [i + 1 for i, l in enumerate(lines) if norm(q) in norm(l)]
                whole = norm(q) in norm("\n".join(lines))
                if ln:
                    try:
                        want = int(ln)
                    except ValueError:
                        err.append(f"{cid}: line must be a whole number")
                        continue
                    if want in hits:
                        quote_ok += 1
                    elif hits:
                        err.append(f"{cid}: quote is on line {hits[0]} of {p}, not line {want}")
                    elif whole:
                        err.append(f"{cid}: quote spans lines in {p}; save one sentence per line and cite that line")
                    else:
                        err.append(f"{cid}: quote not found verbatim in {p}")
                elif hits or whole:
                    quote_ok += 1
                    no_line.append(cid)
                else:
                    err.append(f"{cid}: quote not found verbatim in {p}")
        elif ln and src_dir and qs:
            p, lines = read_saved(src_dir, qs)
            try:
                if lines is not None and not (1 <= int(ln) <= len(lines)):
                    err.append(f"{cid}: line {ln} is past the end of {p}")
            except ValueError:
                err.append(f"{cid}: line must be a whole number")
    if len(claims) >= 6 and len(creds) == 1:
        warn.append("ledger: every claim has the same credibility; grade each claim on its corroboration")
    if src_dir:
        exc = [c for c in claims.values() if s(c.get("quote")) and
               s(srcs.get(s(c.get("quote_source")), {}).get("retrieval")) == "excerpts"]
        n_exc = len(exc)
        n_spot = sum(1 for c in exc if verified(srcs.get(s(c.get("quote_source")))))
        info.append(f"quotes: {quote_ok} verified ({n_exc} from excerpts, {n_spot} of those spot-checked), "
                    f"{quote_nc} NOT CHECKED "
                    f"(summarised retrieval{', of which ' + str(len(paraphrase)) + ' paraphrase' if paraphrase else ''})"
                    + (f", {len(no_line)} without a line number" if no_line else "")
                    + ". Put this count in summary.validation.")
        if quote_nc:
            warn.append(f"quotes: {quote_nc} quote(s) come from summarised retrieval and were NOT CHECKED; say so in "
                        f"summary.validation")
        if no_line:
            warn.append(f"quotes: {len(no_line)} quote(s) have no line field ({' '.join(no_line[:8])}); a fact may say "
                        f"only what its saved line says")
        if unbacked:
            warn.append(f"ledger: {len(unbacked)} sourced claim(s) have no saved extract (quote and line): "
                        f"{' '.join(unbacked[:10])}{' ...' if len(unbacked) > 10 else ''}")

    # key judgments: confidence caps (Rubric B6)
    blocking_claims = set()
    for g in gaps:
        if truthy(g.get("blocking")) and s(g.get("status")) != "Closed":
            blocking_claims |= set(ids(g.get("claim_ids")))
    for cid, c in claims.items():
        if s(c.get("topic")) != "Key judgment":
            continue
        text = s(c.get("claim"))
        term, conf = judgment_parts(text)
        basis = [claims[b] for b in ids(c.get("basis")) if b in claims]
        if not basis or not term:
            continue
        strength = abs(ICD_TERMS.index(term) - 3) if term in ICD_TERMS else 0
        origins, all_secondary = set(), True
        for b in basis:
            for sid in ids(b.get("source_ids")):
                origins |= originators(srcs, sid)
                if s(srcs.get(sid, {}).get("position")) != "Secondary":
                    all_secondary = False
        if all(s(b.get("status")) == "Reported" for b in basis) and all_secondary and (strength > 1 or conf == "high"):
            warn.append(f"{cid}: every claim in its basis is Reported from Secondary sources, so the judgment is capped "
                        f"at 'likely' (or 'unlikely') with moderate confidence (Rubric B6)")
        if len(origins) == 1 and CONF_RANK.get(conf, 0) > 0:
            warn.append(f"{cid}: its basis rests on one originator ({next(iter(origins))}), so confidence is capped at low")
        if all(s(b.get("status")) == "Unknown" for b in basis):
            if CONF_RANK.get(conf, 0) > 0:
                warn.append(f"{cid}: a judgment resting only on the absence of reporting is capped at low confidence")
            if not ABSENCE.search(text):
                warn.append(f"{cid}: say in the judgment that it rests on the absence of reporting")
        if blocking_claims & set(ids(c.get("basis"))) and CONF_RANK.get(conf, 0) > 0:
            warn.append(f"{cid}: its basis includes a claim behind a blocking gap, so confidence is capped at low")

    # references from other collections
    for name in ("timeline", "victims", "ttps", "attribution", "conflicts", "changes", "gaps", "software", "killchain"):
        for row in t.get(name, []):
            for cid in ids(row.get("claim_ids")):
                if cid not in claims:
                    err.append(f"{name}: unknown claim {cid}")
    for g in gaps:
        for sid in ids(g.get("source_ids")):
            if sid not in srcs:
                err.append(f"gaps {g.get('item_id')}: unknown source {sid}")
    for f in t.get("figures", []):
        if s(f.get("claim_id")) not in claims:
            err.append(f"figure {f.get('figure_id')}: unknown claim {f.get('claim_id')}")
    for h in t.get("headlines", []):
        if s(h.get("kind")) not in HEADLINE_KINDS:
            err.append(f"headline {h.get('metric')}: kind must be one of {', '.join(sorted(HEADLINE_KINDS))}")
        for k in ("from_event", "to_event"):
            if s(h.get(k)) and s(h.get(k)) not in events:
                err.append(f"headline {h.get('metric')}: unknown event {h.get(k)}")

    # timeline
    cited_on_timeline, types = set(), set()
    for eid, e in events.items():
        start = None
        try:
            start = iso(e.get("when"))
            if s(e.get("end")) and iso(e.get("end")) < start:
                err.append(f"{eid}: end before start")
        except ValueError:
            err.append(f"{eid}: bad date {e.get('when')}")
        if s(e.get("lane")) not in LANES:
            err.append(f"{eid}: lane must be one of {', '.join(sorted(LANES))}")
        prec = s(e.get("precision"))
        if prec and prec not in PRECISION:
            err.append(f"{eid}: precision must be exact, approx, day or month")
        if s(e.get("event_type")) and s(e.get("event_type")) not in EVENT_TYPES:
            err.append(f"{eid}: event_type must be one of {', '.join(sorted(EVENT_TYPES))}")
        st = s(e.get("status"))
        if st not in CLAIM_STATUS:
            err.append(f"{eid}: status must be a claim status")
        ev = s(e.get("event"))
        if ev and (len(ev.split()) < 4 or GENERIC_EVENT.match(ev)):
            warn.append(f"{eid}: event text '{ev}' is too generic; say who did what")
        types.add(s(e.get("event_type")))
        tl = s(e.get("time_line"))
        if tl and (not re.fullmatch(r"S\d{2,}:\d+", tl) or tl.split(":")[0] not in srcs):
            err.append(f"{eid}: time_line '{tl}' must be a known source and line, such as S01:19")
        ecl = [cl for cl in ids(e.get("claim_ids")) if cl in claims]
        cited_on_timeline |= set(ecl)
        if s(e.get("event_type")) in ("initial-access", "earliest-activity") and ecl:
            ev_texts = [s(claims[cl].get("quote")) or s(claims[cl].get("claim")) for cl in ecl]
            if all(re.search(r"\bdetect", x, re.I) and not ACCESS_VERB.search(x) for x in ev_texts):
                warn.append(f"{eid}: an {s(e.get('event_type'))} event cites only detection; a detection date is never "
                            f"an access date. Leave access undated ('access start undisclosed') unless a source dates it.")
        # status no stronger than the strongest claim
        if ecl and st in STATUS_RANK and st != "Superseded":
            best = max(STATUS_RANK.get(s(claims[cl].get("status")), 0) for cl in ecl)
            if STATUS_RANK[st] > best:
                err.append(f"{eid}: status {st} is stronger than its strongest claim; an event takes the status of "
                           f"the claims behind it")
        # dates against the sources that report the event
        esrc = sorted({sid for cl in ecl for sid in ids(claims[cl].get("source_ids")) if sid in srcs})
        pubs = [day(srcs[x].get("date")) for x in esrc]
        if start and pubs and all(pubs):
            if start.date() > max(pubs):
                warn.append(f"{eid}: dated {start.date()}, after every source that reports it was published "
                            f"(newest {max(pubs)}); check the date")
            if len(esrc) == 1 and start.date() == pubs[0] and s(e.get("event_type")) not in REPORT_DATE_TYPES \
                    and s(e.get("lane")) != "Context":
                warn.append(f"{eid}: its date equals the publication date of its only source ({esrc[0]}); make sure it "
                            f"is the event date, not the report date")
        if prec == "exact":
            if "T" not in s(e.get("when")):
                err.append(f"{eid}: precision exact needs a time of day in when; use day if the source gives only a date")
            else:
                evidence = " ".join(s(claims[cl].get("quote")) for cl in ecl)
                if src_dir:
                    evidence += " " + " ".join((saved.get(x, (None, None))[1] or [""])[0] for x in esrc)
                    tl = s(e.get("time_line"))
                    if tl:
                        tsid, _, tln = tl.partition(":")
                        tlines = (saved.get(tsid) or read_saved(src_dir, tsid))[1]
                        if tlines and tln.isdigit() and 1 <= int(tln) <= len(tlines):
                            evidence += " " + tlines[int(tln) - 1]
                if not TIME_OF_DAY.search(evidence):
                    warn.append(f"{eid}: precision exact, but no time of day appears in its claims' quotes or its "
                                f"sources' first lines; use day or approx unless a source gives the time")
    if not quick and claims:
        orphan = [cid for cid, c in claims.items() if s(c.get("event_date")) and s(c.get("status")) != "Superseded"
                  and s(c.get("topic")) != "Key judgment" and cid not in cited_on_timeline]
        if orphan:
            warn.append(f"timeline: {len(orphan)} dated claim(s) are not on the timeline: {' '.join(orphan[:12])}"
                        f"{' ...' if len(orphan) > 12 else ''}. Add an event, or clear event_date if it is not an event.")
        for need in ("detection", "disclosure"):
            if need == "detection" and re.search(r"detect", " ".join(s(g.get("item")) for g in gaps
                                                                    if s(g.get("kind")) == "Gap"), re.I):
                continue
            if t.get("timeline") and need not in types:
                warn.append(f"timeline: no {need} event; add one if any source gives it, or log a Gap")

    # victims, ttps, incidents
    incidents = set()
    for r in t.get("scope", []):
        if s(r.get("kind")) == "Incident":
            incidents |= {s(r.get("value")), s(r.get("scope_id"))}
    for v in t.get("victims", []):
        vid = s(v.get("victim_id"))
        if s(v.get("tier")) not in TIERS:
            err.append(f"{vid}: tier must be one of {', '.join(sorted(TIERS))}")
        role = s(v.get("role")).lower()
        vclaims = [claims[c] for c in ids(v.get("claim_ids")) if c in claims]
        vsourced = " ".join(s(c.get("claim")) + " " + s(c.get("quote")) for c in vclaims
                            if s(c.get("status")) in ("Confirmed", "Reported"))
        if "compromised" in role and not ATTACKED.search(vsourced):
            warn.append(f"{vid}: role 'compromised party' needs a cited claim in which the victim or an authority says "
                        f"it was attacked; use 'affected party (cause not confirmed)' until then")
        if "pathway" in role and not PATHWAY.search(vsourced):
            warn.append(f"{vid}: role 'possible pathway' needs a cited claim that names the pathway")
        dts = split_list(v.get("data_types"))
        vtext = " ".join(s(claims.get(c, {}).get("claim")) + " " + s(claims.get(c, {}).get("quote"))
                         for c in ids(v.get("claim_ids")))
        for dt in dts:
            canon = DATA_TYPES.get(dt.lower())
            if not canon:
                err.append(f"{vid}: data type '{dt}' must be one of {', '.join(DATA_TYPES.values())}")
            elif not re.search(DATA_TYPE_WORDS[canon], vtext, re.I):
                warn.append(f"{vid}: data type '{canon}' does not appear in its cited claims; never infer a data type "
                            f"the sources do not name")
    seen_tech = {}
    for r in t.get("ttps", []):
        tid, mid = s(r.get("technique_id")), s(r.get("ttp_id")) or s(r.get("technique_id"))
        dom = ttp_domain(r)
        if dom not in DOMAIN_TACTICS:
            err.append(f"{mid}: domain must be enterprise or ics")
            dom = "enterprise"
        if s(r.get("occurrence")) not in OCCURRENCE:
            err.append(f"{mid}: occurrence must be one of {', '.join(sorted(OCCURRENCE))}")
        if s(r.get("confidence")) not in TTP_CONF:
            err.append(f"{mid}: confidence must be High, Medium or Low")
        tac = s(r.get("tactic"))
        if tac not in DOMAIN_TACTICS[dom]:
            err.append(f"{mid}: tactic {tac} is not a current ATT&CK {dom} tactic shortname")
        if tid != "Unmapped" and not re.fullmatch(r"T\d{4}(\.\d{3})?", tid):
            err.append(f"{mid}: bad technique id {tid}")
        elif tid != "Unmapped" and ATTACK:
            known = attack_tech(dom, tid)
            if not known:
                err.append(f"{mid}: {tid} is not a technique in ATT&CK {dom} {PINNED_VERSION}; check the ID (never "
                           f"place a technique from memory)")
            else:
                if tac != "unmapped" and tac not in known["tactics"]:
                    err.append(f"{mid}: {tid} {known['name']} does not carry tactic {tac} in {PINNED_VERSION} (it "
                               f"carries {', '.join(known['tactics'])})")
                nm = s(r.get("name")).lower()
                if nm and known["name"].lower() not in nm and nm not in known["name"].lower():
                    warn.append(f"{mid}: name '{r.get('name')}' does not match ATT&CK's '{known['name']}' for {tid}")
        for ev in ids(r.get("event_ids")):
            if ev not in events:
                err.append(f"{mid}: unknown event {ev}")
        torig = set()
        for cl in ids(r.get("claim_ids")):
            for sid in ids(claims.get(cl, {}).get("source_ids")):
                if sid in srcs and s(srcs[sid].get("retrieval")) != "failed":
                    torig |= originators(srcs, sid)
        tconf, tocc = s(r.get("confidence")), s(r.get("occurrence"))
        if tconf == "High" and len(torig) < 2:
            warn.append(f"{mid}: confidence High needs two or more originators ({len(torig)} behind its claims); "
                        f"use Medium or Low")
        elif tconf == "Medium" and len(torig) < 2 and tocc != "Observed":
            warn.append(f"{mid}: confidence Medium needs two or more originators or an Observed occurrence; use Low")
        if tocc == "Assessed" and not re.search(ICD, s(r.get("how_used")), re.I):
            warn.append(f"{mid}: an Assessed technique states its inference in how_used with an ICD 203 term")
        if incidents and s(r.get("incident")) and s(r.get("incident")) not in incidents:
            warn.append(f"{mid}: incident '{r.get('incident')}' is not a scope row of kind Incident (give its scope_id)")
        key = (tid, tac, s(r.get("phase")), s(r.get("incident")))
        if key in seen_tech and tid != "Unmapped":
            warn.append(f"{mid}: duplicates {seen_tech[key]} (same technique, tactic, phase and incident)")
        seen_tech[key] = mid
    for sc in t.get("scope", []):
        if s(sc.get("kind")) != "Incident":
            continue
        tags = {s(sc.get("scope_id")), s(sc.get("value"))} - {""}
        icl = [c for c in claims.values() if s(c.get("incident")) in tags]
        for name in ("timeline", "victims", "ttps"):
            for r in t.get(name, []):
                if s(r.get("incident")) in tags:
                    icl += [claims[x] for x in ids(r.get("claim_ids")) if x in claims]
        def weak(c):
            if s(c.get("status")) == "Unknown":
                return True
            cs = [srcs.get(x, {}) for x in ids(c.get("source_ids"))]
            return bool(cs) and all(MACHINE_SOURCE.search(s(x.get("type")) + " " + s(x.get("notes"))) for x in cs)
        if icl and all(weak(c) for c in icl):
            warn.append(f"{sc.get('scope_id')}: every claim behind this Incident is Unknown or machine-extracted; activity "
                        f"no source links to the attack is an Out of scope row plus a Watch row")
    for name in ("timeline", "victims", "ledger"):
        for r in t.get(name, []):
            if incidents and s(r.get("incident")) and s(r.get("incident")) not in incidents:
                warn.append(f"{name}: incident '{r.get('incident')}' is not a scope row of kind Incident "
                            f"(give its scope_id)")

    # attribution
    attr = t.get("attribution", [])
    hyps = [a for a in attr if s(a.get("kind")) == "Hypothesis"]
    attr_ids = {s(a.get("row_id")) for a in attr}
    for a in attr:
        rid, kind = s(a.get("row_id")), s(a.get("kind"))
        if kind not in ATTR_KINDS:
            err.append(f"{rid}: kind must be Statement, Hypothesis, Signal or Diamond")
        if kind == "Hypothesis":
            if s(a.get("likelihood")).lower() not in ICD_TERMS:
                err.append(f"{rid}: hypothesis likelihood must be an ICD 203 term")
            if s(a.get("confidence")).lower() not in CONF_LEVELS:
                err.append(f"{rid}: hypothesis confidence must be low, moderate or high")
        if kind == "Signal" and not s(a.get("limits")):
            warn.append(f"{rid}: attribution signal row has no limits")
        if kind == "Diamond" and s(a.get("party")) not in DIAMOND:
            err.append(f"{rid}: Diamond party must be Adversary, Capability, Infrastructure or Victim")
        for f in ("for_signals", "against_signals"):
            if s(a.get(f)) and not re.search(r"\b[SCH]\d{2,}\b", s(a.get(f))):
                warn.append(f"{rid}: {f} cites no source, claim or signal row ID (QA4)")
            for ref in re.findall(r"\bH\d{2,}\b", s(a.get(f))):
                if ref not in attr_ids:
                    err.append(f"{rid}: {f} cites unknown attribution row {ref}")
    if len(hyps) == 1:
        err.append("attribution: one Hypothesis row is not a comparison. Use Hypothesis rows only when the sources "
                   "name two or more credible candidates; otherwise write Signal rows.")
    if attr and not quick:
        missing = DIAMOND - {s(a.get("party")) for a in attr if s(a.get("kind")) == "Diamond"}
        if missing:
            warn.append(f"attribution: Diamond rows missing for {', '.join(sorted(missing))}")
    if s(summ.get("actor_likelihood")) and s(summ.get("actor_likelihood")).lower() not in ICD_TERMS:
        err.append("summary: actor_likelihood must be an ICD 203 term")

    # gaps, conflicts, scope, changes
    for g in gaps:
        gid, kind = s(g.get("item_id")), s(g.get("kind"))
        if kind not in GAP_KINDS:
            err.append(f"{gid}: kind must be Gap, Watch or Action")
        if s(g.get("status")) and s(g.get("status")) not in GAP_STATUS:
            err.append(f"{gid}: status must be Open or Closed")
        if s(g.get("status")) == "Closed":
            if not ids(g.get("closed_by")):
                err.append(f"{gid}: a Closed gap needs closed_by (the claim that answers it)")
            for cl in ids(g.get("closed_by")):
                if cl not in claims:
                    err.append(f"{gid}: closed_by unknown claim {cl}")
        if truthy(g.get("blocking")) and kind != "Gap":
            err.append(f"{gid}: only a Gap row can be blocking")
        if kind in ("Watch", "Action"):
            for f in ("item", "why", "next_step"):
                if UNDEFANGED.search(s(g.get(f))):
                    err.append(f"{gid}: {f} holds an undefanged URL or IP (use hxxp and [.])")
            ns = s(g.get("next_step"))
            if kind == "Action":
                ag = ns.lower().find("analyst guidance:")
                cited_part = ns if ag < 0 else ns[:ag]
                if not re.search(r"\b[CA]\d{2,}\b", cited_part) and ag != 0:
                    warn.append(f"{gid}: next_step puts unsourced steps first; list the sourced steps first with their "
                                f"claim IDs in brackets, then 'Analyst guidance:' and the rest")
            elif not ids(g.get("claim_ids")) and "analyst guidance:" not in ns.lower():
                warn.append(f"{gid}: cites no claims, so the steps come from general knowledge; start them "
                            f"'Analyst guidance:'")
    for r in t.get("scope", []):
        if s(r.get("kind")) not in SCOPE_KINDS:
            err.append(f"{r.get('scope_id')}: kind must be Name, Incident or Out of scope")
    for r in t.get("changes", []):
        if s(r.get("kind")) not in CHANGE_KINDS:
            err.append(f"{r.get('change_id')}: kind must be one of {', '.join(sorted(CHANGE_KINDS))}")

    # software and kill chain (SOC hand-off)
    for p in t.get("software", []):
        pid, ver = s(p.get("software_id")), s(p.get("version"))
        text = " ".join(s(claims.get(c, {}).get("claim")) + " " + s(claims.get(c, {}).get("quote"))
                        for c in ids(p.get("claim_ids")))
        if ver and ver not in ("Any", "Not reported", "Not available in provided reports") and ver.lower() not in text.lower():
            warn.append(f"{pid}: version '{ver}' does not appear in its cited claims; give a version only when a "
                        f"source states it, else 'Any'")
        cve = s(p.get("cve"))
        if cve:
            for c in cve.split():
                if not CVE.match(c):
                    err.append(f"{pid}: bad CVE id {c}")
            for f in ("affected_versions", "fixed_version", "advisory_source"):
                if not s(p.get(f)):
                    warn.append(f"{pid}: CVE in scope but {f} is empty")
            if s(p.get("advisory_source")) and s(p.get("advisory_source")) not in srcs:
                err.append(f"{pid}: advisory_source {p.get('advisory_source')} is not a source")
    orders = []
    for k in t.get("killchain", []):
        kid = s(k.get("stage_id"))
        if s(k.get("observed")) not in KC_OBSERVED:
            err.append(f"{kid}: observed must be Observed, Reported or Not observed")
        if s(k.get("tactic")) and s(k.get("tactic")) not in ALL_TACTICS:
            err.append(f"{kid}: tactic {k.get('tactic')} is not a current ATT&CK tactic shortname")
        try:
            orders.append(int(s(k.get("order"))))
        except ValueError:
            err.append(f"{kid}: order must be a whole number")
        if s(k.get("observed")) != "Not observed" and not ids(k.get("claim_ids")):
            err.append(f"{kid}: an observed or reported stage needs claim_ids")
        sourced = set(ids(k.get("sourced_fields")))
        for f, v in k.items():
            if f in KC_FREE or not s(v):
                continue
            if f not in sourced and not s(v).startswith(UNSOURCED_PREFIXES):
                err.append(f"{kid}: {f} is not listed in sourced_fields, so it must start with 'Analyst guidance:', "
                           f"be 'Not available in provided reports', or (process and parent) 'N/A (no host stage)'")
            if f in sourced and not ids(k.get("claim_ids")):
                err.append(f"{kid}: {f} is marked sourced but the stage cites no claims")
            if UNDEFANGED.search(s(v)):
                err.append(f"{kid}: {f} holds an undefanged URL or IP (use hxxp and [.])")
            if s(v).startswith("N/A (no host stage)") and f not in ("process", "parent"):
                warn.append(f"{kid}: 'N/A (no host stage)' is meant for process and parent only")
    if len(orders) != len(set(orders)):
        err.append("killchain: two stages share the same order")
    if s(summ.get("case_type")) in ("actor", "law-enforcement") and not t.get("killchain") and not s(summ.get("soc_note")):
        warn.append("summary: an actor or law enforcement case with no kill chain needs soc_note (one line on why the "
                    "SOC hand-off is skipped)")

    # facts the tracker must not presuppose (an Unknown claim or a glance field naming an unsupported attack type)
    supported = " ".join(s(c.get("claim")) for c in claims.values()
                         if s(c.get("status")) in ("Confirmed", "Reported", "Actor-asserted", "Assessed")).lower()
    presuppose = " ".join([s(c.get("claim")) for c in claims.values() if s(c.get("status")) == "Unknown"] +
                          [s(summ.get(f)) for f in summ if f.startswith("glance_")]).lower()
    def asserted(word, text):
        """True when the word appears without a negation shortly before it ('no encryption' presupposes nothing)."""
        for m in re.finditer(re.escape(word), text):
            if not re.search(r"\b(no|not|nor|without|neither)\b", text[max(0, m.start() - 40):m.start()]):
                return True
        return False
    for w in PRESUPPOSED:
        if asserted(w, presuppose) and w not in supported:
            warn.append(f"writing: '{w}' appears in an Unknown claim or a glance field, but no sourced claim says it; "
                        f"name only what is in scope (for example 'Payload: not reported')")

    # the summary is never firmer than the claims about the cause
    if s(summ.get("cause_confirmed")).lower() in ("false", "no", "0"):
        for f in ("bluf", "leadership", "glance_type"):
            if s(summ.get(f)) and not HEDGE.search(s(summ.get(f))):
                warn.append(f"summary: cause_confirmed is false, so {f} must say 'suspected' or 'reportedly'")

    # every defanged indicator must come from a saved extract
    if src_dir and saved:
        corpus = norm(" ".join("\n".join(v[1] or []) for v in saved.values()))
        def refang(x):
            return norm(x.replace("[.]", ".").replace("hxxp", "http").replace("[:]", ":"))
        places = [("killchain", k.get("stage_id"), k.get("network")) for k in t.get("killchain", [])]
        places += [("gaps", g.get("item_id"), " ".join(s(g.get(f)) for f in ("item", "why", "next_step"))) for g in gaps]
        places += [("ledger", c.get("claim_id"), c.get("claim")) for c in claims.values()]
        missing_ioc = []
        for coll, rid, text in places:
            for m in DEFANGED.findall(s(text)):
                ioc = m.rstrip(".")
                if refang(ioc) not in corpus and norm(ioc) not in corpus:
                    missing_ioc.append(f"{rid} {ioc}")
        if missing_ioc:
            warn.append(f"indicators: {len(missing_ioc)} defanged value(s) appear in no saved extract: "
                        f"{'; '.join(missing_ioc[:6])}. Save the search or Feedly result they came from as a source.")

    # writing rules and protection of people on everything that gets published
    not_x, caveats, minors, long_rows, loose_ev = [], 0, [], {}, []
    for name in COLLECTIONS:
        for row in (t.get(name) or []):
            if not isinstance(row, dict):
                continue
            for k, v in row.items():
                if k in PRIVATE or k == "url" or not isinstance(v, str):
                    continue
                if "\u2014" in v:
                    err.append(f"{name}: em dash in '{v[:50]}'")
                if NOT_X.search(v):
                    not_x.append(f"{name}.{k}: '{v[:60]}'")
                caveats += len(CAVEAT.findall(v))
                if name not in ("sources", "changes") and k not in LONG_SKIP and k not in KEYS.get(name, ()):
                    prose = re.sub(r"`[^`]*`", "x", v)
                    if any(len(sent.split()) > 25 for sent in re.split(r"(?<=[.!?;])\s+", prose)):
                        rid = next((s(row.get(x)) for x in KEYS.get(name, ()) if s(row.get(x))), k)
                        long_rows.setdefault(name, []).append(rid)
                if (name not in ("sources", "changes") and k not in ("quote", "said_by")
                        and LOOSE_EVIDENCE.search(EVIDENCE_OK.sub("", v)) and not SPEECH.search(v)):
                    loose_ev.append(f"{name}.{k}: '{v[:60]}'")
                m = MINOR.search(v)
                if m:
                    minors.append(f"{name}.{k}: '{m.group(0)}'")
    if loose_ev:
        warn.append(f"writing: {len(loose_ev)} use(s) of 'evidence' in our own words. The tracker produces information, "
                    "not evidence; say cited, sourced, reporting, signal or claim, unless a source is quoted: "
                    + "; ".join(loose_ev[:5]))
    if not_x:
        warn.append(f"writing: {len(not_x)} 'this is not' construction(s); say what it is instead: "
                    + "; ".join(not_x[:5]))
    for name, rids in long_rows.items():
        rids = list(dict.fromkeys(rids))
        warn.append(f"writing: {name} has {len(rids)} row(s) with a sentence over 25 words: {' '.join(rids[:12])}"
                    f"{' ...' if len(rids) > 12 else ''}")
    if caveats > 6:
        warn.append(f"writing: the verification caveat appears {caveats} times; state it once where the claim "
                    f"first appears and let the status label carry it")
    if minors:
        warn.append("people: possible detail about a person under 18 (" + "; ".join(minors[:4]) + "). Never publish "
                    "a name, age, school, town or other detail that could identify a minor (hard rule 7).")
    return err, warn, info


# ---------------------------------------------------------------- incident response metrics
IR_METRICS = [("Dwell time", ("earliest-activity", "initial-access"), ("detection",)),
              ("Time to contain", ("detection",), ("containment",)),
              ("Time to disclose", ("detection",), ("disclosure",)),
              ("Time to notify", ("detection",), ("notification",))]
PREC_ORDER = ["exact", "day", "approx", "month"]


def ir_metrics(t):
    evs = []
    for e in t.get("timeline", []):
        if s(e.get("status")) == "Superseded":
            continue
        try:
            evs.append((iso(e.get("when")), e))
        except (ValueError, TypeError):
            continue
    out = []
    for name, a_types, b_types in IR_METRICS:
        a = sorted([x for x in evs if s(x[1].get("event_type")) in a_types], key=lambda x: x[0])
        b = sorted([x for x in evs if s(x[1].get("event_type")) in b_types], key=lambda x: x[0])
        if not a or not b:
            continue
        (da, ea), (db, eb) = a[0], b[0]
        precs = [s(ea.get("precision")) or "day", s(eb.get("precision")) or "day"]
        worst = max(precs, key=lambda p: PREC_ORDER.index(p) if p in PREC_ORDER else 1)
        days = (db - da).total_seconds() / 86400
        if days < 0:
            continue
        value = round(days, 1) if worst == "exact" else round(days)
        out.append({"metric": name, "value": value, "unit": "days", "from_event": s(ea.get("event_id")),
                    "to_event": s(eb.get("event_id")), "from_when": s(ea.get("when")), "to_when": s(eb.get("when")),
                    "precision": worst,
                    "note": f"{s(ea.get('event_id'))} ({s(ea.get('event_type'))}, {precs[0]}) to "
                            f"{s(eb.get('event_id'))} ({s(eb.get('event_type'))}, {precs[1]})"
                            + ("; approximate" if worst in ("approx", "month") else "")})
    return out


# ---------------------------------------------------------------- publish / html / diff
def published_bundle(t):
    bundle = {}
    for name in COLLECTIONS:
        rows = t.get(name) or []
        if isinstance(rows, dict):
            rows = [rows]
        bundle[name] = [{k: v for k, v in r.items() if k not in PRIVATE} for r in rows]
    if bundle["summary"]:
        nd = newest_source_date(t)
        if nd:
            bundle["summary"][0]["newest_source_date"] = nd
    for r in bundle["ttps"]:
        tid, dom = s(r.get("technique_id")), ttp_domain(r)
        r["domain"] = dom
        if tid and tid != "Unmapped":
            r["attack_url"] = attack_url(tid)
            mits = mitigations_for(dom, tid)
            if mits:
                r["mitigations"] = "; ".join(f"{m} {n}".strip() for m, n in mits)
    bundle["ir_metrics"] = ir_metrics(t)
    tacs = []
    for dom in ("enterprise", "ics"):
        for i, sn in enumerate(DOMAIN_TACTICS[dom][:-1]):
            meta = ATTACK[dom]["tactics"].get(sn, {}) if ATTACK else {}
            tacs.append({"domain": dom, "order": i, "tactic": sn, "name": meta.get("name", sn),
                         "tactic_ref": meta.get("id", "")})
    bundle["tactics"] = tacs
    return bundle


def cmd_publish(t, out):
    os.makedirs(out, exist_ok=True)
    bundle = published_bundle(t)
    with open(os.path.join(out, "tracker-data.json"), "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, indent=1, ensure_ascii=False)
    flat = [{"collection": name, **r} for name, coll in bundle.items() for r in coll]
    with open(os.path.join(out, "tracker-rows.json"), "w", encoding="utf-8") as fh:
        json.dump(flat, fh, ensure_ascii=False)
    attack = s((bundle["summary"] or [{}])[0].get("attack")) or "Attack"
    with open(os.path.join(out, "dash-meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"title": f"{attack} Attack Tracker"}, fh, ensure_ascii=False)
    with open(_asset("dashboard-index.html"), encoding="utf-8") as fh:
        template = fh.read()
    with open(os.path.join(out, "dash-index.json"), "w", encoding="utf-8") as fh:
        json.dump({"text": template}, fh, ensure_ascii=False)
    empty = [n for n in COLLECTIONS if not bundle[n]]
    print(f"wrote {out}/dash-meta.json and {out}/dash-index.json for the dashboard batch")
    print(f"wrote {out}/tracker-data.json and {out}/tracker-rows.json ({len(flat)} rows, "
          f"{len(COLLECTIONS) - len(empty)} non-empty collections, {len(bundle['ir_metrics'])} response metrics)")
    if empty:
        print("EMPTY (the dashboard shows a placeholder for these): " + ", ".join(empty))


def _asset(name):
    for base in (os.path.join(HERE, "..", "assets"), os.path.join(HERE, "assets"), "assets",
                 os.path.join("work", "assets")):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    sys.exit(f"ERROR cannot find assets/{name}; copy the skill's assets folder next to scripts/")


def cmd_html(t, out):
    """One standalone page: the fixed template, the published rows and a small runtime, so it opens offline."""
    summ = summary_row(t)
    bundle = published_bundle(t)
    flat = [{"collection": name, **r} for name, coll in bundle.items() for r in coll]
    with open(_asset("dashboard-index.html"), encoding="utf-8") as fh:
        page = fh.read()
    with open(_asset("standalone-runtime.js"), encoding="utf-8") as fh:
        runtime = fh.read()
    data = json.dumps(flat, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    title = f"{s(summ.get('attack'))} Attack Tracker"
    esc = lambda x: x.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = ("<!doctype html>\n<html lang=\"" + esc(s(summ.get("language")) or "en") + "\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{esc(title)}</title>\n"
            f"<meta name=\"description\" content=\"{esc(s(summ.get('tlp')))} attack tracker exported by track-cyberattack\">\n"
            "<script src=\"https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js\" "
            "onerror=\"this.remove()\"></script>\n"
            f"<script type=\"application/json\" id=\"tracker-data\">{data}</script>\n"
            f"<script>\n{runtime}\n</script>\n</head>\n<body>\n<div id=\"dash-root\">\n"
            f"<p class=\"lx-export-tlp\">{esc(s(summ.get('tlp')))}: standalone export of the attack tracker dashboard, "
            f"iteration {esc(s(summ.get('iteration')))}. Handle under that mark.</p>\n"
            f"{page}\n</div>\n</body>\n</html>\n")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {out} ({len(html) // 1024} KB, {len(flat)} rows); it opens offline in any browser")


DIFF_SKIP = {"changes", "headlines", "summary"}
DIFF_IGNORE = {"quote", "quote_source", "line"}
SUMMARY_WATCH = ["status", "case_type", "tlp", "attack_version", "actor", "actor_likelihood", "actor_confidence",
                 "attribution_statement"]


def _describe(name, r):
    g = lambda k: s(r.get(k))
    return {
        "sources": lambda: f"Source {g('source_id')}: {g('publisher')}, {g('title')}",
        "ledger": lambda: f"Claim {g('claim_id')}: {g('claim')}",
        "timeline": lambda: f"Event {g('event_id')} ({g('when')}): {g('event')}",
        "figures": lambda: f"Figure {g('figure_id')}: {g('label')} {g('value')} {g('unit')}".strip(),
        "victims": lambda: f"Victim {g('victim_id')}: {g('victim')} ({g('tier')})",
        "ttps": lambda: f"Technique {g('technique_id')} {g('name')} ({g('tactic')})",
        "attribution": lambda: f"Attribution {g('row_id')} ({g('kind')}): {g('party')}",
        "conflicts": lambda: f"Conflict {g('conflict_id')}: {g('topic')}",
        "gaps": lambda: f"{g('kind')} {g('item_id')}: {g('item')}",
        "scope": lambda: f"Scope {g('scope_id')} ({g('kind')}): {g('value')}",
        "software": lambda: f"Software {g('software_id')}: {g('software')} {g('version')}".strip(),
        "killchain": lambda: f"Kill chain stage {g('order')} {g('stage')} ({g('observed')})",
    }.get(name, lambda: name)()


MAIN_FIELD = {"sources": "retrieval", "ledger": "claim", "timeline": "event", "figures": "value", "victims": "tier",
              "ttps": "occurrence", "attribution": "position", "conflicts": "resolution", "gaps": "item",
              "scope": "value", "software": "version", "killchain": "observed"}


def cmd_diff(old, new):
    rows = []
    n = max(next_id(new.get("changes", []), "change_id", "D"), next_id(old.get("changes", []), "change_id", "D"))
    iteration = s(summary_row(new).get("iteration"))
    claims = {s(c.get("claim_id")) for c in new.get("ledger", [])}
    cut = lambda v: s(v)[:160]

    def add(kind, item, before, after, cids):
        nonlocal n
        n += 1
        rows.append({"change_id": f"D{n:02d}", "iteration": iteration, "kind": kind, "item": item,
                     "before": cut(before), "after": cut(after),
                     "claim_ids": " ".join(c for c in ids(cids) if c in claims)})

    def key(name, r):
        if name == "ttps" and not s(r.get("ttp_id")):
            return "|".join(s(r.get(k)) for k in ("technique_id", "phase", "incident"))
        return s(r.get(KEYS[name][0]))

    os_, ns = summary_row(old), summary_row(new)
    for f in SUMMARY_WATCH:
        if s(os_.get(f)) != s(ns.get(f)):
            add("Revised", f"Summary {f.replace('_', ' ')}", os_.get(f), ns.get(f), "")
    for name in COLLECTIONS:
        if name in DIFF_SKIP:
            continue
        om = {key(name, r): r for r in old.get(name, [])}
        nm = {key(name, r): r for r in new.get(name, [])}
        if name == "ttps":   # an old row without ttp_id matches a migrated row by technique, phase and incident
            alt = {"|".join(s(r.get(k)) for k in ("technique_id", "phase", "incident")): k2 for k2, r in nm.items()}
            om = {(alt.get(k, k) if "|" in k else k): r for k, r in om.items()}
        for k, r in nm.items():
            cid = s(r.get("claim_id")) if name == "ledger" else s(r.get("claim_ids"))
            if k not in om:
                after = s(r.get("status")) or s(r.get("tier")) or s(r.get("occurrence")) or s(r.get("kind")) or "added"
                add("New", _describe(name, r), "", after, cid)
                continue
            o = om[k]
            changed = [f for f in dict.fromkeys(list(o) + list(r))
                       if f not in DIFF_IGNORE and f not in KEYS[name] and s(o.get(f)) != s(r.get(f))]
            if not changed:
                continue
            if name == "ledger" and "status" in changed:
                kind = "Superseded" if s(r.get("status")) == "Superseded" else "Revised"
                add(kind, _describe(name, r), o.get("status"), r.get("status"),
                    " ".join([cid] + ids(r.get("superseded_by"))))
                changed = [f for f in changed if f not in ("status", "superseded_by", "credibility", "corroboration")]
                if "claim" in changed:
                    add("Revised", f"Claim {cid} reworded", o.get("claim"), r.get("claim"), cid)
                continue
            if name == "gaps" and "status" in changed and s(r.get("status")) == "Closed":
                add("Closed gap", _describe(name, r), "Open", f"Closed by {s(r.get('closed_by'))}",
                    s(r.get("closed_by")))
                continue
            if name == "ledger" and "claim" in changed:
                add("Revised", f"Claim {cid} reworded", o.get("claim"), r.get("claim"), cid)
                continue
            mf = MAIN_FIELD.get(name)
            if mf in changed:
                add("Revised", _describe(name, r), o.get(mf), r.get(mf), cid)
            else:
                add("Revised", _describe(name, r) + f" ({', '.join(changed[:4])} changed)",
                    "; ".join(f"{f}: {s(o.get(f))}" for f in changed[:3]),
                    "; ".join(f"{f}: {s(r.get(f))}" for f in changed[:3]), cid)
        for k, o in om.items():
            if k not in nm:
                add("Removed", _describe(name, o) + " (rows are never deleted; restore it and mark it Superseded or "
                                                    "Closed)", "present", "missing", "")
    print(json.dumps({"changes": rows}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- STIX 2.1
def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "case"


def _stamp(v):
    try:
        d = iso(v)
    except (ValueError, TypeError):
        d = datetime.now(timezone.utc).replace(tzinfo=None)
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def cmd_stix(t, out):
    summ = summary_row(t)
    slug = _slug(s(summ.get("attack")))
    created = _stamp(summ.get("created") or summ.get("as_of"))
    modified = _stamp(summ.get("as_of"))
    if modified < created:
        modified = created
    tlp = s(summ.get("tlp")) or "TLP:CLEAR"
    mid, mval = TLP_DEFS.get(tlp, TLP_DEFS["TLP:CLEAR"])
    marking = {"type": "marking-definition", "spec_version": "2.1", "id": f"marking-definition--{mid}",
               "created": "2022-10-01T00:00:00.000Z", "name": tlp,
               "extensions": {TLP_EXT: {"extension_type": "property-extension", "tlp_2_0": mval}}}

    def sid(kind, key, shared=False):
        return f"{kind}--{uuid.uuid5(STIX_NS, (key if shared else slug + '|' + key) + '|' + kind)}"

    producer = {"type": "identity", "spec_version": "2.1", "id": sid("identity", "track-cyberattack producer", True),
                "created": "2026-01-01T00:00:00.000Z", "modified": "2026-01-01T00:00:00.000Z",
                "name": "track-cyberattack attack tracker", "identity_class": "system",
                "description": "Analyst-graded attack tracker built by the track-cyberattack skill from public reporting."}
    objs = []

    def sdo(kind, key, shared=False, **props):
        o = {"type": kind, "spec_version": "2.1", "id": sid(kind, key, shared), "created": created,
             "modified": modified, "created_by_ref": producer["id"], "object_marking_refs": [marking["id"]]}
        o.update({k: v for k, v in props.items() if v not in (None, "", [], {})})
        objs.append(o)
        return o

    def rel(src, rtype, dst, key, **props):
        return sdo("relationship", f"rel|{src['id']}|{rtype}|{dst['id']}|{key}", relationship_type=rtype,
                   source_ref=src["id"], target_ref=dst["id"], **props)

    srcs = {s(x.get("source_id")): x for x in t.get("sources", [])}

    def ext_refs(source_ids):
        refs = []
        for x in ids(source_ids):
            src = srcs.get(x)
            if not src:
                continue
            r = {"source_name": f"{x} {s(src.get('publisher'))}".strip(), "description": s(src.get("title"))}
            if re.match(r"^https?://", s(src.get("url")), re.I):
                r["url"] = s(src.get("url"))
            refs.append(r)
        return refs

    attacker = sorted(s(e.get("when")) for e in t.get("timeline", [])
                      if s(e.get("lane")) == "Attacker" and s(e.get("status")) != "Superseded" and s(e.get("when")))
    aliases = [s(r.get("value")) for r in t.get("scope", []) if s(r.get("kind")) == "Name"
               and s(r.get("value")) and s(r.get("value")) != s(summ.get("attack"))]
    campaign = sdo("campaign", "campaign", name=s(summ.get("attack")),
                   description=" ".join(x for x in (s(summ.get("bluf")), s(summ.get("scope"))) if x),
                   aliases=aliases, first_seen=_stamp(attacker[0]) if attacker else None,
                   last_seen=_stamp(attacker[-1]) if attacker else None)

    actors = []
    if s(summ.get("actor")):
        actors.append((s(summ.get("actor")), s(summ.get("actor_likelihood")).lower(),
                       s(summ.get("actor_confidence")).lower(), s(summ.get("attribution_statement")), ""))
    for a in t.get("attribution", []):
        if s(a.get("kind")) == "Hypothesis" and s(a.get("party")) and not re.search(r"\b(unknown|unattributed|null)\b",
                                                                                      s(a.get("party")), re.I):
            actors.append((s(a.get("party")), s(a.get("likelihood")).lower(), s(a.get("confidence")).lower(),
                           s(a.get("position")), s(a.get("for_signals"))))
    seen_actor = set()
    for name, lik, conf, why, evid in actors:
        if name.lower() in seen_actor:
            continue
        seen_actor.add(name.lower())
        iset = sdo("intrusion-set", f"actor|{name.lower()}", name=name)
        desc = f"Likelihood: {lik or 'not stated'}; confidence: {conf or 'not stated'}. {why}".strip()
        rel(campaign, "attributed-to", iset, name.lower(), description=desc,
            confidence=ICD_TO_STIX.get(lik), external_references=ext_refs(" ".join(re.findall(r"\bS\d{2,}\b", evid))))

    for r in t.get("ttps", []):
        tid = s(r.get("technique_id"))
        if tid == "Unmapped" or not tid:
            continue
        dom = ttp_domain(r)
        chain = "mitre-ics-attack" if dom == "ics" else "mitre-attack"
        ap = sdo("attack-pattern", f"mitre|{tid}", True, name=s(r.get("name")),
                 external_references=[{"source_name": "mitre-attack", "external_id": tid, "url": attack_url(tid)}],
                 kill_chain_phases=[{"kill_chain_name": chain, "phase_name": s(r.get("tactic"))}]
                 if s(r.get("tactic")) in DOMAIN_TACTICS.get(dom, TACTICS)[:-1] else None)
        rel(campaign, "uses", ap, s(r.get("ttp_id")) or f"{tid}|{s(r.get('phase'))}|{s(r.get('incident'))}",
            description=f"{s(r.get('how_used'))} Occurrence: {s(r.get('occurrence'))}; confidence: "
                        f"{s(r.get('confidence'))}. Claims: {s(r.get('claim_ids'))}.")

    for p in t.get("software", []):
        for cve in s(p.get("cve")).split():
            v = sdo("vulnerability", f"cve|{cve}", True, name=cve,
                    description=f"{s(p.get('software'))}: affected {s(p.get('affected_versions')) or 'not stated'}, "
                                f"fixed in {s(p.get('fixed_version')) or 'not stated'}.",
                    external_references=[{"source_name": "cve", "external_id": cve}] + ext_refs(p.get("advisory_source")))
            rel(campaign, "targets", v, cve)

    sectors = {}
    for v in t.get("victims", []):
        sec = s(v.get("sector"))
        if sec and sec.lower() not in sectors:
            sectors[sec.lower()] = sdo("identity", f"sector|{sec.lower()}", True, name=f"{sec} sector",
                                       identity_class="class", sectors=[_slug(sec)])
            rel(campaign, "targets", sectors[sec.lower()], sec.lower())
        if s(v.get("tier")) == "Confirmed" and s(v.get("victim")):
            dts = "; ".join(split_list(v.get("data_types"))) or "none reported"
            org = sdo("identity", f"victim|{s(v.get('victim_id'))}", identity_class="organization",
                      name=s(v.get("victim")), sectors=[_slug(sec)] if sec else None,
                      description=f"{s(v.get('role'))}. Impact: {s(v.get('impact'))}. Data exposed: {dts}. Counted: "
                                  f"{s(v.get('count_method'))}. Claims: {s(v.get('claim_ids'))}.")
            rel(campaign, "targets", org, s(v.get("victim_id")))

    for c in t.get("ledger", []):
        cid = s(c.get("claim_id"))
        content = (f"{s(c.get('claim'))} Status: {s(c.get('status'))}. Credibility: {s(c.get('credibility'))}. "
                   f"Sources: {s(c.get('source_ids'))}.")
        for f, label in (("corroboration", "Corroboration"), ("basis", "Basis"), ("superseded_by", "Superseded by")):
            if s(c.get(f)):
                content += f" {label}: {s(c.get(f))}."
        sdo("note", f"claim|{cid}", abstract=f"{cid} ({s(c.get('topic'))}, {s(c.get('status'))})", content=content,
            object_refs=[campaign["id"]], external_references=ext_refs(c.get("source_ids")))
    for e in t.get("timeline", []):
        eid = s(e.get("event_id"))
        sdo("note", f"event|{eid}", abstract=f"{eid} {s(e.get('when'))} ({s(e.get('lane'))})",
            content=f"{s(e.get('event'))} Status: {s(e.get('status'))}. Claims: {s(e.get('claim_ids'))}.",
            object_refs=[campaign["id"]])
    for g in t.get("gaps", []):
        gid = s(g.get("item_id"))
        closed = f" Closed by {s(g.get('closed_by'))}." if s(g.get("status")) == "Closed" else ""
        sdo("note", f"gap|{gid}", abstract=f"{gid} {s(g.get('kind'))}{' (closed)' if closed else ''}",
            content=" ".join(x for x in (s(g.get("item")), s(g.get("why")), s(g.get("next_step"))) if x) + closed,
            object_refs=[campaign["id"]])
    for k in t.get("conflicts", []):
        kid = s(k.get("conflict_id"))
        sdo("note", f"conflict|{kid}", abstract=f"{kid} Source conflict: {s(k.get('topic'))}",
            content=f"A: {s(k.get('position_a'))} B: {s(k.get('position_b'))} Resolution: {s(k.get('resolution'))}",
            object_refs=[campaign["id"]])

    refs = [o["id"] for o in objs]
    report = {"type": "report", "spec_version": "2.1", "id": sid("report", "report"), "created": created,
              "modified": modified, "created_by_ref": producer["id"], "object_marking_refs": [marking["id"]],
              "name": f"{s(summ.get('attack'))} attack tracker, iteration {s(summ.get('iteration')) or '1'}",
              "description": " ".join(x for x in (s(summ.get("bluf")), s(summ.get("attribution_statement"))) if x),
              "report_types": ["campaign", "threat-report"], "published": modified, "object_refs": refs,
              "external_references": ext_refs(" ".join(srcs))}
    bundle = {"type": "bundle", "id": f"bundle--{uuid.uuid4()}", "objects": [marking, producer] + objs + [report]}
    problems = validate_stix(bundle)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(bundle, fh, indent=1, ensure_ascii=False)
    counts = {}
    for o in bundle["objects"]:
        counts[o["type"]] = counts.get(o["type"], 0) + 1
    print(f"wrote {out}: " + ", ".join(f"{v} {k}" for k, v in counts.items()))
    for p in problems:
        print("ERROR", p)
    if problems:
        sys.exit(1)


def validate_stix(bundle):
    probs, known = [], {o.get("id") for o in bundle["objects"]}
    for o in bundle["objects"]:
        oid = o.get("id", "")
        if o.get("spec_version") != "2.1":
            probs.append(f"{oid}: spec_version must be 2.1")
        if not re.fullmatch(rf"{re.escape(o.get('type', ''))}--[0-9a-f-]{{36}}", oid):
            probs.append(f"{oid}: id does not match type '{o.get('type')}'")
        for k in ("created", "modified", "published", "first_seen", "last_seen"):
            if k in o and not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", o[k]):
                probs.append(f"{oid}: bad timestamp {k}")
        for k in ("source_ref", "target_ref", "created_by_ref"):
            if k in o and o[k] not in known:
                probs.append(f"{oid}: {k} does not resolve")
        for k in ("object_refs", "object_marking_refs"):
            for r in o.get(k, []):
                if r not in known:
                    probs.append(f"{oid}: {k} entry {r} does not resolve")
        if o.get("type") == "indicator" or o.get("relationship_type") == "indicates":
            probs.append(f"{oid}: indicators are out of scope for this bundle")
    if importlib.util.find_spec("stix2"):
        import stix2
        try:
            stix2.parse(bundle, allow_custom=True)
        except Exception as e:  # noqa: BLE001
            probs.append(f"stix2 library rejected the bundle: {e}")
    return probs


# ---------------------------------------------------------------- ATT&CK Navigator layers
def cmd_navigator(t, out):
    summ = summary_row(t)
    ver = re.search(r"\d+", s(summ.get("attack_version")) or PINNED_VERSION)
    colors = {"Observed": "#1f6fb2", "Reported": "#e08e0b", "Capability": "#7d5ba6", "Assessed": "#9aa3ae"}
    score = {"Observed": 4, "Reported": 3, "Capability": 2, "Assessed": 1}
    written = []
    for dom, nav_domain in (("enterprise", "enterprise-attack"), ("ics", "ics-attack")):
        rows = [r for r in t.get("ttps", []) if ttp_domain(r) == dom]
        if dom == "ics" and not rows:
            continue
        techs, used = [], set()
        for r in rows:
            tid = s(r.get("technique_id"))
            if tid == "Unmapped" or s(r.get("tactic")) not in DOMAIN_TACTICS[dom][:-1]:
                continue
            occ = s(r.get("occurrence"))
            used.add(occ)
            techs.append({"techniqueID": tid, "tactic": s(r.get("tactic")), "score": score.get(occ, 1),
                          "color": colors.get(occ, "#9aa3ae"), "enabled": True, "showSubtechniques": "." in tid,
                          "comment": f"{s(r.get('how_used'))} Occurrence: {occ}; confidence: {s(r.get('confidence'))}. "
                                     f"Phase: {s(r.get('phase'))}. Claims: {s(r.get('claim_ids'))}."})
        layer = {"name": f"{s(summ.get('attack'))} techniques" + (" (ICS)" if dom == "ics" else ""),
                 "domain": nav_domain,
                 "versions": {"attack": ver.group(0) if ver else "20", "navigator": "5.1.0", "layer": "4.5"},
                 "description": f"{'ICS t' if dom == 'ics' else 'T'}echniques from the {s(summ.get('attack'))} case "
                                f"file, iteration {s(summ.get('iteration'))}, as of {s(summ.get('as_of'))}. Colour "
                                f"shows occurrence.",
                 "techniques": techs, "gradient": {"colors": ["#ffffff", "#1f6fb2"], "minValue": 0, "maxValue": 4},
                 "legendItems": [{"label": k, "color": v} for k, v in colors.items() if k in used],
                 "layout": {"layout": "side", "showID": True, "showName": True}, "hideDisabled": False,
                 "selectTechniquesAcrossTactics": False, "showTacticRowBackground": False}
        path = out if dom == "enterprise" else re.sub(r"(\.json)?$", "-ics.json", out, count=1)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(layer, fh, indent=1, ensure_ascii=False)
        written.append(f"{path} ({len(techs)} {dom} techniques)")
    print("wrote " + "; ".join(written))


# ---------------------------------------------------------------- environment and Word check
def cmd_attack(words, domain=None):
    if not ATTACK:
        sys.exit("ERROR the ATT&CK map scripts/attack_v20.json is missing")
    terms = [w.lower() for w in words]
    hits = []
    for dom in ([domain] if domain else ["enterprise", "ics"]):
        if dom not in ("enterprise", "ics"):
            sys.exit("ERROR --domain must be enterprise or ics")
        for tid, tech in ATTACK[dom]["techniques"].items():
            hay = f"{tid} {tech['name']}".lower()
            if all(w in hay for w in terms):
                hits.append(f"{dom:10} {tid:10} {tech['name']}  [{', '.join(tech['tactics'])}]")
    print("\n".join(sorted(hits)) if hits else f"no {PINNED_VERSION} technique matches '{' '.join(words)}'; try a "
                                                  f"shorter keyword or the other domain")


def cmd_preflight():
    rows, fixes = [], []

    def need(name, ok, fix, effect):
        rows.append(("OK     " if ok else "MISSING") + f" {name}" + ("" if ok else f" ({effect})"))
        if not ok and fix:
            fixes.append(fix)
    need("python 3.9+", sys.version_info >= (3, 9), "use Python 3.9 or later", "nothing runs")
    need("ATT&CK map", ATTACK is not None, "", "technique IDs are checked by shape only; restore scripts/attack_v20.json")
    mpl = importlib.util.find_spec("matplotlib") is not None
    need("matplotlib", mpl, "pip install matplotlib (add --break-system-packages if pip refuses)",
         "the timeline, matrix and Diamond images are drawn as SVG instead, which is fine")
    if not mpl:
        conv = any(shutil.which(x) for x in ("rsvg-convert", "magick", "convert", "inkscape"))
        need("SVG to PNG converter", conv, "",
             "the report embeds SVG images that Word 2016 or later shows; older readers see a blank box")
    need("graphviz dot", shutil.which("dot") is not None,
         "apt-get install -y graphviz  (macOS: brew install graphviz)", "no attack-chain image")
    node = shutil.which("node")
    docx_ok = False
    if node:
        r = subprocess.run([node, "-e", "require('docx')"], capture_output=True)
        if r.returncode != 0:
            root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip() if shutil.which("npm") else ""
            r = subprocess.run([node, "-e", f"require({json.dumps(os.path.join(root, 'docx'))})"], capture_output=True)
        docx_ok = r.returncode == 0
    need("node", node is not None, "install Node.js 18 or later", "no Word report")
    need("docx (npm)", docx_ok, "npm install -g docx", "no Word report")
    print("\n".join(rows))
    if fixes:
        print("FIX: " + " && ".join(dict.fromkeys(fixes)))
        print("Carry on without the missing pieces and say in one line what was skipped.")
    else:
        print("READY")


def cmd_verify_docx(docx, tracker=None, images=None):
    probs = []
    with zipfile.ZipFile(docx) as z:
        media = [n for n in z.namelist() if n.startswith("word/media/") and not n.endswith("/")]
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    shown = len(re.findall(r"<a:blip\b", xml))
    text = re.sub(r"<[^>]+>", " ", xml)
    for bad in ("```", "mermaid", "digraph", "flowchart LR", "gantt", "rankdir"):
        if bad in text:
            probs.append(f"diagram source text found ('{bad}'); embed the rendered image instead")
    if images is not None and shown < images:
        probs.append(f"{shown} image(s) embedded, expected {images}")
    if tracker:
        t = load(tracker)
        marks = set(re.findall(r'w:name="([^"]+)"', xml))
        missing = [s(c.get("claim_id")) for c in t.get("ledger", []) if f"claim_{s(c.get('claim_id'))}" not in marks]
        if missing:
            probs.append(f"{len(missing)} claim(s) have no bookmark in the ledger appendix: {' '.join(missing[:10])}")
    print(f"{docx}: {shown} image(s) ({len(media)} media files), {'OK' if not probs else str(len(probs)) + ' problem(s)'}")
    for p in probs:
        print("ERROR", p)
    if probs:
        sys.exit(1)


# ---------------------------------------------------------------- main
def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, args = argv[1], argv[2:]
    opt = lambda name: args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else None
    if cmd == "preflight":
        cmd_preflight()
    elif cmd == "init":
        cmd_init(args[0], opt("--attack") or "Unnamed attack", "--force" in args)
    elif cmd == "add":
        cmd_add(args[0], args[1], "--replace" in args)
    elif cmd == "set":
        if len(args) < 5:
            sys.exit("usage: set tracker.json COLLECTION ID FIELD VALUE   (ID is '-' for summary)")
        cmd_set(args[0], args[1], args[2], args[3], " ".join(args[4:]))
    elif cmd == "migrate":
        cmd_migrate(args[0])
    elif cmd == "check":
        src = opt("--sources")
        if not src:
            base = os.path.dirname(os.path.abspath(args[0]))
            for cand in (os.path.join(base, "work", "sources"), os.path.join(base, "sources")):
                if os.path.isdir(cand):
                    src = cand
                    print(f"INFO  checking quotes against {os.path.relpath(cand)}")
                    break
        e, w, i = check(load(args[0]), src)
        for x in w:
            print("WARN ", x)
        for x in e:
            print("ERROR", x)
        for x in i:
            print("INFO ", x)
        print(f"{len(e)} errors, {len(w)} warnings. check covers references, labels and formats; the audit "
              f"decides whether each claim is supported.")
        sys.exit(1 if e else 0)
    elif cmd == "attack":
        dom = opt("--domain")
        words = [a for a in args if a != "--domain" and a != dom]
        if not words:
            sys.exit("usage: attack KEYWORD [KEYWORD ...] [--domain enterprise|ics]")
        cmd_attack(words, dom)
    elif cmd == "publish":
        cmd_publish(load(args[0]), args[1])
    elif cmd == "html":
        cmd_html(load(args[0]), args[1])
    elif cmd == "diff":
        cmd_diff(load(args[0]), load(args[1]))
    elif cmd == "stix":
        cmd_stix(load(args[0]), args[1])
    elif cmd == "navigator":
        cmd_navigator(load(args[0]), args[1])
    elif cmd == "verify-docx":
        n = opt("--images")
        cmd_verify_docx(args[0], opt("--tracker"), int(n) if n else None)
    else:
        sys.exit(f"unknown command {cmd}\n{__doc__}")


if __name__ == "__main__":
    main(sys.argv)
