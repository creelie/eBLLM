"""The figure of the benchmark crossed: reflexive descents of reflexive polytopes.

Panel (a) is computed here from construction mode (src/ebllm/construct/reflexive.py): the 16
reflexive polygons, every cover between them, and the shortest descent from the largest.
Panels (b) and (c) read the data of the seed run, data/seed/pairs4.json (the pairs of lattice
points of P and of its dual over the Kreuzer-Skarke list, with the longest chain) and
data/seed/delta680.json (the lattice points along the certified descent of the largest polytope,
and the step from which a shorter descent was found).

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
    ax.text(3.85, -0.72, "grey: transition depth; green: r-minimal", fontsize=6.5, ha="right", color=GREY)


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
    ax.set_ylim(4, 6000)
    ax.legend(frameon=False, loc="upper right", markerscale=4, handlelength=1.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    title(ax, "(b) the bound in dimension four")


def panel_delta680(ax):
    d = json.load(open(os.path.join(SEED, "delta680.json")))
    n, m = d["points"], d["dual_points"]
    k, extra = d["shortcut_from"], d["shortcut_steps"]
    steps = range(len(n))
    ax.plot(steps, n, "o-", ms=2.2, lw=0.9, color=BLUE, label=r"$\ell(P_{i})$")
    ax.plot(steps, m, "s-", ms=2.0, lw=0.9, color=GOLD, label=r"$\ell(P_{i}^{*})$")
    # from step k a descent of `extra` complete covers ends at an r-minimal polytope; only its ends are drawn
    end = d["shortcut_end"]
    sx, sy = [k, k + extra], [n[k], end]
    ax.plot(sx, sy, "-", lw=3.2, color=RED, alpha=0.55, zorder=1, label=f"{extra} covers from step {k}")
    ax.plot(sx[-1], sy[-1], "D", ms=4.6, color=RED, mec="none", zorder=5)
    ax.annotate(f"r-minimal, {end} points", (sx[-1], sy[-1]), xytext=(sx[-1] - 19, 4.3), va="center",
                fontsize=6.8, color=RED, arrowprops=dict(arrowstyle="-", lw=0.5, color=RED))
    ax.set_yscale("log")
    ax.set_ylim(3, 3e4)
    ax.set_yticks([10, 100, 1000])
    ax.set_xlabel("step $i$ of the descent")
    ax.set_ylabel("lattice points")
    ax.legend(frameon=False, loc="upper center", ncol=3, columnspacing=1.0, handlelength=1.5, fontsize=6.8)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    title(ax, rf"(c) a descent of $\Delta_{{680}}$ in {k + extra} steps")


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


# -- a descent in dimension three, drawn in space ------------------------------------------------------
P15 = [(1, 0, 0), (0, 1, 0), (-1, -1, 0), (0, 0, 1), (-3, 2, -2), (-2, 3, -2), (-4, 4, -3)]


def descent3():
    """A shortest descent of the reflexive 3-polytope with 15 lattice points and no reflexive vertex
    deletion: at each step the cover of least depth, and among those the one with fewest points."""
    chain = [tuple(R.lattice_points(P15))]
    while R.descent_steps(chain[-1]):
        d = R._depths(chain[-1])[0]
        chain.append(min((tuple(c) for c in R.descent_steps(chain[-1]) if R._depths(tuple(c))[0] == d - 1),
                         key=len))
    return chain


def faces3(lp):
    """The facets of conv(lp) as rings of vertices, ordered around each facet."""
    import math
    vs = R.vertices(lp)
    out = []
    for a, c in R.facets(lp):
        f = [v for v in vs if sum(x * y for x, y in zip(a, v)) == c]
        cx = [sum(v[i] for v in f) / len(f) for i in range(3)]
        # two directions in the facet plane
        u = [f[0][i] - cx[i] for i in range(3)]
        w = [a[1] * u[2] - a[2] * u[1], a[2] * u[0] - a[0] * u[2], a[0] * u[1] - a[1] * u[0]]
        ang = lambda v: math.atan2(sum((v[i] - cx[i]) * w[i] for i in range(3)),
                                   sum((v[i] - cx[i]) * u[i] for i in range(3)))
        out.append(sorted(f, key=ang))
    return out


# a basis of the lattice in which P15 is drawn round: (x, y, z) -> (-z, z - x, y + z)
BASIS = ((0, 0, -1), (-1, 0, 1), (0, 1, 1))


def _map(v):
    return tuple(sum(b * x for b, x in zip(row, v)) for row in BASIS)


def _shade(colour, ring):
    """The face colour lit from the upper left: brighter where the outer normal faces the light."""
    import numpy as np
    from matplotlib.colors import to_rgb
    v = np.array(ring, float)
    n = np.cross(v[1] - v[0], v[2] - v[0])
    if np.dot(n, v.mean(0)) < 0:
        n = -n
    light = np.array([-0.5, -0.7, 0.9])
    t = 0.5 + 0.5 * max(0.0, float(np.dot(n, light) / np.linalg.norm(n) / np.linalg.norm(light)))
    c = np.array(to_rgb(colour))
    return tuple(c * t + (1 - t) * 0.25 * c) if t < 0.75 else tuple(c + (1 - c) * (t - 0.75) * 1.6)


def draw3(ax, lp, colour, alpha=0.5, points=True, lw=0.6, fill=True):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    rings = [[_map(v) for v in f] for f in faces3(lp)]
    if fill:
        ax.add_collection3d(Poly3DCollection(rings, facecolors=[_shade(colour, r) for r in rings], alpha=alpha,
                                             edgecolor=colour, linewidths=lw))
    else:
        ax.add_collection3d(Poly3DCollection(rings, facecolor="none", edgecolor=colour, linewidths=lw))
    if points:
        xs, ys, zs = zip(*[_map(q) for q in lp if q != (0, 0, 0)])
        ax.scatter(xs, ys, zs, s=4, color=colour, depthshade=False, lw=0)
        ax.scatter([0], [0], [0], s=7, color="k", depthshade=False, lw=0)


def frame3(ax, zoom=1.05):
    pts = [_map(v) for v in R.lattice_points(P15)]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect([h - l for l, h in zip(lo, hi)], zoom=zoom)
    ax.view_init(elev=24, azim=-32)
    ax.set_axis_off()


def fig_descent3d():
    chain = descent3()
    dual = [len(R.lattice_points(R.dual(q))) for q in chain]
    fig = plt.figure(figsize=(7.2, 4.1))
    gs = fig.add_gridspec(2, len(chain), height_ratios=[1, 1.45], hspace=0.04, wspace=0.05)
    shades = [BLUE, "#3f6db0", "#6a5aa6", "#9b4f8f", "#c04a5a", GREEN]
    top = []
    for i, q in enumerate(chain):
        ax = fig.add_subplot(gs[0, i], projection="3d")
        draw3(ax, q, shades[i])
        frame3(ax)
        top.append(ax)
        ax.text2D(0.5, 0.14, rf"$\ell(P_{{{i}}})={len(q)}$, $\ell(P_{{{i}}}^{{*}})={dual[i]}$",
                  transform=ax.transAxes, ha="center", va="top", fontsize=6.6)
        if i == len(chain) - 1:
            ax.text2D(0.5, 0.93, "r-minimal", transform=ax.transAxes, ha="center", fontsize=6.8,
                      color=GREEN)
    top[0].text2D(0.0, 1.02, r"(a) a shortest descent of a reflexive $3$-polytope, $P_{0}\supset P_{1}\supset"
                  r"\cdots\supset P_{5}$", transform=top[0].transAxes, fontsize=9, fontweight="bold",
                  ha="left", va="bottom")
    for a, b in zip(top, top[1:]):
        pa, pb = a.get_position(), b.get_position()
        y = pa.y0 + 0.5 * pa.height
        fig.patches.append(FancyArrowPatch((pa.x1 - 0.012, y), (pb.x0 + 0.012, y), transform=fig.transFigure,
                                           arrowstyle="-|>", mutation_scale=7, lw=0.8, color=GREY))
    ax = fig.add_subplot(gs[1, :3], projection="3d")
    for i, q in enumerate(chain[:-1]):
        draw3(ax, q, shades[i], points=(i == 0), lw=0.45 + 0.15 * i, fill=False)
    draw3(ax, chain[-1], GREEN, alpha=0.35)
    frame3(ax, zoom=1.0)
    ax.text2D(0.02, 1.0, "(b) the six nested in one lattice", transform=ax.transAxes, fontsize=9,
              fontweight="bold", ha="left", va="top")
    ax = fig.add_subplot(gs[1, 3:])
    steps = range(len(chain))
    ax.plot(steps, [len(q) for q in chain], "o-", ms=2.6, lw=0.9, color=BLUE, label=r"$\ell(P_{i})$, falls")
    ax.plot(steps, dual, "s-", ms=2.4, lw=0.9, color=GOLD, label=r"$\ell(P_{i}^{*})$, rises")
    ax.set_xlabel("step $i$")
    ax.set_ylabel("lattice points")
    ax.set_xticks(list(steps))
    ax.set_ylim(0, 36)
    ax.legend(frameon=False, loc="center right", handlelength=1.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("(c) the counts along the descent", loc="left", fontweight="bold", pad=8)
    ax.text(0.0, 3.0, f"longest descent of $P_{{0}}$: {R.longest_descent(P15)} steps", fontsize=6.8, color=GREY)
    fig.savefig(os.path.join(OUT, "fig_descent3d.png"), dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print("wrote fig_descent3d.png", [len(q) for q in chain], dual)


if __name__ == "__main__":
    fig_seed()
    fig_descent3d()
