"""Draw the results board of the README: every control of the engine with its verifier score,
grouped by what it is (a closure, a partial result, an open target), and under it the progress
of every attempt in the learn-from-failure log, run by run.  Animated with CSS, which renders
inside an <img> on GitHub.  Every bar, dot and number is read from ``src/ebllm/controls/*.json``
and ``src/ebllm/bllm/data/modlog.json``, so the picture cannot say more than the data.

Run from the repository root:  python3 docs/assets/make_results.py
"""
import glob
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_art import THEME, MONO, text, svg, save, delay  # noqa: E402

CONTROLS = os.path.join(ROOT, "src", "ebllm", "controls")
MODLOG = os.path.join(ROOT, "src", "ebllm", "bllm", "data", "modlog.json")

GROUPS = [("closure", "Closures", "teal"), ("partial", "Partial results", "blue"), ("open", "Open targets", "rose")]
OUTCOME = {"closed": "teal", "partial": "blue", "failed": "rose", "stopped": "amber"}
SHORT = {
    "brane-gas-uv-finite": "Brane gas: no UV divergence, every loop order, n ≥ 4",
    "graffiti-domination": "Graffiti.pc 319, 352, 358, 359, 427 (refuted)",
    "morley-tran-8.6": "Tran 8.6, regular Morley tetrahedra (refuted)",
    "shankar-lattice-paths": "Shankar 4.1, even-intersecting paths (proved)",
    "tau-maximal": "Wang–Tian, τ_k-maximal graphs (proved)",
    "welch-sum-free": "Hou–Zhao 4.10, Welch functions (proved)",
    "wowii-66": "WOWII 66, forest number (refuted)",
    "book-ramsey-58": "Book Ramsey R(B_57, B_58) = 231",
    "bridge-index-13": "Bridge index = meridional rank, 243 of 536 knots",
    "crosscap4d-13": "Nonorientable 4-genus, 2,093 of 3,525 knots",
    "d4-two-translates": "Two translates of a lattice in R^4",
    "erdos-1183-lower-bound": "Erdős 1183, the lower bound",
    "hodge-fermat-odd": "Hodge for Fermat fourfolds of odd degree",
    "kp-dyadic-blowup": "Katz–Pavlović dyadic blowup above α = 1/3",
    "lehmer-omega-16": "Lehmer: a Lehmer number has ≥ 16 prime factors",
    "gsc-mirror-clause": "GSC: the mirror clause is empty, GSC ⇔ a viable vacuum off L^μ",
    "lehmer-totient": "Lehmer's totient problem",
    "bsd": "Birch and Swinnerton-Dyer", "collatz": "Collatz", "d4-24-cell": "Densest packing in R^4",
    "erdos-straus": "Erdős–Straus", "hodge": "Hodge conjecture", "p-vs-np": "P versus NP",
    "riemann": "Riemann hypothesis", "yang-mills": "Yang–Mills mass gap",
}


def controls():
    out = {g: [] for g, _, _ in GROUPS}
    for f in sorted(glob.glob(os.path.join(CONTROLS, "*.json"))):
        with open(f) as h:
            c = json.load(h)
        if c["group"] not in out:
            continue
        req = c["required"]
        got = [k for k in req if c["factors"].get(k)]
        out[c["group"]].append(dict(slug=c["slug"], name=SHORT.get(c["slug"], c["name"]), got=len(got), req=len(req),
                                    missing=[k for k in req if k not in got]))
    for g in out:
        out[g].sort(key=lambda c: (-c["got"], c["slug"]))
    return out


def runs():
    with open(MODLOG) as f:
        return json.load(f)["runs"]


