"""The figure critic: exact checks on the SVG figures of the README, run after every redraw.

Uploaded by a second agent on Tubai's command.  Taken from the critic agent of PaperBanana
(D. Zhu et al., https://github.com/dwzhu-pku/PaperBanana, Apache-2.0), which closes a loop with the
figure maker: draw, critique, revise, draw again.  PaperBanana's critic is a vision-language model
reading a raster; here every rule it states that can be decided exactly on the vector source is a
check, so the critic needs no model, gives the same answer every time, and a figure that fails is
redrawn, not argued with.  The rules, in PaperBanana's order:

    fidelity    the light and dark versions of a figure carry the same text, so a number cannot be
                right in one theme and stale in the other;
    text QA     no empty or unescaped text, and every label lies inside the canvas (its width is
                estimated from the font size and the number of characters, with a margin);
    caption     no 'Figure N:' caption inside the picture: the caption belongs to the page;
    overlap     no two labels on the same baseline run into each other;
    access      the figure has role="img" and an aria-label, which GitHub shows when the image fails;
    motion      a figure with CSS animation stops moving for readers who ask for reduced motion
                (prefers-reduced-motion), and every cycle is under a minute.

Rules that need eyes (is the layout clear, is a colour choice pleasing) stay with the reader.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

NS = "{http://www.w3.org/2000/svg}"
CAPTION = re.compile(r"^\s*(fig\.?|figure)\s*\d+\s*[:.]", re.IGNORECASE)
TRANSLATE = re.compile(r"^\s*translate\(\s*([-\d.]+)[\s,]+([-\d.]+)\s*\)\s*$")
REDUCED = "prefers-reduced-motion"
MARGIN = 0.10  # a label may run this fraction of its estimated width past the canvas before it counts


def _num(s: Optional[str], default: float = 0.0) -> float:
    try:
        return float(str(s).replace("px", ""))
    except (TypeError, ValueError):
        return default


def width_of(s: str, size: float, mono: bool = False, bold: bool = False) -> float:
    """An estimate of the advance width of a label: 0.6 em a character in a monospace face; in a
    sans face narrow letters, wide letters and the rest are weighted separately."""
    if mono:
        return 0.6 * size * len(s)
    w = 0.0
    for ch in s:
        if ch in "il.,:;'|!I ":
            w += 0.28
        elif ch in "mwMW@":
            w += 0.85
        elif ch.isupper() or ch.isdigit():
            w += 0.62
        else:
            w += 0.52
    return w * size * (1.06 if bold else 1.0)


def labels(root: ET.Element) -> List[dict]:
    """Every <text> with its position after the translations of its ancestors; text under any other
    transform (a rotation, a scale) is kept but not placed."""
    out = []

    def walk(el, dx, dy, placed):
        tr = el.get("transform")
        if tr:
            m = TRANSLATE.match(tr)
            if m:
                dx, dy = dx + float(m.group(1)), dy + float(m.group(2))
            else:
                placed = False
        if el.tag == NS + "text" or el.tag == "text":
            s = "".join(el.itertext())
            size = _num(el.get("font-size"), 14.0)
            fam = el.get("font-family") or ""
            out.append(dict(text=s, x=_num(el.get("x")) + dx, y=_num(el.get("y")) + dy, size=size,
                            anchor=el.get("text-anchor") or "start", mono="Mono" in fam or "monospace" in fam,
                            bold=(el.get("font-weight") or "400") >= "600", placed=placed,
                            spaced="letter-spacing" in el.attrib))
        for c in el:
            walk(c, dx, dy, placed)

    walk(root, 0.0, 0.0, True)
    return out


def extent(lab: dict) -> Tuple[float, float]:
    w = width_of(lab["text"], lab["size"], lab["mono"], lab["bold"])
    if lab["anchor"] == "middle":
        return lab["x"] - w / 2, lab["x"] + w / 2
    if lab["anchor"] == "end":
        return lab["x"] - w, lab["x"]
    return lab["x"], lab["x"] + w


def critique(path: str) -> List[str]:
    """The findings on one figure; an empty list means it passes."""
    src = Path(path).read_text(encoding="utf-8")
    name = Path(path).name
    try:
        root = ET.fromstring(src)
    except ET.ParseError as e:
        return [f"{name}: not well-formed XML ({e})"]
    found = []
    vb = (root.get("viewBox") or "").split()
    if len(vb) != 4:
        return [f"{name}: no viewBox"]
    W, H = float(vb[2]), float(vb[3])
    if root.get("role") != "img" or not (root.get("aria-label") or "").strip():
        found.append(f"{name}: needs role=\"img\" and a non-empty aria-label")
    labs = labels(root)
    for lab in labs:
        s = lab["text"]
        if not s.strip():
            found.append(f"{name}: an empty label at ({lab['x']:.0f}, {lab['y']:.0f})")
            continue
        if CAPTION.match(s):
            found.append(f"{name}: a caption inside the picture: {s!r}")
        if not lab["placed"] or lab["spaced"]:
            continue
        a, b = extent(lab)
        slack = MARGIN * (b - a)
        if a < -slack or b > W + slack:
            found.append(f"{name}: label {s!r} runs past the canvas ({a:.0f} to {b:.0f}, width {W:.0f})")
        if lab["y"] < 0 or lab["y"] - 0.2 * lab["size"] > H:
            found.append(f"{name}: label {s!r} lies outside the canvas height (y {lab['y']:.0f}, height {H:.0f})")
    rows: Dict[float, List[dict]] = {}
    for lab in labs:
        if lab["placed"] and not lab["spaced"] and lab["text"].strip():
            rows.setdefault(round(lab["y"], 1), []).append(lab)
    for y, row in rows.items():
        spans = sorted((extent(l), l) for l in row)
        for (a1, l1), (a2, l2) in zip(spans, spans[1:]):
            overlap = a1[1] - a2[0]
            if overlap > 0.25 * min(a1[1] - a1[0], a2[1] - a2[0]) and overlap > 6:
                found.append(f"{name}: labels {l1['text']!r} and {l2['text']!r} overlap on y={y:.0f}")
    # a stylesheet can stop CSS animation; SMIL (<animate>) ignores it, so SMIL is kept to short loops
    if "@keyframes" in src and REDUCED not in src:
        found.append(f"{name}: animated, but does not stop for prefers-reduced-motion")
    for m in re.finditer(r'(?:animation[^;"}]*?\s|dur=")([\d.]+)s', src):
        if float(m.group(1)) > 60:
            found.append(f"{name}: an animation {m.group(1)} s long; keep cycles under a minute")
            break
    return found


def pair(light: str, dark: str) -> List[str]:
    """Fidelity across themes: the two versions carry the same labels in the same order."""
    a = [l["text"] for l in labels(ET.fromstring(Path(light).read_text(encoding="utf-8")))]
    b = [l["text"] for l in labels(ET.fromstring(Path(dark).read_text(encoding="utf-8")))]
    if a == b:
        return []
    diff = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return [f"{Path(light).name} and {Path(dark).name} differ at label {diff}: "
            f"{a[diff] if diff < len(a) else '(none)'!r} against {b[diff] if diff < len(b) else '(none)'!r}"]


def review(folder: str) -> List[str]:
    """Every SVG under ``folder`` and its subfolders, and every light/dark pair among them."""
    folder = Path(folder)
    found = []
    for p in sorted(folder.rglob("*.svg")):
        found += critique(str(p))
        if p.name.endswith("-light.svg"):
            d = p.with_name(p.name[: -len("-light.svg")] + "-dark.svg")
            if d.exists():
                found += pair(str(p), str(d))
    return found
