"""Writes history_body.tex for fig_history: five lanes of dated milestones."""
lanes = [
    ("Logic and\nself-reference", "cpurple", [
        (1931, "G\\\"odel"), (1950, "Turing"), (1955, "L\\\"ob"), (1964, "Solomonoff"),
        (1965, "Good"), (2003, "G\\\"odel machine"), (2005, "AIXI")]),
    ("Information\nand testing", "cblue", [
        (1945, "Wald"), (1948, "Shannon"), (1949, "Kraft"), (1952, "Huffman"),
        (1961, "R\\'enyi"), (1965, "Campbell"), (1978, "Gallager")]),
    ("Branching and\nrandomness", "cgreen", [
        (1875, "Watson--Galton"), (1909, "Borel"), (1949, "Otter"), (1966, "Kesten--Stigum"),
        (1969, "Dwass"), (1972, "Athreya--Ney")]),
    ("Checking\nproofs", "cgold", [
        (1970, "Automath"), (1979, "LCF"), (1980, "Schwartz--Zippel"), (1985, "Babai, GMR"),
        (1998, "PCP theorem"), (2021, "Lean 4")]),
    ("Learning with\nverifiers", "cred", [
        (2016, "AlphaGo"), (2017, "Transformer"), (2018, "AlphaZero"), (2020, "Kaplan"),
        (2020.7, "GPT-f"), (2021.3, "Cobbe"), (2022.1, "STaR"), (2022.8, "Uesato"),
        (2023.4, "Lightman"), (2024.0, "AlphaGeometry"), (2024.6, "Brown, Snell"),
        (2025.1, "Jia et al."), (2025.8, "AlphaProof")]),
]
def X(y):
    if y <= 1940: return (y - 1870) * 0.03
    if y <= 1975: return 2.1 + (y - 1940) * 0.17
    if y <= 2000: return 8.05 + (y - 1975) * 0.08
    if y <= 2015: return 10.05 + (y - 2000) * 0.17
    return 12.6 + (y - 2015) * 0.8
ROWS = [1, -1, 2, -2, 3, -3, 4, -4, 5, -5]
STEP = 0.46
def span(x, lab):
    w = 0.15 * len(lab.replace("\\", "").replace('"', "").replace("--", "-")) + 0.12
    lo, hi = x - w / 2, x + w / 2
    if lo < -0.1:
        lo, hi = x - 0.12, x - 0.12 + w
    elif hi > 21.5:
        lo, hi = x + 0.12 - w, x + 0.12
    return lo, hi
def clash(a, b):
    (x, r, lo, hi), (x2, r2, lo2, hi2) = a, b
    if r2 == r and not (hi + 0.15 < lo2 or lo - 0.15 > hi2):
        return True
    if (r2 > 0) == (r > 0):
        if abs(r2) > abs(r) and lo < x2 < hi:
            return True
        if abs(r2) < abs(r) and lo2 < x < hi2:
            return True
    return False
def place(evs):
    items = [(X(yr), lab) + span(X(yr), lab) for (yr, lab) in evs]
    best = [None, None]
    def dfs(i, acc, cost):
        if best[0] is not None and cost >= best[0]:
            return
        if i == len(items):
            best[0], best[1] = cost, list(acc); return
        x, lab, lo, hi = items[i]
        for k, r in enumerate(ROWS):
            cand = (x, r, lo, hi)
            if any(clash(cand, c) for c in acc):
                continue
            acc.append(cand); dfs(i + 1, acc, cost + abs(r)); acc.pop()
    dfs(0, [], 0)
    return [(c[0], c[1], it[1]) for c, it in zip(best[1], items)]
placed = [place(evs) for (_, _, evs) in lanes]
heights = [2 * (max(abs(c) for _, c, _ in p) * STEP + 0.42) + 0.2 for p in placed]
out = []
top = sum(heights)
ybase = top
for li, (name, col, evs) in enumerate(lanes):
    LH = heights[li]
    yc = ybase - LH / 2
    ybase -= LH
    out.append(f"\\fill[{col}!7] (-0.2,{yc-LH/2+0.08:.3f}) rectangle (21.6,{yc+LH/2-0.08:.3f});")
    out.append(f"\\draw[{col}!70!black,line width=1.1pt] (-0.2,{yc:.3f}) -- (21.6,{yc:.3f});")
    nm = name.replace("\n", "\\\\")
    out.append(f"\\node[font=\\footnotesize\\bfseries,align=right,anchor=east,{col}!70!black] at (-0.35,{yc:.3f}) {{{nm}}};")
    for (x, chosen, lab) in placed[li]:
        out.append(f"\\draw[{col}!60!black,line width=0.35pt] ({x:.3f},{yc:.3f}) -- ({x:.3f},{yc+chosen*STEP:.3f});")
        out.append(f"\\node[circle,inner sep=1.5pt,ball color={col}!70!white] at ({x:.3f},{yc:.3f}) {{}};")
        anchor = "south" if chosen > 0 else "north"
        lx = x
        hw = (0.15 * len(lab.replace("\\", "").replace('"', "").replace("--", "-")) + 0.12) / 2
        if x - hw < -0.1:
            anchor += " west"; lx = x - 0.12
        elif x + hw > 21.5:
            anchor += " east"; lx = x + 0.12
        out.append(f"\\node[font=\\footnotesize,anchor={anchor},inner sep=1pt] at ({lx:.3f},{yc+chosen*STEP:.3f}) {{{lab}}};")
# time axis
out.append(f"\\draw[-{{Stealth[length=2mm]}},line width=0.6pt] (-0.2,-0.15) -- (21.8,-0.15);")
for yr in [1870, 1900, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2015, 2020, 2025]:
    x = X(yr)
    out.append(f"\\draw (({x:.3f},-0.15) -- ({x:.3f},-0.25) node[below,font=\\scriptsize] {{{yr}}};")
    out.append(f"\\draw[gray!35,line width=0.25pt,densely dotted] ({x:.3f},-0.15) -- ({x:.3f},{top:.3f});")
open("history_body.tex", "w").write("\n".join(out).replace("((", "(") + "\n")
