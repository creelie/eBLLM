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
    body.append(text(W / 2, 352, "When an attempt fails, it changes one of its own rules and tries again.", 19,
                     t["sub"], 400, "middle"))
    pill = f"release {version()}"
    pw = 30 + 9.2 * len(pill)
    body.append(f'<rect x="{W - 34 - pw:.1f}" y="26" width="{pw:.1f}" height="34" rx="17" fill="{t["violet"]}" '
                f'fill-opacity="0.14" stroke="{t["violet"]}" stroke-opacity="0.5"/>')
    body.append(text(W - 34 - pw / 2, 48.5, pill, 15, t["violet"], 700, "middle", family=MONO))
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
    W, H = 1280, 388
    n = headline_numbers()
    mc = memory_checks()
    r = ratios()
    m = modlog()
    sd = seed()
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
    ]
    if sd:
        cards.append((sd["big"], t["blue"], sd["rows"]))
    cards.append((f"{m['changes']} changes", t["blue"] if not sd else t["violet"],
                  [f"of its own rules, after {m['attempts'] - m['closed']} attempts", f"that did not close; {m['advanced']} of "
                   f"the {m['built']}", "changes it built moved their target"]))
    if sd and sd.get("crossed"):
        cards.append(("1 of 6", t["rose"],
                      ["benchmarks crossed: the seed", "conjecture. Yang–Mills, Hodge, B,", "Chowla, Erdős 1183 stay open"]))
    else:
        cards.append(("0 of 5", t["rose"],
                      ["benchmark problems solved: Yang–Mills,", "Hodge, standard conjecture B,", "Chowla, Erdős 1183"]))
    body = []
    per = 3
    cw = (W - 24 - 16 * (per - 1)) / per
    ch = (H - 20 - 16) / 2
    for i, (big, col, rows) in enumerate(cards[:6]):
        x = 12 + (i % per) * (cw + 16)
        y = 10 + (i // per) * (ch + 16)
        body.append(f'<clipPath id="c{i}"><rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="16"/>'
                    f'</clipPath>')
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw:.1f}" height="{ch:.1f}" rx="16" fill="{t["card"]}" '
                    f'stroke="{t["edge"]}"/>')
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="7" height="{ch:.1f}" fill="{col}" clip-path="url(#c{i})"/>')
        size = min(36, (cw - 48) / (0.62 * len(big)))
        body.append(text(x + 28, y + 58, big, round(size, 1), col, 700, family=MONO))
        body.append(lines(x + 28, y + 94, rows, 15.5, t["sub"], lh=22))
    return svg(W, H, "".join(body), "Six numbers from the runs of Anaxia")


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
         f"{lean_counts()[0]} + {lean_counts()[1]} theorems"),
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
        if "agents" not in d:  # a round stopped at its time limit before it reported
            continue
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
# ----------------------------------------------------------------------------------- brain and growth
BRAIN = os.path.join(DATA, "brain")
MODLOG = os.path.join(ROOT, "src", "ebllm", "bllm", "data", "modlog.json")
SEED = os.path.join(ROOT, "src", "ebllm", "construct", "data", "seed_summary.json")
PART = {
    "light": {"core": "#64748b", "laws": "#2563eb", "proposers": "#16a34a", "crossing": "#d97706",
              "memory": "#7c3aed", "knowledge": "#0891b2", "benchmarks": "#e11d48", "construction": "#b45309",
              "interface": "#94a3b8"},
    "dark": {"core": "#94a3b8", "laws": "#60a5fa", "proposers": "#4ade80", "crossing": "#fbbf24",
             "memory": "#a78bfa", "knowledge": "#22d3ee", "benchmarks": "#fb7185", "construction": "#f59e0b",
             "interface": "#cbd5e1"},
}
PARTNAME = {"core": "Verified core", "laws": "Laws and checks", "proposers": "Proposers", "crossing": "Crossing network",
            "memory": "Memory and self-change", "knowledge": "Knowledge", "benchmarks": "Benchmarks",
            "construction": "Construction mode", "interface": "Interface"}
