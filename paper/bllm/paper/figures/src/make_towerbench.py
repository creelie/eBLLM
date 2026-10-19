"""Figure of the tower bench (Section on towers at equal cost).

Reads data/towerbench/tower_bench.jsonl, the raw output of
    python -m ebllm.construct.bench --jobs 3 --out tower_bench.jsonl
(also shipped as src/ebllm/construct/data/tower_bench.jsonl), and writes fig_towerbench.png at 400 dpi.
Panels (a) to (c): for each target, the checks each run spent before its first gadget with the goal's
profile, by configuration, with the runs that never reached it drawn at the checks they spent, as open
marks. Panel (d): on G2, the checks from the lemma (the first gadget with the profile 3,3,4) to the goal,
ladder against mesh on the same seed and depth.
"""
import json
import os
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "towerbench", "tower_bench.jsonl")
OUT = os.path.join(HERE, "..")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555"
TARGETS = [("steinberg-g1", "(a) gadget $G_1$: distances $3,3,4$"),
           ("steinberg-g2", "(b) gadget $G_2$: distances all $\\geq4$"),
           ("erdos-k6", "(c) Erd\u0151s: no cycle of length $4$ to $6$")]
# at depth 1 the tower has one layer, so ladder and mesh coincide and one of them is drawn
CONFIGS = [("crossing", 0, "C"), ("crossing-time", 0, "C$_t$"),
           ("ladder", 1, "1"), ("ladder", 2, "L2"), ("mesh", 2, "M2"),
           ("ladder", 3, "L3"), ("mesh", 3, "M3")]
COLOUR = {"crossing": GREY, "crossing-time": GREY, "ladder": BLUE, "mesh": RED}


def main():
    rows = [json.loads(line) for line in open(DATA, encoding="utf-8")]
    fig, grid = plt.subplots(2, 2, figsize=(7.1, 5.4))
    axes = [grid[0, 0], grid[0, 1], grid[1, 0]]
    for ax, (target, title) in zip(axes, TARGETS):
        budget = next(r["budget"] for r in rows if r["target"] == target)
        for x, (wiring, depth, _) in enumerate(CONFIGS):
            rs = [r for r in rows if r["target"] == target and r["wiring"] == wiring and r["depth"] == depth]
            if not rs:
                continue
            spent = [r["goal_at"] if r["goal_at"] is not None else r["checks"] for r in rs]
            hit = [r["goal_at"] is not None for r in rs]
            med = statistics.median(r["goal_at"] if r["goal_at"] is not None else max(budget, r["checks"])
                                    for r in rs)
            c = COLOUR[wiring]
            ax.bar(x, med, width=0.62, color=c, alpha=0.18 if not all(hit) else 0.35,
                   edgecolor=c, linewidth=0.6, hatch="////" if not all(hit) else None)
            for k, (s, h) in enumerate(zip(spent, hit)):
                dx = (k - (len(spent) - 1) / 2) * 0.09
                ax.plot(x + dx, s, "o", ms=3.2, mfc=c if h else "white", mec=c, mew=0.7)
            ax.text(x, 1.3e6, f"{sum(hit)}/{len(rs)}", ha="center", va="center", fontsize=6.8, color=c)
        ax.axhline(budget, color=GOLD, lw=0.8, ls="--")
        ax.text(-0.45, budget * 0.86, "budget", ha="left", va="top", fontsize=6.5, color=GOLD)
        ax.set_yscale("log")
        ax.set_ylim(150, 2.6e6)
        ax.set_xticks(range(len(CONFIGS)))
        ax.set_xticklabels([c[2] for c in CONFIGS], fontsize=7.5)
        ax.set_title(title, fontsize=8.2)
        ax.grid(axis="y", lw=0.3, alpha=0.5)
        ax.set_ylabel("exact checks to the goal")
    lemma_panel(grid[1, 1], rows)
    fig.tight_layout(w_pad=0.8, h_pad=1.0)
    fig.savefig(os.path.join(OUT, "fig_towerbench.png"), dpi=400)
    print("fig_towerbench.png")


def lemma_gap(r):
    """Checks from the first gadget with the profile 3,3,4 to the goal; None if either is missing."""
    lem = next((f[0] for f in r["found"] if sorted(f[1]) == [3, 3, 4]), None)
    if lem is None:
        return None, False
    if r["goal_at"] is None:
        return r["checks"] - lem, False
    return r["goal_at"] - lem, True


def lemma_panel(ax, rows):
    top = 4.0e4
    gaps = {"ladder": [], "mesh": []}
    for x, depth in enumerate((2, 3)):
        for seed in range(1, 6):
            pts = []
            for k, wiring in enumerate(("ladder", "mesh")):
                r = next(r for r in rows if r["target"] == "steinberg-g2" and r["wiring"] == wiring
                         and r["depth"] == depth and r["seed"] == seed)
                g, hit = lemma_gap(r)
                if g is None:
                    break
                gaps[wiring].append(g if hit else float("inf"))
                pts.append((x + (k - 0.5) * 0.36 + (seed - 3) * 0.035, g if hit else top, hit, COLOUR[wiring]))
            if len(pts) < 2:
                continue
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "-", color=GREY, lw=0.5, alpha=0.6, zorder=1)
            for px, py, hit, c in pts:
                ax.plot(px, py, "o", ms=3.6, mfc=c if hit else "white", mec=c, mew=0.8, zorder=2)
    for wiring, (xa, ha) in (("ladder", (0.03, "left")), ("mesh", (0.97, "right"))):
        v = sorted(gaps[wiring])
        med = v[len(v) // 2]
        ax.text(xa, 0.04, f"{wiring}: median {med:,} over {len(v)} runs", transform=ax.transAxes,
                ha=ha, fontsize=6.8, color=COLOUR[wiring])
    ax.axhline(top, color=GREY, lw=0.5, ls=":")
    ax.text(-0.45, top * 1.25, "goal not reached", fontsize=6.5, color=GREY, va="bottom")
    ax.set_yscale("log")
    ax.set_ylim(40, 1.2e5)
    ax.set_xlim(-0.55, 1.55)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["depth $2$", "depth $3$"])
    ax.set_ylabel("exact checks from the lemma to the goal")
    ax.set_title("(d) gadget $G_2$ after the lemma: ladder against mesh", fontsize=8.2)
    ax.grid(axis="y", lw=0.3, alpha=0.5)


if __name__ == "__main__":
    main()
