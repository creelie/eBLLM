"""The figure of the benchmark crossed: descents of reflexive polytopes to minimal seeds.

Panel (a) is computed here from construction mode (src/ebllm/construct/reflexive.py): the 16
reflexive polygons, every descent step between them, and the shortest descent from the largest.
Panels (b) and (c) read the data of the seed run, data/seed/pairs4.json (the pairs of lattice
points of P and of its dual over the Kreuzer-Skarke list, with the longest chain) and
data/seed/delta680.json (the lattice points along the certified descent of the largest polytope).

    python3 make_round8.py && python3 compact_figures.py
"""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..")
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
SEED = os.path.join(HERE, "data", "seed")
sys.path.insert(0, os.path.join(REPO, "src"))
from ebllm.construct import reflexive as R  # noqa: E402

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555"
DPI = 300


def title(ax, s):
    ax.set_title(s, loc="left", fontweight="bold")


def polygon_graph():
    polys = R.reflexive_polygons()
    key = {R._canonical2(p): i for i, p in enumerate(polys)}
    edges = set()
    for i, p in enumerate(polys):
        for q in R.descent_steps(p):
            edges.add((i, key[R._canonical2(q)]))
    return polys, sorted(edges)


def shortest_path(polys, edges, start):
    nxt = {}
    for a, b in edges:
        nxt.setdefault(a, []).append(b)
    depth = {i: R.shortest_descent(p) for i, p in enumerate(polys)}
    path = [start]
    while depth[path[-1]]:
        path.append(min((b for b in nxt[path[-1]] if depth[b] == depth[path[-1]] - 1),
                        key=lambda b: len(polys[b])))
    return path, depth


def _box(pts):
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    return min(xs), max(xs), min(ys), max(ys)


def draw_polygon(ax, pts, cx, cy, s, colour, lw=0.9):
    """Draw the polygon with the centre of its bounding box at (cx, cy); return its drawn box."""
    import math
    x0, x1, y0, y1 = _box(pts)
    ox, oy = cx - s * (x0 + x1) / 2, cy - s * (y0 + y1) / 2
    vs = R.vertices(pts)
    mx = sum(v[0] for v in vs) / len(vs)
    my = sum(v[1] for v in vs) / len(vs)
    ring = sorted(vs, key=lambda v: math.atan2(v[1] - my, v[0] - mx))
    ax.add_patch(Polygon([(ox + s * x, oy + s * y) for x, y in ring], closed=True,
                         facecolor=colour, alpha=0.16, edgecolor=colour, lw=lw, zorder=3))
    ax.add_patch(Polygon([(ox + s * x, oy + s * y) for x, y in ring], closed=True,
                         facecolor="none", edgecolor=colour, lw=lw, zorder=3))
    for x, y in pts:
        ax.plot(ox + s * x, oy + s * y, "o", ms=2.0 if (x, y) != (0, 0) else 2.6,
                color="k" if (x, y) == (0, 0) else colour, zorder=4, mec="none")
    return ox + s * x0, ox + s * x1, oy + s * y0, oy + s * y1


def panel_polygons(ax):
    polys, edges = polygon_graph()
    top = max(range(len(polys)), key=lambda i: len(polys[i]))
    path, depth = shortest_path(polys, edges, top)
    rows = {}
    for i, p in enumerate(polys):
        rows.setdefault(len(p), []).append(i)
    S, DX, DY = 0.27, 1.6, 1.45
    pos = {}
    for n, ids in rows.items():
        ids.sort(key=lambda i: (depth[i], R._canonical2(polys[i])))
        for k, i in enumerate(ids):
            pos[i] = ((k - (len(ids) - 1) / 2) * DX, (n - 4) * DY)
    box = {}
    for i, p in enumerate(polys):
        minimal = not R.descent_steps(p)
        colour = GREEN if minimal else (RED if i in path else BLUE)
        box[i] = draw_polygon(ax, p, *pos[i], S, colour)
        ax.text(box[i][1] + 0.08, box[i][2], str(depth[i]), fontsize=6.5, color=GREY, ha="left", va="bottom")
    on_path = set(zip(path, path[1:]))
    for a, b in edges:
        red = (a, b) in on_path
        ax.add_patch(FancyArrowPatch((pos[a][0], box[a][2] - 0.06), (pos[b][0], box[b][3] + 0.06),
                                     arrowstyle="-|>", mutation_scale=5, lw=1.3 if red else 0.45,
                                     color=RED if red else "#9a9a9a", zorder=2 if red else 1,
                                     shrinkA=0, shrinkB=0))
    for n in rows:
        ax.text(-4.3, (n - 4) * DY, f"{n}", fontsize=7.5, ha="right", va="center")
    ax.text(-4.3, 6 * DY + 0.75, "lattice points", fontsize=7, ha="right", va="bottom")
    ax.set_xlim(-5.1, 3.9)
    ax.set_ylim(-0.75, 6 * DY + 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    title(ax, "(a) every descent in the plane")
    ax.text(3.85, -0.72, "grey: fewest steps to a minimal polygon (green)", fontsize=6.5, ha="right", color=GREY)


def panel_pairs(ax):
    d = json.load(open(os.path.join(SEED, "pairs4.json")))
    xs, ys = zip(*d["pairs"])
    ax.scatter(xs, ys, s=1.0, color="#9ab3d6", lw=0, rasterized=True, label="pairs that occur")
    cx, cy = zip(*d["chain"])
    ax.plot(cx, cy, "-", color=RED, lw=0.9, label=f"longest chain, {len(d['chain']) - 1} steps")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"lattice points of $P$")
    ax.set_ylabel(r"lattice points of $P^{*}$")
    ax.legend(frameon=False, loc="upper right")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    title(ax, "(b) the bound in dimension four")


def panel_delta680(ax):
    d = json.load(open(os.path.join(SEED, "delta680.json")))
    n, m = d["points"], d["dual_points"]
    steps = range(len(n))
    ax.plot(steps, n, "o-", ms=2.2, lw=0.9, color=BLUE, label=r"points of $P_{i}$")
    ax.plot(steps, m, "s-", ms=2.0, lw=0.9, color=GOLD, label=r"points of $P_{i}^{*}$")
    ax.set_yscale("log")
    ax.set_xlabel("step $i$ of the descent")
    ax.legend(frameon=False, loc="center right")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    title(ax, rf"(c) $\Delta_{{680}}$ to a seed in {len(n) - 1} steps")


def fig_seed():
    have = all(os.path.exists(os.path.join(SEED, f)) for f in ("pairs4.json", "delta680.json"))
    if have:
        fig = plt.figure(figsize=(7.2, 3.15))
        gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1], hspace=0.75, wspace=0.28)
        panel_polygons(fig.add_subplot(gs[:, 0]))
        panel_pairs(fig.add_subplot(gs[0, 1]))
        panel_delta680(fig.add_subplot(gs[1, 1]))
    else:
        fig = plt.figure(figsize=(4.2, 3.4))
        panel_polygons(fig.add_subplot(1, 1, 1))
    fig.savefig(os.path.join(OUT, "fig_seed.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("wrote fig_seed.png", "(three panels)" if have else "(panel a only: no seed data yet)")


if __name__ == "__main__":
    fig_seed()
