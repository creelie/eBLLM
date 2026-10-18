"""Figures of the crossing network and of the monochromatic sublattices of Erdos problem 1183.

Reads data/crossing_round2.json and data/crossing_novel.json (summaries written by
experiments/crossing/summarise.py of the eBLLM package) and data/sublattice_levels.json (the exhaustive
scans of level colourings).  PNG at 400 dpi.
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

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
ARMS = ["network", "select", "random", "blind"]
COL = {"network": BLUE, "select": PURPLE, "random": GOLD, "blind": GREY}
DPI = 400


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=DPI, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def title(ax, s):
    ax.set_title(s, loc="left", fontweight="bold")


def bars3d(ax, d, key, zlabel):
    G = len(d[ARMS[0]][key])
    for i, a in enumerate(ARMS):
        z = np.array(d[a][key], float)
        ax.bar3d(np.arange(1, G + 1) - 0.35, np.full(G, i) - 0.3, np.zeros(G), 0.7, 0.6, z,
                 color=COL[a], alpha=0.85, edgecolor="k", linewidth=0.2, shade=True)
    ax.set_xlabel("generation", labelpad=-2)
    ax.set_yticks(range(len(ARMS)))
    ax.set_yticklabels(ARMS, fontsize=6.5)
    if zlabel:
        ax.set_zlabel(zlabel, labelpad=-1)
    ax.view_init(elev=24, azim=-58)
    ax.tick_params(pad=-1)


def fig_crossing():
    r2 = json.load(open(os.path.join(DATA, "crossing_round2.json")))
    nv = json.load(open(os.path.join(DATA, "crossing_novel.json")))
    fig = plt.figure(figsize=(7.3, 2.6))
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    bars3d(ax, r2, "passed_per_gen_mean", None)
    title(ax, "(a) passing offspring per run")
    ax = fig.add_subplot(1, 3, 2, projection="3d")
    bars3d(ax, r2, "new_per_gen_mean", None)
    title(ax, "(b) new colourings per run")
    ax = fig.add_subplot(1, 3, 3)
    x = np.arange(len(ARMS))
    for k, (dd, lab, off) in enumerate(((r2, "free", -0.18), (nv, "novelty rule", 0.18))):
        m = [dd[a]["new_colourings_mean"] for a in ARMS]
        s = [dd[a]["new_colourings_sd"] for a in ARMS]
        ax.bar(x + off, m, 0.34, yerr=s, capsize=2, color=[COL[a] for a in ARMS],
               alpha=0.55 if k == 0 else 0.95, edgecolor="k", linewidth=0.4, label=lab,
               hatch="//" if k == 0 else None)
    ax.set_xticks(x)
    ax.set_xticklabels(ARMS, fontsize=7)
    ax.set_ylabel("new colourings, mean of 5 runs")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#bbbbbb", edgecolor="k", hatch="//", label="free"),
                       Patch(facecolor="#555555", edgecolor="k", label="novelty rule")],
              frameon=False, loc="upper left")
    title(ax, "(c) the controls")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.subplots_adjust(wspace=0.5)
    save(fig, "fig_crossing")


def fig_sublattice():
    d = json.load(open(os.path.join(DATA, "sublattice_levels.json")))
    fig = plt.figure(figsize=(7.1, 2.7))
    ax = fig.add_subplot(1, 2, 1)
    n = np.arange(1, 21)
    ax.plot(n, (n + 2) // 2, color=GREY, lw=1.0, ls="--", label=r"chain bound $\lceil (n+1)/2\rceil$")
    odd = np.arange(11, 21, 2)
    ax.plot(odd, (odd + 3) // 2, "v", color=RED, ms=4, label=r"Lean lower bound $(n+3)/2$, odd $n\geq 11$")
    ax.plot([20], [12], "^", color=GOLD, ms=4.5, label=r"twenty-level lower bound, $n=20$")
    fv = {int(k): v for k, v in d["f"].items()}
    ax.plot(sorted(fv), [fv[k] for k in sorted(fv)], "o", color=BLUE, ms=3.6, label=r"$f(n)$, exact")
    lv = {int(k): v for k, v in d["level_min"].items()}
    ax.plot(sorted(lv), [lv[k] for k in sorted(lv)], "s", mfc="none", color=GREEN, ms=6,
            label="best level colouring")
    ax.set_xlabel(r"$n$")
    ax.set_ylabel("largest monochromatic sublattice")
    ax.set_xticks(range(2, 21, 2))
    ax.legend(frameon=False, loc="upper left", fontsize=6.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    title(ax, r"(a) values of $f(n)$")
    ax = fig.add_subplot(1, 2, 2, projection="3d")
    H = {int(k): {int(a): b for a, b in v.items()} for k, v in d["hist"].items()}
    ns = sorted(H)
    for i, m in enumerate(ns):
        tot = sum(H[m].values())
        c = (m + 2) // 2
        for e in range(0, 4):
            z = H[m].get(c + e, 0) / tot
            ax.bar3d(m - 0.35, e - 0.35, 0, 0.7, 0.7, z, color=[BLUE, GREEN, GOLD, RED][e], alpha=0.85,
                     edgecolor="k", linewidth=0.2)
    ax.set_xlabel(r"$n$", labelpad=-2)
    ax.set_ylabel("excess over chain bound", labelpad=-2)
    ax.set_yticks(range(4))
    ax.set_zlabel("share of level words", labelpad=-1)
    ax.view_init(elev=26, azim=-50)
    ax.tick_params(pad=-1)
    title(ax, "(b) all level colourings")
    fig.subplots_adjust(wspace=0.12)
    save(fig, "fig_sublattice")


if __name__ == "__main__":
    fig_crossing()
    fig_sublattice()
