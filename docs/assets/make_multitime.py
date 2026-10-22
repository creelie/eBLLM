"""Draw the board of the several-times result in the README: the signature plane with the three
lines s - t = 8, 0, -8 on which a super Yang-Mills theory built in Nishino's manner can live and
the claimed families off them; the count 2(d - 2) against the size of a Weyl spinor, which meet
only at d = 3, 4, 6, 10; and, for one time, the least multiplet against a vector multiplet.
Animated with SMIL and CSS, which render inside an <img> on GitHub.  Every number is read from
``ebllm.construct.multitime_sym`` (the Fierz residuals need numpy).

Run from the repository root:  PYTHONPATH=src python3 docs/assets/make_multitime.py
"""
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_art import THEME, MONO, text, svg, save  # noqa: E402
from ebllm.construct import multitime_sym as M  # noqa: E402

ALGEBRAS = {3: "R", 4: "C", 6: "H", 10: "O"}


def signature_plane(t, x0, y0, w, h):
    """s to the right, t upwards; the allowed lines in teal, the claimed signatures in rose."""
    smax, tmax = 30, 12
    X = lambda s: x0 + 34 + (w - 50) * s / smax  # noqa: E731
    Y = lambda tt: y0 + h - 30 - (h - 60) * tt / tmax  # noqa: E731
    out = [text(x0, y0 - 14, "Where a theory can live", 16, t["ink"], 700)]
    out.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(smax):.1f}" y2="{Y(0):.1f}" stroke="{t["faint"]}"/>')
    out.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(0):.1f}" y2="{Y(tmax):.1f}" stroke="{t["faint"]}"/>')
    for s in range(0, smax + 1, 5):
        out.append(text(X(s), Y(0) + 18, str(s), 11, t["faint"], 500, "middle", family=MONO))
    for tt in range(0, tmax + 1, 4):
        out.append(text(X(0) - 10, Y(tt) + 4, str(tt), 11, t["faint"], 500, "end", family=MONO))
    out.append(text(X(smax), Y(0) + 34, "s (space)", 12, t["sub"], 600, "end"))
    out.append(text(X(0) - 26, Y(tmax) - 10, "t (time)", 12, t["sub"], 600))
    # the three lines s - t = 8, 0, -8 that survive the Main Theorem, labelled along the line
    angle = math.degrees(math.atan2(Y(0) - Y(1), X(1) - X(0)))
    for i, diff in enumerate((8, 0, -8)):
        s0, s1 = max(0, diff), min(smax, tmax + diff)
        out.append(f'<line class="draw" pathLength="1" style="animation-delay:{0.3 * i:.1f}s" x1="{X(s0):.1f}" '
                   f'y1="{Y(s0 - diff):.1f}" x2="{X(s1):.1f}" y2="{Y(s1 - diff):.1f}" stroke="{t["teal"]}" '
                   f'stroke-width="3" stroke-linecap="round"/>')
        tt, side = {8: (5.6, 1), 0: (8.0, -1), -8: (10.2, -1)}[diff]
        lx, ly = X(tt + diff), Y(tt)
        nx, ny = -math.sin(math.radians(angle)), -math.cos(math.radians(angle))
        lx, ly = lx + side * 13 * nx, ly + side * 13 * ny + (8 if side < 0 else 0)
        out.append(text(lx, ly, f"s − t = {diff}", 11.5, t["teal"], 700, "middle", family=MONO,
                        extra=f'transform="rotate({-angle:.1f} {lx:.1f} {ly:.1f})"'))
    # Nishino's signatures (9+m)+(1+m), each with k = m null vectors and D' = 10
    for m in range(0, 12):
        s, tt = M.nishino(m)
        if M.theory_allowed(s, tt):
            out.append(f'<circle class="fade" style="animation-delay:{0.9 + 0.06 * m:.2f}s" cx="{X(s):.1f}" '
                       f'cy="{Y(tt):.1f}" r="5" fill="{t["teal"]}"/>')
    # the claimed families for n = 1, 2: every real frame leaves D' >= 16
    for fi, f in enumerate(M.FAMILIES):
        for n in (1, 2):
            s, tt = M.family(f, n)
            assert not M.theory_allowed(s, tt)
            cx, cy, r = X(s), Y(tt), 6
            out.append(f'<circle class="ping" style="animation-delay:{0.2 * fi + 0.5 * n:.1f}s" cx="{cx:.1f}" '
                       f'cy="{cy:.1f}" r="7" fill="none" stroke="{t["rose"]}" stroke-width="1.5"/>')
            out.append(f'<path d="M{cx - r:.1f},{cy - r:.1f} L{cx + r:.1f},{cy + r:.1f} M{cx + r:.1f},{cy - r:.1f} '
                       f'L{cx - r:.1f},{cy + r:.1f}" stroke="{t["rose"]}" stroke-width="2.6" stroke-linecap="round"/>')
    out.append(text(X(27) - 12, Y(3) + 4, "27+3", 11.5, t["rose"], 700, "end", family=MONO))
    out.append(text(X(19) - 12, Y(3) + 4, "19+3", 11.5, t["rose"], 700, "end", family=MONO))
    for i, row in enumerate(("claimed for n = 1, 2:", "(9+8n)+1, (10+8n)+2,", "(11+8n)+3, (12+8n)+4;", "none exists")):
        out.append(text(X(smax), Y(8.6) + 16 * i, row, 11.5, t["rose"], 700 if i == 3 else 600, "end"))
    return out


