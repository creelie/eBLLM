"""Figures of the crossing network with boosters, memory, the attack channel and the agents.

Reads, from data/ (copied from the eBLLM package):
  amp_synapses.json, amp_rounds.json, amp_graph.json, amp_composites_summary.json  (experiments/amplify)
  memory_study.json                                                                  (experiments/superbrain)
  loop_state.json                                                                    (experiments/loop)
Writes fig_boosters, fig_graph, fig_memory and fig_channel as PNG at 400 dpi.
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY, PURPLE = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555", "#5b2a86"
DPI = 400
OUTCOME_COL = {"accepted": GREEN, "rejected": RED, "stopped": GOLD}


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def title(ax, s):
    ax.set_title(s, loc="left", fontweight="bold")


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def short(key):
    return key.replace("ym.", "").replace("h.", "")


# ---------------------------------------------------------------- boosters
def fig_boosters():
    syn = load("amp_synapses.json")
    rounds = load("amp_rounds.json")
    comp = load("amp_composites_summary.json")
    fig = plt.figure(figsize=(7.2, 2.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.25, 1.0, 1.0], wspace=0.95)

    ax = fig.add_subplot(gs[0])
    keys = []
    for r in syn:
        for f in r["fired"]:
            k = f["a"].split("<-")[0].strip("()") + "|" + f["b"]
            if k in r["weights"] and k not in keys:
                keys.append(k)
    for r in syn:
        for k in r["weights"]:
            if k not in keys:
                keys.append(k)
    keys = keys[:16]
    M = np.full((len(keys), len(syn)), np.nan)
    for j, r in enumerate(syn):
        for i, k in enumerate(keys):
            if k in r["weights"]:
                M[i, j] = r["weights"][k]
    im = ax.imshow(M, aspect="auto", cmap="viridis", vmin=0, vmax=max(2.0, np.nanmax(M)))
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([short(k).replace("|", " × ") for k in keys], fontsize=5.2)
    ax.set_xticks(range(len(syn)))
    ax.set_xticklabels([str(r["round"]) for r in syn])
    ax.set_xlabel("round")
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03)
    cb.ax.tick_params(labelsize=6)
    cb.ax.set_title("weight", fontsize=6.0)
    title(ax, "(a) synapse weights")

    ax = fig.add_subplot(gs[1])
    for arm, col, off in (("boosted", BLUE, -0.08), ("unboosted", GREY, 0.08)):
        x = np.array([r["round"] for r in rounds[arm]]) + off
        y = np.array([r["share"] for r in rounds[arm]])
        e = np.array([r["se"] for r in rounds[arm]])
        ax.errorbar(x, y, yerr=e, color=col, marker="o", ms=3.5, lw=1.0, capsize=2, label=arm)
    ax.axhline(0, color=GOLD, lw=1.0, ls=":", label="random (0 of 200)")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xlabel("round")
    ax.set_ylabel(r"share of runs reaching $\beta_W<\frac{1}{3}$")
    ax.set_ylim(-0.01, 0.2)
    ax.legend(frameon=False, loc="upper left")
    clean(ax)
    title(ax, "(b) reaching the step")

    ax = fig.add_subplot(gs[2])
    depths = sorted(comp["by_depth"], key=int)
    bottom = np.zeros(len(depths))
    for o in ("accepted", "rejected", "stopped"):
        v = np.array([comp["by_depth"][d].get(o, 0) for d in depths], float)
        ax.bar(range(len(depths)), v, bottom=bottom, color=OUTCOME_COL[o], edgecolor="k", lw=0.3, label=o)
        bottom += v
    ax.set_yscale("symlog", linthresh=10)
    ax.set_xticks(range(len(depths)))
    ax.set_xticklabels(depths)
    ax.set_xlabel("depth")
    ax.set_ylabel("closed composites")
    ax.legend(frameon=False, loc="upper left")
    clean(ax)
    title(ax, "(c) outcomes by depth")
    fig.savefig(os.path.join(OUT, "fig_boosters.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- graph
def fig_graph():
    g = load("amp_graph.json")
    comp = load("amp_composites_summary.json")
    lib = [n for n in g["nodes"] if n.get("library")]
    by_type = {}
    for n in lib:
        by_type.setdefault(n["gives"], []).append(n["id"])
    level = {}

    def lev(n, seen=()):
        if n["id"] in level:
            return level[n["id"]]
        best = 0
        for t in n["needs"]:
            for m in lib:
                if m["gives"] == t and m["id"] not in seen and m["id"] != n["id"]:
                    best = max(best, 1 + lev(m, seen + (n["id"],)))
        level[n["id"]] = best
        return best

    for n in lib:
        lev(n)
    fig = plt.figure(figsize=(7.2, 3.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.7, 1.0, 1.0], wspace=0.45)
    ax = fig.add_subplot(gs[0])
    pos = {}
    for side, prob in ((0, "yang-mills"), (1, "hodge")):
        nodes = [n for n in lib if n["problem"] == prob]
        for L in sorted({level[n["id"]] for n in nodes}):
            row = [n for n in nodes if level[n["id"]] == L]
            for k, n in enumerate(row):
                x = (k - (len(row) - 1) / 2) * (0.62 if side == 0 else 0.72) + (3.0 if side == 0 else 10.2)
                pos[n["id"]] = (x, L)
    head = {"ym.dobrushin", "ym.quarter", "ym.vmf", "ym.maxtree"}
    for n in lib:
        for t in n["needs"]:
            for b in by_type.get(t, []):
                if b in pos and n["id"] in pos and b != n["id"]:
                    (x0, y0), (x1, y1) = pos[b], pos[n["id"]]
                    hot = b in head and n["id"] in head
                    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                                arrowprops=dict(arrowstyle="-|>", lw=0.9 if hot else 0.35,
                                                color=BLUE if hot else "#999999", shrinkA=4, shrinkB=4,
                                                mutation_scale=5))
    for n in lib:
        x, y = pos[n["id"]]
        col = BLUE if n["id"] in head else (GREY if n["problem"] == "yang-mills" else PURPLE)
        ax.scatter([x], [y], s=26, color=col, zorder=3, edgecolor="k", lw=0.3)
        ax.text(x, y + 0.16, short(n["id"]), fontsize=4.3, ha="left", va="bottom", rotation=55)
    ax.text(2.2, -0.9, "Yang–Mills", ha="center", fontsize=7.5)
    ax.text(10.2, -0.9, "Hodge", ha="center", fontsize=7.5)
    ax.set_ylim(-1.2, max(level.values()) + 1.3)
    ax.set_xlim(-0.2, 12.6)
    ax.axis("off")
    title(ax, "(a) the library")

    ax = fig.add_subplot(gs[1])
    ct = g["cross_thread"]
    names = [c["source"].replace("creelie/", "").split(" (")[0] for c in ct]
    vals = [len(c["feeds"]) for c in ct]
    ax.barh(range(len(ct)), vals, color=[GREEN if v else "#cccccc" for v in vals], edgecolor="k", lw=0.3)
    ax.set_yticks(range(len(ct)))
    ax.set_yticklabels(names, fontsize=6)
    ax.invert_yaxis()
    ax.set_xlabel("library nodes fed")
    clean(ax)
    title(ax, "(b) feeding workstreams")

    ax = fig.add_subplot(gs[2])
    parts = sorted(comp["by_parts"], key=int)
    bottom = np.zeros(len(parts))
    for o in ("accepted", "rejected", "stopped"):
        v = np.array([comp["by_parts"][p].get(o, 0) for p in parts], float)
        ax.bar(range(len(parts)), v, bottom=bottom, color=OUTCOME_COL[o], edgecolor="k", lw=0.3, label=o)
        bottom += v
    ax.set_xticks(range(len(parts)))
    ax.set_xticklabels(parts, fontsize=6.5)
    ax.set_xlabel("parts")
    ax.set_ylabel("closed composites")
    ax.set_ylim(0, 390)
    ax.legend(frameon=False, loc="upper left", ncol=3, fontsize=5.6, handlelength=1.0, columnspacing=0.8)
    clean(ax)
    title(ax, "(c) by number of parts")
    fig.savefig(os.path.join(OUT, "fig_graph.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- memory and agents
def fig_memory():
    m = load("memory_study.json")
    loop = load("loop_state.json")
    fig = plt.figure(figsize=(7.2, 2.6))
    gs = fig.add_gridspec(1, 3, wspace=0.45)
    arms = [("full", "memory + retrieval", BLUE), ("full-noretrieve", "memory, no retrieval", PURPLE),
            ("boosted", "boosters only", GREY), ("unboosted", "no boosters", GOLD), ("random", "random", RED)]
    ax = fig.add_subplot(gs[0])
    for key, lab, col in arms:
        rows = m["arms"][key]["rows"]
        x = np.cumsum([r["checks"] for r in rows])
        y = [r["cum"] for r in rows]
        ax.plot(np.r_[0, x], np.r_[0, y], marker="o", ms=2.8, lw=1.0, color=col, label=lab)
    ax.set_xlabel("checks (cumulative)")
    ax.set_ylabel("distinct survivors")
    ax.legend(frameon=False, fontsize=5.6, loc="lower right")
    clean(ax)
    title(ax, "(a) survivors against checks")

    ax = fig.add_subplot(gs[1])
    w = 0.38
    for k, (key, lab, col) in enumerate(arms[:4]):
        rows = m["arms"][key]["rows"]
        useful = sum(r["checks"] - r["wasted"] for r in rows)
        wasted = sum(r["wasted"] for r in rows)
        ax.bar(k, useful, color=col, edgecolor="k", lw=0.3)
        ax.bar(k, wasted, bottom=useful, color="white", hatch="////", edgecolor=col, lw=0.6)
        ax.text(k, useful + wasted + 1.5, f"{useful + wasted:.0f}", ha="center", fontsize=6.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(["memory", "no retr.", "boosters", "none"], fontsize=6.5)
    ax.set_ylabel("checks over five rounds")
    ax.set_ylim(0, 118)
    ax.text(-0.4, 110, "hatched: checks spent on composites already decided", fontsize=5.6, ha="left", color=GREY)
    clean(ax)
    title(ax, "(b) where the checks go")

    ax = fig.add_subplot(gs[2])
    R = loop["rounds"]
    xa = np.cumsum([r["agents_total"]["checks"] for r in R])
    ya = [r["agents_total"]["known"] for r in R]
    xc = np.cumsum([r["control"]["checks"] for r in R])
    yc = [r["control"]["known"] for r in R]
    ax.plot(np.r_[0, xa], np.r_[0, ya], marker="o", ms=2.8, lw=1.0, color=BLUE, label="five target agents")
    ax.plot(np.r_[0, xc], np.r_[0, yc], marker="s", ms=2.8, lw=1.0, color=GREY, label="single loop")
    ax.set_xlabel("checks (cumulative)")
    ax.set_ylabel("distinct survivors")
    ax.legend(frameon=False, loc="lower right")
    clean(ax)
    title(ax, f"(c) agents, {len(R)} rounds")
    fig.savefig(os.path.join(OUT, "fig_memory.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- channel
def fig_channel():
    fig, ax = plt.subplots(figsize=(7.2, 2.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(-2.5, 34)
    ax.axis("off")

    def box(x, y, w, h, text, col, fs=6.6):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6", fc=col, ec="k", lw=0.5, alpha=0.95))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    def arrow(x0, y0, x1, y1, lab=None, col="k", dy=1.2):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color=col, mutation_scale=8))
        if lab:
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 + dy, lab, ha="center", fontsize=5.6, color=GREY)

    box(1, 13, 13, 8, "target point\n(one statement,\none type)", "#e8eef8")
    box(20, 22, 15, 9, "memory\nnodes, events, parts,\nweights, blocks", "#eeeeee", 6.0)
    box(20, 3, 15, 9, "barrier × pattern\nmatrix, ceilings,\nliterature checks", "#eeeeee", 6.0)
    box(40, 12, 14, 10, "attack bundle\nretrievals, cells,\nsynapses, refuted,\nblocks", "#fff3d6", 6.0)
    box(59, 12, 14, 10, "proposers\ntyped, novelty,\nuniform, local LM\n(spiking race)", "#e8f4ea", 6.0)
    box(78, 22, 20, 9, "check, refuter, Lean\naccept / reject / stop", "#f8e8e8", 6.0)
    box(78, 3, 20, 9, "boosters and memory\nweights, events, blocks", "#e8eef8", 6.0)
    arrow(14, 18, 40, 17, "distance to target")
    arrow(35, 26, 40, 20)
    arrow(35, 8, 40, 14)
    arrow(54, 17, 59, 17)
    arrow(73, 19, 78, 25)
    arrow(88, 22, 88, 12.5)
    ax.text(89, 17, "outcome", fontsize=5.6, color=GREY, ha="left")
    ax.plot([78, 76, 76, 17.5, 17.5], [5, 5, 0.4, 0.4, 26.5], color=BLUE, lw=0.8)
    arrow(17.5, 26.5, 20, 26.5, col=BLUE)
    ax.text(47, -1.3, "every outcome flows back into memory and the weights", fontsize=5.8, color=BLUE, ha="center")
    fig.savefig(os.path.join(OUT, "fig_channel.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_boosters()
    fig_graph()
    fig_memory()
    fig_channel()
