"""Draw the artwork of the README: the banner, the four headline numbers, the round of the engine,
five charts from the run data and two badges, each in a light and a dark version.

Every number on a chart is read from the data files of the repository:

    paper/bllm/paper/figures/src/data/memory_study.json   memory arms, 60 seeds, five rounds
    paper/bllm/paper/figures/src/data/loop_state.json     five agents against a single loop, eleven rounds
    paper/bllm/paper/figures/src/data/amp_composites_summary.json and the table tab:amplify of
        paper/bllm/paper/sections/sec10c_headline.tex     the amplified round, depth four
    paper/bllm/paper/figures/src/data/idea_gap.json       human and language-model idea profiles
    experiments/hodge/rounds/round_*.json                 the Hodge-only run

Run from the repository root:  python3 docs/assets/make_art.py
"""
import glob
import json
import math
import os
import random
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "paper", "bllm", "paper", "figures", "src", "data")
SANS = "Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"

THEME = {
    "light": dict(bg="#ffffff", card="#f8fafc", edge="#e2e8f0", ink="#0f172a", sub="#475569",
                  faint="#94a3b8", grid="#e2e8f0", rose="#e11d48", teal="#0d9488", blue="#2563eb",
                  amber="#d97706", violet="#7c3aed", hero0="#ffffff", hero1="#eef2ff", node=0.30, wire=0.16),
    "dark": dict(bg="#0d1117", card="#161b22", edge="#30363d", ink="#e6edf3", sub="#9da7b3",
                 faint="#6e7681", grid="#21262d", rose="#fb7185", teal="#2dd4bf", blue="#60a5fa",
                 amber="#fbbf24", violet="#a78bfa", hero0="#0b1020", hero1="#1b1640", node=0.45, wire=0.20),
}


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=14, fill="#000", weight=400, anchor="start", family=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def lines(x, y, rows, size, fill, lh=None, weight=400, anchor="start"):
    lh = lh or size * 1.42
    return "".join(text(x, y + i * lh, r, size, fill, weight, anchor) for i, r in enumerate(rows))


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(label)}">{body}</svg>\n')


def save(name, theme, content):
    with open(os.path.join(OUT, f"{name}-{theme}.svg"), "w") as f:
        f.write(content)


# ------------------------------------------------------------------------------------------- banner
def letters(x0, y0, h, t, stroke):
    """ANAXIA in straight strokes; the X is two typed strands crossing at a checked node."""
    sw = stroke
    out = []
    path = lambda pts, col, w=sw: ('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
                                   f'" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" '
                                   'stroke-linejoin="round"/>')
    gap = 0.29 * h
    x = x0

    def A(x):
        w = 0.80 * h
        out.append(path([(x, y0 + h), (x + w / 2, y0), (x + w, y0 + h)], t["ink"]))
        yb = y0 + 0.66 * h
        dx = (w / 2) * (1 - 0.66)
        out.append(path([(x + dx + sw * 0.35, yb), (x + w - dx - sw * 0.35, yb)], t["ink"]))
        return x + w + gap

    def N(x):
        w = 0.62 * h
        out.append(path([(x, y0 + h), (x, y0), (x + w, y0 + h), (x + w, y0)], t["ink"]))
        return x + w + gap

    def X(x):
        w = 0.74 * h
        cx, cy = x + w / 2, y0 + h / 2
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.36 * h:.1f}" fill="none" stroke="{t["violet"]}" '
                   f'stroke-opacity="0.35" stroke-width="2" stroke-dasharray="3 7"/>')
        out.append(path([(x, y0), (x + w, y0 + h)], "url(#strandA)"))
        out.append(path([(x + w, y0), (x, y0 + h)], "url(#strandB)"))
        for (px, py, col) in [(x, y0, t["rose"]), (x + w, y0 + h, t["blue"]), (x + w, y0, t["teal"]),
                              (x, y0 + h, t["amber"])]:
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{sw * 0.62:.1f}" fill="{col}"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.26 * h:.1f}" fill="{t["violet"]}" fill-opacity="0.18"/>')
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.15 * h:.1f}" fill="{t["violet"]}" '
                   f'stroke="{t["hero0"]}" stroke-width="5"/>')
        r = 0.15 * h
        out.append(path([(cx - 0.45 * r, cy + 0.02 * r), (cx - 0.1 * r, cy + 0.38 * r), (cx + 0.5 * r, cy - 0.36 * r)],
                        "#ffffff", w=sw * 0.32))
        return x + w + gap

    def I(x):
        out.append(path([(x, y0), (x, y0 + h)], t["ink"]))
        return x + gap

    for f in (A, N, A, X, I, A):
        x = f(x)
    return "".join(out), x - gap


