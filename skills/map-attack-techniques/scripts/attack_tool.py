#!/usr/bin/env python3
"""
attack_tool.py - helper for the map-attack-techniques skill (v2).

Subcommands
  version [--history-version X.Y]
        Resolve the latest Enterprise, ICS and Mobile ATT&CK versions from the
        attack-stix-data collection index, plus the current Navigator release.
        With --history-version (the version read from a LIVE fetch of
        https://attack.mitre.org/resources/versions/), also prints the
        version-disagreement decision the skill must follow.
  tactics [--domain D]
        Tactics (shortname, ID, name) in matrix order for a domain.
  lookup ID [ID ...] [--domain D]
        Resolve technique IDs: name, tactics, status (current / revoked /
        deprecated / not found), replacement for revoked IDs, created date,
        and how many groups, campaigns and software use it (diagnosticity).
        T0### IDs are resolved against ICS automatically.
  verify-quotes MAPPINGS
        Check every quote in a mappings file against the source text files
        named in sources[].text_path. PASS / FAIL / NOT CHECKED per quote.
  build-layer MAPPINGS -o OUT [--domain D]
        Build one ATT&CK Navigator layer (format 4.5) for one domain from a
        mappings file. Validates IDs, names and tactics against the pinned
        release, checks quotes and source-ID reconciliation, and prints a
        named check report. Writes nothing if any check FAILS.
  validate LAYER
        Re-check a layer file and print the same named check report.
  build-comparison-layer MAPPINGS FEEDLY_CONTEXT -o OUT [--domain D]
        Optional (Step 8). Build a Feedly comparison layer for one domain from
        the mappings file and feedly-context.json: each technique is grouped as
        Corroborated, New for this entity, or Not in this report. Context only,
        never a mapping. Checks ATT&CK content; quote verification and source
        ID reconciliation are NOT APPLICABLE. Writes nothing if a check FAILS.
  export-stix MAPPINGS -o OUT
        Optional STIX 2.1 bundle: one note per mapping (all quotes, confidence,
        occurrence) referencing the ATT&CK attack-pattern objects.

Common options
  --attack-version X.Y   Pin a release instead of the latest in the index.
  --bundle PATH          Use a local STIX bundle for the selected domain.
  --offline              No network. ATT&CK content checks report NOT CHECKED.

Only the Python standard library is used. Bundles are cached in
~/.cache/map-attack-techniques/ (Enterprise about 55 MB, ICS about 4 MB).

Global options may go before or after the subcommand.
Check results are always one of PASS, FAIL, NOT CHECKED or NOT APPLICABLE.
Quote verification and the layer's ATT&CK content check cover the domain being
built; source ID reconciliation always covers the whole mappings file.
This tool never claims a check it did not run: it does not run the full
Navigator layer schema and cannot import a layer into the Navigator.
"""
import argparse
import datetime as _dt
import json
import os
import re
import sys
import unicodedata
import urllib.request
import uuid

INDEX_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/index.json"
NAV_PKG_URL = "https://raw.githubusercontent.com/mitre-attack/attack-navigator/master/nav-app/package.json"
NAV_FALLBACK_VERSION = "5.3.2"  # latest known when this helper was written
LAYER_FORMAT = "4.5"
CACHE_DIR = os.path.expanduser("~/.cache/map-attack-techniques")

# key -> (collection name in index, Navigator domain, kill_chain_name)
DOMAINS = {
    "enterprise": ("Enterprise ATT&CK", "enterprise-attack", "mitre-attack"),
    "ics": ("ICS ATT&CK", "ics-attack", "mitre-ics-attack"),
    "mobile": ("Mobile ATT&CK", "mobile-attack", "mitre-mobile-attack"),
}

CONF_SCORE = {"high": 100, "moderate": 66, "low": 33}
CONF_COLOR = {"high": "#8ec843", "moderate": "#ffe766", "low": "#ff6666"}
CONF_RANK = {"low": 1, "moderate": 2, "high": 3}
CONF_STIX = {"high": 85, "moderate": 50, "low": 15}  # STIX 2.1 Appendix A, High/Med/Low scale
OCCURRENCE = {
    "observed": "Observed by the source author",
    "reported": "Reported to the source author by a third party",
    "source-assessed": "Assessed by the source author, not directly observed",
    "capability-only": "Capability described (code, tool, kit); execution against a victim not established",
}
PARENT_NEUTRAL_COLOR = "#a6cee3"
TID_RE = re.compile(r"^T\d{4}(\.\d{3})?$")
HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
DEFAULT_GENERATED_BY = ("map-attack-techniques skill. Model-made claims: review each mapping "
                        "against its quotes before distribution.")

PASS, FAIL, NC, NA = "PASS", "FAIL", "NOT CHECKED", "NOT APPLICABLE"


# --------------------------------------------------------------------------- helpers
def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "map-attack-techniques-skill"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _vtuple(v):
    return tuple(int(p) for p in str(v).split(".") if p.isdigit())


def domain_of(tid, default="enterprise"):
    return "ics" if re.match(r"^T0\d{3}$", tid or "") else default


def _mdomain(m):
    return (m.get("domain") or domain_of((m.get("technique_id") or "").strip().upper())).strip().lower()


def _norm_conf(c):
    c = (c or "").strip().lower()
    c = {"med": "moderate", "medium": "moderate", "m": "moderate", "h": "high", "l": "low"}.get(c, c)
    if c not in CONF_SCORE:
        raise ValueError(f"confidence must be high / moderate / low, got {c!r}")
    return c


def _tech_url(tid):
    return f"https://attack.mitre.org/techniques/{tid.replace('.', '/')}/"


def _quotes(m):
    """Normalise a mapping's evidence to a list of {text, locator, source_ref}."""
    qs = m.get("quotes")
    if qs is None and m.get("quote"):  # v1 schema
        qs = [{"text": m["quote"], "locator": m.get("source", "")}]
    out = []
    for q in qs or []:
        if isinstance(q, str):
            q = {"text": q}
        out.append({"text": (q.get("text") or "").strip(), "locator": (q.get("locator") or "").strip(),
                    "source_ref": q.get("source_ref", m.get("source_ref"))})
    return out


# --------------------------------------------------------------------------- versions / bundles
def load_index():
    return json.loads(_get(INDEX_URL))


def resolve_version(domain="enterprise", requested=None, index=None):
    idx = index or load_index()
    cname = DOMAINS[domain][0]
    coll = next(c for c in idx["collections"] if c["name"] == cname)
    versions = coll["versions"]
    if requested:
        match = [v for v in versions if v["version"] == requested]
        if not match:
            raise SystemExit(f"{cname} version {requested} has no bundle in the collection index. "
                             f"Available: {', '.join(v['version'] for v in versions[:8])} ...")
        v = match[0]
    else:
        v = max(versions, key=lambda x: _vtuple(x["version"]))
    return {"domain": domain, "version": v["version"], "modified": v["modified"], "url": v["url"]}


def navigator_version():
    try:
        return json.loads(_get(NAV_PKG_URL, timeout=30))["version"], "github package.json"
    except Exception:
        return NAV_FALLBACK_VERSION, "fallback (could not reach GitHub)"


def version_decision(index_ver, history_ver):
    """The rule from SKILL.md Step 2: always map against a version whose bundle exists."""
    if not history_ver:
        return {"status": "History page NOT CHECKED",
                "map_against": index_ver,
                "action": "Read the Version History page with a live fetch (not a search snippet) "
                          "and re-run with --history-version. Until then mark section 0 'History page NOT CHECKED'."}
    a, b = _vtuple(index_ver), _vtuple(history_ver)
    if a == b:
        return {"status": "Verified against both sources", "map_against": index_ver, "action": "Proceed."}
    if b > a:
        return {"status": "Sources disagree", "map_against": index_ver,
                "action": f"History page reports {history_ver} but the index only has a bundle for "
                          f"{index_ver}. Map and validate against {index_ver}, state the discrepancy in "
                          f"section 0, and say that {history_ver} content was NOT CHECKED. Do not label "
                          f"the mapping as {history_ver}."}
    return {"status": "Sources disagree", "map_against": index_ver,
            "action": f"Index has {index_ver}, history page shows {history_ver} (page likely not yet "
                      f"updated). Map against {index_ver} and state the discrepancy in section 0."}