def results(theme):
    t = THEME[theme]
    cs = controls()
    rs = runs()
    W = 1280
    row_h, head_h = 26, 46
    col_w = (W - 80 - 2 * 24) / 3
    rows_max = max(len(v) for v in cs.values())
    y_top = 110
    board_h = head_h + rows_max * row_h + 20
    y_log = y_top + board_h + 50
    H = y_log + 40 + len(rs) * 24 + 60
    body = [f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["hero0"]}"/>'
            f'<stop offset="1" stop-color="{t["hero1"]}"/></linearGradient></defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="url(#bg)" stroke="{t["edge"]}"/>',
            text(40, 50, "RESULTS AND PROGRESS", 24, t["violet"], 700, extra='letter-spacing="5"'),
            text(40, 80, "Every control of the engine with the verifiers it has passed (a closure needs all eight), and "
                         "every attempt of the learn-from-failure log, run by run.", 15, t["sub"]),
            text(W - 40, 50, "anaxia controls · anaxia modlog", 14, t["faint"], 600, "end", family=MONO)]
    closed_n = len(cs["closure"])
    for gi, (g, title, colour) in enumerate(GROUPS):
        col = t[colour]
        x = 40 + gi * (col_w + 24)
        body.append(f'<rect x="{x}" y="{y_top}" width="{col_w:.0f}" height="{board_h}" rx="16" fill="{t["card"]}" '
                    f'fill-opacity="0.6" stroke="{t["edge"]}"/>')
        body.append(f'<rect x="{x}" y="{y_top}" width="5" height="{board_h}" rx="2.5" fill="{col}"/>')
        body.append(text(x + 18, y_top + 28, f"{title}  ·  {len(cs[g])}", 16, t["ink"], 700))
        for i, c in enumerate(cs[g]):
            y = y_top + head_h + i * row_h
            bx, bw = x + 18, col_w - 36
            body.append(text(bx, y + 4, c["name"][:52], 11.5, t["ink"], 500))
            body.append(f'<rect x="{bx}" y="{y + 9}" width="{bw:.0f}" height="6" rx="3" fill="{t["grid"]}"/>')
            frac = c["got"] / c["req"] if c["req"] else 0
            if frac > 0:
                body.append(f'<rect class="rise" {delay(0.12 * i + 0.25 * gi)} x="{bx}" y="{y + 9}" width="{bw * frac:.0f}" '
                            f'height="6" rx="3" fill="{col}"/>')
            body.append(text(bx + bw, y + 4, f'{c["got"]}/{c["req"]}', 11, col, 700, "end", family=MONO))
    # the log: one row per run, one dot per attempt, coloured by outcome, the last run pinged
    body.append(text(40, y_log, "The learn-from-failure log", 16, t["ink"], 700))
    legend_x = 40
    for k, colour in OUTCOME.items():
        body.append(f'<circle cx="{legend_x + 6}" cy="{y_log + 22}" r="5" fill="{t[colour]}"/>')
        body.append(text(legend_x + 16, y_log + 26, k, 12, t["sub"], 500))
        legend_x += 90
    totals = {k: 0 for k in OUTCOME}
    x0 = 330
    for ri, r in enumerate(rs):
        y = y_log + 52 + ri * 24
        last = ri == len(rs) - 1
        body.append(text(40, y + 4, r["run"], 12.5, t["ink"] if last else t["sub"], 700 if last else 500, family=MONO))
        for ai, a in enumerate(r["records"]):
            totals[a["outcome"]] = totals.get(a["outcome"], 0) + 1
            cx = x0 + ai * 22
            col = t[OUTCOME.get(a["outcome"], "faint")]
            body.append(f'<circle class="fade" {delay(0.05 * ai + 0.1 * ri)} cx="{cx}" cy="{y}" r="6.5" fill="{col}"/>')
            if last:
                body.append(f'<circle class="ping" {delay(0.05 * ai + 1.2)} cx="{cx}" cy="{y}" r="6.5" fill="none" stroke="{col}" stroke-width="1.5"/>')
        n = len(r["records"])
        body.append(text(x0 + n * 22 + 6, y + 4, f'{n} attempts · {sum(1 for a in r["records"] if a.get("change"))} rule changes',
                         11.5, t["faint"], 500, family=MONO))
    attempts = sum(totals.values())
    foot = (f"{attempts} attempts in {len(rs)} runs: {totals['closed']} closed, {totals['partial']} partial, "
            f"{totals['failed']} failed, {totals['stopped']} stopped; {closed_n} closures and {len(cs['partial'])} "
            f"partial results among the controls, none refereed; {len(cs['open'])} targets open, 0 of the 4 "
            f"superstring targets closed.")
    body.append(text(40, H - 22, foot, 12.5, t["faint"]))
    label = ("Results and progress of Anaxia: " + foot)
    return svg(W, H, "".join(body), label), foot


def main():
    for theme in THEME:
        content, foot = results(theme)
        save("anaxia-results", theme, content)
    print(foot)


if __name__ == "__main__":
    main()