def banner(theme):
    t = THEME[theme]
    W, H = 1280, 400
    rng = random.Random(7)
    body = [f'<defs><linearGradient id="hero" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["hero0"]}"/>'
            f'<stop offset="1" stop-color="{t["hero1"]}"/></linearGradient>'
            f'<linearGradient id="strandA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["rose"]}"/>'
            f'<stop offset="1" stop-color="{t["blue"]}"/></linearGradient>'
            f'<linearGradient id="strandB" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["teal"]}"/>'
            f'<stop offset="1" stop-color="{t["amber"]}"/></linearGradient></defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="url(#hero)" stroke="{t["edge"]}"/>']
    # the library: typed nodes, wired where a cross is possible
    cols = [t["rose"], t["teal"], t["blue"], t["amber"]]
    pts = []
    while len(pts) < 64:
        x, y = rng.uniform(30, W - 30), rng.uniform(26, H - 26)
        if 300 < x < 980 and 70 < y < 340:
            continue
        if all((x - a) ** 2 + (y - b) ** 2 > 52 ** 2 for a, b, _ in pts):
            pts.append((x, y, rng.randrange(4)))
    for i, (x, y, k) in enumerate(pts):
        near = sorted(range(len(pts)), key=lambda j: (pts[j][0] - x) ** 2 + (pts[j][1] - y) ** 2)[1:3]
        for j in near:
            if j > i or i not in sorted(range(len(pts)), key=lambda m: (pts[m][0] - pts[j][0]) ** 2 +
                                         (pts[m][1] - pts[j][1]) ** 2)[1:3]:
                body.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{pts[j][0]:.1f}" y2="{pts[j][1]:.1f}" '
                            f'stroke="{t["faint"]}" stroke-opacity="{t["wire"]}" stroke-width="1.2"/>')
    for x, y, k in pts:
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.choice([3, 3.5, 4.5])}" fill="{cols[k]}" '
                    f'fill-opacity="{t["node"]}"/>')
    word, x1 = letters(0, 0, 120, t, 15)
    width = x1
    x0 = (W - width) / 2
    body.append(f'<g transform="translate({x0:.1f},62)">{word}</g>')
    body.append(text(W / 2, 252, "THE  BLLM  ENGINE", 26, t["violet"], 700, "middle", extra='letter-spacing="6"'))
    body.append(text(W / 2, 296, "Known mathematics as typed nodes. New candidates by crossing them.", 19, t["sub"],
                     400, "middle"))
    body.append(text(W / 2, 324, "Nothing counts until a program checks it and a refuter fails to break it.", 19,
                     t["sub"], 400, "middle"))
    return svg(W, H, "".join(body), "Anaxia, the BLLM engine")


# ------------------------------------------------------------------------------------------ numbers
def headline_numbers():
    tab = open(os.path.join(ROOT, "paper", "bllm", "paper", "sections", "sec10c_headline.tex")).read()
    row = re.search(r"Total & \$([\d{},]+)\$ & \$(\d+)\$ & \$(\d+)\$ & \$(\d+)\$ & \$(\d+)\$", tab)
    closed, stopped, rejected, refuted, survived = (int(g.replace("{", "").replace("}", "").replace(",", ""))
                                                    for g in row.groups())
    amp = load("amp_composites_summary.json")
    assert amp["closed"] == closed
    acc = sum(v.get("accepted", 0) for v in amp["by_depth"].values())
    assert acc == closed - stopped - rejected == refuted + survived
    return dict(bred=amp["total"], closed=closed, stopped=stopped, rejected=rejected, accepted=acc,
                refuted=refuted, survived=survived)


def memory_checks():
    m = load("memory_study.json")["arms"]
    return {k: sum(r["checks"] for r in m[k]["rows"]) for k in m}


def ratios():
    """Cost of each proposer over the optimum (sum of sqrt of the need)^2, need = the human profile."""
    g = load("idea_gap.json")["shares"]
    out = {}
    for ax in ("opportunity", "method"):
        h = g["Human"][ax]
        h = [x / sum(h) for x in h]
        opt = sum(math.sqrt(x) for x in h) ** 2
        for name, v in g.items():
            q = [x / sum(v[ax]) for x in v[ax]]
            out.setdefault(name, {})[ax] = sum(a / b for a, b in zip(h, q)) / opt
    return out


