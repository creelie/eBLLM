"""Draw the audit figure of the README: the nine stages of the stored audit with a pulse passing
through them, the findings sorted into their five kinds, the triage gate of the bundled example, and
the loop of the figure critic.  Every number is read from the package: the audit from
``bllm/data/audits/``, the triage from ``bllm/data/triage.example.json`` through ``triage.triage``,
and the critic count from ``figcritic.review`` on this folder.

Run from the repository root after make_art.py and make_sections.py:
    PYTHONPATH=src python3 docs/assets/make_audit.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from make_art import THEME, MONO, text, svg, delay, save  # noqa: E402
from ebllm.bllm import audit as AU, triage as TR, figcritic as FC  # noqa: E402

W, H = 1280, 560
KIND = [("substantive", "S", "rose"), ("absorbable", "B", "amber"), ("typo", "C", "faint"),
        ("confirmed", "D", "teal"), ("conclusion", "E", "violet")]


def figure(theme, nfig, critic):
    t = THEME[theme]
    name = AU.names()[0]
    a = AU.load(name)
    v = AU.verdict(AU.findings_of(a))
    rep = TR.triage(json.load(open(os.path.join(ROOT, "src", "ebllm", "bllm", "data", "triage.example.json"))))
    css = ("<style>@keyframes travel{0%{transform:translateX(0)}100%{transform:translateX(960px)}}"
           ".travel{animation:travel 5s cubic-bezier(.45,0,.55,1) infinite}"
           "@keyframes spin{to{transform:rotate(360deg)}}"
           ".spin{transform-box:fill-box;transform-origin:center;animation:spin 9s linear infinite}</style>")
    b = [css, f'<rect width="{W}" height="{H}" rx="22" fill="{t["card"]}" stroke="{t["edge"]}"/>',
         text(40, 50, "AUDIT · TRIAGE · CRITIC", 22, t["rose"], 700, extra='letter-spacing="4"'),
         text(40, 78, "Re-derive a published calculation stage by stage, check each stage with separate code, and sort "
                      "every difference by what it does.", 15, t["sub"])]
    # ---- the stages
    st = a["stages"]
    x0, x1, y = 100, 1060, 140
    b.append(f'<line class="march" x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["rose"]}" stroke-width="3"/>')
    for i, s in enumerate(st):
        x = x0 + (x1 - x0) * i / (len(st) - 1)
        b.append(f'<circle class="fade" cx="{x:.1f}" cy="{y}" r="15" fill="{t["card"]}" stroke="{t["rose"]}" '
                 f'stroke-width="3" {delay(0.1 * i)}/>')
        b.append(text(x, y + 5, str(s["n"]), 13, t["rose"], 700, "middle", family=MONO))
        rows = [""]
        for word in s["name"].split():  # greedy wrap, so neighbouring stage names never meet
            rows[-1:] = [rows[-1] + " " + word] if rows[-1] and len(rows[-1]) + len(word) < 17 else \
                [rows[-1], word] if rows[-1] else [word]
        for k, r in enumerate(rows):
            b.append(text(x, y + 36 + 15 * k, r, 11.5, t["sub"], 500, "middle"))
    b.append(f'<circle class="travel" cx="{x0}" cy="{y}" r="7" fill="{t["rose"]}"/>')
    rr = a.get("rerun")
    tag = (f"{rr['passed']} of {rr['runs']} stored checks reproduced here" if rr else "checks not rerun here")
    b.append(text(1200, y - 24, "golden", 12, t["faint"], 600, "end", family=MONO))
    b.append(text(1200, y + 6, f"{rr['passed']}/{rr['runs']}" if rr else "-", 26, t["teal"], 700, "end", family=MONO))
    b.append(text(1200, y + 28, "pass", 12, t["faint"], 600, "end", family=MONO))
    # ---- the findings
    fy = 236
    b.append(text(40, fy, "Findings by kind", 16, t["ink"], 700))
    b.append(text(40, fy + 22, "only a substantive finding can change a conclusion", 12.5, t["sub"]))
    top = max(v["counts"].values())
    for i, (k, letter, col) in enumerate(KIND):
        n = v["counts"][k]
        bx, by = 40, fy + 44 + i * 30
        w = 360 * n / top
        b.append(text(bx + 118, by + 15, f"{letter}  {k}", 12.5, t["ink"], 600, "end"))
        b.append(f'<rect class="rise" x="{bx + 128}" y="{by}" width="{w:.1f}" height="20" rx="5" fill="{t[col]}" '
                 f'fill-opacity=".85" {delay(0.6 + 0.15 * i)}/>')
        b.append(text(bx + 136 + w, by + 15, str(n), 13, t["ink"], 700, family=MONO, extra=f'class="fade" {delay(1.2 + 0.15 * i)}'))
    ok = v["conclusion_survives"]
    b.append(f'<rect x="40" y="{fy + 202}" width="490" height="36" rx="10" fill="{t["teal" if ok else "rose"]}" fill-opacity=".12" '
             f'stroke="{t["teal" if ok else "rose"]}"/>')
    b.append(text(56, fy + 225, ("the printed conclusion survives" if ok else "the conclusion is changed") +
                  f" · {tag}", 13, t["ink"], 600))
    b.append(text(56, fy + 262, "label: audit, not a closure", 12, t["faint"], 600, family=MONO))
    # ---- triage
    tx = 600
    b.append(text(tx, fy, "Triage before the attack", 16, t["ink"], 700))
    b.append(text(tx, fy + 22, f"no-go below closability {rep['constraints']['min_closability']} "
                               f"or above risk {rep['constraints']['max_risk']} (example ratings)", 12.5, t["sub"]))
    best = max(r["score"] for r in rep["ranking"])
    for i, r in enumerate(rep["ranking"]):
        by = fy + 44 + i * 30
        w = 200 * r["score"] / best
        col = t["teal"] if r["go"] else t["faint"]
        b.append(text(tx + 168, by + 15, r["id"], 12, t["ink"], 600, "end", family=MONO))
        b.append(f'<rect class="rise" x="{tx + 178}" y="{by}" width="{w:.1f}" height="20" rx="5" fill="{col}" '
                 f'fill-opacity=".85" {delay(0.8 + 0.15 * i)}/>')
        b.append(text(tx + 186 + w, by + 15, "go" if r["go"] else "no-go", 12, col, 700, family=MONO,
                      extra=f'class="fade" {delay(1.4 + 0.15 * i)}'))
    # ---- the critic loop
    cx, cy = 1160, fy + 120
    b.append(text(1220, fy, "Figure critic", 16, t["ink"], 700, "end"))
    b.append(f'<circle class="spin" cx="{cx}" cy="{cy}" r="46" fill="none" stroke="{t["violet"]}" stroke-width="3" '
             f'stroke-dasharray="40 14"/>')
    for k, (lab, dy) in enumerate((("draw", -62), ("critique", 4), ("redraw", 70))):
        b.append(text(cx, cy + dy, lab, 12, t["violet"], 700, "middle", family=MONO,
                      extra=f'class="fade" {delay(0.3 * k)}'))
    b.append(text(1220, fy + 222, f"{critic} findings on {nfig} figures", 13, t["ink"], 700, "end", family=MONO))
    b.append(text(1220, fy + 242, "canvas, overlap, captions, themes,", 12, t["sub"], 400, "end"))
    b.append(text(1220, fy + 258, "alt text, reduced motion", 12, t["sub"], 400, "end"))
    return svg(W, H, "".join(b), f"Audit, triage and figure critic: {len(st)} stages, findings "
               + ", ".join(f"{k} {n}" for k, n in v["counts"].items()) + f"; {tag}")


def main():
    # count and critique before writing, so both themes carry the same numbers; this figure's own
    # two files are counted whether or not an older copy exists
    files = {p for p in os.listdir(HERE) if p.endswith(".svg")} | {f"anaxia-audit-{th}.svg" for th in THEME}
    nfig = len(files) + sum(p.endswith(".svg") for p in os.listdir(os.path.join(HERE, "sections")))
    critic = None
    while True:  # the count includes this figure itself, so redraw until it is stable
        for theme in THEME:
            save("anaxia-audit", theme, figure(theme, nfig, critic or 0))
        now = len(FC.review(HERE))
        if now == critic:
            break
        critic = now


if __name__ == "__main__":
    main()