def dimension_count(t, x0, y0, w, h):
    """log2 of N = 2(d - 2) against log2 of a Weyl spinor; N is a multiple of it only at 3, 4, 6, 10."""
    dmin, dmax, top = 3, 14, 6.5
    X = lambda d: x0 + 30 + (w - 44) * (d - dmin) / (dmax - dmin)  # noqa: E731
    Y = lambda v: y0 + h - 30 - (h - 60) * v / top  # noqa: E731
    out = [text(x0, y0 - 14, "Why ten", 16, t["ink"], 700)]
    out.append(f'<line x1="{X(dmin):.1f}" y1="{Y(0):.1f}" x2="{X(dmax):.1f}" y2="{Y(0):.1f}" stroke="{t["faint"]}"/>')
    for d in range(dmin, dmax + 1):
        out.append(text(X(d), Y(0) + 18, str(d), 11, t["faint"], 500, "middle", family=MONO))
    out.append(text(X(dmax), Y(0) + 34, "d, the residual dimension", 12, t["sub"], 600, "end"))
    for v in range(0, 7, 2):
        out.append(text(X(dmin) - 10, Y(v) + 4, f"2^{v}", 10.5, t["faint"], 500, "end", family=MONO))
        out.append(f'<line x1="{X(dmin):.1f}" y1="{Y(v):.1f}" x2="{X(dmax):.1f}" y2="{Y(v):.1f}" stroke="{t["grid"]}"/>')
    lin = " ".join(f"{X(d):.1f},{Y(math.log2(2 * (d - 2))):.1f}" for d in range(dmin, dmax + 1))
    steps = []
    for d in range(dmin, dmax + 1):
        v = math.log2(M.weyl_dimension(d))
        steps += [f"{X(d - 0.5 if d > dmin else d):.1f},{Y(v):.1f}", f"{X(d + 0.5 if d < dmax else d):.1f},{Y(v):.1f}"]
    out.append(f'<polyline class="draw" pathLength="1" points="{" ".join(steps)}" fill="none" stroke="{t["violet"]}" '
               f'stroke-width="3" stroke-linejoin="round"/>')
    out.append(f'<polyline class="draw" pathLength="1" style="animation-delay:.4s" points="{lin}" fill="none" '
               f'stroke="{t["teal"]}" stroke-width="3" stroke-linejoin="round"/>')
    out.append(text(X(12.2), Y(math.log2(M.weyl_dimension(13))) - 10, "Weyl spinor 2^(⌈d/2⌉−1)", 11.5, t["violet"], 700,
                    "end"))
    out.append(text(X(13.9), Y(math.log2(2 * 12)) + 22, "N = 2(d − 2)", 11.5, t["teal"], 700, "end"))
    for i, d in enumerate(M.vector_structure_dimensions()):
        cx, cy = X(d), Y(math.log2(2 * (d - 2)))
        out.append(f'<circle class="ping" style="animation-delay:{1.2 + 0.3 * i:.1f}s" cx="{cx:.1f}" cy="{cy:.1f}" r="9" '
                   f'fill="none" stroke="{t["amber"]}" stroke-width="1.6"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{t["amber"]}"/>')
        out.append(text(cx, cy - 16, ALGEBRAS[d], 13, t["amber"], 800, "middle"))
    out.append(text(x0, y0 + h + 18, "N is a multiple of the Weyl dimension only at d = 3, 4, 6, 10,", 12, t["sub"]))
    out.append(text(x0, y0 + h + 34, "the dimensions of R, C, H, O plus two", 12, t["sub"]))
    return out