def stats(theme):
    t = THEME[theme]
    W, H = 1280, 200
    n = headline_numbers()
    mc = memory_checks()
    r = ratios()
    llm = [v[a] for k, v in r.items() if k != "Human" for a in v]
    hum = min(r["Human"].values())
    cards = [
        (f"{n['bred']:,} → {n['survived']}", t["violet"],
         ["composites bred to depth four in the", f"amplified round; {n['survived']} pass their check",
          "and survive the refuter"]),
        (f"{mc['full']:.1f} vs {mc['boosted']:.1f}", t["teal"],
         ["checks to the same plateau with", "memory and without it: nothing", "decided is checked twice"]),
        (f"{hum:.2f} vs {min(llm):.1f}–{max(llm):.1f}", t["amber"],
         ["human research ideas against nine", "language models, in multiples of the", "proposer bound"]),
        ("0 of 5", t["rose"],
         ["open problems solved: Yang–Mills,", "Hodge, standard conjecture B,", "Chowla, Erdős 1183"]),
    ]
    body = []
    cw = 299
    for i, (big, col, rows) in enumerate(cards):
        x = 12 + i * (cw + 16)
        body.append(f'<rect x="{x}" y="10" width="{cw}" height="{H - 20}" rx="16" fill="{t["card"]}" stroke="{t["edge"]}"/>')
        body.append(f'<rect x="{x}" y="10" width="6" height="{H - 20}" rx="3" fill="{col}"/>')
        size = min(34, 252 / (0.62 * len(big)))
        body.append(text(x + 26, 70, big, round(size, 1), col, 700, family=MONO))
        body.append(lines(x + 26, 106, rows, 15, t["sub"], lh=22))
    return svg(W, H, "".join(body), "Four numbers from the runs of Anaxia")


# --------------------------------------------------------------------------------------------- round
def round_diagram(theme):
    t = THEME[theme]
    W, H = 1280, 566
    n = headline_numbers()
    mc = memory_checks()
    body = [f'<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{t["faint"]}"/></marker></defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="{t["card"]}" stroke="{t["edge"]}"/>',
            text(40, 50, "One round of Anaxia", 22, t["ink"], 700),
            text(40, 76, "Each station is code in src/ebllm/bllm; each tag is a measured number from the runs.",
                 14.5, t["sub"])]
    cw, ch, top = 182, 186, 110
    xs = [40 + i * (cw + 24) for i in range(6)]
    top_row = [
        ("1", "Target point", t["rose"], ["the statement that", "would settle the", "problem; its distance", "is measured each round"],
         "none reached yet"),
        ("2", "Channel", t["blue"], ["brings every record", "of memory that bears", "on the target back", "to the proposers"],
         "saves 3% of checks"),
        ("3", "Proposers", t["amber"], ["typed crossing, a", "local model, language", "models; a cross needs", "matching types"],
         "random: 45/48 ill-typed"),
        ("4", "Check", t["teal"], ["a program decides a", "closed composite:", "accepted, rejected", "or stopped"],
         f"{n['closed']:,} closed → {n['accepted']} accepted"),
        ("5", "Refuter", t["rose"], ["breaks it when a", "stronger result is", "known or it repeats", "an accepted one"],
         f"{n['refuted']} broken \u00b7 {n['survived']} survive"),
        ("6", "Lean", t["violet"], ["kernel check and", "axiom audit of what", "is stated as proved;", "no native_decide"],
         "59 + 30 theorems"),
    ]
    for (num, title, col, rows, tag), x in zip(top_row, xs):
        body.append(card(t, x, top, cw, ch, num, title, col, rows, tag))
    for i in range(5):
        body.append(f'<line x1="{xs[i] + cw + 2}" y1="{top + 52}" x2="{xs[i + 1] - 4}" y2="{top + 52}" '
                    f'stroke="{t["faint"]}" stroke-width="2" marker-end="url(#ar)"/>')
    # bottom row: memory and boosters, flowing back
    by = 404
    mx, mw = xs[2], xs[5] + cw - xs[2]
    body.append(card(t, mx, by, mw, 126, "7", "Memory", t["teal"],
                     ["one SQLite store of nodes, verdicts, weights, blocks, literature and the channel;",
                      "every verdict is written once, and a decided composite is never checked again"],
                     f"{mc['full']:.1f} checks against {mc['boosted']:.1f} without it"))
    bx, bw = xs[0], xs[1] + cw - xs[0]
    body.append(card(t, bx, by, bw, 126, "8", "Boosters", t["amber"],
                     ["Hebbian weights on the synapses between", "constructions, raised by survivors"],
                     "12 and 14 of 200 runs against 21: no gain"))
    arrow = lambda x1, y1, x2, y2: (f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{t["faint"]}" '
                                    f'stroke-width="2" marker-end="url(#ar)"/>')
    for x in (xs[3] + cw / 2, xs[4] + cw / 2, xs[5] + cw / 2):
        body.append(arrow(x, top + ch + 4, x, by - 6))
    body.append(arrow(mx - 4, by + 50, bx + bw + 8, by + 50))
    body.append(f'<path d="M{xs[1] + cw / 2},{by - 6} L{xs[1] + cw / 2},{top + ch + 6}" fill="none" '
                f'stroke="{t["faint"]}" stroke-width="2" marker-end="url(#ar)"/>')
    body.append(f'<path d="M{xs[0] + cw - 30},{by - 6} C{xs[0] + cw - 10},{by - 60} {xs[2] + 40},{by - 50} '
                f'{xs[2] + 50},{top + ch + 6}" fill="none" stroke="{t["faint"]}" stroke-width="2" '
                f'stroke-dasharray="5 5" marker-end="url(#ar)"/>')
    body.append(text(xs[1] + cw / 2 + 10, by - 20, "next round", 12.5, t["faint"], 600))
    return svg(W, H, "".join(body), "One round of Anaxia: target point, channel, proposers, check, refuter, Lean, "
                                    "memory and boosters")


