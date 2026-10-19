"""Figures of the anatomy of Anaxia, of its growth, and of the way it changes its own rules.

Reads data/brain/anatomy.json and data/brain/growth.json (written by collect_brain.py from the
package and its git history) and the bundled learn-from-failure log src/ebllm/bllm/data/modlog.json.
Writes fig_anatomy, fig_growth, fig_modloop and fig_modladder as PNG.

    python3 collect_brain.py && python3 make_round7.py && python3 compact_figures.py
"""
import json
import math
import os
from datetime import datetime, timezone

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.lines  # noqa: F401
import matplotlib.patches  # noqa: F401
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers the 3d projection)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "brain")
OUT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
MODLOG = os.path.join(REPO, "src", "ebllm", "bllm", "data", "modlog.json")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY, PURPLE = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555", "#5b2a86"
DPI = 300
AZIM = -126
BOX = (1.2, 2.0, 1.0)
TREE_VERSION = "3.1.0"  # the release the working tree becomes

SUBCOL = {
    "core": "#7f7f7f", "laws": "#1f4e99", "proposers": "#1b7837", "crossing": "#d08c00",
    "memory": "#5b2a86", "knowledge": "#2c8c99", "benchmarks": "#b2182b", "construction": "#a6611a",
    "interface": "#bdbdbd",
}
SUBNAME = {
    "core": "verified core", "laws": "laws and checks", "proposers": "proposers and selector",
    "crossing": "crossing network", "memory": "memory and self-change", "knowledge": "knowledge and sources",
    "benchmarks": "benchmarks", "construction": "construction mode", "interface": "interface",
}
# where each subsystem sits on the map: sensing on the left, integration in the middle, action on the
# right, feedback along the bottom (the plan of Fig. brainmap)
CENTRE = {
    "knowledge": (0.13, 0.76), "proposers": (0.13, 0.33), "laws": (0.41, 0.84), "crossing": (0.41, 0.49),
    "memory": (0.42, 0.13), "benchmarks": (0.69, 0.84), "construction": (0.69, 0.42), "core": (0.91, 0.66),
    "interface": (0.91, 0.20),
}
STAGE = {"knowledge": "sense", "proposers": "sense", "laws": "integrate", "crossing": "integrate",
         "memory": "feed back", "benchmarks": "act", "construction": "act", "core": "act", "interface": "act"}


def load(path):
    with open(path) as f:
        return json.load(f)


def title(ax, s):
    ax.set_title(s, loc="left", fontweight="bold")


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def stem(module):
    s = module[:-3]
    s = s.replace("/__init__", "")
    s = s.split("/")[-1] if "/" in s else s
    return {"__init__": "ebllm", "__main__": "main"}.get(s, s)


# ---------------------------------------------------------------- anatomy
RING = ["knowledge", "proposers", "laws", "crossing", "benchmarks", "construction", "core", "interface", "memory"]
NEW = ("bllm/selfmod.py", "construct/reflexive.py")  # modules new in this release, ringed in black
RINGNAME = {"knowledge": "knowledge", "proposers": "proposers", "laws": "laws, checks", "crossing": "crossing",
            "benchmarks": "benchmarks", "construction": "construction", "core": "verified core",
            "interface": "interface", "memory": "memory, self-change"}
STAGES = [("sense", ["knowledge", "proposers"]), ("integrate", ["laws", "crossing"]),
          ("act", ["benchmarks", "construction", "core", "interface"]), ("feed back", ["memory"])]


def ring_layout(mods):
    """Modules on a circle, grouped by part in the order sense, integrate, act, feed back."""
    order = []
    for sub in RING:
        order += sorted([m for m in mods if m["subsystem"] == sub], key=lambda m: -m["loc"])
    gap = 2.2  # empty slots between parts
    slots = len(order) + gap * len(RING)
    ang, k = {}, 0.0
    spans = {}
    for sub in RING:
        ms = [m for m in order if m["subsystem"] == sub]
        a0 = 2 * math.pi * k / slots
        for m in ms:
            ang[m["module"]] = 2 * math.pi * k / slots
            k += 1
        spans[sub] = (a0, 2 * math.pi * (k - 1) / slots)
        k += gap
    rot = math.pi / 2 - (spans["knowledge"][0] - math.pi / slots * gap)
    ang = {m: a + rot for m, a in ang.items()}
    spans = {s: (a + rot, b + rot) for s, (a, b) in spans.items()}
    return ang, spans


