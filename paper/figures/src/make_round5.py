"""Figure of the headline benchmark: the typed crossing on the open steps of Yang-Mills and Hodge.

Reads data/headline_rounds.json (written by experiments/headline.py of the eBLLM package).  PNG at 400 dpi.
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
DPI = 400

YM_LEAVES = [("YM.lean", "Lean"), ("YM.strong", "strong"), ("YM.weak", "weak"), ("YM.window.lower", r"$\frac{1}{3}$"),
             ("YM.window.box", "box"), ("YM.window.lift", "lift"), ("YM.window.lsi", "LSI"),
             ("YM.continuum", "cont.")]
H_LEAVES = [("H.lean", "Lean"), ("H.F2.dim5", r"dim$\leq5$"), ("H.F2.cm", "CM"), ("H.F2.weil8", "Weil 8"),
            ("H.F2.E06", r"$E_0^6$"), ("H.F2.weil6", "Weil 6"), ("H.F3p.K3RM", "K3 RM"),
            ("H.F3p.fermat.reduction", "Fermat"), ("H.F3p.fermat110", "110"), ("H.F3p.fermat220", "220")]


def title(ax, s):
    ax.set_title(s, loc="left", fontweight="bold")


def panel_arms(ax, arms):
    names = ["network", "select", "random"]
    keys = [("offspring", "bred"), ("ill_typed", "ill-typed"), ("checked", "checked"), ("accepted", "kept")]
    cols = [BLUE, PURPLE, GOLD]
    for i, a in enumerate(names):
        z = np.log10(1 + np.array([arms[a][k] for k, _ in keys], float))
        ax.bar3d(np.arange(len(keys)) - 0.35, np.full(len(keys), i) - 0.3, np.zeros(len(keys)), 0.7, 0.6, z,
                 color=cols[i], alpha=0.85, edgecolor="k", linewidth=0.2, shade=True)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([l for _, l in keys], fontsize=6.0, rotation=0, ha="center")
    ax.set_yticks(range(3))
    ax.set_yticklabels(names, fontsize=6.5)
    ax.set_zticks([0, 1, 2])
    ax.set_zticklabels(["1", "10", "100"], fontsize=6.5)
    ax.view_init(elev=24, azim=-60)
    ax.tick_params(pad=-1)


def panel_coupling(ax):
    rows = [("Bakry\u2013\u00c9mery", 1 / 12, GREY), ("no gauge, 18 partners", 2 / 9, GOLD),
            ("temporal gauge, 14", 2 / 7, PURPLE), ("one link per plaquette, 12", 1 / 3, BLUE)]
    for k, (lab, b, c) in enumerate(rows):
        ax.barh(k, b, height=0.6, color=c, alpha=0.9, edgecolor="k", linewidth=0.4)
        ax.text(b + 0.012, k, lab.replace("\\'E", "É"), va="center", fontsize=6.6)
    ax.axvline(1 / 3, color=RED, lw=0.9, ls="--")
    ax.text(1 / 3 + 0.005, 3.75, "ceiling of every forest", color=RED, fontsize=6.4)
    ax.axvspan(1 / 3, 1.0, color="#dddddd", alpha=0.6, lw=0)
    ax.text(0.665, -0.55, "open window up to weak coupling (Ba\u0142aban) \u2192", ha="center", fontsize=6.4, color=GREY)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.8, 4.3)
    ax.set_yticks([])
    ax.set_xticks([0, 1 / 12, 2 / 9, 2 / 7, 1 / 3, 1.0])
    ax.set_xticklabels(["0", r"$\frac{1}{12}$", r"$\frac{2}{9}$", "", r"$\frac{1}{3}$", "1"])
    ax.set_xlabel(r"Wilson coupling $\beta_W$ of $\mathrm{SU}(2)$ in four dimensions")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)


def panel_closure(ax, after, rnd):
    status = {}
    for root in ("YM", "H"):
        c = after[root]
        for n in c["open"]:
            status[n] = "open"
        for n in c["blocked"]:
            status[n] = "blocked"
    for j, leaves in enumerate((YM_LEAVES, H_LEAVES)):
        for i, (node, _) in enumerate(leaves):
            s = status.get(node, "proved")
            h = {"proved": 1.0, "open": 0.18, "blocked": 0.08}[s]
            c = {"proved": GREEN, "open": GOLD, "blocked": RED}[s]
            if node == "YM.window.lower":
                c = BLUE
            ax.bar3d(i - 0.35, j - 0.3, 0, 0.7, 0.6, h, color=c, alpha=0.88, edgecolor="k", linewidth=0.2)
    ax.set_xticks(range(len(H_LEAVES)))
    ax.set_xticklabels([str(i + 1) for i in range(len(H_LEAVES))], fontsize=6.0)
    ax.set_xlabel("leaf", labelpad=-4)
    ax.set_yticks([0, 1])
    ax.set_yticklabels([f"YM {after['YM']['proved']}/{after['YM']['leaves']}",
                        f"Hodge {after['H']['proved']}/{after['H']['leaves']}"], fontsize=6.5)
    ax.set_zticks([])
    ax.view_init(elev=30, azim=-62)
    ax.tick_params(pad=-1)


def main():
    rounds = json.load(open(os.path.join(DATA, "headline_rounds.json")))
    r = rounds[-1]
    fig = plt.figure(figsize=(7.3, 2.7))
    ax = fig.add_subplot(1, 3, 1, projection="3d")
    panel_arms(ax, r["arms"])
    title(ax, "(a) the arms, per run (log scale)")
    ax = fig.add_subplot(1, 3, 2)
    panel_coupling(ax)
    title(ax, "(b) the strong-coupling ranges")
    ax = fig.add_subplot(1, 3, 3, projection="3d")
    panel_closure(ax, r["closure_after"], r["round"])
    title(ax, "(c) leaves after round %d" % r["round"])
    fig.subplots_adjust(wspace=0.32)
    fig.savefig(os.path.join(OUT, "fig_headline.png"), dpi=DPI, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


if __name__ == "__main__":
    main()