def card(t, x, y, w, h, num, title, col, rows, tag=""):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{t["bg"]}" stroke="{t["edge"]}"/>',
         f'<circle cx="{x + 26}" cy="{y + 28}" r="14" fill="{col}"/>',
         text(x + 26, y + 33.5, num, 15, "#ffffff", 700, "middle"),
         text(x + 50, y + 34, title, 17, t["ink"], 700),
         lines(x + 18, y + 64, rows, 13.5, t["sub"], lh=19.5)]
    if tag:
        s.append(f'<path d="M{x},{y + h - 34} h{w} v20 a14,14 0 0 1 -14,14 h-{w - 28} a14,14 0 0 1 -14,-14 z" '
                 f'fill="{col}" fill-opacity="0.13"/>')
        s.append(text(x + 18, y + h - 12, tag, 12.5, col, 700))
    return "".join(s)


def tagline(t, x, y, w, s, col, anchor="start"):
    tx = x + w if anchor == "end" else x
    return text(tx, y + 14, s, 13, col, 600, anchor, family=MONO)


# -------------------------------------------------------------------------------------------- charts
class Chart:
    W, H = 620, 380

    def __init__(self, theme, title, sub, x0=70, x1=590, y0=320, y1=110):
        self.t = THEME[theme]
        self.px0, self.px1, self.py0, self.py1 = x0, x1, y0, y1
        self.body = [f'<rect width="{self.W}" height="{self.H}" rx="18" fill="{self.t["card"]}" stroke="{self.t["edge"]}"/>',
                     text(28, 42, title, 19, self.t["ink"], 700), lines(28, 68, sub, 13.5, self.t["sub"], lh=19)]

    def axes(self, xr, yr, xt, yt, xlabel, ylabel, xlog=False, xfmt=str, yfmt=str):
        self.xr, self.yr, self.xlog = xr, yr, xlog
        t = self.t
        for v in yt:
            y = self.Y(v)
            self.body.append(f'<line x1="{self.px0}" y1="{y:.1f}" x2="{self.px1}" y2="{y:.1f}" stroke="{t["grid"]}"/>')
            self.body.append(text(self.px0 - 10, y + 4.5, yfmt(v), 12, t["faint"], 400, "end"))
        for v in xt:
            x = self.X(v)
            self.body.append(f'<line x1="{x:.1f}" y1="{self.py0}" x2="{x:.1f}" y2="{self.py0 + 5}" stroke="{t["faint"]}"/>')
            self.body.append(text(x, self.py0 + 20, xfmt(v), 12, t["faint"], 400, "middle"))
        self.body.append(f'<line x1="{self.px0}" y1="{self.py0}" x2="{self.px1}" y2="{self.py0}" stroke="{t["faint"]}"/>')
        if xlabel:
            self.body.append(text((self.px0 + self.px1) / 2, self.py0 + 42, xlabel, 12.5, t["sub"], 400, "middle"))
        if ylabel:
            self.body.append(text(18, (self.py0 + self.py1) / 2, ylabel, 12.5, t["sub"], 400, "middle",
                                  extra=f'transform="rotate(-90 18 {(self.py0 + self.py1) / 2:.1f})"'))

    def X(self, v):
        a, b = self.xr
        if self.xlog:
            a, b, v = math.log10(a), math.log10(b), math.log10(v)
        return self.px0 + (v - a) / (b - a) * (self.px1 - self.px0)

    def Y(self, v):
        a, b = self.yr
        return self.py0 - (v - a) / (b - a) * (self.py0 - self.py1)

    def line(self, xs, ys, col, dash="", marker="circle", width=2.4):
        pts = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in zip(xs, ys))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{width}" '
                         f'stroke-linejoin="round"{d}/>')
        for x, y in list(zip(xs, ys))[1:]:
            if marker == "circle":
                self.body.append(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="3.6" fill="{col}"/>')
            else:
                self.body.append(f'<rect x="{self.X(x) - 3.4:.1f}" y="{self.Y(y) - 3.4:.1f}" width="6.8" height="6.8" fill="{col}"/>')

    def legend(self, items, x, y):
        for i, (lab, col) in enumerate(items):
            yy = y + i * 20
            self.body.append(f'<line x1="{x}" y1="{yy - 4}" x2="{x + 20}" y2="{yy - 4}" stroke="{col}" stroke-width="3"/>')
            self.body.append(text(x + 28, yy, lab, 12.5, self.t["sub"]))

    def svg(self, label):
        return svg(self.W, self.H, "".join(self.body), label)


def chart_funnel(theme):
    n = headline_numbers()
    c = Chart(theme, "The amplified round",
              ["Yang–Mills and Hodge libraries crossed to depth four;", "the check and the refuter decide what counts."],
              x0=210, x1=590, y0=330, y1=118)
    t = c.t
    c.xr, c.xlog = (10, 80000), True
    rows = [("bred", n["bred"], t["faint"]), ("closed", n["closed"], t["blue"]),
            ("accepted by the check", n["accepted"], t["teal"]), ("survived the refuter", n["survived"], t["violet"])]
    for i, (lab, v, col) in enumerate(rows):
        y = 124 + i * 52
        w = c.X(v) - c.px0
        c.body.append(f'<rect x="{c.px0}" y="{y}" width="{w:.1f}" height="30" rx="7" fill="{col}" fill-opacity="0.85"/>')
        c.body.append(text(c.px0 - 12, y + 20, lab, 13.5, t["ink"], 600, "end"))
        c.body.append(text(c.px0 + w + 8, y + 20, f"{v:,}", 13.5, t["ink"], 700, family=MONO))
    c.body.append(text(28, 348, f"Of the closed ones {n['stopped']} stop without a checkable form and {n['rejected']} are rejected;",
                       12.5, t["sub"]))
    c.body.append(text(28, 367, f"the refuter breaks {n['refuted']}, as weaker than a known range or a repeat. Log scale.",
                       12.5, t["sub"]))
    return c.svg("The amplified round: composites bred, closed, accepted and surviving")


def chart_memory(theme):
    m = load("memory_study.json")["arms"]
    c = Chart(theme, "Memory halves the checks",
              ["Distinct survivors against checks, 60 seeds, five rounds;", "every arm ends at the same plateau."])
    t = c.t
    c.axes((0, 100), (0, 7), [0, 20, 40, 60, 80, 100], [0, 2, 4, 6], "checks (cumulative)", "distinct survivors")
    arms = [("full", "memory and retrieval", t["violet"], ""), ("full-noretrieve", "memory, no retrieval", t["blue"], "5 4"),
            ("boosted", "boosters, no memory", t["amber"], ""), ("unboosted", "neither", t["faint"], "5 4"),
            ("random", "random pairing", t["rose"], "2 4")]
    for key, lab, col, dash in arms:
        rows = m[key]["rows"]
        xs, ys, s = [0], [0], 0
        for r in rows:
            s += r["checks"]
            xs.append(s)
            ys.append(r["cum"])
        c.line(xs, ys, col, dash)
        if key in ("full", "boosted"):
            c.body.append(text(c.X(xs[-1]), c.Y(ys[-1]) - 14, f"{xs[-1]:.1f} checks", 12, col, 700, "middle", MONO))
    c.legend([(lab, col) for _, lab, col, _ in arms], 400, 236)
    return c.svg("Memory halves the checks needed to reach the plateau of survivors")


def chart_agents(theme):
    R = load("loop_state.json")["rounds"]
    c = Chart(theme, "Five agents against one loop",
              ["Survivors against checks over eleven rounds; agents level off", "early, the loop buys known results."])
    t = c.t
    c.axes((0, 820), (0, 30), [0, 200, 400, 600, 800], [0, 10, 20, 30], "checks (cumulative)", "distinct survivors")
    for key, lab, col, mk in (("agents_total", "five target agents", t["violet"], "circle"),
                              ("control", "single loop, no memory", t["faint"], "square")):
        xs, ys, s = [0], [0], 0
        for r in R:
            s += r[key]["checks"]
            xs.append(s)
            ys.append(r[key]["known"])
        c.line(xs, ys, col, marker=mk)
        c.body.append(text(c.X(xs[-1]) - 4, c.Y(ys[-1]) - 12, f"{ys[-1]} for {xs[-1]}", 12, col, 700, "end", MONO))
    c.legend([("five target agents", t["violet"]), ("single loop, no memory", t["faint"])], 360, 262)
    return c.svg("Five target agents reach 24 survivors for 250 checks, a single loop 27 for 797")


def chart_proposers(theme):
    r = ratios()
    c = Chart(theme, "Human ideas sit at the proposer bound",
              ["Proposals needed, as a multiple of the optimum (\u03a3 \u221a\u03c0\u1d62)\u00b2, where \u03c0 is", "the human profile of 11,683 papers (Chen, Zhao and Cohan 2026)."],
              x0=150, x1=590, y0=300, y1=120)
    t = c.t
    c.axes((0.9, 4.6), (0, 2), [1, 2, 3, 4], [], "multiple of the bound", "")
    for k, (ax, lab) in enumerate((("opportunity", "opportunities"), ("method", "methods"))):
        y = 160 + k * 80
        c.body.append(text(c.px0 - 14, y + 4, lab, 13.5, t["ink"], 600, "end"))
        c.body.append(f'<line x1="{c.px0}" y1="{y}" x2="{c.px1}" y2="{y}" stroke="{t["grid"]}" stroke-width="10" '
                      'stroke-linecap="round"/>')
        llm = sorted(v[ax] for name, v in r.items() if name != "Human")
        for i, v in enumerate(llm):
            c.body.append(f'<circle cx="{c.X(v):.1f}" cy="{y + (i % 2) * 0 :.1f}" r="7" fill="{t["amber"]}" '
                          f'fill-opacity="0.85" stroke="{t["card"]}" stroke-width="1.5"/>')
        h = r["Human"][ax]
        hx = c.X(h)
        c.body.append(f'<path d="M{hx:.1f},{y - 10} L{hx + 10:.1f},{y} L{hx:.1f},{y + 10} L{hx - 10:.1f},{y} z" '
                      f'fill="{t["violet"]}"/>')
        c.body.append(text(hx + 12, y - 13, f"{h:.2f}", 12, t["violet"], 700, "start", MONO))
        c.body.append(text(c.X(llm[0]), y + 26, f"{llm[0]:.2f}", 12, t["amber"], 700, "middle", MONO))
        c.body.append(text(c.X(llm[-1]), y + 26, f"{llm[-1]:.2f}", 12, t["amber"], 700, "middle", MONO))
    c.body.append(f'<path d="M{c.X(1):.1f},{c.py1 + 4} L{c.X(1):.1f},{c.py0}" stroke="{t["teal"]}" stroke-width="2" '
                  'stroke-dasharray="4 4"/>')
    c.body.append(text(c.X(1), c.py1 - 2, "bound", 12, t["teal"], 700, "middle"))
    c.body.append(f'<path d="M70,357 l8,-8 l8,8 l-8,8 z" fill="{t["violet"]}"/>')
    c.body.append(text(92, 362, "human profile", 12.5, t["sub"]))
    c.body.append(f'<circle cx="220" cy="357" r="6.5" fill="{t["amber"]}"/>')
    c.body.append(text(234, 362, "nine language models", 12.5, t["sub"]))
    return c.svg("Human research ideas need 1.08 times the optimum number of proposals, language models 1.5 to 4.3 times")


def hodge_rounds():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "experiments", "hodge", "rounds", "round_*.json"))):
        d = json.load(open(f))
        checks = sum(a.get("checks", 0) for a in d["agents"])
        chains = (d.get("chains") or {}).get("checked", 0)
        out.append(dict(round=d["round"], checks=checks, chains=chains, burst=d.get("mode") == "burst",
                        new=len(d["new_non_known_survivors"]), reached=len(d["target_points_reached"])))
    return out


