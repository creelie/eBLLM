"""Figures of the Hodge-only run of the crossing network (Section on the Hodge round).

Reads, from data/hodge/ (copied from the run directory of experiments/hodge_loop.py):
  state.json         rounds 1 to 11, memory statistics, distances of the five target points
  round_012_stopped.json  the burst round 12, counted from the memory events (stopped at its time limit)
  figdata.json       Ext block matrices of the pieces on E_0^6 and the bounds of every configuration
  e06_count.json     the least lower bound of each family of configurations
  e06_chains.json    closed chains and restricted Euler bounds
  candidates.json    the explicit candidate constructions C1 to C8
  sources.json       the sources read and what was taken from each
Writes fig_hodgepieces, fig_hodgerounds, fig_hodgebounds and fig_hodgemap as PNG at 400 dpi.
"""
import json
import os
from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "hodge")
OUT = os.path.join(HERE, "..")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY, PURPLE, TEAL = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555", "#5b2a86", "#0b7285"
DPI = 400
TARGETS = ["F2.lift", "F2.E06", "F2.link", "F3.cubic", "F3.sqrt"]
TLABEL = {"F2.lift": "F2: lift from a CM point", "F2.E06": "F2: object on $E_0^6$", "F2.link": "F2: link class",
          "F3.cubic": "F3$'$: cubic correspondence", "F3.sqrt": "F3$'$: $\\sqrt{10}$, $\\sqrt{14}$ families"}
TCOL = {"F2.lift": BLUE, "F2.E06": RED, "F2.link": PURPLE, "F3.cubic": GREEN, "F3.sqrt": GOLD}


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def title(ax, s, **kw):
    ax.set_title(s, loc="left", fontweight="bold", **kw)


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


ARG = {"1": 0, "i": 1, "-1": 2, "-i": 3}


def zeta_index(s):
    """Fraction pair '(Fraction(a, b), Fraction(c, d))' -> 0..3 for 1, i, -1, -i."""
    s = s.replace("Fraction(", "").replace(")", "").replace(" ", "")
    a, b = s.strip("(").split(",")[0::2] if s.count(",") == 3 else (s.strip("(").split(",")[0], "0")
    x = int(a.split("/")[0]) if a else 0
    parts = s.strip("()").split(",")
    # the tuple printed by e06_count is ((re_num, re_den), (im_num, im_den)) flattened
    nums = [int(p) for p in parts]
    re, im = nums[0], nums[2]
    if re == 1 and im == 0:
        return 0
    if re == 0 and im == 1:
        return 1
    if re == -1 and im == 0:
        return 2
    return 3


def parse_zetas(fd):
    """fd['zetas'] entries are lists of str(Fraction pair); return (n, 3) integer indices or None."""
    out = []
    for z in fd["zetas"]:
        if z is None:
            out.append(None)
            continue
        idx = []
        for c in z:
            idx.append(zeta_index(c))
        out.append(idx)
    return out