def load_bundle(args, domain):
    """Return (bundle or None, info, reason_if_none)."""
    if args.bundle:
        with open(args.bundle) as f:
            b = json.load(f)
        ver = args.attack_version or _bundle_version(b) or "unknown"
        return b, {"domain": domain, "version": ver, "modified": None, "url": args.bundle}, None
    if args.offline:
        return None, {"domain": domain, "version": args.attack_version, "modified": None, "url": None}, \
            "offline mode"
    try:
        info = resolve_version(domain, args.attack_version)
    except SystemExit:
        raise
    except Exception as e:
        return None, {"domain": domain, "version": args.attack_version, "modified": None, "url": None}, \
            f"could not read the collection index ({e.__class__.__name__})"
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{DOMAINS[domain][1]}-{info['version']}.json")
    if not os.path.exists(path):
        print(f"Downloading {DOMAINS[domain][0]} {info['version']} STIX bundle ...", file=sys.stderr)
        try:
            data = _get(info["url"], timeout=300)
        except Exception as e:
            return None, info, f"could not download the {info['version']} bundle ({e.__class__.__name__})"
        with open(path + ".tmp", "wb") as f:
            f.write(data)
        os.replace(path + ".tmp", path)
    with open(path) as f:
        return json.load(f), info, None


def _bundle_version(b):
    for o in b.get("objects", []):
        if o.get("type") == "x-mitre-collection":
            return o.get("x_mitre_version")
    return None


def _ext_id(o):
    for r in o.get("external_references", []):
        if r.get("source_name") in ("mitre-attack", "mitre-ics-attack", "mitre-mobile-attack"):
            return r.get("external_id"), r.get("url")
    return None, None


class Attack:
    def __init__(self, bundle, domain="enterprise"):
        self.domain = domain
        kcn = DOMAINS[domain][2]
        objs = bundle["objects"]
        by_stix = {o["id"]: o for o in objs}
        self.tech = {}
        for o in objs:
            if o.get("type") != "attack-pattern":
                continue
            tid, url = _ext_id(o)
            if not tid:
                continue
            rec = {
                "id": tid, "name": o.get("name"),
                "url": url or _tech_url(tid),
                "tactics": [k["phase_name"] for k in o.get("kill_chain_phases", [])
                            if k.get("kill_chain_name") == kcn],
                "is_subtechnique": bool(o.get("x_mitre_is_subtechnique")),
                "revoked": bool(o.get("revoked")),
                "deprecated": bool(o.get("x_mitre_deprecated")),
                "stix_id": o["id"], "created": (o.get("created") or "")[:10],
                "obj": o,
            }
            prev = self.tech.get(tid)
            if prev is None or (prev["revoked"] or prev["deprecated"]) and not (rec["revoked"] or rec["deprecated"]):
                self.tech[tid] = rec
        stix_to_tid = {}
        for o in objs:
            if o.get("type") == "attack-pattern":
                t, _ = _ext_id(o)
                if t:
                    stix_to_tid[o["id"]] = t
        self.revoked_by, self.used_by = {}, {}
        live = lambda o: o is not None and not o.get("revoked") and not o.get("x_mitre_deprecated")
        for o in objs:
            if o.get("type") != "relationship":
                continue
            if o.get("relationship_type") == "revoked-by":
                src = stix_to_tid.get(o["source_ref"])
                tgt_obj = by_stix.get(o["target_ref"])
                if src and tgt_obj:
                    self.revoked_by[src] = _ext_id(tgt_obj)[0]
            elif o.get("relationship_type") == "uses" and live(o):
                tgt = stix_to_tid.get(o["target_ref"])
                src = by_stix.get(o["source_ref"])
                if tgt and live(src):
                    kind = {"intrusion-set": "groups", "campaign": "campaigns",
                            "malware": "software", "tool": "software"}.get(src["type"])
                    if kind:
                        self.used_by.setdefault(tgt, {"groups": set(), "campaigns": set(), "software": set()})
                        self.used_by[tgt][kind].add(src["id"])
        matrix = next((o for o in objs if o.get("type") == "x-mitre-matrix"
                       and not o.get("revoked") and not o.get("x_mitre_deprecated")), None)
        tac_objs = {o["id"]: o for o in objs if o.get("type") == "x-mitre-tactic"}
        order = matrix["tactic_refs"] if matrix else list(tac_objs)
        self.tactics = []
        for ref in order:
            t = tac_objs.get(ref)
            if t and not t.get("revoked") and not t.get("x_mitre_deprecated"):
                self.tactics.append({"shortname": t["x_mitre_shortname"], "id": _ext_id(t)[0], "name": t["name"]})
        self.tactic_order = {t["shortname"]: i for i, t in enumerate(self.tactics)}

    def lookup(self, tid):
        tid = tid.strip().upper()
        rec = self.tech.get(tid)
        if rec is None:
            return {"id": tid, "domain": self.domain, "status": "not found"}
        out = {k: rec[k] for k in ("id", "name", "url", "tactics", "is_subtechnique", "created")}
        out["domain"] = self.domain
        u = self.used_by.get(tid, {})
        out["used_by"] = {k: len(u.get(k, ())) for k in ("groups", "campaigns", "software")}
        if rec["revoked"]:
            out["status"] = "revoked"
            out["replaced_by"] = self.revoked_by.get(tid)
            if out["replaced_by"] and out["replaced_by"] in self.tech:
                r = self.tech[out["replaced_by"]]
                out["replaced_by_name"] = r["name"]
                out["replaced_by_tactics"] = r["tactics"]
        elif rec["deprecated"]:
            out["status"] = "deprecated"
        else:
            out["status"] = "current"
        return out


# --------------------------------------------------------------------------- quote verification
_QMAP = {"‘": "'", "’": "'", "‚": "'", "‛": "'", "“": '"', "”": '"',
         "„": '"', " ": " ", "–": "-", "—": "-", "−": "-", "­": ""}


def _norm_text(s):
    s = unicodedata.normalize("NFKC", s or "")
    s = "".join(_QMAP.get(ch, ch) for ch in s)
    s = re.sub(r"-\s*\n\s*", "-", s)   # hyphen split across a line
    return re.sub(r"\s+", " ", s).strip()


MIN_QUOTE_WORDS = 4


def quote_in_text(quote, text):
    """Exact match after whitespace and typographic normalisation, on word boundaries.
    '[...]' or '...' marks an omission: each segment must appear, in order."""
    nt = _norm_text(text)
    segs = [p.strip() for p in re.split(r"\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…", _norm_text(quote)) if p.strip()]
    pos = 0
    for seg in segs:
        m = re.compile(r"(?<![0-9A-Za-z])" + re.escape(seg) + r"(?![0-9A-Za-z])").search(nt, pos)
        if not m:
            return False
        pos = m.end()
    return bool(segs)


def quote_too_short(quote):
    words = re.findall(r"[0-9A-Za-z][^\s]*", re.sub(r"\[\s*(?:\.\.\.|\u2026)\s*\]", " ", quote or ""))
    return len(words) < MIN_QUOTE_WORDS


