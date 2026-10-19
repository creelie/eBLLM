"""Writes branchtree_body.tex: a small hand-chosen branching history for fig_branchtree."""
# children types per accepted good parent: G good accepted, R rejected, B bad accepted
plan = [
    [["G", "G", "R"]],
    [["G", "G", "R"], ["G", "B", "R"]],
    [["G", "G", "R"], ["G", "R"], ["G", "G", "B"]],
    [["G", "G"], ["G", "R"], ["G", "G", "R"], ["G", "R", "R"], ["G", "G"]],
]
gens = [[("G", None)]]
for k, groups in enumerate(plan):
    goods = [i for i, (t, _) in enumerate(gens[k]) if t == "G"]
    assert len(goods) == len(groups)
    row = []
    for parent, kids in zip(goods, groups):
        for t in kids:
            row.append((t, parent))
    gens.append(row)
pos = []
H = 6.2
for k, row in enumerate(gens):
    n = len(row)
    pts = []
    for j in range(n):
        z = H / 2 if n == 1 else 0.25 + (H - 0.5) * j / (n - 1)
        y = 0.9 + 0.35 * ((j % 2) - 0.5)
        pts.append((3.0 * k, y, z))
    pos.append(pts)
out = []
for k in range(1, len(gens)):
    for j, (t, par) in enumerate(gens[k]):
        x0, y0, z0 = pos[k - 1][par]
        x1, y1, z1 = pos[k][j]
        style = {"G": "edgeG", "R": "edgeR", "B": "edgeB"}[t]
        out.append(f"\\draw[{style}] ({x0:.3f},{y0:.3f},{z0:.3f}) -- ({x1:.3f},{y1:.3f},{z1:.3f});")
for k, row in enumerate(gens):
    for j, (t, _) in enumerate(row):
        x, y, z = pos[k][j]
        style = {"G": "good", "R": "rej", "B": "bad"}[t]
        out.append(f"\\node[{style}] at ({x:.3f},{y:.3f},{z:.3f}) {{}};")
        if t == "B":
            out.append(f"\\node[quar] at ({x:.3f},{y:.3f},{z:.3f}) {{}};")
open("branchtree_body.tex", "w").write("\n".join(out) + "\n")
print([sum(1 for t, _ in r if t == "G") for r in gens], [sum(1 for t, _ in r if t == "B") for r in gens])