# ------------------------------------------------------------------ fig_hodgepieces
def fig_hodgepieces():
    fd = load("figdata.json")
    blk = fd["C1_blocks"]
    n = len(blk["pieces"])
    shifts = np.array(blk["shifts"])
    kinds = blk["kinds"]
    twists = blk["twists"]
    zetas = parse_zetas(blk)
    deg = {int(k): np.array(v) for k, v in blk["by_degree"].items()}

    fig = plt.figure(figsize=(7.3, 7.6))
    # (a) the pieces in the cube of characters
    ax = fig.add_axes([-0.03, 0.50, 0.5, 0.47], projection="3d")
    for a in range(n):
        if zetas[a] is None:
            continue
        x, y, z = zetas[a]
        par = (x + y + z) % 4  # 0: prod zeta = 1, 2: prod zeta = -1
        c = BLUE if par == 0 else RED
        ax.scatter([x], [y], [z], s=60 + 40 * twists[a], c=c, depthshade=False, edgecolors="k", linewidths=0.3)
        ax.text(x, y, z + 0.18, f"$[{shifts[a]}]$", fontsize=5.5, ha="center")
    # the four line bundles, drawn on the diagonal above the cube
    for j, a in enumerate([k for k in range(n) if kinds[k] == "L"]):
        ax.scatter([3.9 + 0.0], [-0.9], [j * 0.9], s=90, marker="s", c=GOLD, edgecolors="k", linewidths=0.3,
                   depthshade=False)
        ax.text(3.9, -0.9, j * 0.9 + 0.22, f"$L^{twists[a]}[{shifts[a]}]$", fontsize=6, ha="center")
    ax.set_xticks(range(4)); ax.set_yticks(range(4)); ax.set_zticks(range(4))
    lab = ["$1$", "$i$", "$-1$", "$-i$"]
    ax.set_xticklabels(lab, fontsize=6); ax.set_yticklabels(lab, fontsize=6); ax.set_zticklabels(lab, fontsize=6)
    ax.set_xlabel(r"$\zeta_1$", labelpad=-6, fontsize=7); ax.set_ylabel(r"$\zeta_2$", labelpad=-6, fontsize=7)
    ax.set_zlabel(r"$\zeta_3$", labelpad=-8, fontsize=7)
    ax.tick_params(pad=-2)
    ax.view_init(elev=24, azim=-58)
    ax.set_box_aspect((1.2, 1, 0.9))
    ax.scatter([], [], [], c=BLUE, s=30, label=r"$\prod\zeta=1$, shift $0$")
    ax.scatter([], [], [], c=RED, s=30, label=r"$\prod\zeta=-1$, shift $1$")
    ax.scatter([], [], [], c=GOLD, marker="s", s=30, label=r"line bundles $L^{l}[t]$")
    ax.legend(loc="upper left", fontsize=6, frameon=False, bbox_to_anchor=(0.0, 0.98))
    fig.text(0.02, 0.975, "(a) the 36 pieces of candidate C1 on $E_0^6$: $O_{Z_\\zeta}[s]$ at $\\zeta\\in\\mu_4^3$, "
             "$\\prod\\zeta=\\pm1$, and $L^1[-2],L^2[-1],L^3[0],L^4[1]$", fontsize=7.5, fontweight="bold")

    # (b) row sums by total degree per piece
    ax = fig.add_axes([0.57, 0.58, 0.41, 0.34])
    order = np.array(sorted(range(n), key=lambda a: (0 if kinds[a] == "Z" else 1, shifts[a], twists[a])))
    width = 0.27
    for j, (d, c) in enumerate([(1, GOLD), (2, GREEN), (3, RED)]):
        M = deg.get(d)
        if M is None:
            continue
        ax.bar(np.arange(n) + (j - 1) * width, M.sum(1)[order], width, color=c, label=f"total degree {d}")
    ax.set_xticks(range(n))
    ax.set_xticklabels([("$Z$" if kinds[a] == "Z" else f"$L^{twists[a]}$") for a in order], fontsize=4.5,
                       rotation=90)
    ax.set_ylabel(r"$\sum_b \dim\mathrm{Ext}^{\bullet}(F_a,F_b)$")
    ax.set_yscale("log")
    ax.legend(frameon=False, loc="upper left", fontsize=6.5)
    clean(ax)
    title(ax, "(b) outgoing Ext dimensions of each piece, by total degree", fontsize=7.5)

    # (c), (d), (e) block matrices of total degree 1, 2, 3
    panels = [(1, "(c) total degree 1: the differential $d_E$"), (2, "(d) total degree 2: $\\mathrm{Ext}^2$ budget"),
              (3, "(e) total degree 3: targets of $d_E$")]
    vmax = max(int(deg[d].max()) for d, _ in panels if d in deg)
    for j, (d, t) in enumerate(panels):
        ax = fig.add_axes([0.05 + j * 0.325, 0.04, 0.27, 0.46])
        M = deg[d][np.ix_(order, order)].astype(float)
        M[M == 0] = np.nan
        im = ax.imshow(M, cmap="viridis", norm=LogNorm(vmin=1, vmax=vmax), interpolation="nearest")
        # separators between parity classes and the line bundles
        cuts = [i for i in range(1, n) if (kinds[order[i]], shifts[order[i]]) != (kinds[order[i - 1]], shifts[order[i - 1]])]
        for cpos in cuts:
            ax.axhline(cpos - 0.5, color="w", lw=0.5); ax.axvline(cpos - 0.5, color="w", lw=0.5)
        ax.set_xticks([]); ax.set_yticks([])
        groups = [(0, "$Z$, shift 0")] + [(cpos, {("Z", 1): "$Z$, shift 1"}.get((kinds[order[cpos]], shifts[order[cpos]]),
                                                                              f"$L^{twists[order[cpos]]}$")) for cpos in cuts]
        for k, (start, lab) in enumerate(groups):
            end = groups[k + 1][0] if k + 1 < len(groups) else n
            ax.text(-0.8, 0.5 * (start + end - 1), lab, ha="right", va="center", fontsize=5.5)
        ax.set_xlabel("piece $F_b$", fontsize=7)
        title(ax, t, fontsize=7.5)
        tot = int(np.nansum(M))
        ax.text(0.99, -0.06, f"sum {tot:,}", transform=ax.transAxes, ha="right", fontsize=6.5)
    cax = fig.add_axes([0.975, 0.10, 0.01, 0.34])
    cb = fig.colorbar(im, cax=cax, ticks=[1, 10, 100, 1000, 10000])
    cb.ax.set_yticklabels(["1", "10", "100", "1000", "10000"])
    cb.set_label(r"$\dim\mathrm{Ext}$ (log)", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    fig.savefig(os.path.join(OUT, "fig_hodgepieces.png"), dpi=DPI)
    plt.close(fig)


# ------------------------------------------------------------------ fig_hodgerounds
def fig_hodgerounds():
    st = load("state.json")
    rounds = st["rounds"]
    r12 = load("round_012_stopped.json")
    R = [r["round"] for r in rounds]
    stopped = [r["stopped"] for r in rounds]
    rejected = [r["rejected"] for r in rounds]
    known = [len(r["survivors"]) for r in rounds]
    survivors_new = [len(r["new_non_known_survivors"]) for r in rounds]
    R12 = r12["round"]
    cond12 = sum(v for k, v in r12["by_stop"].items() if k.startswith("oc."))
    other12 = r12["outcomes"].get("stopped", 0) - cond12
    rej12 = r12["outcomes"].get("rejected", 0)

    fig = plt.figure(figsize=(7.3, 3.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.3, 1.0, 1.0], wspace=1.05)

    ax = fig.add_subplot(gs[0])
    ax.axvspan(R12 - 0.5, R12 + 0.5, color=GOLD, alpha=0.15, lw=0)
    ax.bar(R, rejected, color=RED, label="rejected by the refuter")
    ax.bar(R, stopped, bottom=rejected, color=GOLD, label="stopped at an open step")
    ax.bar(R, known, bottom=np.array(rejected) + np.array(stopped), color=GREY, label="survivor, a known result")
    ax.bar([R12], [rej12], color=RED)
    ax.bar([R12], [other12], bottom=[rej12], color=GOLD)
    ax.bar([R12], [cond12], bottom=[rej12 + other12], color=PURPLE, hatch="////", edgecolor="white", lw=0,
           label="stopped: open conjecture as hypothesis")
    ax.plot(R + [R12], survivors_new + [r12["new_non_known_survivors"]], "o-", color=GREEN, ms=3, lw=0.8,
            label="new non-known survivors")
    ax.annotate("burst, stopped\nat its time limit", xy=(R12, rej12 + other12 + cond12), xytext=(R12 - 3.2, 52),
                fontsize=5.5, ha="center", arrowprops=dict(arrowstyle="-", color=GREY, lw=0.5))
    ax.set_xlabel("round"); ax.set_ylabel("checked composites")
    ax.set_xticks([1, 3, 5, 7, 9, 11, 12])
    ax.legend(frameon=False, fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2)
    clean(ax)
    title(ax, "(a) checks per round (round 12 a burst)")

    ax = fig.add_subplot(gs[1])
    gaps = rounds[-1]["gaps"]
    ys = np.arange(len(TARGETS))
    rej = [g["checked"].get("rejected", 0) for g in gaps]
    stp = [g["checked"].get("stopped", 0) for g in gaps]
    ax.barh(ys, rej, color=RED, label="rejected")
    ax.barh(ys, stp, left=rej, color=GOLD, label="stopped")
    for y, g in zip(ys, gaps):
        ax.text(rej[y] + stp[y] + 1, y, f"depth {g['depth']}", va="center", fontsize=6.5)
    ax.set_yticks(ys); ax.set_yticklabels([TLABEL[g["target"]] for g in gaps], fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel("composites aimed at the target point")
    ax.legend(frameon=False, fontsize=6, loc="lower right")
    clean(ax)
    title(ax, f"(b) per target, after round {R[-1]}")

    ax = fig.add_subplot(gs[2])
    for i, t in enumerate(TARGETS):
        d = [r["gaps"][i]["depth"] for r in rounds]
        ax.plot(R, np.array(d) + 0.03 * (i - 2), "-", color=TCOL[t], lw=1.2, label=TLABEL[t])
        reached = [r["gaps"][i]["reached"] for r in rounds]
        if any(reached):
            ax.plot([R[k] for k in range(len(R)) if reached[k]], [0] * sum(reached), "*", color=TCOL[t])
    ax.set_ylim(-0.3, 3.6)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_xlabel("round"); ax.set_ylabel("open steps to the target point")
    ax.set_xticks([1, 3, 5, 7, 9, 11])
    ax.legend(frameon=False, fontsize=5.5, loc="upper right")
    clean(ax)
    title(ax, "(c) the gap by round")
    fig.savefig(os.path.join(OUT, "fig_hodgerounds.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ fig_hodgebounds
def fig_hodgebounds():
    fd = load("figdata.json")
    cnt = load("e06_count.json")
    A = fd.get("family_a_rows", [])
    C = fd.get("family_c_rows", [])
    fig = plt.figure(figsize=(7.3, 3.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.05, 1.0], wspace=0.75)

    ax = fig.add_subplot(gs[0])
    if A:
        safe = np.array([r["safe"] for r in A])
        ax.hist(safe, bins=40, color=BLUE, alpha=0.85, label=f"(a) four or five line bundles, {len(A)} configurations")
    if C:
        safe_c = np.array([r["safe"] for r in C])
        ax.hist(safe_c, bins=40, color=GREEN, alpha=0.7, label=f"(c) one threefold at three twists, {len(C)}")
    ax.axvline(57, color=RED, lw=1, ls="--")
    ax.text(57, 0.97, "$r=57$", transform=ax.get_xaxis_transform(), color=RED, fontsize=6.5, ha="left")
    ax.set_xlabel(r"lower bound for $\dim\mathrm{Ext}^2(E,E)$ (isolated blocks)")
    ax.set_ylabel("configurations")
    ax.set_yscale("log")
    ax.legend(frameon=False, fontsize=5.5, loc="upper right", bbox_to_anchor=(1.0, 0.9))
    clean(ax)
    title(ax, "(a) the isolated-block bound", fontsize=8)

    ax = fig.add_subplot(gs[1])
    if A:
        c1 = np.array([r["C1"] for r in A]); c2 = np.array([r["C2"] for r in A]); c3 = np.array([r["C3"] for r in A])
        sc = ax.scatter(c1 + c3, c2, c=safe, s=4, cmap="viridis", linewidths=0, label="(a)")
        cax = ax.inset_axes([0.06, 0.45, 0.04, 0.45])
        cb = fig.colorbar(sc, cax=cax)
        cb.set_label("isolated blocks", fontsize=6); cb.ax.tick_params(labelsize=5.5)
    if C:
        c1 = np.array([r["C1"] for r in C]); c2 = np.array([r["C2"] for r in C]); c3 = np.array([r["C3"] for r in C])
        ax.scatter(c1 + c3, c2, s=6, marker="^", color=GREEN, linewidths=0, label="(c)")
    lim = ax.get_xlim()
    ax.plot(lim, lim, color=GREY, lw=0.6, ls=":")
    ax.text(lim[1], lim[1], "Euler $=0$", fontsize=6, ha="right", va="bottom", color=GREY)
    ax.set_xlabel("$C^1+C^3$"); ax.set_ylabel("$C^2$")
    ax.legend(frameon=False, fontsize=6, loc="upper left")
    clean(ax)
    title(ax, "(b) Euler characteristic, negative throughout", fontsize=8)

    ax = fig.add_subplot(gs[2])
    rows = [("35 pieces, $L$ at $[0,0,0]$", cnt["base35 L(1, 2, 3) shifts(0, 0, 0)"]["lower"]),
            ("35 pieces, $L$ at $[2,3,4]$", cnt["base35 L(1, 2, 3) shifts(2, 3, 4)"]["lower"]),
            ("(d) same shift", cnt["family_d"]["least"][0]),
            ("(a) $\\geq4$ line bundles", cnt["family_a"]["least"][0]),
            ("(c) three twists", cnt["family_c"]["least"][0]),
            ("$E_0^8$, six shifts", 640), ]
    labels = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    need = [57, 57, 57, 57, 57, 104]
    ys = np.arange(len(rows))
    cols = [RED if v > nd else GOLD for v, nd in zip(vals, need)]
    ax.barh(ys, [max(v, 1) for v in vals], color=cols)
    for y, v, nd in zip(ys, vals, need):
        ax.plot([nd, nd], [y - 0.4, y + 0.4], color="k", lw=1)
        ax.text(max(v, 1) * 1.15 if v > 0 else 1.3, y, f"{v}" + (" (excluded)" if v > nd else " (not excluded)"),
                va="center", fontsize=6)
    ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xscale("log"); ax.set_xlim(0.8, 3e4)
    ax.set_xlabel("least lower bound; tick = required rank $r$")
    clean(ax)
    title(ax, "(c) least bound of each family", fontsize=8)
    fig.savefig(os.path.join(OUT, "fig_hodgebounds.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ fig_hodgemap
def box(ax, x, y, w, h, text, fc, ec="k", fs=6.2, lw=0.6, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, color=GREY, lw=0.7, style="-|>"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=7, color=color, lw=lw))


def fig_hodgemap():
    cand = load("candidates.json")
    st = load("state.json")
    src = load("sources.json")
    chains = load("e06_chains.json")
    r12 = load("round_012_stopped.json")
    fig = plt.figure(figsize=(7.3, 8.2))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # top row: the two statements and the five target points
    box(ax, 0.02, 0.93, 0.44, 0.05, "(F2)  Hodge classes on abelian varieties outside R(Y) are algebraic\n"
        "equivalent: algebraicity lifts from a CM point of every family", "#dbe6f5", bold=False, fs=6.4)
    box(ax, 0.54, 0.93, 0.44, 0.05, "(F3$'$)  $\\mathrm{Hdg}^p = \\mathrm{Ab}^p$: every Hodge class comes from "
        "abelian varieties\n(the Hodge conjecture is (F2) and (F3$'$) together)", "#e3f1e0", fs=6.4)
    xs = {"F2.lift": 0.02, "F2.E06": 0.21, "F2.link": 0.40, "F3.cubic": 0.59, "F3.sqrt": 0.78}
    depth = {g["target"]: g["depth"] for g in st["rounds"][-1]["gaps"]}
    checked = {g["target"]: g["checked"] for g in st["rounds"][-1]["gaps"]}
    for t, x in xs.items():
        ch = checked[t]
        box(ax, x + 0.01, 0.82, 0.17, 0.075, f"{TLABEL[t]}\n{depth[t]} open step(s)\n"
            f"{ch.get('rejected', 0)} rejected, {ch.get('stopped', 0)} stopped", "#f6f6f6", ec=TCOL[t], lw=1.2, fs=6)
        arrow(ax, x + 0.095, 0.93, x + 0.095, 0.901, color=TCOL[t])
    # candidates under their targets
    import textwrap
    SHORT = {"C1": "32 threefolds and L^1[-2], L^2[-1], L^3[0], L^4[1]",
             "C8": "six or more line bundles, each threefold once",
             "C2": "one threefold at twists 1,1,2,2, shifts -1,0,1,2",
             "C3": "two threefolds at one shift, meeting along a surface",
             "C4": "Weil family of dim 9 through E_0^6 with the product object",
             "C5": "the link class as a Hodge class on the CM sixfold",
             "C6": "correspondences of S_lambda: Mukai vectors, Buskin, self-maps",
             "C7": "S -> Y <- S' by symplectic Z/2 and Z/5, multiplier 2/5 = 10"}
    DEC = {"C1": "dies: its chains reach one parity of shift", "C8": "open: Maurer-Cartan with two line bundles at one shift",
           "C2": "open: ranks of m_3 to m_5", "C3": "dies: isolated >= 5325 > 57",
           "C4": "open: C8 and C2, then one discriminant", "C5": "dies: it is the statement itself; Hom(X, Z_K) = 0",
           "C6": "dies: f^2 = n in a cubic field forces f rational", "C7": "dies: order five forces rank T <= 5"}
    slots = {t: 0 for t in xs}
    for c in cand:
        t = c["target"]
        k = slots[t]; slots[t] += 1
        y = 0.705 - k * 0.105
        st_ = c["status"]
        fc = "#fde9e7" if st_.startswith("dies") else "#fff6dc"
        inv = c["invariants"]
        line = ""
        if "C2" in inv:
            line = f"C1,C2,C3 = {inv.get('C1')}, {inv.get('C2')}, {inv.get('C3')}; isolated {inv.get('safe_classes', '')}"
        if c["id"] == "C4":
            line = f"family dim {inv.get('dim_family')}, r = {inv.get('r')}"
        if c["id"] == "C7":
            line = "coinvariant rank 16, T rank <= 6"
        if c["id"] == "C8":
            line = "sum eps = sum eps k = 0 over the threefolds"
        txt = "\n".join([f"{c['id']}: " + textwrap.fill(SHORT[c['id']], 31), textwrap.fill(line, 31),
                         textwrap.fill(DEC[c['id']], 31)])
        box(ax, xs[t] + 0.01, y, 0.17, 0.088, txt, fc, ec=TCOL[t], fs=4.9)
        arrow(ax, xs[t] + 0.095, 0.82 if k == 0 else 0.705 - (k - 1) * 0.105, xs[t] + 0.095, y + 0.088,
              color=TCOL[t], lw=0.5)
    # the library and the memory, lower band
    mem = st["memory"]
    box(ax, 0.02, 0.19, 0.30, 0.15,
        f"Library: 76 nodes\n19 results of BB26c (p.*), 9 of BMB26b (h8.*), 34 literature (l.*),\n"
        f"6 explosion moves (x.*), 6 OpenConjecture entries (oc.*), 2 counts (h.*)\n\n"
        f"Memory after round {st['rounds'][-1]['round']}: {mem['events']} events, {mem['survivors']} survivors "
        f"(all known results),\n{mem['blocks']} blocks, {mem['literature']} sources, {mem['retrievals']} retrievals\n"
        f"Round {r12['round']}, a burst: {r12['checks_committed']} checks before its time limit, "
        f"{r12['survivors']} survivors",
        "#f0f0f0", fs=5.3)
    box(ax, 0.35, 0.19, 0.30, 0.15,
        "Closed chains on $E_0^6$ (candidates C1, C8):\nwith at most five line bundles a chain through a threefold\n"
        "has four or five line bundles and reaches one parity of shift;\nthe Chern character puts equally many "
        "threefolds at each,\nso one lies on no chain and $\\mathrm{ev}_E(v)\\neq0$: C1 dies, $m_6$ not needed\n\n"
        f"restricted Euler bound {chains['(a) L^1..4 at shifts -2..1']['restricted_euler']}, isolated blocks "
        f"{chains['(a) L^1..4 at shifts -2..1']['safe']}:\ncounting alone decides nothing", "#f0f0f0", fs=5.3)
    taken = sum(1 for s in src if "absorbed" in s["verdict"])
    box(ax, 0.68, 0.19, 0.30, 0.15,
        f"Sources read: {len(src)}\n{taken} methods or data absorbed (closure policy, LeanVerify split,\n"
        f"tournament ranking, vault rules, Hodge bundle traces,\n3531 open conjectures), {len(src) - taken} left out\n\n"
        "No source contains a construction for any target point", "#f0f0f0", fs=5.3)
    for x in (0.17, 0.50, 0.83):
        arrow(ax, x, 0.34, x, 0.36, color=GREY)
    ax.text(0.5, 0.365, "every candidate is checked against the library, the counts and the sources before it is recorded",
            ha="center", fontsize=6, color=GREY)
    # bottom line: verdict
    box(ax, 0.02, 0.05, 0.96, 0.10,
        "State after the run: no target point is reached; (F2) and (F3$'$) are unchanged.\n"
        "Decided negatively: C1 and every convolution with at most five line bundles (parity of the Chern character), "
        "C3 ($\\geq 5325 > 57$),\nevery configuration of the 35 pieces ($\\geq 2605$), everything on $E_0^8$ within six shifts "
        "($\\geq 640 > 104$), C7 (rank $T\\leq5$ under order five).\n"
        "Open: C8 (six or more line bundles), C2 ($m_3$ to $m_5$), C4 (through C8 and C2). Dead as constructions: C5, C6.",
        "#ffffff", ec="k", fs=6.3)
    title(ax, "", fontsize=1)
    fig.savefig(os.path.join(OUT, "fig_hodgemap.png"), dpi=DPI)
    plt.close(fig)


if __name__ == "__main__":
    fig_hodgepieces()
    fig_hodgerounds()
    fig_hodgebounds()
    fig_hodgemap()
    print("done")