PARTWHAT = {
    "core": ["release algebra, obligation graphs,", "the verifiers of version 1"],
    "laws": ["entropy and Rényi schedules,", "the gap law and its estimators"],
    "proposers": ["four proposers, five agents,", "the spiking selector"],
    "crossing": ["typed crossing, target points,", "the attack channel, the refuter"],
    "memory": ["one store, the vault, and the", "log of failed attempts it learns from"],
    "knowledge": ["literature constructions, task", "records, the registry of sources"],
    "benchmarks": ["six benchmarks with pass lines and the", "comparison of whole systems"],
    "construction": ["the builder, the tower of layers,", "lattice polytopes, independent checks"],
    "interface": ["the command anaxia and the", "update check of the image"],
}


def lean_counts():
    """Theorems of the paper (its axiom audit) and of the engine (lean/Audit.lean)."""
    paper = sum(1 for line in open(os.path.join(ROOT, "paper", "bllm", "lean", "axioms.txt"))
                if "depend" in line and "axioms" in line)
    engine = sum(1 for line in open(os.path.join(ROOT, "lean", "Audit.lean")) if line.startswith("#print axioms"))
    return paper, engine


def version():
    m = re.search(r'^version\s*=\s*"([^"]+)"', open(os.path.join(ROOT, "pyproject.toml")).read(), re.M)
    return m.group(1)


def anatomy():
    with open(os.path.join(BRAIN, "anatomy.json")) as f:
        a = json.load(f)
    mods = a["modules"]
    sub = {m["module"]: m["subsystem"] for m in mods}
    parts = {}
    for m in mods:
        p = parts.setdefault(m["subsystem"], dict(modules=0, loc=0))
        p["modules"] += 1
        p["loc"] += m["loc"]
    imports = sum(len(m["imports"]) for m in mods)
    between = sum(1 for m in mods for t in m["imports"] if sub.get(t) != m["subsystem"])
    return dict(parts=parts, modules=len(mods), loc=sum(m["loc"] for m in mods), imports=imports, between=between)


def growth_rows():
    with open(os.path.join(BRAIN, "growth.json")) as f:
        rows = json.load(f)["rows"]
    keep = {}
    for r in rows:
        if r.get("release") == "tree":
            keep[version()] = dict(r, release=version())
        elif r.get("release"):
            keep[r["release"]] = r
    return [r for v, r in keep.items() if v.endswith(".0") or v == version()]


def modlog():
    with open(MODLOG) as f:
        runs = json.load(f)["runs"]
    recs = [r for run in runs for r in run["records"]]
    changes = [r for r in recs if r.get("change")]
    kinds = {}
    for r in changes:
        kinds[r["change"]["kind"]] = kinds.get(r["change"]["kind"], 0) + 1
    retry = {}
    for r in changes:
        k = r.get("retry") or "not yet built"
        retry[k] = retry.get(k, 0) + 1
    return dict(runs=len(runs), attempts=len(recs), targets=len({(run["run"], r["target"]) for run in runs
                                                                  for r in run["records"]}),
                changes=len(changes), built=sum(1 for r in changes if r.get("retry")),
                advanced=sum(1 for r in changes if r.get("retry") in ("closed", "partial")),
                closed=sum(1 for r in recs if r["outcome"] == "closed"), kinds=kinds, retry=retry)


def seed():
    if not os.path.exists(SEED):
        return None
    with open(SEED) as f:
        return json.load(f)


def arrowhead(t, mid="ar"):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{t["faint"]}"/></marker>')


