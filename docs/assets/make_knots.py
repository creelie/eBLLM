"""Draw the knot-table board of the README: a knot whose crossing opens into a twisted band (the
pinch move), the open entries of the nonorientable four-genus table by crossing number as they
fill with settled values, the fourth pass lit on top (pinch upper bounds meeting Donaldson lower
bounds), and the bridge-index table with the walls it met.  Animated with SMIL and CSS, which
render inside an <img> on GitHub.  The counts are those of crosscap4d/README.md and data/ in
creelie/conjecture-to-choose (fourth pass); the 382 lower bounds and 84 certificates of the
fourth pass are read from ``ebllm.construct.goeritz_lattice``.

Run from the repository root:  PYTHONPATH=src python3 docs/assets/make_knots.py
"""
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from make_art import THEME, MONO, text, svg, save  # noqa: E402
from ebllm.construct import goeritz_lattice as GL  # noqa: E402

# crossings: (open in KnotInfo, settled at 1, settled at 2, settled at 3, interval narrowed, unchanged)
TABLE = {11: (59, 0, 49, 0, 1, 9), 12: (455, 45, 308, 7, 35, 60), 13: (3011, 475, 1638, 15, 340, 543)}
BRIDGE = (536, 243, 293)
WALLS = [("Sp(4,q), q ≤ 11 and O(4,q), q ≤ 7", "no new certificate"),
         ("Alexander quandles mod p < 110", "dimension ≤ 3, wall"),
         ("closed 3-braids (53,309)", "none is open, wall")]


def trefoil(cx, cy, r, phase=0.0, n=240):
    pts = []
    for i in range(n + 1):
        s = 2 * math.pi * i / n
        x = math.sin(s) + 2 * math.sin(2 * s)
        y = math.cos(s) - 2 * math.cos(2 * s)
        w = 1 + 0.04 * math.sin(3 * s + phase)
        pts.append((cx + r * x * w / 3, cy + r * y * w / 3))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"


