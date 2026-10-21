"""Draw the section strips of the README: one animated band under each heading that has no figure of
its own, so that every part of the page moves.  A strip carries a glyph for what the section does, a
kicker, one line saying what the reader finds there, and the command that goes with it.  The glyphs
are drawn with the motion sheet of make_art (draw, grow, fade, ping, march, orbit) and a blinking
cursor; readers who ask for reduced motion get the final frame.

Run from the repository root:  python3 docs/assets/make_sections.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_art import THEME, MONO, text, svg, delay  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sections")
W, H = 1280, 118

# slug, colour, glyph, kicker, line, command
SECTIONS = [
    ("contents", "violet", "net", "CONTENTS", "Every part of the engine, in the order a round uses them.", ""),
    ("audits", "rose", "audit", "AUDITS · TRIAGE · FIGURE CRITIC",
     "Check a published calculation stage by stage; decide go or no-go before an attack.", "anaxia audit · anaxia triage"),
    ("conjecture", "rose", "target", "POINT IT AT A CONJECTURE",
     "Tasks, attack plans and the barrier atlas of the four targets.", "anaxia attack <task>"),
    ("proved", "violet", "check", "WHAT ANAXIA HAS PROVED",
     "Theorems of the engine, each one kernel-checked in Lean 4 or proved in the text.", "lake build"),
    ("builds", "amber", "build", "IT BUILDS, TOO",
     "Construction mode: gadgets, reflexive polytopes, definition repair, independent checks.", "anaxia construct"),
    ("sources", "teal", "net", "WHAT IT DRAWS ON",
     "Every system, corpus and method taken from others, and what was left out.", "anaxia sources"),
    ("install", "teal", "box", "INSTALL AND UPDATE",
     "pip or the container image, and the check for a newer image.", "docker pull ghcr.io/creelie/bllm-engine"),
    ("commands", "blue", "terminal", "COMMANDS",
     "Every subcommand of anaxia, with what it prints.", "anaxia --help"),
    ("target", "rose", "target", "ADD A TARGET",
     "A library of typed constructions, a check, a refuter and the point that settles it.", "anaxia superstring"),
    ("paper", "blue", "book", "THE PAPER",
     "The BLLM paper, its Lean development and its numeric checks.", "preprintBLLM/BLLM.pdf"),
    ("labels", "violet", "tags", "LABELS OF THE RECORDED RESULTS",
     "What a label means; it is computed by the release algebra, never written by hand.", "anaxia controls"),
    ("checks", "teal", "shield", "CHECKS",
     "What continuous integration runs on every push: Python, C, C++, Julia, Lean.", "checks/run_all.sh"),
    ("releases", "amber", "tags", "RELEASES AND THE CLOSURE RULE",
     "How a release is cut and archived, and when a result may be called closed.", "RELEASING.md"),
    ("layout", "blue", "tree", "LAYOUT",
     "Where each part of the engine lives in the repository.", "src/ebllm/"),
    ("citing", "violet", "book", "CITING",
     "The concept DOI and the DOI of every archived version.", "CITATION.cff"),
    ("licence", "teal", "shield", "LICENCE",
     "MIT for Anaxia's own code; third-party material keeps its own licence.", "THIRD_PARTY.md"),
]

BLINK = "<style>@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.blink{animation:blink 1.1s steps(1) infinite}</style>"


def glyph(kind, t, col, cx, cy):
    """A 72-pixel glyph centred at (cx, cy)."""
    g = []
    if kind == "terminal":
        g.append(f'<rect x="{cx - 34}" y="{cy - 26}" width="68" height="52" rx="8" fill="none" stroke="{col}" stroke-width="2.5"/>')
        g.append(f'<line x1="{cx - 34}" y1="{cy - 14}" x2="{cx + 34}" y2="{cy - 14}" stroke="{col}" stroke-opacity=".5"/>')
        g.append(f'<polyline class="draw" pathLength="1" points="{cx - 24},{cy - 4} {cx - 14},{cy + 4} {cx - 24},{cy + 12}" '
                 f'fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        g.append(f'<rect class="blink" x="{cx - 8}" y="{cy + 8}" width="14" height="4" fill="{col}"/>')
    elif kind == "check":
        g.append(f'<circle class="ping" cx="{cx}" cy="{cy}" r="26" fill="none" stroke="{col}" stroke-width="2"/>')
        g.append(f'<circle cx="{cx}" cy="{cy}" r="26" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-width="2.5"/>')
        g.append(f'<polyline class="draw" pathLength="1" points="{cx - 12},{cy + 1} {cx - 3},{cy + 10} {cx + 13},{cy - 9}" '
                 f'fill="none" stroke="{col}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" {delay(0.3)}/>')
    elif kind == "build":
        for i, h in enumerate((22, 38, 54)):
            x = cx - 30 + i * 22
            g.append(f'<rect class="grow" x="{x}" y="{cy + 28 - h}" width="16" height="{h}" rx="3" fill="{col}" '
                     f'fill-opacity="{0.45 + 0.25 * i:.2f}" {delay(0.2 * i)}/>')
        g.append(f'<line class="march" x1="{cx - 36}" y1="{cy + 30}" x2="{cx + 36}" y2="{cy + 30}" stroke="{col}" stroke-width="2"/>')
    elif kind == "net":
        pts = [(cx - 26, cy - 18), (cx + 24, cy - 22), (cx - 20, cy + 22), (cx + 26, cy + 16), (cx, cy)]
        for a, b in ((0, 4), (1, 4), (2, 4), (3, 4), (0, 1), (2, 3)):
            g.append(f'<line class="march" x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}" '
                     f'stroke="{col}" stroke-width="2"/>')
        for i, (x, y) in enumerate(pts):
            r = 8 if i == 4 else 5
            g.append(f'<circle class="fade" cx="{x}" cy="{y}" r="{r}" fill="{col}" {delay(0.12 * i)}/>')
        g.append(f'<circle class="ping" cx="{cx}" cy="{cy}" r="9" fill="none" stroke="{col}" stroke-width="2"/>')
    elif kind == "box":
        g.append(f'<path class="draw" pathLength="1" d="M{cx},{cy - 28} L{cx + 26},{cy - 14} L{cx + 26},{cy + 16} L{cx},{cy + 30} '
                 f'L{cx - 26},{cy + 16} L{cx - 26},{cy - 14} Z M{cx - 26},{cy - 14} L{cx},{cy} L{cx + 26},{cy - 14} M{cx},{cy} '
                 f'L{cx},{cy + 30}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>')
        g.append(f'<circle class="orbit" cx="{cx}" cy="{cy}" r="36" fill="none" stroke="{col}" stroke-opacity=".4" '
                 f'stroke-dasharray="2 8" stroke-width="2"/>')
    elif kind == "book":
        g.append(f'<path d="M{cx},{cy - 20} C{cx - 12},{cy - 28} {cx - 28},{cy - 28} {cx - 34},{cy - 24} L{cx - 34},{cy + 24} '
                 f'C{cx - 28},{cy + 20} {cx - 12},{cy + 20} {cx},{cy + 28} C{cx + 12},{cy + 20} {cx + 28},{cy + 20} {cx + 34},{cy + 24} '
                 f'L{cx + 34},{cy - 24} C{cx + 28},{cy - 28} {cx + 12},{cy - 28} {cx},{cy - 20} Z" fill="{col}" fill-opacity=".1" '
                 f'stroke="{col}" stroke-width="2.5"/>')
        g.append(f'<line x1="{cx}" y1="{cy - 20}" x2="{cx}" y2="{cy + 28}" stroke="{col}" stroke-width="2"/>')
        for i in range(3):
            for side in (-1, 1):
                x0, x1 = (cx - 26, cx - 7) if side < 0 else (cx + 7, cx + 26)
                g.append(f'<line class="draw" pathLength="1" x1="{x0}" y1="{cy - 10 + 11 * i}" x2="{x1}" y2="{cy - 10 + 11 * i}" '
                         f'stroke="{col}" stroke-width="2" stroke-linecap="round" {delay(0.15 * (2 * i + (side > 0)))}/>')
    elif kind == "tags":
        for i in range(3):
            y = cy - 20 + 18 * i
            x = cx - 30 + 6 * i
            g.append(f'<path class="fade" d="M{x},{y - 7} L{x + 40},{y - 7} L{x + 50},{y} L{x + 40},{y + 7} L{x},{y + 7} Z" '
                     f'fill="{col}" fill-opacity="{0.3 + 0.25 * i:.2f}" stroke="{col}" stroke-width="1.5" {delay(0.2 * i)}/>')
        g.append(f'<circle class="ping" cx="{cx + 22}" cy="{cy + 16}" r="4" fill="{col}"/>')
    elif kind == "shield":
        g.append(f'<path class="draw" pathLength="1" d="M{cx},{cy - 30} L{cx + 26},{cy - 20} L{cx + 24},{cy + 6} C{cx + 20},{cy + 20} '
                 f'{cx + 10},{cy + 26} {cx},{cy + 31} C{cx - 10},{cy + 26} {cx - 20},{cy + 20} {cx - 24},{cy + 6} L{cx - 26},{cy - 20} Z" '
                 f'fill="{col}" fill-opacity=".1" stroke="{col}" stroke-width="2.5" stroke-linejoin="round"/>')
        g.append(f'<polyline class="draw" pathLength="1" points="{cx - 10},{cy} {cx - 2},{cy + 8} {cx + 12},{cy - 8}" fill="none" '
                 f'stroke="{col}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" {delay(0.6)}/>')
    elif kind == "tree":
        g.append(f'<line class="draw" pathLength="1" x1="{cx - 24}" y1="{cy - 24}" x2="{cx - 24}" y2="{cy + 22}" stroke="{col}" stroke-width="2.5"/>')
        for i in range(4):
            y = cy - 14 + 12 * i
            g.append(f'<line class="draw" pathLength="1" x1="{cx - 24}" y1="{y}" x2="{cx - 10}" y2="{y}" stroke="{col}" '
                     f'stroke-width="2.5" {delay(0.2 + 0.15 * i)}/>')
            g.append(f'<rect class="fade" x="{cx - 6}" y="{y - 4}" width="{30 - 4 * (i % 2)}" height="8" rx="3" fill="{col}" '
                     f'fill-opacity=".55" {delay(0.3 + 0.15 * i)}/>')
    elif kind == "target":
        for i, r in enumerate((28, 19, 10)):
            g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="2.5" stroke-opacity="{0.4 + 0.3 * i:.1f}"/>')
        g.append(f'<circle class="ping" cx="{cx}" cy="{cy}" r="10" fill="none" stroke="{col}" stroke-width="2"/>')
        g.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{col}"/>')
        g.append(f'<line class="draw" pathLength="1" x1="{cx + 36}" y1="{cy - 36}" x2="{cx + 4}" y2="{cy - 4}" stroke="{col}" '
                 f'stroke-width="3" stroke-linecap="round" {delay(0.4)}/>')
    elif kind == "audit":
        g.append(f'<rect x="{cx - 24}" y="{cy - 30}" width="40" height="52" rx="5" fill="{col}" fill-opacity=".1" stroke="{col}" stroke-width="2.5"/>')
        for i in range(4):
            g.append(f'<line class="draw" pathLength="1" x1="{cx - 16}" y1="{cy - 18 + 11 * i}" x2="{cx + 8}" y2="{cy - 18 + 11 * i}" '
                     f'stroke="{col}" stroke-width="2" stroke-linecap="round" {delay(0.15 * i)}/>')
        g.append(f'<circle cx="{cx + 14}" cy="{cy + 14}" r="12" fill="{t["card"]}" stroke="{col}" stroke-width="3"/>')
        g.append(f'<line x1="{cx + 23}" y1="{cy + 23}" x2="{cx + 33}" y2="{cy + 33}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>')
        g.append(f'<circle class="ping" cx="{cx + 14}" cy="{cy + 14}" r="12" fill="none" stroke="{col}" stroke-width="2"/>')
    return "".join(g)


def strip(theme, slug, colour, kind, kicker, line, command):
    t = THEME[theme]
    col = t[colour]
    body = [BLINK,
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["hero1"]}"/>'
            f'<stop offset=".55" stop-color="{t["card"]}"/><stop offset="1" stop-color="{t["hero0"]}"/></linearGradient>'
            f'<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0"><stop offset=".4" stop-color="{col}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{col}" stop-opacity=".12"/><stop offset=".6" stop-color="{col}" stop-opacity="0"/>'
            f'</linearGradient><clipPath id="clip"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath></defs>',
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#bg)" stroke="{t["edge"]}"/>',
            f'<g clip-path="url(#clip)"><rect class="sweep" x="0" y="0" width="{W}" height="{H}" fill="url(#sheen)"/>'
            f'<rect class="grow" x="0" y="0" width="8" height="{H}" fill="{col}"/></g>',
            f'<circle cx="84" cy="{H / 2}" r="44" fill="{col}" fill-opacity=".08"/>',
            glyph(kind, t, col, 84, H / 2),
            text(160, 48, kicker, 14, col, 700, extra='letter-spacing="3" class="fade"'),
            text(160, 82, line, 21, t["ink"], 600, extra=f'class="fade" {delay(0.15)}'),
            f'<line class="march" x1="160" y1="{H - 14}" x2="{W - 40}" y2="{H - 14}" stroke="{col}" stroke-opacity=".5" stroke-width="2"/>']
    if command:
        body.append(text(W - 40, 48, command, 14, t["faint"], 600, "end", family=MONO, extra=f'class="fade" {delay(0.3)}'))
    return svg(W, H, "".join(body), f"{kicker.title()}: {line}")


def main():
    os.makedirs(OUT, exist_ok=True)
    for slug, colour, kind, kicker, line, command in SECTIONS:
        for theme in THEME:
            with open(os.path.join(OUT, f"{slug}-{theme}.svg"), "w") as f:
                f.write(strip(theme, slug, colour, kind, kicker, line, command))
    print(len(SECTIONS), "strips")


if __name__ == "__main__":
    main()