def part_card(t, theme, key, x, y, w, h, p, top):
    col = PART[theme][key]
    bar = (w - 36) * p["loc"] / top
    return "".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{t["bg"]}" stroke="{t["edge"]}"/>',
        f'<rect x="{x}" y="{y + 14}" width="5" height="{h - 28}" rx="2.5" fill="{col}"/>',
        text(x + 20, y + 30, PARTNAME[key], 16.5, t["ink"], 700),
        text(x + w - 16, y + 30, f'{p["modules"]} mod', 12.5, col, 700, "end", family=MONO),
        lines(x + 20, y + 54, PARTWHAT[key], 12.8, t["sub"], lh=18),
        f'<rect x="{x + 20}" y="{y + h - 24}" width="{w - 36}" height="8" rx="4" fill="{t["grid"]}"/>',
        f'<rect x="{x + 20}" y="{y + h - 24}" width="{bar:.1f}" height="8" rx="4" fill="{col}"/>',
        text(x + w - 16, y + h - 30, f'{p["loc"]:,} lines', 11.5, t["sub"], 600, "end", family=MONO),
    ])


def brain(theme):
    t = THEME[theme]
    a = anatomy()
    W, H = 1280, 560
    parts = a["parts"]
    top = max(p["loc"] for p in parts.values())
    body = [f'<defs>{arrowhead(t)}</defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="{t["card"]}" stroke="{t["edge"]}"/>',
            text(40, 50, "The brain of Anaxia", 22, t["ink"], 700),
            text(40, 76, f'Release {version()}: {a["modules"]} modules and {a["loc"]:,} lines of Python in nine parts, '
                         f'wired by {a["imports"]} imports, {a["between"]} of them between parts.', 14.5, t["sub"])]
    stages = [("SENSE", 40, ["knowledge", "proposers"]), ("INTEGRATE", 330, ["laws", "crossing"]),
              ("ACT", 620, ["construction", "benchmarks"]), ("ACT", 910, ["core", "interface"])]
    cw, ch, y0 = 290 - 20, 124, 128
    for name, x, keys in stages:
        if name != "ACT" or x == 620:
            body.append(text(x + 4, y0 - 12, name, 12.5, t["faint"], 700, extra='letter-spacing="3"'))
        for i, k in enumerate(keys):
            body.append(part_card(t, theme, k, x, y0 + i * (ch + 16), cw, ch, parts.get(k, dict(modules=0, loc=0)),
                                  top))
    mid = y0 + ch + 8
    for x in (40 + cw, 330 + cw):
        body.append(f'<line x1="{x + 2}" y1="{mid}" x2="{x + 18}" y2="{mid}" stroke="{t["faint"]}" stroke-width="2" '
                    f'marker-end="url(#ar)"/>')
    my = y0 + 2 * ch + 16 + 34
    mh = 92
    body.append(text(44, my - 12, "FEED BACK", 12.5, t["faint"], 700, extra='letter-spacing="3"'))
    mem = parts.get("memory", dict(modules=0, loc=0))
    col = PART[theme]["memory"]
    body.append(f'<rect x="40" y="{my}" width="{W - 80}" height="{mh}" rx="14" fill="{t["bg"]}" stroke="{t["edge"]}"/>')
    body.append(f'<rect x="40" y="{my + 14}" width="5" height="{mh - 28}" rx="2.5" fill="{col}"/>')
    body.append(text(60, my + 32, PARTNAME["memory"], 16.5, t["ink"], 700))
    body.append(text(60, my + 56, "every verdict is written once and never checked again; every failed attempt writes a "
                                  "record that changes one rule,", 12.8, t["sub"]))
    body.append(text(60, my + 75, "and the next attempt reads the rule book that the record changed", 12.8, t["sub"]))
    body.append(text(W - 56, my + 32, f'{mem["modules"]} modules · {mem["loc"]:,} lines', 12.5, col, 700, "end",
                     family=MONO))
    for x in (620 + cw / 2, 910 + cw / 2):
        body.append(f'<line x1="{x}" y1="{y0 + 2 * ch + 18}" x2="{x}" y2="{my - 4}" stroke="{t["faint"]}" '
                    f'stroke-width="2" marker-end="url(#ar)"/>')
    body.append(f'<path d="M{40 + cw / 2},{my - 2} L{40 + cw / 2},{y0 + 2 * ch + 20}" fill="none" stroke="{col}" '
                f'stroke-width="2.2" stroke-dasharray="6 5" marker-end="url(#ar)"/>')
    body.append(text(40 + cw / 2 + 10, my - 14, "next attempt", 12.5, col, 600))
    body.append(text(40, H - 18, "Counts read from the source by paper/bllm/paper/figures/src/collect_brain.py; "
                                 "bars are lines of Python, on one scale.", 12, t["faint"]))
    return svg(W, H, "".join(body), f'The brain of Anaxia: {a["modules"]} modules in nine parts')