def verify_quotes(spec, base_dir=".", domain=None):
    """Return (status, detail list). status is PASS / FAIL / NOT CHECKED."""
    sources = spec.get("sources") or ([spec["source"]] if spec.get("source") else [])
    texts = {}
    for i, s in enumerate(sources):
        sid = str(s.get("id", i + 1))
        p = s.get("text_path")
        if p:
            p = p if os.path.isabs(p) else os.path.join(base_dir, p)
            if os.path.exists(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    texts[sid] = f.read()
    default_sid = (str(sources[0].get("id", "1")) if sources else None)
    detail, n_pass, n_fail, n_nc = [], 0, 0, 0
    for i, m in enumerate(spec.get("mappings", []), 1):
        if domain and _mdomain(m) != domain:
            continue
        for j, q in enumerate(_quotes(m), 1):
            sid = str(q.get("source_ref") or default_sid)
            if quote_too_short(q["text"]):
                st = FAIL
                n_fail += 1
            elif sid not in texts:
                st = NC
                n_nc += 1
            elif quote_in_text(q["text"], texts[sid]):
                st = PASS
                n_pass += 1
            else:
                st = FAIL
                n_fail += 1
            detail.append({"mapping": m.get("ref", str(i)), "quote": j, "source": sid, "result": st,
                           "why": f"shorter than {MIN_QUOTE_WORDS} words: quote the full passage"
                           if quote_too_short(q["text"]) else ""})
    total = n_pass + n_fail + n_nc
    if total == 0:
        return NA, detail, "no quotes"
    if n_fail:
        return FAIL, detail, f"{n_fail} of {total} quotes not found verbatim or too short"
    if n_nc:
        return NC, detail, \
            f"{n_pass} of {total} verified; {n_nc} NOT CHECKED (no source text supplied)"
    return PASS, detail, f"{n_pass} of {total} quotes found verbatim"


# --------------------------------------------------------------------------- layer building
def mapping_errors(m, ref):
    errs = []
    if not _quotes(m) or not all(q["text"] for q in _quotes(m)):
        errs.append(f"mapping {ref}: no verbatim quote. If you cannot quote it, you cannot map it.")
    elif not all(q["locator"] for q in _quotes(m)):
        errs.append(f"mapping {ref}: every quote needs a locator (section, page, heading or paragraph).")
    occ = (m.get("occurrence") or "").strip().lower()
    if occ not in OCCURRENCE:
        errs.append(f"mapping {ref}: occurrence must be one of {', '.join(OCCURRENCE)}; got {occ!r}")
    return errs


RECON_STATUSES = ("current", "renamed", "revoked", "deprecated", "merged", "refined to sub-technique",
                  "generalised to parent", "not supported by the narrative",
                  "not in the matrix the source claims", "profile claim, not incident claim")


def reconciliation_check(spec):
    cited = [c.strip().upper() for c in spec.get("source_cited_ids", [])]
    rec = [r.get("id", "").strip().upper() for r in spec.get("reconciliation", [])]
    if "source_cited_ids" not in spec:
        return NC, "source_cited_ids not stated in the mappings file"
    if not cited:
        return NA, "the source cites 0 ATT&CK IDs"
    missing = sorted(set(cited) - set(rec))
    dup = sorted({r for r in rec if rec.count(r) > 1})
    extra = sorted(set(rec) - set(cited))
    bad = sorted(r.get("id", "?") for r in spec.get("reconciliation", [])
                 if not str(r.get("disposition", "")).strip().lower().startswith(RECON_STATUSES))
    if missing or dup or extra or bad:
        bits = []
        if missing:
            bits.append("not reconciled: " + ", ".join(missing))
        if dup:
            bits.append("reconciled more than once: " + ", ".join(dup))
        if extra:
            bits.append("reconciled but not cited: " + ", ".join(extra))
        if bad:
            bits.append("disposition missing or not a section 2 status: " + ", ".join(bad))
        return FAIL, "; ".join(bits)
    return PASS, f"{len(set(cited))} cited, {len(set(rec))} reconciled, each once"


def build_layer(spec, attack, info, nav_ver, domain):
    errors, warnings = [], []
    min_conf = _norm_conf(spec.get("min_confidence", "low"))
    parent_mode = spec.get("parent_highlight", "none")
    if parent_mode not in ("neutral", "match", "none"):
        errors.append("parent_highlight must be neutral, match or none")
    include_rationale = spec.get("include_rationale_in_comments", True)
    sources = spec.get("sources") or ([spec["source"]] if spec.get("source") else [])
    pub_by_id = {str(s.get("id", i + 1)): s.get("published") for i, s in enumerate(sources)}
    default_sid = str(sources[0].get("id", 1)) if sources else None
    all_refs = [str(m.get("ref", i)) for i, m in enumerate(spec.get("mappings", []), 1)]
    for r in sorted({r for r in all_refs if all_refs.count(r) > 1}):
        errors.append(f"ref {r} is used by more than one mapping; refs must be unique")

    entries = {}
    for i, m in enumerate(spec.get("mappings", []), 1):
        ref = str(m.get("ref", i))
        tid = (m.get("technique_id") or "").strip().upper()
        if _mdomain(m) != domain:
            continue
        if m.get("paired_with") and str(m["paired_with"]) not in all_refs:
            errors.append(f"mapping {ref}: paired_with {m['paired_with']!r} is not the ref of any mapping")
        tactic = (m.get("tactic") or "").strip().lower()
        try:
            conf = _norm_conf(m.get("confidence"))
        except ValueError as e:
            errors.append(f"mapping {ref}: {e}")
            continue
        if not TID_RE.match(tid):
            errors.append(f"mapping {ref}: technique_id {tid!r} is not T#### or T####.###")
            continue
        if not tactic:
            errors.append(f"mapping {ref}: tactic shortname is required")
            continue
        errors += mapping_errors(m, ref)
        if attack is not None:
            lk = attack.lookup(tid)
            if lk["status"] != "current":
                hint = f" (replaced by {lk.get('replaced_by')})" if lk.get("replaced_by") else ""
                errors.append(f"mapping {ref}: {tid} is {lk['status']} in {DOMAINS[domain][0]} {info['version']}{hint}")
                continue
            if tactic not in lk["tactics"]:
                errors.append(f"mapping {ref}: {tid} ({lk['name']}) does not sit under tactic "
                              f"'{tactic}' in {info['version']}; valid: {', '.join(lk['tactics'])}")
                continue
            given = (m.get("technique_name") or "").strip().lower()
            if given and given != lk["name"].lower() and given.split(":")[-1].strip() != lk["name"].lower():
                errors.append(f"mapping {ref}: name {m['technique_name']!r} does not match "
                              f"{tid} = {lk['name']!r} in {info['version']}")
                continue
            qsrc = {str(q.get("source_ref") or default_sid) for q in _quotes(m)}
            pubs = [pub_by_id[x] for x in qsrc if pub_by_id.get(x)]
            pub = max(pubs) if pubs else None
            if pub and lk.get("created") and lk["created"] > pub:
                warnings.append(f"mapping {ref}: {tid} was created in ATT&CK on {lk['created']}, after the "
                                f"source publication date {pub}. Record this under Source Issues "
                                f"(the source may have been revised without a new date).")
            name = lk["name"]
        else:
            if tactic not in KNOWN_TACTICS_FALLBACK.get(domain, set()):
                warnings.append(f"mapping {ref}: tactic '{tactic}' is not in the built-in {domain} v19 tactic "
                                f"list. Unverified offline: confirm it on attack.mitre.org.")
            name = m.get("technique_name", "")
        if CONF_RANK[conf] < CONF_RANK[min_conf]:
            continue
        key = (tid, tactic)
        e = entries.setdefault(key, {"tid": tid, "tactic": tactic, "name": name, "conf": conf,
                                     "items": [], "implied": False})
        if CONF_RANK[conf] > CONF_RANK[e["conf"]]:
            e["conf"] = conf
        e["items"].append({"ref": ref, "conf": conf, "quotes": _quotes(m),
                           "occurrence": (m.get("occurrence") or "").lower(),
                           "procedure": m.get("procedure", ""), "rationale": m.get("rationale", ""),
                           "paired_with": m.get("paired_with", "")})

    for (tid, tactic), e in list(entries.items()):
        if "." not in tid:
            continue
        pkey = (tid.split(".")[0], tactic)
        if pkey not in entries:
            pname = attack.lookup(pkey[0]).get("name", "") if attack else ""
            entries[pkey] = {"tid": pkey[0], "tactic": tactic, "name": pname, "conf": None,
                             "items": [], "implied": True}

    subs_by_parent = {}
    for (tid, tactic), e in entries.items():
        if "." in tid:
            subs_by_parent.setdefault((tid.split(".")[0], tactic), []).append(e)

    def first_ref(e):
        items = e["items"] + [it for k in subs_by_parent.get((e["tid"], e["tactic"]), []) for it in k["items"]]
        return min((int(it["ref"]) if str(it["ref"]).isdigit() else 9999) for it in items) if items else 9999

    techniques = []
    for e in sorted(entries.values(), key=lambda e: (first_ref(e), 0 if e["implied"] else 1, e["tid"])):
        tid, tactic = e["tid"], e["tactic"]
        kids = subs_by_parent.get((tid, tactic), [])
        t = {"techniqueID": tid, "tactic": tactic, "comment": "", "enabled": True,
             "metadata": [], "links": [{"label": f"ATT&CK {tid}", "url": _tech_url(tid)}],
             "showSubtechniques": bool(kids)}
        if e["implied"]:
            kid_ids = ", ".join(sorted(k["tid"] for k in kids))
            best = max((k["conf"] for k in kids), key=lambda c: CONF_RANK[c])
            t["comment"] = f"Display entry only, not a mapped procedure. Parent of mapped sub-technique(s): {kid_ids}."
            t["metadata"] = [{"name": "mapping", "value": "parent display entry (not a mapped procedure)"},
                             {"name": "sub-techniques", "value": kid_ids}]
            if parent_mode == "neutral":
                t["color"] = PARENT_NEUTRAL_COLOR
            elif parent_mode == "match":
                t["score"], t["color"] = CONF_SCORE[best], CONF_COLOR[best]
            else:
                t["color"] = ""
        else:
            conf = e["conf"]
            t["score"], t["color"] = CONF_SCORE[conf], CONF_COLOR[conf]
            parts = [f"Confidence: {conf.capitalize()}"]
            md = [{"name": "mapping", "value": "direct"}, {"name": "confidence", "value": conf}]
            for it in e["items"]:
                block = [f"Mapping #{it['ref']} ({it['conf'].capitalize()}; occurrence: {it['occurrence']})"]
                if it["procedure"]:
                    block.append(f"Procedure: {it['procedure']}")
                for n, q in enumerate(it["quotes"], 1):
                    block.append(f"Evidence {n}: \"{q['text']}\" [{q['locator']}]")
                if include_rationale and it["rationale"]:
                    block.append(f"Rationale: {it['rationale']}")
                if it["paired_with"]:
                    block.append(f"Cross-domain pair: mapping #{it['paired_with']}")
                parts.append("\n".join(block))
                md += [{"divider": True}, {"name": "mapping #", "value": it["ref"]},
                       {"name": "occurrence", "value": it["occurrence"]}]
                for n, q in enumerate(it["quotes"], 1):
                    md.append({"name": f"source_quote {n}", "value": q["text"]})
                    md.append({"name": f"source_locator {n}", "value": q["locator"]})
            t["comment"] = "\n\n".join(parts)
            t["metadata"] = md
        techniques.append(t)

    legend = [{"label": "High confidence", "color": CONF_COLOR["high"]},
              {"label": "Moderate confidence", "color": CONF_COLOR["moderate"]},
              {"label": "Low confidence", "color": CONF_COLOR["low"]}]
    if parent_mode == "neutral" and any(e["implied"] for e in entries.values()):
        legend.append({"label": "Parent of mapped sub-technique", "color": PARENT_NEUTRAL_COLOR})

    layer_md = []
    for s in sources:
        layer_md.append({"name": "source", "value": " | ".join(
            x for x in (s.get("title"), s.get("url"), ("published " + s["published"]) if s.get("published") else None,
                      ("reliability " + s["reliability"]) if s.get("reliability") else None) if x)})
    layer_md += [
        {"name": "ATT&CK version mapped", "value": f"{DOMAINS[domain][0]} {info.get('version')}"},
        {"name": "version verification", "value": spec.get("verification_status", "NOT STATED")},
        {"name": "version checked", "value": spec.get("version_checked", _dt.date.today().isoformat())},
        {"name": "minimum confidence shown", "value": min_conf},
        {"name": "generated", "value": _dt.date.today().isoformat()},
        {"name": "generated by", "value": spec.get("generated_by", DEFAULT_GENERATED_BY)},
    ]
    links = [{"label": s.get("title") or s["url"], "url": s["url"]} for s in sources
             if str(s.get("url", "")).startswith("http")]
    major = str(info["version"]).split(".")[0] if info.get("version") else None
    name = spec.get("layer_name") or "ATT&CK Technique Mapping"
    if spec.get("_multi_domain"):
        name = f"{name} ({DOMAINS[domain][0]})"
    layer = {
        "name": name,
        "versions": {"attack": major, "navigator": nav_ver, "layer": LAYER_FORMAT},
        "domain": DOMAINS[domain][1],
        "description": spec.get("description", ""),
        "sorting": 0,
        "layout": {"layout": "side", "showID": True, "showName": True, "showAggregateScores": False,
                   "countUnscored": False, "aggregateFunction": "average",
                   "expandedSubtechniques": "annotated"},
        "hideDisabled": False,
        "techniques": techniques,
        "gradient": {"colors": [CONF_COLOR["low"], CONF_COLOR["moderate"], CONF_COLOR["high"]],
                     "minValue": 0, "maxValue": 100},
        "legendItems": legend,
        "showTacticRowBackground": False,
        "tacticRowBackground": "#dddddd",
        "selectTechniquesAcrossTactics": True,
        "selectSubtechniquesWithParent": False,
        "selectVisibleTechniques": False,
        "metadata": layer_md,
        "links": links,
    }
    if "NOT VERIFIED" in str(spec.get("verification_status", "")).upper():
        layer_md.append({"name": "status", "value": "DRAFT: ATT&CK version NOT VERIFIED"})
    if attack is None:
        layer_md.append({"name": "status", "value": "DRAFT: ATT&CK content NOT CHECKED (no STIX bundle)"})
        warnings.append("ATT&CK content NOT CHECKED: IDs, names and tactics were not compared with a STIX "
                        "bundle. Treat the layer as a draft.")
    if major is None:
        del layer["versions"]["attack"]
        warnings.append("No ATT&CK version known: versions.attack omitted.")
    return layer, errors, warnings


KNOWN_TACTICS_FALLBACK = {  # v19 shortnames; used only to warn in offline mode
    "enterprise": {"reconnaissance", "resource-development", "initial-access", "execution", "persistence",
                   "privilege-escalation", "stealth", "defense-impairment", "credential-access", "discovery",
                   "lateral-movement", "collection", "command-and-control", "exfiltration", "impact"},
    "ics": {"initial-access", "execution", "persistence", "privilege-escalation", "evasion", "discovery",
            "lateral-movement", "collection", "command-and-control", "inhibit-response-function",
            "impair-process-control", "impact"},
    "mobile": {"initial-access", "execution", "persistence", "privilege-escalation", "defense-evasion",
               "credential-access", "discovery", "lateral-movement", "collection", "command-and-control",
               "exfiltration", "impact"},
}


# --------------------------------------------------------------------------- layer validation
def structure_errors(layer):
    errs = []

    def req(obj, key, typ, where):
        if key not in obj:
            errs.append(f"{where}: missing required '{key}'")
            return False
        if not isinstance(obj[key], typ):
            errs.append(f"{where}: '{key}' has the wrong type")
            return False
        return True

    if not isinstance(layer, dict):
        return ["layer must be a JSON object"]
    req(layer, "name", str, "layer")
    if req(layer, "domain", str, "layer") and layer["domain"] not in ("enterprise-attack", "mobile-attack", "ics-attack"):
        errs.append("layer: invalid domain")
    v = layer.get("versions")
    if not isinstance(v, dict):
        errs.append("versions must be an object")
    else:
        if v.get("layer") != LAYER_FORMAT:
            errs.append(f"versions.layer must be '{LAYER_FORMAT}'")
        if not isinstance(v.get("navigator"), str):
            errs.append("versions.navigator must be a string")
        if "attack" in v and not isinstance(v["attack"], str):
            errs.append("versions.attack must be a string")
    for k, typ in (("description", str), ("sorting", int), ("hideDisabled", bool), ("showTacticRowBackground", bool),
                   ("selectTechniquesAcrossTactics", bool), ("selectSubtechniquesWithParent", bool),
                   ("selectVisibleTechniques", bool), ("tacticRowBackground", str)):
        if k in layer and not isinstance(layer[k], typ):
            errs.append(f"layer: '{k}' must be {typ.__name__}")
    g = layer.get("gradient")
    if g is not None:
        if not isinstance(g.get("colors"), list) or len(g["colors"]) < 2:
            errs.append("gradient.colors must list at least two colours")
        elif not all(isinstance(c, str) and HEX_RE.match(c) for c in g["colors"]):
            errs.append("gradient.colors must be hex colours")
        if not (isinstance(g.get("minValue"), (int, float)) and isinstance(g.get("maxValue"), (int, float))
                and g["maxValue"] > g["minValue"]):
            errs.append("gradient min/max invalid")
    for i, li in enumerate(layer.get("legendItems", [])):
        if not isinstance(li.get("label"), str) or not isinstance(li.get("color"), str) or not HEX_RE.match(li["color"]):
            errs.append(f"legendItems[{i}] needs string label and hex color")
    seen = set()
    for i, t in enumerate(layer.get("techniques", [])):
        w = f"techniques[{i}]"
        if not req(t, "techniqueID", str, w):
            continue
        if not TID_RE.match(t["techniqueID"]):
            errs.append(f"{w}: bad techniqueID {t['techniqueID']}")
        key = (t["techniqueID"], t.get("tactic"))
        if key in seen:
            errs.append(f"{w}: duplicate entry for {key[0]} / {key[1]}")
        seen.add(key)
        if "score" in t and not isinstance(t["score"], (int, float)):
            errs.append(f"{w}: score must be a number")
        if t.get("color") not in (None, "") and not (isinstance(t["color"], str) and HEX_RE.match(t["color"])):
            errs.append(f"{w}: color must be hex or empty")
        for k, typ in (("comment", str), ("enabled", bool), ("showSubtechniques", bool), ("tactic", str)):
            if k in t and not isinstance(t[k], typ):
                errs.append(f"{w}: '{k}' must be {typ.__name__}")
        for j, m in enumerate(t.get("metadata", [])):
            if not (m.get("divider") is True or (isinstance(m.get("name"), str) and isinstance(m.get("value"), str))):
                errs.append(f"{w}.metadata[{j}] needs string name/value or divider:true")
        for j, l in enumerate(t.get("links", [])):
            if not (l.get("divider") is True or (isinstance(l.get("label"), str)
                                                  and str(l.get("url", "")).startswith(("http://", "https://")))):
                errs.append(f"{w}.links[{j}] needs label and http(s) url")
    ids = {(t.get("techniqueID"), t.get("tactic")): t for t in layer.get("techniques", [])}
    for (tid, tac) in ids:
        if tid and "." in tid:
            p = ids.get((tid.split(".")[0], tac))
            if p is None or not p.get("showSubtechniques"):
                errs.append(f"{tid} ({tac}): parent entry with showSubtechniques:true is missing")
    return errs


def content_errors(layer, attack):
    errs = []
    for i, t in enumerate(layer.get("techniques", [])):
        tid = t.get("techniqueID", "")
        lk = attack.lookup(tid)
        if lk["status"] != "current":
            errs.append(f"techniques[{i}]: {tid} is {lk['status']}")
        elif t.get("tactic") and t["tactic"] not in lk["tactics"]:
            errs.append(f"techniques[{i}]: {tid} not under tactic {t['tactic']} (valid: {', '.join(lk['tactics'])})")
    return errs


def layer_counts(layer):
    ts = layer.get("techniques", [])
    if any(m.get("name") == "layer type" and str(m.get("value", "")).startswith("Feedly comparison")
           for m in layer.get("metadata", [])):
        groups = {g: 0 for g in CMP_ORDER}
        for t in ts:
            for m in t.get("metadata", []):
                if m.get("name") == "group" and m.get("value") in groups:
                    groups[m["value"]] += 1
        parents = sum(1 for t in ts if any(str(m.get("value", "")).startswith("parent display entry")
                                           for m in t.get("metadata", [])))
        return {"comparison": groups, "parent_display_entries": parents, "total_layer_entries": len(ts)}
    parents = sum(1 for t in ts if any(str(m.get("value", "")).startswith("parent display entry")
                                       or m.get("value") == "implied by sub-technique" for m in t.get("metadata", [])))
    refs = set()
    for t in ts:
        for m in t.get("metadata", []):
            if m.get("name") == "mapping #":
                refs.add(m["value"])
    return {"direct_mappings": len(refs), "direct_layer_entries": len(ts) - parents,
            "parent_display_entries": parents, "total_layer_entries": len(ts)}


def print_report(title, checks, counts=None, warnings=(), errors=()):
    print(f"== {title} ==")
    width = max(len(c[0]) for c in checks)
    for name, status, note in checks:
        print(f"  {name.ljust(width)}  {status}" + (f"  ({note})" if note else ""))
    if counts and "comparison" in counts:
        g = counts["comparison"]
        print("  Counts (layer entries by group): " + "; ".join(f"{k}: {v}" for k, v in g.items()) +
              f"; {counts['parent_display_entries']} parent display entr"
              f"{'y' if counts['parent_display_entries'] == 1 else 'ies'}; context only, not mappings.")
        for line in counts.get("per_entity", []):
            print("   ", line)
    elif counts:
        print(f"  Counts: {counts['direct_mappings']} direct mapping(s) in "
              f"{counts['direct_layer_entries']} coloured entr{'y' if counts['direct_layer_entries'] == 1 else 'ies'}; "
              f"{counts['parent_display_entries']} parent display entr{'y' if counts['parent_display_entries'] == 1 else 'ies'} "
              f"(not mapped procedures); {counts['total_layer_entries']} layer entries in total.")
    for w in warnings:
        print("  WARNING:", w)
    for e in errors:
        print("  ERROR:", e)
    failed = any(s == FAIL for _, s, _ in checks)
    if failed:
        print("  RESULT: FAIL. Fix the mapping, not the check, and re-run.")
    else:
        passed = [n for n, s, _ in checks if s == PASS]
        unchecked = [n for n, s, _ in checks if s == NC]
        print("  RESULT: passed: " + (", ".join(passed) or "none") +
              (". Not checked: " + ", ".join(unchecked) if unchecked else "") + ".")
    return not failed


# --------------------------------------------------------------------------- Feedly comparison layer
CMP_CORR, CMP_NEW, CMP_NOT = "Corroborated", "New for this entity", "Not in this report"
CMP_ORDER = (CMP_CORR, CMP_NEW, CMP_NOT)
CMP_COLOR = {CMP_CORR: "#3d7ecb", CMP_NEW: "#a05eb5", CMP_NOT: "#c2c2c2"}
CMP_SCORE = {CMP_CORR: 100, CMP_NEW: 66, CMP_NOT: 33}
CMP_MIN_ARTICLES = 2
CMP_TOP_N = 25


def _parent(tid):
    return tid.split(".")[0]


def _related(a, b):
    """Same technique, or parent and one of its sub-techniques (parent-level match)."""
    if a == b:
        return "exact"
    if "." in a and "." not in b and _parent(a) == b:
        return "parent-level"
    if "." in b and "." not in a and _parent(b) == a:
        return "parent-level"
    return None


def build_comparison_layer(spec, ctx, attack, info, nav_ver, domain):
    errors, warnings, input_errs = [], [], []
    min_conf = _norm_conf(spec.get("min_confidence", "low"))
    window = ctx.get("window") or {}
    win = f"{window.get('start', '?')} to {window.get('end', '?')}"
    qdate = ctx.get("query_date", "")
    ents = [e.get("feedly_entity") for e in ctx.get("entities", []) if e.get("feedly_entity")]
    attrib = {e.get("feedly_entity"): (e.get("attribution") or "") for e in ctx.get("entities", [])}
    if not ents:
        input_errs.append("feedly context: no entities with a feedly_entity")
    if not qdate or not window.get("start") or not window.get("end"):
        input_errs.append("feedly context: query_date and window.start / window.end are required (R6.5)")

    # mapped techniques in this domain, at or above the threshold
    mapped = {}  # tid -> list of {ref, conf, tactic}
    for i, m in enumerate(spec.get("mappings", []), 1):
        if _mdomain(m) != domain:
            continue
        tid = (m.get("technique_id") or "").strip().upper()
        try:
            conf = _norm_conf(m.get("confidence"))
        except ValueError:
            continue
        if not TID_RE.match(tid) or CONF_RANK[conf] < CONF_RANK[min_conf]:
            continue
        mapped.setdefault(tid, []).append({"ref": str(m.get("ref", i)), "conf": conf,
                                           "tactic": (m.get("tactic") or "").strip().lower()})

    # profile rows in this domain, per entity
    prof = {}
    for n, r in enumerate(ctx.get("profile", [])):
        tid = (r.get("technique_id") or "").strip().upper()
        dom = (r.get("domain") or domain_of(tid)).strip().lower()
        if dom != domain:
            continue
        ent = r.get("entity")
        if ent not in ents:
            input_errs.append(f"profile[{n}]: entity {ent!r} is not in entities[].feedly_entity")
            continue
        if not TID_RE.match(tid):
            input_errs.append(f"profile[{n}]: technique_id {tid!r} is not T#### or T####.###")
            continue
        if not isinstance(r.get("article_count"), int) or r["article_count"] < 0:
            input_errs.append(f"profile[{n}]: article_count must be a whole number")
            continue
        prof.setdefault(ent, []).append(dict(r, technique_id=tid))

    cells = {}  # (tid, tactic) -> {"tid","tactic","results":[...], "refs": [...]}

    def cell(tid, tactic):
        return cells.setdefault((tid, tactic), {"tid": tid, "tactic": tactic, "results": [], "refs": []})

    for tid, items in mapped.items():
        for it in items:
            c = cell(tid, it["tactic"])
            c["refs"].append(it)

    per_entity = []
    for ent in ents:
        rows = prof.get(ent, [])
        counts = {g: 0 for g in CMP_ORDER}
        matched_feedly = set()
        for tid in mapped:
            hits = [(r, _related(r["technique_id"], tid)) for r in rows]
            hits = [(r, k) for r, k in hits if k]
            for tac in {it["tactic"] for it in mapped[tid]}:
                c = cell(tid, tac)
                if hits:
                    n = sum(r["article_count"] for r, _ in hits)
                    arts = sorted((a for r, _ in hits for a in r.get("articles", [])),
                                  key=lambda a: a.get("date", ""), reverse=True)
                    c["results"].append({"entity": ent, "group": CMP_CORR, "count": n, "articles": arts,
                                         "parent_level": any(k == "parent-level" for _, k in hits)})
                else:
                    c["results"].append({"entity": ent, "group": CMP_NEW, "count": 0, "articles": [],
                                         "parent_level": False})
            if hits:
                counts[CMP_CORR] += 1
                matched_feedly |= {r["technique_id"] for r, _ in hits}
            else:
                counts[CMP_NEW] += 1
        rest = [r for r in rows if r["technique_id"] not in matched_feedly]
        listed = sorted((r for r in rest if r["article_count"] >= CMP_MIN_ARTICLES),
                        key=lambda r: (-r["article_count"], r["technique_id"]))[:CMP_TOP_N]
        unlisted = len(rest) - len(listed)
        counts[CMP_NOT] = len(listed)
        for r in listed:
            tid = r["technique_id"]
            tacs = [r["tactic"].strip().lower()] if r.get("tactic") else []
            if not tacs:
                if attack is not None and attack.lookup(tid).get("tactics"):
                    tacs = attack.lookup(tid)["tactics"]
                else:
                    input_errs.append(f"profile {ent} {tid}: tactic missing and no STIX bundle to fill it")
                    continue
            arts = sorted(r.get("articles", []), key=lambda a: a.get("date", ""), reverse=True)
            for tac in tacs:
                cell(tid, tac)["results"].append({"entity": ent, "group": CMP_NOT, "count": r["article_count"],
                                                  "articles": arts, "parent_level": False})
        per_entity.append(f"{ent}: {counts[CMP_CORR]} corroborated, {counts[CMP_NEW]} new for this entity, "
                          f"{counts[CMP_NOT]} not in this report (listed), {unlisted} further not listed "
                          f"(fewer than {CMP_MIN_ARTICLES} articles or beyond the top {CMP_TOP_N})")

    # ATT&CK content
    content_errs = []
    names = {}
    for (tid, tac) in cells:
        if attack is None:
            continue
        lk = attack.lookup(tid)
        if lk["status"] != "current":
            hint = f" (replaced by {lk.get('replaced_by')})" if lk.get("replaced_by") else ""
            content_errs.append(f"{tid} is {lk['status']} in {DOMAINS[domain][0]} {info['version']}{hint}; "
                                f"replace it or list it as not comparable")
        elif tac not in lk["tactics"]:
            content_errs.append(f"{tid} ({lk['name']}) does not sit under tactic '{tac}'; "
                                f"valid: {', '.join(lk['tactics'])}")
        else:
            names[tid] = lk["name"]

    # parent display entries
    for (tid, tac) in list(cells):
        if "." in tid and (_parent(tid), tac) not in cells:
            cells[(_parent(tid), tac)] = {"tid": _parent(tid), "tactic": tac, "results": [], "refs": [],
                                          "implied": True}

    def best(c):
        gs = [r["group"] for r in c["results"]]
        return next((g for g in CMP_ORDER if g in gs), None)

    techniques = []
    order = attack.tactic_order if attack is not None else {}
    for c in sorted(cells.values(), key=lambda c: (order.get(c["tactic"], 99), c["tid"])):
        tid, tac = c["tid"], c["tactic"]
        has_kids = any(k[0] != tid and _parent(k[0]) == tid and k[1] == tac for k in cells)
        t = {"techniqueID": tid, "tactic": tac, "enabled": True, "showSubtechniques": has_kids,
             "links": [{"label": f"ATT&CK {tid}", "url": _tech_url(tid)}]}
        g = best(c)
        if c.get("implied") or g is None:
            t["color"] = ""
            t["comment"] = "Display entry only, not a mapped procedure and not a Feedly result."
            t["metadata"] = [{"name": "mapping", "value": "parent display entry (not a mapped procedure)"}]
            techniques.append(t)
            continue
        t["score"], t["color"] = CMP_SCORE[g], CMP_COLOR[g]
        parts = [f"Group: {g} (Feedly Threat Graph, queried {qdate}, window {win}). Context only, not a mapping."]
        if c["refs"]:
            parts.append("In this mapping: " + "; ".join(f"mapping #{r['ref']} ({r['conf'].capitalize()})"
                                                        for r in c["refs"]))
        md = [{"name": "group", "value": g}, {"name": "feedly window", "value": win}]
        links = []
        for r in c["results"]:
            if r["group"] == CMP_CORR:
                line = f"{r['entity']}: Corroborated. Also reported for {r['entity']} in {r['count']} other article(s)"
                if r["parent_level"]:
                    line += " (parent-level match)"
            elif r["group"] == CMP_NEW:
                line = f"{r['entity']}: New for this entity. Not in Feedly's {r['entity']} profile for {win}"
            else:
                line = (f"{r['entity']}: Not in this report. Reported for {r['entity']} elsewhere; not observed "
                        f"in this source ({r['count']} article(s))")
            if "tentative" in attrib.get(r["entity"], "").lower():
                line += f". The source's attribution of this activity to {r['entity']} is tentative, so this comparison is too"
            titles = [f"\"{a.get('title', '')}\" ({a.get('publisher', '')}, {a.get('date', '')})"
                      for a in r["articles"][:3]]
            if titles:
                line += ". Articles: " + "; ".join(titles)
            parts.append(line + ".")
            md += [{"divider": True}, {"name": "entity", "value": r["entity"]},
                   {"name": "entity group", "value": r["group"]},
                   {"name": "feedly article count", "value": str(r["count"])}]
            for a in r["articles"][:3]:
                u = str(a.get("url", ""))
                if u.startswith(("http://", "https://")) and len(links) < 3 and u not in [l["url"] for l in links]:
                    links.append({"label": (a.get("title") or "Feedly article")[:80], "url": u})
        for r in c["refs"]:
            md.append({"name": "mapping #", "value": r["ref"]})
        t["comment"] = "\n\n".join(parts)
        t["metadata"] = md
        t["links"] += links
        techniques.append(t)

    sources = spec.get("sources") or []
    layer_md = [{"name": "source", "value": " | ".join(
        x for x in (s.get("title"), s.get("url"), ("published " + s["published"]) if s.get("published") else None)
        if x)} for s in sources]
    layer_md += [
        {"name": "layer type", "value": "Feedly comparison (context only, not a mapping)"},
        {"name": "ATT&CK version mapped", "value": f"{DOMAINS[domain][0]} {info.get('version')}"},
        {"name": "version verification", "value": spec.get("verification_status", "NOT STATED")},
        {"name": "minimum confidence shown", "value": min_conf},
        {"name": "feedly query date", "value": qdate},
        {"name": "feedly window", "value": win},
        {"name": "feedly entities", "value": ", ".join(f"{e} ({attrib.get(e) or 'attribution not stated'})"
                                                         for e in ents)},
        {"name": "generated", "value": _dt.date.today().isoformat()},
        {"name": "generated by", "value": spec.get("generated_by", DEFAULT_GENERATED_BY)},
    ]
    if attack is None:
        layer_md.append({"name": "status", "value": "DRAFT: ATT&CK content NOT CHECKED (no STIX bundle)"})
        warnings.append("ATT&CK content NOT CHECKED: treat the comparison layer as a draft.")
    major = str(info["version"]).split(".")[0] if info.get("version") else None
    base_name = spec.get("layer_name") or "ATT&CK Technique Mapping"
    layer = {
        "name": f"{base_name}: Feedly comparison ({DOMAINS[domain][0]})",
        "versions": {"attack": major, "navigator": nav_ver, "layer": LAYER_FORMAT},
        "domain": DOMAINS[domain][1],
        "description": f"Feedly Threat Graph comparison for {', '.join(ents)}, queried {qdate}, window {win}. "
                       f"Context only: this layer is not a mapping and does not change it.",
        "sorting": 0,
        "layout": {"layout": "side", "showID": True, "showName": True, "showAggregateScores": False,
                   "countUnscored": False, "aggregateFunction": "average",
                   "expandedSubtechniques": "annotated"},
        "hideDisabled": False,
        "techniques": techniques,
        "gradient": {"colors": [CONF_COLOR["low"], CONF_COLOR["moderate"], CONF_COLOR["high"]],
                     "minValue": 0, "maxValue": 100},
        "legendItems": [{"label": g, "color": CMP_COLOR[g]} for g in CMP_ORDER],
        "showTacticRowBackground": False,
        "tacticRowBackground": "#dddddd",
        "selectTechniquesAcrossTactics": True,
        "selectSubtechniquesWithParent": False,
        "selectVisibleTechniques": False,
        "metadata": layer_md,
        "links": [{"label": s.get("title") or s["url"], "url": s["url"]} for s in sources
                  if str(s.get("url", "")).startswith("http")],
    }
    if major is None:
        del layer["versions"]["attack"]
        warnings.append("No ATT&CK version known: versions.attack omitted.")
    if ctx.get("not_comparable"):
        warnings.append("Not comparable (left out): " + ", ".join(map(str, ctx["not_comparable"])))
    return layer, input_errs, content_errs, warnings, per_entity


# --------------------------------------------------------------------------- STIX export
def export_stix(spec, attacks):
    min_conf = _norm_conf(spec.get("min_confidence", "low"))
    sources = spec.get("sources") or []
    pubs = sorted(s["published"] for s in sources if s.get("published"))
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    ident = {"type": "identity", "spec_version": "2.1", "id": f"identity--{uuid.uuid4()}", "created": now,
             "modified": now, "name": "map-attack-techniques skill",
             "identity_class": "system"}
    published = (pubs[-1] + "T00:00:00.000Z") if pubs else now
    objs, aps = [ident], {}
    for m in spec.get("mappings", []):
        tid = (m.get("technique_id") or "").strip().upper()
        if not tid:
            raise SystemExit(f"export-stix: mapping {m.get('ref')} has no technique_id")
        if CONF_RANK[_norm_conf(m.get("confidence"))] < CONF_RANK[min_conf]:
            continue
        dom = _mdomain(m)
        a = attacks.get(dom)
        if a is None or tid not in a.tech:
            raise SystemExit(f"export-stix: cannot resolve {tid} in {dom}; run online or pass --bundle")
        st = a.lookup(tid)["status"]
        if st != "current":
            raise SystemExit(f"export-stix: {tid} is {st}; fix the mapping before exporting")
        rec = a.tech[tid]
        if rec["stix_id"] not in aps:
            ap = {k: v for k, v in rec["obj"].items()}
            aps[rec["stix_id"]] = ap
        conf = _norm_conf(m.get("confidence"))
        content = [f"Procedure: {m.get('procedure', '')}",
                   f"Occurrence: {m.get('occurrence', '')} ({OCCURRENCE.get(m.get('occurrence', ''), '')})"]
        content += [f"Evidence {n}: \"{q['text']}\" [{q['locator']}]" for n, q in enumerate(_quotes(m), 1)]
        if m.get("rationale"):
            content.append(f"Rationale: {m['rationale']}")
        objs.append({"type": "note", "spec_version": "2.1", "id": f"note--{uuid.uuid4()}", "created": now,
                     "modified": now, "created_by_ref": ident["id"],
                     "abstract": f"Mapping #{m.get('ref')}: {tid} {rec['name']} ({m.get('tactic')})",
                     "content": "\n".join(content), "object_refs": [rec["stix_id"]],
                     "confidence": CONF_STIX[conf],
                     "labels": [f"confidence:{conf}", f"occurrence:{m.get('occurrence', '')}"]})
    objs += list(aps.values())
    refs = [{"source_name": s.get("title", "source"), **({"url": s["url"]} if s.get("url") else {})} for s in sources]
    objs.append({"type": "report", "spec_version": "2.1", "id": f"report--{uuid.uuid4()}", "created": now,
                 "modified": now, "created_by_ref": ident["id"], "name": spec.get("layer_name", "ATT&CK mapping"),
                 "published": published, "report_types": ["attack-pattern"],
                 "object_refs": [o["id"] for o in objs if o["type"] in ("note", "attack-pattern")],
                 **({"external_references": refs} if refs else {})})
    return {"type": "bundle", "id": f"bundle--{uuid.uuid4()}", "objects": objs}


# --------------------------------------------------------------------------- CLI
def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--attack-version", default=argparse.SUPPRESS)
    common.add_argument("--bundle", default=argparse.SUPPRESS)
    common.add_argument("--offline", action="store_true", default=argparse.SUPPRESS)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                 parents=[common])
    sub = ap.add_subparsers(dest="cmd", required=True)
    _add = sub.add_parser
    sub.add_parser = lambda *a, **k: _add(*a, parents=[common], **k)
    vp0 = sub.add_parser("version")
    vp0.add_argument("--history-version", help="version read from a live fetch of the Version History page")
    tp = sub.add_parser("tactics")
    tp.add_argument("--domain", choices=DOMAINS, default="enterprise")
    lp = sub.add_parser("lookup")
    lp.add_argument("ids", nargs="+")
    lp.add_argument("--domain", choices=DOMAINS)
    qp = sub.add_parser("verify-quotes")
    qp.add_argument("mappings")
    bp = sub.add_parser("build-layer")
    bp.add_argument("mappings")
    bp.add_argument("-o", "--out", required=True)
    bp.add_argument("--domain", choices=DOMAINS, default=None,
                    help="domain to build; default: the only domain present in the mappings")
    vp = sub.add_parser("validate")
    vp.add_argument("layer")
    cp = sub.add_parser("build-comparison-layer")
    cp.add_argument("mappings")
    cp.add_argument("feedly_context")
    cp.add_argument("-o", "--out", required=True)
    cp.add_argument("--domain", choices=DOMAINS, default=None)
    sp = sub.add_parser("export-stix")
    sp.add_argument("mappings")
    sp.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    for k, v in (("attack_version", None), ("bundle", None), ("offline", False)):
        if not hasattr(args, k):
            setattr(args, k, v)

    if args.cmd == "version":
        if args.offline:
            raise SystemExit("version needs network access")
        idx = load_index()
        out = {d: resolve_version(d, args.attack_version, idx) for d in DOMAINS}
        nv, nsrc = navigator_version()
        res = {"collection_index": out, "navigator": {"version": nv, "source": nsrc},
               "layer_format": LAYER_FORMAT,
               "checked": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
               "index_url": INDEX_URL,
               "decision": {d: version_decision(out[d]["version"], args.history_version) for d in DOMAINS}}
        print(json.dumps(res, indent=2))
        return

    if args.cmd in ("tactics", "lookup"):
        groups = {}
        if args.cmd == "tactics":
            groups[args.domain] = []
        else:
            for i in args.ids:
                groups.setdefault(domain_of(i.strip().upper(), args.domain or "enterprise"), []).append(i)
        results = []
        for dom, ids in groups.items():
            b, info, why = load_bundle(args, dom)
            if b is None:
                raise SystemExit(f"{args.cmd} needs the {dom} STIX bundle ({why}); drop --offline or pass --bundle")
            a = Attack(b, dom)
            if args.cmd == "tactics":
                print(json.dumps({"domain": dom, "version": info["version"], "tactics": a.tactics}, indent=2))
                return
            results += [dict(a.lookup(i), version=info["version"]) for i in ids]
        order = {i.strip().upper(): n for n, i in enumerate(args.ids)}
        results.sort(key=lambda r: order.get(r["id"], 0))
        print(json.dumps({"results": results}, indent=2))
        return

    if args.cmd in ("verify-quotes", "build-layer", "export-stix", "build-comparison-layer"):
        with open(args.mappings) as f:
            spec = json.load(f)
        base = os.path.dirname(os.path.abspath(args.mappings))
        if spec.get("attack_version") and not args.attack_version:
            args.attack_version = spec["attack_version"]

    if args.cmd == "verify-quotes":
        st, detail, note = verify_quotes(spec, base)
        for d in detail:
            print(f"  mapping {d['mapping']} quote {d['quote']} (source {d['source']}): {d['result']}"
                  + (f" ({d['why']})" if d["why"] else ""))
        print(f"Quote verification: {st} ({note})")
        sys.exit(2 if st == FAIL else 0)

    if args.cmd == "export-stix":
        doms = {(m.get("domain") or domain_of(m.get("technique_id", "").upper())).lower() for m in spec.get("mappings", [])}
        attacks = {}
        for d in doms:
            b, info, why = load_bundle(args, d)
            if b is None:
                raise SystemExit(f"export-stix needs the {d} bundle ({why})")
            attacks[d] = Attack(b, d)
        with open(args.out, "w") as f:
            json.dump(export_stix(spec, attacks), f, indent=2, ensure_ascii=False)
        print(json.dumps({"written": args.out, "notes": len(spec.get("mappings", [])),
                          "check": "STIX output was NOT CHECKED against a STIX 2.1 validator"}, indent=2))
        return

    if args.cmd == "build-layer":
        doms = sorted({(m.get("domain") or domain_of((m.get("technique_id") or "").upper())).lower()
                       for m in spec.get("mappings", [])})
        domain = args.domain or (doms[0] if len(doms) == 1 else None)
        if domain is None:
            raise SystemExit(f"The mappings span {', '.join(doms)}. A Navigator layer holds one domain: "
                             f"run build-layer once per domain with --domain.")
        spec["_multi_domain"] = len(doms) > 1
        if args.offline and not args.attack_version:
            raise SystemExit("--offline build needs --attack-version (the version the analyst confirmed)")
        b, info, why = load_bundle(args, domain)
        a = Attack(b, domain) if b else None
        nv = navigator_version()[0] if not args.offline else NAV_FALLBACK_VERSION
        layer, errors, warnings = build_layer(spec, a, info, nv, domain)
        s_errs = structure_errors(layer)
        q_st, q_detail, q_note = verify_quotes(spec, base, domain)
        r_st, r_note = reconciliation_check(spec)
        content_errs = [e for e in errors if " is revoked" in e or " is deprecated" in e or " is not found" in e
                        or "does not sit under" in e or "does not match" in e]
        other_errs = [e for e in errors if e not in content_errs]
        checks = [
            ("Mapping records (quotes, locators, occurrence)", FAIL if other_errs else PASS, ""),
            ("Local layer structure", FAIL if s_errs else PASS, "subset of the Navigator 4.5 layer format"),
            (f"ATT&CK content ({DOMAINS[domain][0]} {info.get('version')})",
             (FAIL if content_errs else PASS) if a else NC, "" if a else why),
            ("Quote verification against source text", q_st, q_note),
            ("Source ID reconciliation", r_st, r_note),
            ("Full Navigator layer schema", NC, "this tool does not run it"),
            ("Navigator application import", NC, "import the file in the Navigator to confirm"),
        ]
        if q_st == FAIL:
            errors += [f"mapping {d['mapping']} quote {d['quote']}: " +
                       (d["why"] or f"not found verbatim in source {d['source']}")
                       for d in q_detail if d["result"] == FAIL]
        layer["metadata"] += [{"name": f"check: {n}", "value": s + (f" ({note})" if note else "")}
                              for n, s, note in checks]
        counts = layer_counts(layer)
        ok = print_report(f"build-layer {args.out}", checks, counts, warnings, errors + s_errs)
        if not ok:
            print("LAYER NOT WRITTEN.")
            sys.exit(2)
        with open(args.out, "w") as f:
            json.dump(layer, f, indent=2, ensure_ascii=False)
        print(json.dumps({"written": args.out, "domain": DOMAINS[domain][1], "attack_version": info.get("version"),
                          "navigator": nv, **counts}, indent=2))
        return

    if args.cmd == "build-comparison-layer":
        with open(args.feedly_context) as f:
            ctx = json.load(f)
        doms = sorted({(m.get("domain") or domain_of((m.get("technique_id") or "").upper())).lower()
                       for m in spec.get("mappings", [])} |
                      {(r.get("domain") or domain_of((r.get("technique_id") or "").upper())).lower()
                       for r in ctx.get("profile", [])})
        domain = args.domain or (doms[0] if len(doms) == 1 else None)
        if domain is None:
            raise SystemExit(f"The inputs span {', '.join(doms)}. Run build-comparison-layer once per domain "
                             f"with --domain.")
        if args.offline and not args.attack_version:
            raise SystemExit("--offline build needs --attack-version")
        b, info, why = load_bundle(args, domain)
        a = Attack(b, domain) if b else None
        nv = navigator_version()[0] if not args.offline else NAV_FALLBACK_VERSION
        layer, in_errs, c_errs, warnings, per_entity = build_comparison_layer(spec, ctx, a, info, nv, domain)
        s_errs = structure_errors(layer)
        checks = [
            ("Comparison inputs (entities, window, profile rows)", FAIL if in_errs else PASS, ""),
            ("Local layer structure", FAIL if s_errs else PASS, "subset of the Navigator 4.5 layer format"),
            (f"ATT&CK content ({DOMAINS[domain][0]} {info.get('version')})",
             (FAIL if c_errs else PASS) if a else NC, "" if a else why),
            ("Quote verification against source text", NA, "comparison layer carries no source quotes"),
            ("Source ID reconciliation", NA, "applies to the main mapping only"),
            ("Full Navigator layer schema", NC, "this tool does not run it"),
            ("Navigator application import", NC, "import the file in the Navigator to confirm"),
        ]
        layer["metadata"] += [{"name": f"check: {n}", "value": s + (f" ({note})" if note else "")}
                              for n, s, note in checks]
        counts = layer_counts(layer)
        counts["per_entity"] = per_entity
        ok = print_report(f"build-comparison-layer {args.out}", checks, counts, warnings, in_errs + c_errs + s_errs)
        if not ok:
            print("LAYER NOT WRITTEN.")
            sys.exit(2)
        with open(args.out, "w") as f:
            json.dump(layer, f, indent=2, ensure_ascii=False)
        print(json.dumps({"written": args.out, "domain": DOMAINS[domain][1], "attack_version": info.get("version"),
                          "groups": counts["comparison"], "per_entity": per_entity}, indent=2))
        return

    if args.cmd == "validate":
        with open(args.layer) as f:
            layer = json.load(f)
        rc = 0
        user_pin = args.attack_version
        for i, l in enumerate(layer if isinstance(layer, list) else [layer]):
            dom = next((k for k, v in DOMAINS.items() if v[1] == l.get("domain")), "enterprise")
            args.attack_version = user_pin
            if not args.attack_version and isinstance(l.get("versions"), dict):
                pinned = next((m["value"].split()[-1] for m in l.get("metadata", [])
                               if m.get("name") == "ATT&CK version mapped"), None)
                args.attack_version = pinned if pinned and _vtuple(pinned) else None
            s_errs = structure_errors(l)
            b, info, why = load_bundle(args, dom)
            c_errs = content_errors(l, Attack(b, dom)) if b else []
            checks = [
                ("Local layer structure", FAIL if s_errs else PASS, "subset of the Navigator 4.5 layer format"),
                (f"ATT&CK content ({DOMAINS[dom][0]} {info.get('version')})",
                 (FAIL if c_errs else PASS) if b else NC, "" if b else why),
                ("Full Navigator layer schema", NC, "this tool does not run it"),
                ("Navigator application import", NC, "import the file in the Navigator to confirm"),
            ]
            if not print_report(f"validate {args.layer} [{i}]", checks, layer_counts(l), (), s_errs + c_errs):
                rc = 2
        sys.exit(rc)


if __name__ == "__main__":
    main()
