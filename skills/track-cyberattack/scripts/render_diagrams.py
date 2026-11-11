#!/usr/bin/env python3
"""Render the report's diagrams from tracker.json. Generic: works for any attack.

  python3 render_diagrams.py tracker.json OUTDIR [--svg]

writes OUTDIR/timeline, OUTDIR/attack-matrix and OUTDIR/diamond as PNG (matplotlib) and OUTDIR/attack-chain.png
(Graphviz dot). Without matplotlib, or with --svg, the first three are written as plain SVG instead, so the report
keeps its images on locked-down systems; build_report.js embeds SVG with a PNG fallback. A missing tool skips only
the image that needs it, and the script says which one.
"""
import json, os, shutil, subprocess, sys, textwrap
from xml.sax.saxutils import escape

t = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]
FORCE_SVG = "--svg" in sys.argv
os.makedirs(out, exist_ok=True)
made, skipped = [], []

LANE_COLOR = {"Attacker": "#C0392B", "Victim and response": "#1F6FB2", "Disclosure": "#7D5BA6",
              "Government and law enforcement": "#2E8B57", "Context": "#9AA3AE"}
OCC = {"Observed": "#1F6FB2", "Reported": "#E08E0B", "Capability": "#7D5BA6", "Assessed": "#9AA3AE"}
OCC_WORD = {"Observed": "blue", "Reported": "amber", "Capability": "purple", "Assessed": "grey"}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

try:
    _attack = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "attack_v20.json"), encoding="utf-8"))
    ENT, ICS = _attack["enterprise"]["tactic_order"], _attack["ics"]["tactic_order"]
except (OSError, ValueError, KeyError):
    ENT = ["reconnaissance", "resource-development", "initial-access", "execution", "persistence",
           "privilege-escalation", "stealth", "defense-impairment", "credential-access", "discovery",
           "lateral-movement", "collection", "command-and-control", "exfiltration", "impact"]
    ICS = []
COLUMNS = [("enterprise", x) for x in ENT] + [("ics", x) for x in ICS] + [("enterprise", "unmapped"), ("ics", "unmapped")]

ttps = t.get("ttps", [])
summary = (t.get("summary") or [{}])[0]
diamond = {r.get("party"): r.get("position", "") for r in t.get("attribution", []) if r.get("kind") == "Diamond"}


def domain(r):
    d = (r.get("domain") or "").strip().lower()
    if d:
        return d
    tid = r.get("technique_id", "")
    return "ics" if tid.startswith("T0") else "enterprise"


def col_label(key):
    d, tac = key
    return ("ICS: " if d == "ics" else "") + tac.replace("-", " ").title()


incidents = []
for r in ttps:
    inc = (r.get("incident") or "").strip()
    if inc not in incidents:
        incidents.append(inc)
multi = len([i for i in incidents if i]) > 1


def when_label(s):
    if len(s) < 10:
        return f"{MON[int(s[5:7]) - 1]} {s[:4]}"
    d = f"{int(s[8:10])} {MON[int(s[5:7]) - 1]} {s[:4]}"
    return d + (f", {s[11:16]}" if "T" in s else "")


def timeline_rows():
    ev = sorted(t.get("timeline", []), key=lambda e: (e["when"][:10], e["when"][11:16] if "T" in e["when"] else "99",
                                                     e["event_id"]))
    rows = []
    for e in ev:
        end = f" to {e['end'][11:16]}" if e.get("end") and "T" in e["end"] else ""
        label = e["event"] + (f" [{e['incident']}]" if multi and e.get("incident") else "")
        rows.append((when_label(e["when"]) + end, textwrap.wrap(label, 62) or [""], e["lane"], e["status"]))
    return rows


def matrix_cells():
    used = [c for c in COLUMNS if any((domain(r), r["tactic"]) == c for r in ttps)]
    cells = {c: [] for c in used}
    for r in ttps:
        c = (domain(r), r["tactic"])
        if c not in cells:
            continue
        if (r["technique_id"], r["name"]) not in [(x["technique_id"], x["name"]) for x in cells[c]]:
            cells[c].append(r)
    return used, cells