def failure_loop(theme):
    t = THEME[theme]
    m = modlog()
    W, H = 1280, 470
    body = [f'<defs>{arrowhead(t)}</defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="{t["card"]}" stroke="{t["edge"]}"/>',
            text(40, 50, "It learns from every failure", 22, t["ink"], 700),
            text(40, 76, f'{m["attempts"]} attempts on {m["targets"]} targets, {m["changes"]} rule changes. Each change '
                         f'names the rule, its old and new value, and the measurement it should move.', 14.5, t["sub"])]
    cx, cy, r = 330, 268, 124
    steps = [("Attempt", "under the rule book v", t["blue"]), ("Fail", "name the part that failed", t["rose"]),
             ("Record", "target, evidence, diagnosis", t["amber"]), ("Change", "one rule, tied to a number", t["violet"]),
             ("Retry", "under the rule book v+1", t["teal"])]
    pts = []
    for i in range(len(steps)):
        th = -math.pi / 2 + 2 * math.pi * i / len(steps)
        pts.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    for i in range(len(steps)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(steps)]
        a1 = math.atan2(y1 - cy, x1 - cx) + 0.30
        a2 = math.atan2(y2 - cy, x2 - cx) - 0.30
        if a2 < a1:
            a2 += 2 * math.pi
        sx, sy = cx + r * math.cos(a1), cy + r * math.sin(a1)
        ex, ey = cx + r * math.cos(a2), cy + r * math.sin(a2)
        body.append(f'<path d="M{sx:.1f},{sy:.1f} A{r},{r} 0 0 1 {ex:.1f},{ey:.1f}" fill="none" stroke="{t["faint"]}" '
                    f'stroke-width="2" marker-end="url(#ar)"/>')
    for (name, sub, col), (x, y) in zip(steps, pts):
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="30" fill="{col}"/>')
        body.append(text(x, y + 5, name, 13.5, "#ffffff", 700, "middle"))
        dx = 0 if abs(x - cx) < 10 else (1 if x > cx else -1)
        tx = x + dx * 40
        ty = y - 40 if y < cy - 60 else y + 50 if y > cy + 60 else y + 50
        body.append(text(tx, ty, sub, 12.5, t["sub"], 500, "middle" if dx == 0 else "start" if dx > 0 else "end"))
    body.append(text(cx, cy - 4, f'{m["changes"]}', 30, t["ink"], 700, "middle", family=MONO))
    body.append(text(cx, cy + 20, "rule changes", 13, t["sub"], 600, "middle"))
    # right: what was changed, and what the retries did
    x0, y = 640, 120
    body.append(text(x0, y, "What was changed", 16, t["ink"], 700))
    kinds = sorted(m["kinds"].items(), key=lambda kv: -kv[1])
    top = max(v for _, v in kinds)
    for i, (k, v) in enumerate(kinds):
        yy = y + 22 + i * 30
        w = 200 * v / top
        body.append(text(x0 + 110, yy + 15, k, 13, t["ink"], 600, "end"))
        body.append(f'<rect x="{x0 + 120}" y="{yy}" width="{w:.1f}" height="20" rx="5" fill="{t["violet"]}" '
                    f'fill-opacity="0.85"/>')
        body.append(text(x0 + 128 + w, yy + 15, str(v), 13, t["ink"], 700, family=MONO))
    x1 = 1010
    body.append(text(x1, y, "The retry", 16, t["ink"], 700))
    oc = {"closed": t["teal"], "partial": t["blue"], "failed": t["rose"], "stopped": t["amber"], "not yet built": t["faint"]}
    order = [k for k in ("closed", "partial", "failed", "stopped", "not yet built") if k in m["retry"]]
    for i, k in enumerate(order):
        yy = y + 22 + i * 30
        body.append(f'<rect x="{x1}" y="{yy}" width="20" height="20" rx="5" fill="{oc[k]}"/>')
        body.append(text(x1 + 30, yy + 15, k, 13, t["ink"], 600))
        body.append(text(W - 50, yy + 15, str(m["retry"][k]), 13, t["ink"], 700, "end", family=MONO))
    body.append(lines(x1, y + 22 + len(order) * 30 + 24,
                      [f'{m["advanced"]} of the {m["built"]} changes that were', "built moved their target;",
                       f'{m["closed"]} targets closed in all.'], 12.8, t["sub"], lh=19))
    body.append(text(40, H - 18, "From src/ebllm/bllm/data/modlog.json; anaxia modlog prints it, and anaxia modlog "
                                 "--patterns ranks the kinds of change by what they achieved.", 12, t["faint"]))
    return svg(W, H, "".join(body), "The learn-from-failure loop of Anaxia and what its changes did")