def knots(theme):
    t = THEME[theme]
    certs = GL.certificates()
    lower = GL.lower_bounds()
    low3 = sum(d["bound"] == 3 for d in lower)
    W, H = 1280, 640
    css = (
        "@keyframes flow{to{stroke-dashoffset:-120}}"
        "@keyframes breathe{0%,100%{opacity:.35}50%{opacity:1}}"
        "@keyframes rise{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".strand{stroke-dasharray:18 12;animation:flow 3s linear infinite}"
        ".halo{animation:breathe 1.6s ease-in-out infinite}"
        ".bar{transform-box:fill-box;transform-origin:left;animation:rise 1.6s cubic-bezier(.2,.8,.2,1) both}"
        ".turn{transform-box:fill-box;transform-origin:center;animation:spin 24s linear infinite}"
    )
    body = [f"<style>{css}</style>",
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["hero0"]}"/>'
            f'<stop offset="1" stop-color="{t["hero1"]}"/></linearGradient>'
            f'<linearGradient id="kn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["teal"]}"/>'
            f'<stop offset="1" stop-color="{t["violet"]}"/></linearGradient>'
            f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter></defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="url(#bg)" stroke="{t["edge"]}"/>',
            text(40, 50, "THE KNOT TABLES", 24, t["violet"], 700, extra='letter-spacing="5"'),
            text(40, 80, "A pinch gives an upper bound, checked in Regina; Donaldson's theorem on the "
                 "Goeritz lattices gives a lower bound. Where they meet, the entry is settled.", 15, t["sub"]),
            text(W - 40, 50, "construct/pinch.py · goeritz_lattice.py", 14, t["faint"], 600, "end", family=MONO)]
    # the knot and its pinch
    cx, cy, r = 200, 300, 120
    body.append(f'<circle class="halo" cx="{cx}" cy="{cy}" r="{r + 26}" fill="{t["violet"]}" fill-opacity="0.08"/>')
    body.append(f'<g class="turn"><path d="{trefoil(cx, cy, r)}" fill="none" stroke="url(#kn)" stroke-width="9" stroke-linecap="round" stroke-opacity="0.35"/>'
                f'<path class="strand" d="{trefoil(cx, cy, r)}" fill="none" stroke="url(#kn)" stroke-width="5" stroke-linecap="round">'
                f'<animate attributeName="d" dur="5s" repeatCount="indefinite" values="'
                + ";".join(trefoil(cx, cy, r, p) for p in (0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi))
                + '"/></path></g>')
    # the pinched crossing: a small twisted band that opens and closes
    bx, by = cx, cy - r * 1.0
    body.append(f'<circle class="halo" cx="{bx:.1f}" cy="{by:.1f}" r="22" fill="{t["amber"]}" filter="url(#glow)"/>')
    body.append(f'<path d="M{bx - 16:.1f},{by - 10:.1f} C{bx:.1f},{by + 10:.1f} {bx:.1f},{by - 10:.1f} {bx + 16:.1f},{by + 10:.1f}" '
                f'fill="none" stroke="{t["amber"]}" stroke-width="4" stroke-linecap="round">'
                f'<animate attributeName="d" dur="2.4s" repeatCount="indefinite" values="'
                f'M{bx - 16:.1f},{by - 10:.1f} C{bx:.1f},{by + 10:.1f} {bx:.1f},{by - 10:.1f} {bx + 16:.1f},{by + 10:.1f};'
                f'M{bx - 16:.1f},{by - 10:.1f} C{bx - 4:.1f},{by - 22:.1f} {bx + 4:.1f},{by + 22:.1f} {bx + 16:.1f},{by + 10:.1f};'
                f'M{bx - 16:.1f},{by - 10:.1f} C{bx:.1f},{by + 10:.1f} {bx:.1f},{by - 10:.1f} {bx + 16:.1f},{by + 10:.1f}"/></path>')
    body.append(text(cx, cy + r + 60, "γ₄(K) ≤ γ₄(K′) + 1,  = 1 if K′ is slice", 14, t["ink"], 700, "middle", family=MONO))
    body.append(text(cx, cy + r + 82, "pinch: the smoothing against the orientation", 12, t["sub"], 400, "middle"))
    # the four-genus table
    x0, x1 = 430, W - 60
    body.append(text(x0, 128, "Nonorientable four-genus, entries open in KnotInfo 2026.10.5", 16, t["ink"], 700))
    tot = [sum(v[i] for v in TABLE.values()) for i in range(6)]
    body.append(text(x0, 150, f"{tot[1] + tot[2] + tot[3]:,} of {tot[0]:,} settled ({tot[1]} at 1, {tot[2]:,} at 2, "
                     f"{tot[3]} at 3), {tot[4]} narrowed, {tot[4] + tot[5]:,} open", 13, t["sub"], 600, family=MONO))
    big = max(v[0] for v in TABLE.values())
    y = 186
    for k, (n, s1, s2, s3, low, op) in TABLE.items():
        width = (x1 - x0 - 70) * (0.25 + 0.75 * n / big)
        body.append(text(x0, y + 18, f"{k}", 16, t["ink"], 700, family=MONO))
        xs = x0 + 40
        segs = [(s1, t["teal"]), (s2, t["blue"]), (s3, t["violet"]), (low, t["amber"]), (op, t["faint"])]
        for i, (v, col) in enumerate(segs):
            w = width * v / n
            if w <= 0:
                continue
            body.append(f'<rect class="bar" style="animation-delay:{0.25 * i + 0.15 * (k - 11):.2f}s" x="{xs:.1f}" y="{y}" '
                        f'width="{w:.1f}" height="26" rx="5" fill="{col}" fill-opacity="{0.9 if i < 3 else 0.6}"/>')
            xs += w
        body.append(text(x0 + 40 + width + 10, y + 18, f"{n:,}", 13, t["sub"], 600, family=MONO))
        y += 46
    leg = [("γ₄ = 1", t["teal"]), ("γ₄ = 2", t["blue"]), ("γ₄ = 3", t["violet"]), ("narrowed", t["amber"]), ("open", t["faint"])]
    lx = x0 + 40
    for name, col in leg:
        body.append(f'<rect x="{lx}" y="{y}" width="14" height="14" rx="3" fill="{col}"/>')
        body.append(text(lx + 20, y + 12, name, 12.5, t["sub"]))
        lx += 128
    # the fourth pass, lit
    y += 44
    body.append(f'<rect x="{x0}" y="{y - 22}" width="{x1 - x0}" height="62" rx="14" fill="{t["card"]}" fill-opacity="0.7" stroke="{t["teal"]}"/>')
    body.append(f'<circle class="halo" cx="{x0 + 26}" cy="{y + 9}" r="10" fill="{t["teal"]}" filter="url(#glow)"/>')
    body.append(f'<circle cx="{x0 + 26}" cy="{y + 9}" r="6" fill="{t["teal"]}"/>')
    body.append(text(x0 + 48, y + 4, f"fourth pass: +444 settled, {len(lower)} lower bounds ({low3} to γ₄ ≥ 3), "
                     f"{len(certs)} new pinches", 15, t["ink"], 700))
    body.append(text(x0 + 48, y + 26, "learned from failure: when the band search stalled, the change was of kind, "
                     "from upper bounds to lower bounds", 12.5, t["sub"]))
    # the bridge-index table and its walls
    y += 70
    n, done, rest = BRIDGE
    body.append(text(x0, y, f"Bridge index [3,4] at 13 crossings: {done} of {n} settled, {rest} open", 16, t["ink"], 700))
    y += 16
    wd = x1 - x0
    body.append(f'<rect x="{x0}" y="{y}" width="{wd}" height="16" rx="8" fill="{t["faint"]}" fill-opacity="0.35"/>')
    body.append(f'<rect class="bar" x="{x0}" y="{y}" width="{wd * done / n:.1f}" height="16" rx="8" fill="{t["violet"]}"/>')
    y += 42
    for i, (route, verdict) in enumerate(WALLS):
        xx = x0 + i * (wd / 3)
        body.append(f'<rect x="{xx + 2:.1f}" y="{y - 18}" width="{wd / 3 - 8:.1f}" height="50" rx="10" fill="{t["card"]}" '
                    f'fill-opacity="0.7" stroke="{t["rose"]}" stroke-opacity="0.6"/>')
        body.append(text(xx + 14, y + 2, route, 12, t["ink"], 600))
        body.append(text(xx + 14, y + 22, verdict, 11.5, t["rose"], 700, family=MONO))
        body.append(f'<line x1="{xx + 14:.1f}" y1="{y + 18}" x2="{xx + 14:.1f}" y2="{y + 18}" stroke="{t["rose"]}" stroke-width="2">'
                    f'<animate attributeName="x2" dur="2.4s" begin="{0.4 * i:.1f}s" repeatCount="indefinite" '
                    f'values="{xx + 14:.1f};{xx + wd / 3 - 20:.1f};{xx + wd / 3 - 20:.1f}" keyTimes="0;0.6;1"/></line>')
    body.append(text(40, H - 22, "partial results on finite lists, not refereed; repository "
                     "github.com/creelie/conjecture-to-choose (crosscap4d, fourth pass)", 12.5, t["faint"]))
    label = (f"The knot tables: a pinch move on a trefoil; the nonorientable four-genus settled for "
             f"{tot[1] + tot[2] + tot[3]:,} of {tot[0]:,} open knots, 444 in the fourth pass with {len(lower)} "
             f"lower bounds from Donaldson's theorem; the bridge index "
             f"settled for {done} of {n}, with the walls the pass met")
    return svg(W, H, "".join(body), label)


def main():
    for theme in THEME:
        save("anaxia-knots", theme, knots(theme))


if __name__ == "__main__":
    main()