plt = None
if not FORCE_SVG:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
    except ImportError:
        plt = None


# ---------------------------------------------------------------- plain SVG writers (no dependencies)
def svg_doc(w, h, parts):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'font-family="Arial, Helvetica, sans-serif">\n<rect width="100%" height="100%" fill="#FFFFFF"/>\n'
            + "\n".join(parts) + "\n</svg>\n")


def svg_text(x, y, s, size=11, color="#222222", anchor="start", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{escape(str(s))}</text>')


def svg_timeline(path):
    rows = timeline_rows()
    line_h, gap, x_dot = 15, 9, 170
    y = 24
    parts = []
    tops = []
    for lab, lines, lane, status in rows:
        c = LANE_COLOR.get(lane, "#9AA3AE")
        faded = status == "Superseded"
        tops.append(y)
        op = ' opacity="0.4"' if faded else ""
        parts.append(f'<circle cx="{x_dot}" cy="{y - 4}" r="5" fill="{c}" stroke="#FFFFFF" stroke-width="1.5"{op}/>')
        parts.append(svg_text(x_dot - 14, y, lab, 11, "#333333", "end"))
        for k, ln in enumerate(lines):
            parts.append(svg_text(x_dot + 16, y + k * line_h, ln, 11, "#777777" if lane == "Context" or faded else "#222222"))
        parts.append(svg_text(690, y, status, 10, "#666666", "end"))
        y += len(lines) * line_h + gap
    parts.insert(0, f'<line x1="{x_dot}" y1="10" x2="{x_dot}" y2="{y - gap}" stroke="#C9CED6" stroke-width="2"/>')
    lx = 20
    y += 10
    for lane, c in LANE_COLOR.items():
        if any(r[2] == lane for r in rows):
            parts.append(f'<circle cx="{lx + 5}" cy="{y - 4}" r="5" fill="{c}"/>')
            parts.append(svg_text(lx + 14, y, lane, 10, "#444444"))
            lx += 24 + 6.2 * len(lane)
    open(path, "w", encoding="utf-8").write(svg_doc(700, y + 14, parts))


def svg_matrix(path):
    used, cells = matrix_cells()
    band = 6
    bands = [used[i:i + band] for i in range(0, len(used), band)]
    col_w, cell_h, head_h = 112, 46, 30
    parts, top = [], 10
    for b in bands:
        for i, key in enumerate(b):
            x0 = 10 + i * col_w
            parts.append(f'<rect x="{x0 + 3}" y="{top}" width="{col_w - 6}" height="{head_h - 4}" rx="4" fill="#EEF0F3"/>')
            for k, ln in enumerate(textwrap.wrap(col_label(key), 18)[:2]):
                parts.append(svg_text(x0 + col_w / 2, top + 11 + k * 11, ln, 9, "#333333", "middle", "bold"))
            yy = top + head_h
            for r in cells[key]:
                c = OCC.get(r["occurrence"], "#9AA3AE")
                parts.append(f'<rect x="{x0 + 3}" y="{yy}" width="{col_w - 6}" height="{cell_h}" rx="4" fill="#FFFFFF" '
                             f'stroke="{c}" stroke-width="2"/>')
                head = "" if r["technique_id"] == "Unmapped" else r["technique_id"]
                lines = ([head] if head else []) + textwrap.wrap(r["name"], 19)[:2]
                for k, ln in enumerate(lines):
                    parts.append(svg_text(x0 + col_w / 2, yy + 14 + k * 12, ln, 9, "#222222", "middle"))
                yy += cell_h + 5
        top += head_h + max(len(cells[k]) for k in b) * (cell_h + 5) + 14
    lx = 14
    for k in [k for k in OCC if any(r["occurrence"] == k for r in ttps)]:
        parts.append(f'<rect x="{lx}" y="{top}" width="10" height="10" fill="#FFFFFF" stroke="{OCC[k]}" stroke-width="2"/>')
        parts.append(svg_text(lx + 15, top + 9, k, 10, "#444444"))
        lx += 30 + 6 * len(k)
    parts.append(svg_text(lx + 6, top + 9, "(border shows occurrence)", 10, "#777777"))
    open(path, "w", encoding="utf-8").write(svg_doc(20 + col_w * min(band, len(used)), top + 24, parts))


VERTEX = {"Adversary": (0.5, 0.12), "Capability": (0.86, 0.5), "Victim": (0.5, 0.88), "Infrastructure": (0.14, 0.5)}


def svg_diamond(path):
    w, h = 640, 460
    pts = {k: (x * w, y * h) for k, (x, y) in VERTEX.items()}
    order = ["Adversary", "Capability", "Victim", "Infrastructure", "Adversary"]
    parts = ['<polyline fill="none" stroke="#C9CED6" stroke-width="2" points="'
             + " ".join(f"{pts[k][0]:.0f},{pts[k][1]:.0f}" for k in order) + '"/>',
             f'<line x1="{pts["Adversary"][0]}" y1="{pts["Adversary"][1]}" x2="{pts["Victim"][0]}" y2="{pts["Victim"][1]}" '
             f'stroke="#C9CED6" stroke-dasharray="5 5"/>',
             f'<line x1="{pts["Infrastructure"][0]}" y1="{pts["Infrastructure"][1]}" x2="{pts["Capability"][0]}" '
             f'y2="{pts["Capability"][1]}" stroke="#C9CED6" stroke-dasharray="5 5"/>']
    bw = 190
    for k, (x, y) in pts.items():
        lines = textwrap.wrap(diamond.get(k) or "Not available in provided reports", 32)[:5]
        bh = 26 + 13 * len(lines)
        parts.append(f'<rect x="{x - bw / 2:.0f}" y="{y - bh / 2:.0f}" width="{bw}" height="{bh}" rx="6" fill="#FFFFFF" '
                     f'stroke="#1F6FB2" stroke-width="1.6"/>')
        parts.append(svg_text(x, y - bh / 2 + 16, k, 11, "#1A1A1A", "middle", "bold"))
        for i, ln in enumerate(lines):
            parts.append(svg_text(x, y - bh / 2 + 31 + i * 13, ln, 9.5, "#333333", "middle"))
    parts.append(svg_text(w / 2, h / 2 + 4, textwrap.shorten(summary.get("attack", ""), 40), 12, "#555555", "middle", "bold"))
    open(path, "w", encoding="utf-8").write(svg_doc(w, h, parts))


def write_svg(name, fn):
    fn(os.path.join(out, name + ".svg"))
    made.append(name + ".svg")
    png = os.path.join(out, name + ".png")
    if os.path.exists(png):
        os.remove(png)   # the report prefers PNG; never let a stale PNG shadow a new SVG


# ---------------------------------------------------------------- matplotlib versions
def mpl_timeline(path):
    rows = timeline_rows()
    heights = [max(1, len(r[1])) for r in rows]
    fig_h = 0.6 + sum(0.26 * h + 0.16 for h in heights)
    fig, ax = plt.subplots(figsize=(7.2, fig_h), dpi=200)
    ax.set_xlim(0, 10); ax.set_ylim(0, fig_h); ax.axis("off")
    y = fig_h - 0.35
    ax.plot([2.55, 2.55], [0.2, y], color="#C9CED6", lw=1.5, zorder=1)
    for (lab, lines, lane, status), h in zip(rows, heights):
        c = LANE_COLOR.get(lane, "#9AA3AE")
        faded = status == "Superseded"
        ax.scatter([2.55], [y - 0.06], s=55, color=c, zorder=3, edgecolors="white", linewidths=1,
                   alpha=0.4 if faded else 1)
        ax.text(2.35, y - 0.06, lab, ha="right", va="center", fontsize=7.5, color="#333333")
        for k, ln in enumerate(lines):
            ax.text(2.8, y - 0.06 - k * 0.26, ln, ha="left", va="center", fontsize=7.5,
                    color="#777777" if lane == "Context" or faded else "#222222")
        ax.text(9.95, y - 0.06, status, ha="right", va="center", fontsize=6.5, color="#666666")
        y -= 0.26 * h + 0.16
    handles = [plt.Line2D([], [], marker="o", ls="", color=c, label=l) for l, c in LANE_COLOR.items()
               if any(e["lane"] == l for e in t["timeline"])]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.02), ncol=len(handles), fontsize=6.5,
              frameon=False)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def mpl_matrix(path):
    used, cells = matrix_cells()
    band = 6
    bands = [used[i:i + band] for i in range(0, len(used), band)]
    col_w, cell_h, head_h = 1.55, 0.7, 0.42
    band_h = [head_h + max(len(cells[x]) for x in b) * (cell_h + 0.08) + 0.2 for b in bands]
    W = col_w * min(band, len(used)) + 0.2
    H = sum(band_h) + 0.45
    fig, ax = plt.subplots(figsize=(W, H), dpi=200)
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    top = H - 0.1
    for b, bh in zip(bands, band_h):
        for i, key in enumerate(b):
            x0 = 0.1 + i * col_w
            ax.add_patch(FancyBboxPatch((x0 + 0.04, top - head_h), col_w - 0.08, head_h - 0.06,
                                        boxstyle="round,pad=0,rounding_size=0.04", fc="#EEF0F3", ec="none"))
            ax.text(x0 + col_w / 2, top - head_h / 2 - 0.03, "\n".join(textwrap.wrap(col_label(key), 18)[:2]),
                    ha="center", va="center", fontsize=7.5, fontweight="bold", color="#333333", linespacing=1.0)
            yy = top - head_h - 0.06
            for r in cells[key]:
                c = OCC.get(r["occurrence"], "#9AA3AE")
                ax.add_patch(FancyBboxPatch((x0 + 0.04, yy - cell_h), col_w - 0.08, cell_h,
                                            boxstyle="round,pad=0,rounding_size=0.04", fc="white", ec=c, lw=1.8))
                head = "" if r["technique_id"] == "Unmapped" else r["technique_id"]
                name = "\n".join(textwrap.wrap(r["name"], 20)[:2])
                ax.text(x0 + col_w / 2, yy - cell_h / 2, (head + "\n" if head else "") + name, ha="center",
                        va="center", fontsize=7.2, color="#222222", linespacing=1.15)
                yy -= cell_h + 0.08
        top -= bh
    present = [k for k in OCC if any(r["occurrence"] == k for r in ttps)]
    handles = [plt.Line2D([], [], marker="s", ls="", mfc="white", mec=OCC[k], mew=1.8, label=k) for k in present]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0), ncol=len(handles), fontsize=6.5,
              frameon=False, title="Border shows occurrence", title_fontsize=6.5)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def mpl_diamond(path):
    fig, ax = plt.subplots(figsize=(6.4, 4.6), dpi=200)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    pts = {k: (x, 1 - y) for k, (x, y) in VERTEX.items()}
    ring = ["Adversary", "Capability", "Victim", "Infrastructure", "Adversary"]
    ax.plot([pts[k][0] for k in ring], [pts[k][1] for k in ring], color="#C9CED6", lw=1.6, zorder=1)
    for a, b in (("Adversary", "Victim"), ("Infrastructure", "Capability")):
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]], color="#C9CED6", lw=1, ls="--", zorder=1)
    for k, (x, y) in pts.items():
        text = "\n".join(textwrap.wrap(diamond.get(k) or "Not available in provided reports", 32)[:5])
        ax.text(x, y, f"{k}\n" + text, ha="center", va="center", fontsize=6.6, color="#222222", zorder=3,
                linespacing=1.25, bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#1F6FB2", lw=1.2))
    ax.text(0.5, 0.5, textwrap.shorten(summary.get("attack", ""), 40), ha="center", va="center", fontsize=8,
            fontweight="bold", color="#555555", zorder=2)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render(name, has, mpl_fn, svg_fn):
    if not has:
        return
    if plt:
        mpl_fn(os.path.join(out, name + ".png"))
        made.append(name + ".png")
        stale = os.path.join(out, name + ".svg")
        if os.path.exists(stale):
            os.remove(stale)
    else:
        write_svg(name, svg_fn)


render("timeline", bool(t.get("timeline")), mpl_timeline, svg_timeline)
render("attack-matrix", bool(ttps), mpl_matrix, svg_matrix)
render("diamond", bool(diamond), mpl_diamond, svg_diamond)
if not plt and (t.get("timeline") or ttps or diamond):
    skipped.append("matplotlib " + ("not used (--svg)" if FORCE_SVG else "is missing") + "; timeline, matrix and Diamond "
                   "were written as SVG")

# ---------- attack chain: Graphviz clusters per phase, one row of phases per incident ----------
if ttps and shutil.which("dot"):
    esc = lambda s: str(s).replace('"', "'")
    lines = ['digraph G {', 'rankdir=LR; compound=true; nodesep=0.15; ranksep=0.5; newrank=true;',
             'node [shape=box, style="rounded,filled", fillcolor="#FFFFFF", fontname="Helvetica", fontsize=10, '
             'penwidth=2.2, width=2.3];', 'edge [color="#555555", penwidth=1.4];']
    groups = incidents if multi else [None]
    n = 0
    for g_i, inc in enumerate(groups):
        rows = [r for r in ttps if (r.get("incident") or "").strip() == inc] if inc is not None else ttps
        if not rows:
            continue
        phases = []
        for r in rows:
            if r["phase"] not in phases:
                phases.append(r["phase"])
        if multi:
            lines.append(f'subgraph cluster_inc{g_i} {{ label="{esc(inc or "Unassigned")}"; fontname="Helvetica-Bold"; '
                         f'fontsize=12; style="dashed"; color="#9AA3AE";')
        first = []
        for p_i, p in enumerate(phases):
            n += 1
            lines.append(f'subgraph cluster_{n} {{ label="{esc(p)}"; fontname="Helvetica-Bold"; fontsize=11; '
                         f'style="rounded"; color="#C9CED6";')
            node_ids = []
            for j, r in enumerate([x for x in rows if x["phase"] == p]):
                nid = f"n{n}_{j}"
                node_ids.append(nid)
                head = "Unmapped" if r["technique_id"] == "Unmapped" else r["technique_id"]
                name = "\\n".join(textwrap.wrap(r["name"], 28))
                lines.append(f'{nid} [label="{head}\\n{esc(name)}\\n{r["occurrence"]} / {r["confidence"]}", '
                             f'color="{OCC.get(r["occurrence"], "#9AA3AE")}"];')
            lines.append("{rank=same; " + " ".join(node_ids) + "}")
            lines.append("}")
            first.append((node_ids[0], n))
        for (a, ca), (b, cb) in zip(first, first[1:]):
            lines.append(f'{a} -> {b} [ltail=cluster_{ca}, lhead=cluster_{cb}];')
        if multi:
            lines.append("}")
    present = [k for k in OCC if any(r["occurrence"] == k for r in ttps)]
    legend = "Border: " + ", ".join(f"{OCC_WORD[k]} {k}" for k in present)
    lines.append(f'legend [shape=plaintext, penwidth=0, label="{legend}"];')
    lines.append("}")
    dot_src = os.path.join(out, "attack-chain.dot")
    open(dot_src, "w", encoding="utf-8").write("\n".join(lines))
    r = subprocess.run(["dot", "-Tpng", "-Gdpi=200", dot_src, "-o", os.path.join(out, "attack-chain.png")],
                       capture_output=True, text=True)
    if r.returncode == 0:
        made.append("attack-chain.png")
    else:
        skipped.append(f"attack-chain.png (dot failed: {r.stderr.strip()[:200]})")
elif ttps:
    skipped.append("attack-chain.png (Graphviz dot is missing)")

print("wrote " + (", ".join(os.path.join(out, m) for m in made) or "nothing"))
for s in skipped:
    print("SKIPPED " + s)