def growth(theme):
    t = THEME[theme]
    rows = growth_rows()
    W, H = 1280, 470
    keys = ["core", "interface", "laws", "proposers", "crossing", "benchmarks", "knowledge", "memory", "construction"]
    body = [f'<rect width="{W}" height="{H}" rx="22" fill="{t["card"]}" stroke="{t["edge"]}"/>',
            text(40, 50, "How it grew", 22, t["ink"], 700),
            text(40, 76, "Lines of Python in each part at each minor release and today, with the tests and the Lean "
                         "theorems of each.", 14.5, t["sub"])]
    x0, x1, yb, yt = 90, 900, 380, 120
    top = max(r["loc_total"] for r in rows)
    step = (x1 - x0) / len(rows)
    bw = min(96, step * 0.56)
    for g in range(0, top + 1, 2000):
        y = yb - (yb - yt) * g / top
        body.append(f'<line x1="{x0 - 10}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{t["grid"]}"/>')
        body.append(text(x0 - 16, y + 4, f"{g:,}", 11.5, t["faint"], 500, "end", family=MONO))
    for i, r in enumerate(rows):
        x = x0 + step * (i + 0.5) - bw / 2
        y = yb
        for k in keys:
            h = (yb - yt) * r["loc"].get(k, 0) / top
            if h > 0:
                body.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                            f'fill="{PART[theme][k]}"/>')
            y -= h
        body.append(text(x + bw / 2, y - 10, f'{r["loc_total"]:,}', 13, t["ink"], 700, "middle", family=MONO))
        body.append(text(x + bw / 2, yb + 22, r["release"], 14, t["ink"], 700, "middle"))
        lean = r["lean_paper"] + r["lean_engine"]
        body.append(text(x + bw / 2, yb + 42, f'{r["tests"]} tests · {lean} Lean', 11.8, t["sub"], 500, "middle"))
    lx, ly = 950, 128
    for i, k in enumerate(reversed(keys)):
        body.append(f'<rect x="{lx}" y="{ly + i * 26}" width="16" height="16" rx="4" fill="{PART[theme][k]}"/>')
        body.append(text(lx + 26, ly + i * 26 + 13, PARTNAME[k], 13, t["ink"], 500))
    body.append(text(40, H - 18, "Read at the tagged commit of each release by collect_brain.py; patch releases are left "
                                 "out.", 12, t["faint"]))
    return svg(W, H, "".join(body), "How Anaxia grew, release by release")


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
        save("anaxia-brain", theme, brain(theme))
        save("anaxia-loop", theme, failure_loop(theme))
        save("anaxia-growth", theme, growth(theme))
    with open(os.path.join(OUT, "badge-lean.svg"), "w") as f:
        f.write(badge("Lean 4", "kernel-checked", "#6d28d9"))
    with open(os.path.join(OUT, "badge-text.svg"), "w") as f:
        f.write(badge("proof", "in the text", "#0f766e"))
    print("headline", headline_numbers())
    print("memory", {k: round(v, 1) for k, v in memory_checks().items()})
    print("hodge", hodge_rounds())


if __name__ == "__main__":
    main()