def one_time(t, x0, y0, w, h):
    """In (9+8n)+1 every massless multiplet without tensor charges has at least 2^(2^(2+4n)) states."""
    out = [text(x0, y0 - 14, "One time: too many states", 16, t["ink"], 700)]
    out.append(text(x0, y0 + 8, "log₂ log₂ of the number of states", 12, t["sub"]))
    rows = [M.single_time_bound(n) for n in range(4)]
    top = math.log2(rows[-1]["log2_states"])
    bw = w - 170
    for n, r in enumerate(rows):
        y = y0 + 36 + n * 66
        least = math.log2(r["log2_states"])
        vec = math.log2(math.log2(2 * r["vector_bosons"]))
        ok = r["log2_states"] <= math.log2(2 * r["vector_bosons"])
        col = t["teal"] if ok else t["rose"]
        out.append(text(x0, y + 12, f"({9 + 8 * n},1)", 12.5, t["ink"], 700, family=MONO))
        bx = x0 + 70
        out.append(f'<rect class="rise" style="animation-delay:{0.25 * n:.2f}s" x="{bx}" y="{y}" '
                   f'width="{bw * least / top:.1f}" height="14" rx="4" fill="{col}"/>')
        out.append(f'<rect class="rise" style="animation-delay:{0.25 * n + 0.1:.2f}s" x="{bx}" y="{y + 20}" '
                   f'width="{bw * vec / top:.1f}" height="8" rx="3" fill="{t["blue"]}" fill-opacity="0.75"/>')
        exp = r["log2_states"]
        out.append(text(bx + bw * least / top + 8, y + 12, f"≥ 2^{exp}", 12, col, 700, family=MONO))
        out.append(text(bx + bw * vec / top + 8, y + 29, f"{2 * r['vector_bosons']} in a vector multiplet", 11,
                        t["blue"], 600))
    out.append(text(x0, y0 + h + 18, "only n = 0, ten dimensions, has room for a vector field", 12, t["sub"]))
    out.append(text(x0, y0 + h + 34, "(assuming no tensor charges on the multiplet)", 12, t["faint"]))
    return out


def board(theme):
    t = THEME[theme]
    W, H = 1280, 700
    css = ("@keyframes breathe{0%,100%{opacity:.35}50%{opacity:1}}"
           ".halo{animation:breathe 1.8s ease-in-out infinite}")
    body = [f"<style>{css}</style>",
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["hero0"]}"/>'
            f'<stop offset="1" stop-color="{t["hero1"]}"/></linearGradient>'
            f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter></defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="url(#bg)" stroke="{t["edge"]}"/>',
            text(40, 50, "SEVERAL TIMES", 24, t["violet"], 700, extra='letter-spacing="5"'),
            text(40, 80, "Super Yang–Mills built in Nishino's manner: k real null vectors, k ≤ min(s, t), and a residual "
                 "dimension s + t − 2k that must be 10 (or 2).", 15, t["sub"]),
            text(W - 40, 50, "construct/multitime_sym.py", 14, t["faint"], 600, "end", family=MONO)]
    y0, h = 150, 330
    for x, w in ((40, 400), (480, 380), (900, 340)):
        body.append(f'<rect x="{x - 14}" y="{y0 - 44}" width="{w + 28}" height="{h + 100}" rx="16" fill="{t["card"]}" '
                    f'fill-opacity="0.55" stroke="{t["edge"]}"/>')
    body += signature_plane(t, 40, y0, 400, h)
    body += dimension_count(t, 480, y0, 380, h)
    body += one_time(t, 900, y0, 340, h)
    # the refuters and the numbers
    ref = M.refuter()
    try:
        good = max(M.fierz_residual(*st) for st in ((9, 1), (5, 5), (1, 9)))
        bad = min(M.fierz_residual(*st) for st in ((17, 1), (13, 5), (9, 9)))
        fierz = f"cubic identity: residual ≤ {good:.0e} in (9,1), (5,5), (1,9); ≥ {bad:.2f} in (17,1), (13,5), (9,9)"
    except ImportError:
        fierz = "cubic identity: run with numpy for the residuals"
    yb = 600
    body.append(f'<rect x="26" y="{yb - 26}" width="{W - 52}" height="64" rx="14" fill="{t["card"]}" fill-opacity="0.7" '
                f'stroke="{t["amber"]}" stroke-opacity="0.7"/>')
    body.append(f'<circle class="halo" cx="52" cy="{yb + 6}" r="10" fill="{t["amber"]}" filter="url(#glow)"/>')
    body.append(f'<circle cx="52" cy="{yb + 6}" r="6" fill="{t["amber"]}"/>')
    body.append(text(74, yb, f"refuters: the mod-8 rule admits {len(ref['mod8_rule'])} of the claimed signatures with "
                     f"n = 1, 2, complex null frames admit {len(ref['complex_frames'])}; real frames reject all of them",
                     14, t["ink"], 700))
    body.append(text(74, yb + 22, fierz, 12.5, t["sub"], 500, family=MONO))
    body.append(text(40, H - 22, "proved under five axioms that Nishino's construction satisfies; not refereed; repository "
                     "github.com/creelie/cs-grav, release v1.0.0, doi:10.5281/zenodo.23558751", 12.5, t["faint"]))
    label = ("Several times: a super Yang-Mills theory built in Nishino's manner lives only on the lines "
             "s - t = 8, 0, -8, so none exists in (9+8n)+1, (10+8n)+2, (11+8n)+3, (12+8n)+4 for n >= 1; "
             "2(d-2) is a multiple of the Weyl dimension only at d = 3, 4, 6, 10; for one time every massless "
             "multiplet without tensor charges in (9+8n)+1 has at least 2^(2^(2+4n)) states")
    return svg(W, H, "".join(body), label)


def main():
    for theme in THEME:
        save("anaxia-multitime", theme, board(theme))


if __name__ == "__main__":
    main()
