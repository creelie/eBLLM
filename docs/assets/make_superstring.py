"""Draw the superstring of the README: the four attack chains, one string per target, with an
attacker at every stage, the pulse that runs each chain to the end and stops at the first stage
without an independently checked certificate.  Animated with SMIL and CSS, which render inside an
<img> on GitHub.  Every stage, zone and stop is read from ``bllm/data/attackers.json`` through
``ebllm.bllm.superstring.run``, so the picture cannot say more than the data.

Run from the repository root:  PYTHONPATH=src python3 docs/assets/make_superstring.py
"""
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from make_art import THEME, SANS, MONO, text, svg, save, esc  # noqa: E402
from ebllm.bllm import superstring as S  # noqa: E402

COLOUR = {"hodge": "rose", "strings": "teal", "seed": "amber", "yang-mills": "blue"}
TITLE = {"hodge": "Hodge  (F2) and (F3')", "strings": "Strings  GSC", "seed": "Seed  D4 = 22",
         "yang-mills": "Yang-Mills  Dobrushin window"}


def wave(x0, x1, y, amp, n, phase=0.0, steps=160):
    pts = []
    for i in range(steps + 1):
        u = i / steps
        pts.append((x0 + (x1 - x0) * u, y + amp * math.sin(2 * math.pi * n * u + phase)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def superstring(theme):
    t = THEME[theme]
    data = S.load()
    res = S.run(data)
    W, H = 1280, 150 + 118 * len(res)
    css = (
        "@keyframes hue{0%{filter:hue-rotate(0deg)}100%{filter:hue-rotate(360deg)}}"
        "@keyframes flow{to{stroke-dashoffset:-96}}"
        "@keyframes breathe{0%,100%{opacity:.35}50%{opacity:1}}"
        ".string{stroke-dasharray:14 10;animation:flow 2.6s linear infinite}"
        ".halo{animation:breathe 1.8s ease-in-out infinite}"
        ".spin{animation:hue 14s linear infinite}"
    )
    body = [f"<style>{css}</style>",
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["hero0"]}"/>'
            f'<stop offset="1" stop-color="{t["hero1"]}"/></linearGradient>'
            f'<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter></defs>',
            f'<rect width="{W}" height="{H}" rx="22" fill="url(#bg)" stroke="{t["edge"]}"/>',
            text(40, 50, "THE SUPERSTRING", 24, t["violet"], 700, extra='letter-spacing="5"'),
            text(40, 80, "One chain per target, an attacker on every zone and piece, run to the end; "
                 "the pulse stops where no independently checked certificate exists.", 15, t["sub"]),
            text(W - 40, 50, "anaxia superstring", 14, t["faint"], 600, "end", family=MONO)]
    y = 130
    for name, r in res.items():
        col = t[COLOUR[name]]
        stages = r["stages"]
        n = len(stages)
        x0, x1 = 250, W - 70
        xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
        stop_i = next(i for i, s in enumerate(stages) if s["id"] == r["first_stop"]) if r["first_stop"] else n - 1
        body.append(f'<rect x="28" y="{y - 46}" width="{W - 56}" height="104" rx="16" fill="{t["card"]}" '
                    f'fill-opacity="0.6" stroke="{t["edge"]}"/>')
        body.append(f'<rect x="28" y="{y - 32}" width="5" height="76" rx="2.5" fill="{col}"/>')
        body.append(text(50, y - 14, TITLE[name], 17, t["ink"], 700))
        body.append(text(50, y + 10, f"{n} attackers, stop at stage {stop_i + 1}", 12.5, col, 600, family=MONO))
        body.append(text(50, y + 32, "verdict: " + r["verdict"].split(";")[0], 12, t["sub"]))
        # the string itself: a slow wave in the faint colour, a flowing dashed strand over it
        body.append(f'<path d="{wave(x0, x1, y, 9, 3)}" fill="none" stroke="{col}" stroke-opacity="0.25" stroke-width="2">'
                    f'<animate attributeName="d" dur="6s" repeatCount="indefinite" values="'
                    + ";".join(wave(x0, x1, y, 9, 3, p) for p in (0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi))
                    + '"/></path>')
        body.append(f'<path class="string" d="M{x0},{y} L{xs[stop_i]:.1f},{y}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        body.append(f'<path d="M{xs[stop_i]:.1f},{y} L{x1},{y}" fill="none" stroke="{t["faint"]}" stroke-width="2" stroke-dasharray="3 7"/>')
        for i, s in enumerate(stages):
            x = xs[i]
            closed = s["state"] == "closed"
            if i == stop_i:
                body.append(f'<circle class="halo" cx="{x:.1f}" cy="{y}" r="16" fill="{col}" filter="url(#glow)"/>')
                body.append(f'<circle cx="{x:.1f}" cy="{y}" r="9" fill="{t["bg"]}" stroke="{col}" stroke-width="3"/>')
                body.append(text(x, y - 24, "STOP", 11, col, 800, "middle", family=MONO, extra='letter-spacing="2"'))
            elif closed:
                body.append(f'<circle cx="{x:.1f}" cy="{y}" r="7" fill="{col}"/>')
                body.append(f'<path d="M{x - 3.2:.1f},{y} l2.2,2.4 l4.2,-4.6" fill="none" stroke="{t["bg"]}" stroke-width="1.8" stroke-linecap="round"/>')
            else:
                body.append(f'<circle cx="{x:.1f}" cy="{y}" r="6" fill="{t["bg"]}" stroke="{col if i < stop_i else t["faint"]}" stroke-width="2"/>')
            label = s["id"].split(".", 1)[1]
            body.append(text(x, y + 24 + (14 if i % 2 else 0), label, 10, t["sub"] if i <= stop_i else t["faint"], 600, "middle", family=MONO))
        # the pulse: runs from the start to the stop, flashes, and starts again
        dur = 1.2 + 0.35 * stop_i
        body.append(f'<circle r="5.5" fill="{col}" class="spin">'
                    f'<animate attributeName="cx" dur="{dur + 0.8:.1f}s" repeatCount="indefinite" keyTimes="0;{dur / (dur + 0.8):.3f};1" '
                    f'values="{x0};{xs[stop_i]:.1f};{xs[stop_i]:.1f}" calcMode="linear"/>'
                    f'<animate attributeName="cy" dur="{dur + 0.8:.1f}s" repeatCount="indefinite" values="{y};{y}"/>'
                    f'<animate attributeName="r" dur="{dur + 0.8:.1f}s" repeatCount="indefinite" keyTimes="0;{dur / (dur + 0.8):.3f};{(dur + 0.4) / (dur + 0.8):.3f};1" values="5.5;5.5;13;0"/>'
                    f'<animate attributeName="opacity" dur="{dur + 0.8:.1f}s" repeatCount="indefinite" keyTimes="0;{dur / (dur + 0.8):.3f};1" values="1;1;0"/>'
                    f'</circle>')
        y += 118
    body.append(text(40, H - 22, "closure rule: a stage closes only on a lean, proved or computed certificate checked by someone other than its producer; "
                     "0 of 4 targets closed.", 12.5, t["faint"]))
    label = ("The superstring: four attack chains (Hodge, strings, seed, Yang-Mills), each with its attackers, "
             "the stage where each one stops, and 0 of 4 targets closed")
    return svg(W, H, "".join(body), label)


def main():
    for theme in THEME:
        save("anaxia-superstring", theme, superstring(theme))
    for name, r in S.run(S.load()).items():
        print(name, "stops at", r["first_stop"])


if __name__ == "__main__":
    main()
