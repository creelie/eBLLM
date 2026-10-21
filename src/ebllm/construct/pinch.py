"""The nonorientable four-genus of knots from pinch moves, and two walls of the bridge-index table.

The smooth nonorientable four-genus gamma_4(K) is the least first Betti number of a smooth
nonorientable surface in B^4 bounded by K (gamma_4 = 1 for slice knots).  A pinch move smooths one
crossing of a diagram against the orientation, so the result K' is again a knot.  It is a band move
whose band does not respect the orientation, so

    gamma_4(K) <= 1                 if K' is slice or the unknot,
    gamma_4(K) <= gamma_4(K') + 1   in general.

When the bound equals the lower end of the KnotInfo interval (1 for a knot that is not slice, or 2
from the Arf and linking-form obstructions of Yasuhara and of Murakami-Yasuhara recorded by Lee and
Sabloff), gamma_4(K) is settled.

What it settles (data/crosscap4d_pass3.json.gz, from
https://github.com/creelie/conjecture-to-choose/releases/tag/v1.1.0): KnotInfo 2026.10.5 leaves
gamma_4 open for 3,525 prime knots with 11 to 13 crossings.  The repository settles 2,093 of them
(465 at gamma_4 = 1, 1,628 at gamma_4 = 2) and lowers the upper bound of 575 more; 1,432 stay open.
The 139 certificates of the third pass are stored here.  They were missed before because the
verifier compared knot complements from one simplified triangulation; forty simplifications under
fixed seeds, with one level of Pachner moves, find a common triangulation (``seeded`` in the modlog
run ``knot-tables-pass3``).  The identification of the pinched diagram with its target uses Regina
and Gordon-Luecke and is done by crosscap4d/verify/verify.py in that repository; this module checks
everything that needs no topology: the diagram is a knot diagram with the stored crossing count,
the smoothing is the nonorientable one (one component), and the bound follows from the KnotInfo
values of the target and settles the interval.

Two walls of the bridge-index table (modlog run ``knot-tables-pass3``), with the functions that
reproduce them on small cases:

    Alexander quandles   ``alexander_colourings(pd, p, t)`` is the dimension of the colourings of
                         a diagram by F_p with a > b = t a + (1 - t) b.  If m meridians generate the
                         knot group, every colouring is fixed by the colours of m arcs, so this
                         dimension is a lower bound for the meridional rank.  For the 293 open
                         13-crossing knots it is at most 3 over every F_p[t]/(g), p < 110.
    closed 3-braids      a closed 3-braid has bridge index at most 3; none of the 293 is the closure
                         of a 3-braid in Murasugi normal form in the range searched.

Standard library only.
"""
from __future__ import annotations

import gzip
import json
import os
from typing import Dict, List, Optional, Sequence

DATA = os.path.join(os.path.dirname(__file__), "data")

PD = List[List[int]]


def _components(pd: Sequence[Sequence[int]]) -> int:
    """Number of components of the link with this (unoriented) PD code: each crossing joins
    a to c and b to d."""
    parent: Dict[int, int] = {}

    def find(x: int) -> int:
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, c, d in pd:
        parent[find(a)] = find(c)
        parent[find(b)] = find(d)
    return len({find(x) for t in pd for x in t})


def smooth(pd: Sequence[Sequence[int]], idx: int, kind: int) -> PD:
    """Remove crossing idx, joining the strands (a,b),(c,d) if kind == 0 and (a,d),(b,c) if
    kind == 1.  Raises ValueError if the smoothing leaves a free circle."""
    a, b, c, d = pd[idx]
    rest = [list(t) for k, t in enumerate(pd) if k != idx]
    pairs = [(a, b), (c, d)] if kind == 0 else [(a, d), (b, c)]
    for p in range(2):
        x, y = pairs[p]
        if x == y:
            raise ValueError("smoothing leaves a free circle")
        for t in rest:
            for q in range(4):
                if t[q] == y:
                    t[q] = x
        pairs = [(u if u != y else x, v if v != y else x) for u, v in pairs]
    return rest