def chart_hodge(theme):
    R = hodge_rounds()
    c = Chart(theme, "The Hodge-only run",
              [f"Checks per round, five agents on the targets of (F2) and (F3′);",
               "the line is the count of survivors that were not already known."])
    t = c.t
    top = max(r["checks"] + r["chains"] for r in R)
    ymax = 10 * math.ceil(top * 1.15 / 10)
    c.axes((0.4, len(R) + 0.6), (0, ymax), [r["round"] for r in R], [0, ymax // 2, ymax], "round", "checks")
    bw = (c.px1 - c.px0) / (len(R) + 0.2) * 0.62
    for r in R:
        x = c.X(r["round"])
        y = c.Y(r["checks"])
        c.body.append(f'<rect x="{x - bw / 2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{c.py0 - y:.1f}" rx="4" '
                      f'fill="{t["blue"]}" fill-opacity="0.8"/>')
        if r["chains"]:
            y2 = c.Y(r["checks"] + r["chains"])
            c.body.append(f'<rect x="{x - bw / 2:.1f}" y="{y2:.1f}" width="{bw:.1f}" height="{y - y2:.1f}" rx="4" '
                          f'fill="{t["amber"]}" fill-opacity="0.85"/>')
    c.line([r["round"] for r in R], [r["new"] for r in R], t["rose"], width=3)
    c.body.append(text(c.px1, 128, f"new results: {sum(r['new'] for r in R)}", 13, t["rose"], 700, "end", MONO))
    c.body.append(text(c.px1, 147, f"target points reached: {sum(r['reached'] for r in R)}", 13, t["rose"],
                       700, "end", MONO))
    if any(r["chains"] for r in R):
        c.legend([("agents", t["blue"]), ("long chains of a burst round", t["amber"])], 300, 168)
    return c.svg("The Hodge-only run: checks per round and no new result")


# -------------------------------------------------------------------------------------------- badges
def badge(left, right, colour):
    lw, rw = 8 + 7.2 * len(left), 10 + 6.9 * len(right)
    w = lw + rw
    return svg(round(w), 20,
               f'<rect width="{w:.0f}" height="20" rx="4" fill="#334155"/>'
               f'<rect x="{lw:.0f}" width="{rw:.0f}" height="20" rx="4" fill="{colour}"/>'
               f'<rect x="{lw:.0f}" width="6" height="20" fill="{colour}"/>'
               + text(lw / 2, 14, left, 11.5, "#ffffff", 700, "middle")
               + text(lw + rw / 2, 14, right, 11.5, "#ffffff", 600, "middle"), f"{left} {right}")


def main():
    for theme in THEME:
        save("anaxia-banner", theme, banner(theme))
        save("anaxia-numbers", theme, stats(theme))
        save("anaxia-round", theme, round_diagram(theme))
        save("chart-amplified", theme, chart_funnel(theme))
        save("chart-memory", theme, chart_memory(theme))
        save("chart-agents", theme, chart_agents(theme))
        save("chart-proposers", theme, chart_proposers(theme))
        save("chart-hodge", theme, chart_hodge(theme))
    with open(os.path.join(OUT, "badge-lean.svg"), "w") as f:
        f.write(badge("Lean 4", "kernel-checked", "#6d28d9"))
    with open(os.path.join(OUT, "badge-text.svg"), "w") as f:
        f.write(badge("proof", "in the text", "#0f766e"))
    print("headline", headline_numbers())
    print("memory", {k: round(v, 1) for k, v in memory_checks().items()})
    print("hodge", hodge_rounds())


if __name__ == "__main__":
    main()