def fig_anatomy():
    a = load(os.path.join(DATA, "anatomy.json"))
    mods = a["modules"]
    subs = [s["key"] for s in a["subsystems"]]
    sub_of = {m["module"]: m["subsystem"] for m in mods}
    ang, spans = ring_layout(mods)

    fig = plt.figure(figsize=(7.2, 4.75))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.45, 1.0], height_ratios=[1.0, 1.0], wspace=0.30, hspace=0.62)

    ax = fig.add_subplot(gs[:, 0])
    ax.set_xlim(-1.78, 1.78)
    ax.set_ylim(-1.78, 1.78)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"(a) The {len(mods)} modules, grouped by part, and their imports", loc="left", fontweight="bold", y=1.0)
    P = {m: (math.cos(t), math.sin(t)) for m, t in ang.items()}
    for m in mods:
        x0, y0 = P[m["module"]]
        for t in m["imports"]:
            if t not in P:
                continue
            x1, y1 = P[t]
            same = sub_of[t] == m["subsystem"]
            k = 0.62 if same else 0.18
            cx, cy = k * (x0 + x1) / 2, k * (y0 + y1) / 2
            tt = np.linspace(0, 1, 30)
            bx = (1 - tt) ** 2 * x0 + 2 * (1 - tt) * tt * cx + tt ** 2 * x1
            by = (1 - tt) ** 2 * y0 + 2 * (1 - tt) * tt * cy + tt ** 2 * y1
            ax.plot(bx * 0.97, by * 0.97, color=SUBCOL[m["subsystem"]], lw=0.45 if same else 0.55,
                    alpha=0.35 if same else 0.5, zorder=1, solid_capstyle="round")
    for m in mods:
        x, y = P[m["module"]]
        r = 0.010 + 0.0021 * math.sqrt(m["loc"])
        ax.add_patch(Circle((x, y), r, fc=SUBCOL[m["subsystem"]], ec="white", lw=0.3, zorder=3))
        t = ang[m["module"]]
        deg = math.degrees(t) % 360
        flip = 90 < deg < 270
        lx, ly = 1.075 * math.cos(t), 1.075 * math.sin(t)
        name = stem(m["module"])
        if m["module"] in NEW:
            ax.add_patch(Circle((x, y), r + 0.012, fc="none", ec="k", lw=0.6, zorder=4))
        ax.text(lx, ly, name, rotation=deg + (180 if flip else 0), rotation_mode="anchor",
                ha="right" if flip else "left", va="center", fontsize=4.6, color="#222222")
    for sub in RING:
        a0, a1 = spans[sub]
        th = np.linspace(a0 - 0.035, a1 + 0.035, 40)
        ax.plot(1.50 * np.cos(th), 1.50 * np.sin(th), color=SUBCOL[sub], lw=3.0, solid_capstyle="butt")
        mid = (a0 + a1) / 2
        n = sum(1 for m in mods if m["subsystem"] == sub)
        cx, cy = 1.57 * math.cos(mid), 1.57 * math.sin(mid)
        ax.text(cx, cy, f"{RINGNAME[sub]}\n{n} modules", ha="left" if cx > 0.15 else "right" if cx < -0.15 else "center",
                va="bottom" if cy > 0.3 else "top" if cy < -0.3 else "center", fontsize=5.6, color=SUBCOL[sub],
                fontweight="bold", linespacing=1.0)
    for lab, group in STAGES:
        a0 = min(spans[s][0] for s in group)
        a1 = max(spans[s][1] for s in group)
        mid = (a0 + a1) / 2
        rr = 0.80 if lab == "feed back" else 0.60
        ax.text(rr * math.cos(mid), rr * math.sin(mid), lab, ha="center", va="center", fontsize=6.4,
                color=GREY, style="italic")

    ax = fig.add_subplot(gs[0, 1])
    M = np.zeros((len(subs), len(subs)), int)
    idx = {s: i for i, s in enumerate(subs)}
    for m in mods:
        for t in m["imports"]:
            if t in sub_of:
                M[idx[m["subsystem"]], idx[sub_of[t]]] += 1
    ax.imshow(np.log1p(M), cmap="Purples", aspect="auto")
    for i in range(len(subs)):
        for j in range(len(subs)):
            if M[i, j]:
                ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=4.8,
                        color="white" if M[i, j] > 6 else "k")
    short = [SUBNAME[s].split()[0] for s in subs]
    ax.set_xticks(range(len(subs)))
    ax.set_xticklabels(short, rotation=60, ha="right", fontsize=5.2)
    ax.set_yticks(range(len(subs)))
    ax.set_yticklabels(short, fontsize=5.2)
    ax.set_xlabel("imported part", fontsize=6.2, labelpad=1)
    ax.set_ylabel("importing part", fontsize=6.2)
    title(ax, "(b) Imports between parts")

    ax = fig.add_subplot(gs[1, 1])
    lines = [sum(m["loc"] for m in mods if m["subsystem"] == s) for s in subs]
    order = np.argsort(lines)
    ax.barh(range(len(subs)), [lines[i] for i in order], color=[SUBCOL[subs[i]] for i in order], height=0.7)
    for k, i in enumerate(order):
        n = sum(1 for m in mods if m["subsystem"] == subs[i])
        ax.text(lines[i] + 30, k, f"{lines[i]:,} ({n})", va="center", fontsize=5.2)
    ax.set_yticks(range(len(subs)))
    ax.set_yticklabels([SUBNAME[subs[i]] for i in order], fontsize=5.4)
    ax.set_xlim(0, max(lines) * 1.42)
    ax.tick_params(axis="x", labelsize=6)
    ax.set_xlabel("non-blank lines of Python (modules)", fontsize=6.2)
    clean(ax)
    title(ax, "(c) Size of each part")
    fig.savefig(os.path.join(OUT, "fig_anatomy.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- growth
MILESTONES = {
    "1.0.0": "verified-release core",
    "2.0.0": "crossing network, memory,\nagents, five benchmarks",
    "2.1.0": "Hodge engine, Lean\nchecks of the paper",
    "3.0.0": "construction mode,\ntower $B^n$, registry",
    "3.1.0": "learn-from-failure loop,\nlattice polytopes",
}
RELEASES = ("1.0.0", "2.0.0", "2.1.0", "3.0.0", "3.1.0")
SHORT = {"core": "core", "laws": "laws", "proposers": "proposers", "crossing": "crossing", "memory": "memory",
         "knowledge": "knowledge", "benchmarks": "benchmarks", "construction": "construction",
         "interface": "interface"}


def growth_rows():
    rows = load(os.path.join(DATA, "growth.json"))["rows"]
    for r in rows:
        if r["label"] == "tree":
            r["version"] = TREE_VERSION
    return rows


def at_release(rows):
    """The state of the package at the tagged commit of each release in RELEASES (the working tree for
    the release in preparation)."""
    at = {}
    for r in rows:
        if r.get("release") == "tree":
            at[TREE_VERSION] = r
        elif r.get("release"):
            at[r["release"]] = r
    return [at[v] for v in RELEASES if v in at]


def utc(d):
    return datetime.fromisoformat(d).astimezone(timezone.utc)


def fig_growth():
    rows = growth_rows()
    rel = at_release(rows)
    subs = ["core", "laws", "proposers", "crossing", "memory", "knowledge", "benchmarks", "construction",
            "interface"]
    fig = plt.figure(figsize=(7.2, 4.3))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.0], height_ratios=[1.0, 1.0], hspace=0.55, wspace=0.30)

    ax = fig.add_subplot(gs[:, 0], projection="3d")
    n = len(rel)
    final = rel[-1]["loc"]
    subs = sorted(subs, key=lambda s: final[s])  # the smallest parts in front
    for j, s in enumerate(subs):
        zs = np.array([r["loc"][s] for r in rel], float)
        xs = np.arange(n)[zs > 0]
        zs = zs[zs > 0]
        ax.bar3d(xs - 0.3, np.full(len(xs), j) - 0.3, np.zeros(len(xs)), 0.6, 0.6, zs, color=SUBCOL[s],
                 alpha=0.95, shade=True, edgecolor="none")
    ax.set_xticks(range(n))
    ax.set_xticklabels([r["version"] for r in rel], fontsize=6, ha="right", va="center")
    ax.set_yticks(range(len(subs)))
    ax.set_yticklabels([])
    ax.legend(handles=[matplotlib.patches.Patch(color=SUBCOL[s], label=SHORT[s]) for s in reversed(subs)],
              ncol=3, fontsize=5.6, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.06),
              handlelength=1.0, columnspacing=0.9, labelspacing=0.3)
    ax.set_zlabel("lines of Python", fontsize=6.2, labelpad=-1)
    ax.tick_params(axis="z", labelsize=5.4, pad=0)
    ax.tick_params(axis="x", pad=-3)
    ax.tick_params(axis="y", pad=-3)
    ax.view_init(elev=20, azim=AZIM)
    ax.set_box_aspect(BOX, zoom=1.05)
    ax.set_title("(a) Lines of each part at each release", loc="left", fontweight="bold", fontsize=8.5, y=0.97)

    ax = fig.add_subplot(gs[0, 1])
    x = np.arange(n)
    series = [("modules", "modules", BLUE, "o"), ("tests", "test methods", GREEN, "s"),
              ("lean_paper", "Lean theorems, paper", PURPLE, "^"), ("lean_engine", "Lean theorems, engine", "#9e9ac8", "v"),
              ("library", "literature constructions", GOLD, "D"), ("registry", "registry entries", RED, "P"),
              ("figures", "figures of the paper", GREY, "X"), ("commands", "commands", "#2c8c99", "*")]
    for key, lab, col, mk in series:
        ax.plot(x, [r[key] for r in rel], "-", marker=mk, ms=2.6, lw=0.9, color=col, label=lab)
    ax.set_xticks(x)
    ax.set_xticklabels([r["version"] for r in rel], fontsize=6)
    ax.set_xlim(-0.2, n - 0.8)
    ax.tick_params(axis="y", labelsize=6)
    ax.set_ylabel("count", fontsize=6.5)
    ax.legend(ncol=2, fontsize=5.0, frameon=False, loc="upper left", handlelength=1.3, columnspacing=0.7,
              borderaxespad=0.1, labelspacing=0.25)
    ax.set_ylim(0, max(max(r[k] for r in rel) for k, *_ in series) * 1.75)
    clean(ax)
    title(ax, "(b) What each release contains")

    ax = fig.add_subplot(gs[1, 1])
    t0 = utc([r for r in rows if r["version"] == "2.0.0"][0]["date"])
    pts = [((utc(r["date"]) - t0).total_seconds() / 3600, r["loc_total"], r) for r in rows if r["version"] != "1.0.0"]
    pts.sort(key=lambda p: p[0])
    hs = [p[0] for p in pts]
    ts = [p[1] for p in pts]
    ax.step(hs, ts, where="post", color=BLUE, lw=1.0)
    ax.plot(hs, ts, "o", ms=2.0, color=BLUE)
    v1 = [r for r in rows if r["version"] == "1.0.0"][-1]
    ax.plot([-2.2], [v1["loc_total"]], "o", ms=2.6, color=GREY)
    ax.annotate(f"1.0.0, 10 Oct: {v1['loc_total']:,} lines,\n{MILESTONES['1.0.0']}", xy=(-2.2, v1["loc_total"]),
                xytext=(0.6, 1500), fontsize=5.0, color="#222222", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.4, color=GREY))
    place = {"2.0.0": (2.5, 4200), "2.1.0": (1.0, 12600), "3.0.0": (6.5, 16200), "3.1.0": (13.6, 12800)}
    for v, (tx, ty) in place.items():
        hit = [p for p in pts if p[2].get("release") == v or (v == TREE_VERSION and p[2].get("release") == "tree")]
        if not hit:
            continue
        h, t, _ = hit[0]
        ax.annotate(f"{v}: {MILESTONES[v]}", xy=(h, t), xytext=(tx, ty), fontsize=5.0, color="#222222",
                    va="center", arrowprops=dict(arrowstyle="-", lw=0.4, color=GREY))
    ax.set_xlim(-3.2, max(hs) + 1.0)
    ax.set_ylim(0, 18000)
    ax.tick_params(labelsize=6)
    ax.set_xlabel("hours after the merge of 2.0.0 (18 Oct, %s UTC)" % t0.strftime("%H:%M"), fontsize=6.2)
    ax.set_ylabel("lines of Python", fontsize=6.5)
    clean(ax)
    title(ax, "(c) Growth in time, merge by merge")
    fig.savefig(os.path.join(OUT, "fig_growth.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- the learn-from-failure loop
KIND_ORDER = ["missing-mode", "filter-cost", "generator", "rules-silent", "arrangement", "scale", "representation",
              "overclaim", "retrieval"]
RULE_ORDER = ["mode", "representation", "strategy", "library", "reduction", "scope", "check", "retrieval", "budget"]


def modlog():
    return load(MODLOG)["runs"]


def fig_modloop():
    runs = modlog()
    recs = [r for run in runs for r in run["records"]]
    fig = plt.figure(figsize=(7.2, 3.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.40)

    ax = fig.add_subplot(gs[0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 64)
    ax.axis("off")
    title(ax, "(a) One turn of the loop")

    def box(x, y, w, h, text, col, fs=5.4):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8", fc=col, ec="k", lw=0.5))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.05)

    def arrow(x0, y0, x1, y1, lab=None, col="k", off=(0, 1.3), rad=0.0):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=7, lw=0.7, color=col,
                                     connectionstyle=f"arc3,rad={rad}"))
        if lab:
            ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], lab, ha="center", fontsize=5.0, color=GREY)

    box(1.0, 46, 20, 11, "attempt\nunder rule book\nversion $v$", "#e8eef8")
    box(28, 46, 18, 11, "checks, refuter,\nLean", "#f8e8e8")
    box(56, 50, 16, 7, "closed: stop,\nkeep the rules", "#e8f4ea")
    box(56, 36, 16, 8, "failed, partial\nor stopped", "#fff3d6")
    box(78, 36, 20, 21, "log record:\ntarget, attempt,\nfailed part and\nits measured\nevidence", "#eeeeee")
    box(78, 8, 20, 18, "diagnosis\none of 9 failure\nkinds", "#eeeeee")
    box(46, 8, 24, 18, "playbook ranks\n9 rule kinds:\nprior table, then\nthe retries in the log", "#efe6f5")
    box(12, 8, 26, 18, "change one rule:\nold value, new value\nand the measurement\nit must improve", "#efe6f5")
    arrow(21.8, 51.5, 28, 51.5)
    arrow(46, 53, 56, 53.5)
    arrow(46, 49, 56, 41)
    arrow(72, 40, 78, 44)
    arrow(88, 36, 88, 26)
    arrow(78, 17, 70, 17)
    arrow(46, 17, 38, 17)
    arrow(13, 26.5, 8, 46, col=BLUE, rad=-0.15)
    ax.text(1.0, 33, "retry\nunder\nversion\n$v+1$", fontsize=5.0, color=BLUE, ha="left", va="center")
    ax.text(50, 1.2, "a change that was already tried on the target is refused;\n"
            "every record goes to the shared memory (table modlog)", ha="center", fontsize=5.0, color=GREY)

    ax = fig.add_subplot(gs[1])
    rows = [k for k in KIND_ORDER if any(r.get("change") and r["diagnosis"] == k for r in recs)]
    cols = [k for k in RULE_ORDER if any(r.get("change") and r["change"]["kind"] == k for r in recs)]
    C = np.zeros((len(rows), len(cols)), int)
    W = np.zeros_like(C)
    for r in recs:
        if r.get("change") and r["diagnosis"] in rows and r["change"]["kind"] in cols:
            i, j = rows.index(r["diagnosis"]), cols.index(r["change"]["kind"])
            C[i, j] += 1
            W[i, j] += r.get("retry") in ("closed", "partial")
    ax.imshow(C, cmap="Oranges", vmin=0, vmax=max(1, C.max()) * 2.4, aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)):
            if C[i, j]:
                ax.text(j, i, f"{C[i, j]}" + (f"\n{W[i, j]} won" if W[i, j] else ""), ha="center", va="center",
                        fontsize=5.2, color=GREEN if W[i, j] else "k", fontweight="bold" if W[i, j] else "normal")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=40, ha="right", fontsize=5.6)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=5.6)
    ax.set_xlabel("kind of rule changed", fontsize=6.5)
    ax.set_ylabel("diagnosis of the failure", fontsize=6.5)
    tot = int(C.sum())
    won = int(W.sum())
    title(ax, f"(b) {tot} changes; {won} retries closed or advanced")
    fig.savefig(os.path.join(OUT, "fig_modloop.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


OCOL = {"closed": GREEN, "partial": "#7fbf7b", "failed": RED, "stopped": GOLD}
RUNNAME = {"construction": "construction mode, 19 October (graph colouring gadgets)",
           "seed": "Calabi\u2013Yau seed conjecture, 19 October (reflexive polytopes)"}


def fig_modladder():
    runs = modlog()
    rows = []  # ("run", name) or ("target", run, name, records)
    for run in runs:
        rows.append(("run", run["run"], run.get("title", RUNNAME.get(run["run"], run["run"]))))
        seen = []
        for r in run["records"]:
            if r["target"] not in seen:
                seen.append(r["target"])
        for t in seen:
            rows.append(("target", run["run"], t, [r for r in run["records"] if r["target"] == t]))
    STEP = 4.2
    NAME = -7.4
    maxa = max(len(r[3]) for r in rows if r[0] == "target")
    h = 0.30 * sum(1 for r in rows if r[0] == "target") + 0.20 * sum(1 for r in rows if r[0] == "run") + 0.55
    fig, ax = plt.subplots(figsize=(7.2, h))
    y = 0.0
    for row in rows:
        if row[0] == "run":
            y -= 0.15
            ax.text(NAME, y, row[2], ha="left", va="center", fontsize=6.4, color=BLUE,
                    fontweight="bold")
            ax.plot([NAME, maxa * STEP], [y - 0.42, y - 0.42], color=BLUE, lw=0.4)
            y -= 1.0
            continue
        _, run, t, rs = row
        for r in rs:
            x = (r["attempt"] - 1) * STEP
            ax.add_patch(FancyBboxPatch((x, y - 0.3), 0.9, 0.6, boxstyle="round,pad=0.05", fc=OCOL[r["outcome"]],
                                        ec="k", lw=0.4))
            ax.text(x + 0.45, y, str(r["attempt"]), ha="center", va="center", fontsize=5.5, color="white",
                    fontweight="bold")
            if r.get("change"):
                c = r["change"]
                built = bool(r.get("retry"))
                ax.annotate("", xy=(x + STEP - 0.05 if built else x + STEP - 1.0, y), xytext=(x + 1.0, y),
                            arrowprops=dict(arrowstyle="-|>", lw=0.5, color=GREY, mutation_scale=6,
                                            linestyle="-" if built else (0, (2, 1.5))))
                mid = x + 0.95 + (STEP - 1.0) / 2
                ax.text(mid, y + 0.10, r["diagnosis"], ha="center", va="bottom", fontsize=4.5, color="#444444")
                ax.text(mid, y - 0.08, c["kind"], ha="center", va="top", fontsize=4.5, color=PURPLE,
                        style="italic")
        ax.text(NAME + 0.3, y, t, ha="left", va="center", fontsize=5.6)
        y -= 1.0
    handles = [matplotlib.patches.Patch(color=c, label=l) for l, c in OCOL.items()]
    handles.append(matplotlib.lines.Line2D([], [], color=GREY, lw=0.6, linestyle=(0, (2, 1.5)),
                                           label="change recorded, not yet built"))
    ax.legend(handles=handles, ncol=5, fontsize=5.6, frameon=False, loc="upper center",
              bbox_to_anchor=(0.5, 0.0), handlelength=1.6, columnspacing=1.2)
    ax.text(maxa * STEP, 0.45, "above each arrow: diagnosis of the failure;  below: kind of rule changed",
            ha="right", va="bottom", fontsize=5.2, color=GREY)
    ax.set_xlim(NAME - 0.2, maxa * STEP + 0.2)
    ax.set_ylim(y + 0.5, 0.9)
    ax.axis("off")
    fig.savefig(os.path.join(OUT, "fig_modladder.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_anatomy()
    fig_growth()
    fig_modloop()
    fig_modladder()
    print("done")