def is_knot_diagram(pd: Sequence[Sequence[int]]) -> bool:
    labels: Dict[int, int] = {}
    for t in pd:
        if len(t) != 4:
            return False
        for x in t:
            labels[x] = labels.get(x, 0) + 1
    return all(v == 2 for v in labels.values()) and (not pd or _components(pd) == 1)


def is_pinch(pd: Sequence[Sequence[int]], idx: int, kind: int) -> bool:
    """True if the smoothing is the nonorientable one: the result has one component."""
    try:
        out = smooth(pd, idx, kind)
    except ValueError:
        return False
    return not out or _components(out) == 1


def bound(target_slice: bool, target_gamma4: int) -> int:
    return 1 if target_slice else target_gamma4 + 1


def check_certificate(c: dict) -> Optional[str]:
    """None if the certificate passes every check that needs no topology, else the reason."""
    pd = c["diagram"]
    if not is_knot_diagram(pd):
        return "not a knot diagram"
    if not 0 <= c["crossing"] < len(pd):
        return "no such crossing"
    if not is_pinch(pd, c["crossing"], c["smoothing"]):
        return "the smoothing is orientable (two components) or leaves a circle"
    if c["target"] == "unknot" and not c["target_slice"]:
        return "the unknot is slice"
    b = bound(c["target_slice"], c["target_gamma4"])
    if b != c["bound"]:
        return "bound %d does not follow (computed %d)" % (c["bound"], b)
    lo, hi = c["knotinfo_range"]
    if b != lo or not lo < hi:
        return "the bound does not settle the KnotInfo interval"
    return None


def certificates() -> List[dict]:
    with gzip.open(os.path.join(DATA, "crosscap4d_pass3.json.gz"), "rt") as f:
        return json.load(f)["certificates"]


def refute(c: dict) -> Optional[str]:
    """The refuter: the other smoothing of the same crossing is orientable (two components), so
    it gives no nonorientable band; it must fail where the certificate passes."""
    other = dict(c, smoothing=1 - c["smoothing"])
    return check_certificate(other)


# --- the Alexander-quandle wall ---------------------------------------------------------------

def _rank_mod(rows: List[List[int]], p: int) -> int:
    rows = [[x % p for x in r] for r in rows]
    rank, col, n = 0, 0, len(rows[0]) if rows else 0
    while rank < len(rows) and col < n:
        piv = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if piv is None:
            col += 1
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        inv = pow(rows[rank][col], p - 2, p)
        rows[rank] = [x * inv % p for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                f = rows[i][col]
                rows[i] = [(x - f * y) % p for x, y in zip(rows[i], rows[rank])]
        rank += 1
        col += 1
    return rank


def alexander_colourings(pd: Sequence[Sequence[int]], p: int, t: int) -> int:
    """Dimension over F_p of the colourings of an oriented KnotInfo PD diagram by the Alexander
    quandle a > b = t a + (1 - t) b (t a unit).  Arcs are the classes of edges joined through
    over-crossings; at each crossing the outgoing under arc is t (incoming) + (1 - t) (over),
    or the same with t^-1 when the over strand runs the other way."""
    n2 = 2 * len(pd)
    parent: Dict[int, int] = {}

    def find(x: int) -> int:
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x

    for a, b, c, d in pd:
        find(a), find(c)
        parent[find(b)] = find(d)
    roots = sorted({find(e) for cr in pd for e in cr})
    idx = {r: i for i, r in enumerate(roots)}
    m = len(roots)
    tinv = pow(t, p - 2, p)
    rows = []
    for a, b, c, d in pd:
        s = t if b == d % n2 + 1 else tinv
        r = [0] * m
        r[idx[find(c)]] += 1
        r[idx[find(a)]] -= s
        r[idx[find(b)]] -= 1 - s
        rows.append(r)
    return m - _rank_mod(rows, p)
