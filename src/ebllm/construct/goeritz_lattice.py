"""Lower bounds for the nonorientable four-genus from definite Goeritz lattices (Donaldson).

For a reduced alternating diagram both checkerboard Goeritz forms are definite.  Write P_+ = G_+
and P_- = -G_- (both positive definite, ranks r_+ and r_-), sigma = sign(G) - mu for either
colouring (Gordon-Litherland), s = sigma + 4 Arf(K) mod 8, and call l admissible when l | det K and
det K / l is a square.  Jabuka and Kelly (Algebr. Geom. Topol. 18 (2018), Theorems 2.10-2.12):

    s = 2   no admissible l with P_- + [l] inside Z^{r_- + 1}               =>  gamma_4 >= 2
    s = 6   no admissible l with P_+ + [l] inside Z^{r_+ + 1}               =>  gamma_4 >= 2
    s = 0   neither of the two above                                        =>  gamma_4 >= 2
    s = 4   neither P_+ inside Z^{r_+ + 2} nor P_- inside Z^{r_- + 2}       =>  gamma_4 >= 3

A Moebius band (or, for s = 4, a surface with b_1 = 2) bounded by K would give a closed definite
four-manifold containing these lattices in full rank, and Donaldson's theorem makes its form
diagonal.  An embedding of P + [l] in Z^{r+1} is an embedding of P whose orthogonal complement,
spanned by a primitive w, has l = k^2 |w|^2.  ``embeddings`` lists every embedding of P in Z^N up
to signed permutations of the coordinates: each new basis vector is any vector on the coordinates
already used, followed by a nonincreasing run of positive entries on fresh coordinates.

What it settles (data/crosscap4d_pass4.json.gz, from creelie/conjecture-to-choose, fourth pass):
the obstruction raises the KnotInfo 2026.10.5 lower end of 382 open alternating knots with 11 to
13 crossings (360 to gamma_4 >= 2, 22 to gamma_4 >= 3).  With the 84 new pinch certificates of
the same pass the repository settles 2,537 of the 3,525 open knots (520 at 1, 1,995 at 2, 22 at
3); 988 stay open.  The modlog run ``knot-tables-pass4`` records how the attempt got there: the
pinch generator had stalled (attempt 2 of ``knot-tables-pass3``), and the change of kind was from
upper bounds to lower bounds.

Standard library only.
"""
from __future__ import annotations

import gzip
import json
import os
from fractions import Fraction
from math import gcd, isqrt
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

DATA = os.path.join(os.path.dirname(__file__), "data")
Matrix = List[List[int]]


# --- Goeritz forms and the Gordon-Litherland signature ------------------------------------------

def _faces(pd: Sequence[Sequence[int]]) -> Tuple[List[list], Dict[tuple, int]]:
    """Corner (X, i) is the region between edges i and i+1 of crossing X (counterclockwise)."""
    pos: Dict[int, list] = {}
    for X, t in enumerate(pd):
        for i, e in enumerate(t):
            pos.setdefault(e, []).append((X, i))
    of: Dict[tuple, int] = {}
    faces: List[list] = []
    for X in range(len(pd)):
        for i in range(4):
            c = (X, i)
            if c in of:
                continue
            f = []
            while c not in of:
                of[c] = len(faces)
                f.append(c)
                Xc, ic = c
                e = pd[Xc][(ic + 1) % 4]
                o = [p for p in pos[e] if p != (Xc, (ic + 1) % 4)]
                c = o[0] if o else (Xc, (ic + 1) % 4)
            faces.append(f)
    return faces, of


def goeritz(pd: Sequence[Sequence[int]], shade: int) -> Tuple[Matrix, int]:
    """Goeritz matrix of the surface on the regions of colour `shade` (one unshaded region of
    largest degree deleted) and mu = sum of eta over the type II crossings.  KnotInfo PD codes:
    (a, b, c, d) counterclockwise from the incoming under-strand, labels increasing along the
    orientation."""
    faces, of = _faces(pd)
    if len(faces) != len(pd) + 2:
        raise ValueError("not a connected planar diagram")
    col = {0: 0}
    adj: Dict[int, set] = {k: set() for k in range(len(faces))}
    for X in range(len(pd)):
        for i in range(4):
            a, b = of[(X, i)], of[(X, (i + 1) % 4)]
            adj[a].add(b)
            adj[b].add(a)
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in col:
                col[v] = 1 - col[u]
                stack.append(v)
    white = [k for k in range(len(faces)) if col[k] != shade]
    idx = {k: j for j, k in enumerate(white)}
    m = len(white)
    G = [[0] * m for _ in range(m)]
    mu = 0
    n2 = 2 * len(pd)
    for X, (a, b, c, d) in enumerate(pd):
        r = [of[(X, i)] for i in range(4)]
        odd = col[r[1]] == shade
        eta = 1 if odd else -1
        i, j = (idx[r[0]], idx[r[2]]) if odd else (idx[r[1]], idx[r[3]])
        if i != j:
            G[i][j] -= eta
            G[j][i] -= eta
            G[i][i] += eta
            G[j][j] += eta
        inin = 0 if (d - b) % n2 == 1 else 3
        if col[r[inin]] == shade:
            mu += eta
    k = max(range(m), key=lambda t: abs(G[t][t]))
    keep = [t for t in range(m) if t != k]
    return [[G[i][j] for j in keep] for i in keep], mu


def _positive_definite(P: Matrix) -> bool:
    """Sylvester: all pivots of a symmetric elimination positive."""
    A = [[Fraction(x) for x in row] for row in P]
    n = len(A)
    for i in range(n):
        if A[i][i] <= 0:
            return False
        for j in range(i + 1, n):
            f = A[j][i] / A[i][i]
            for k in range(i, n):
                A[j][k] -= f * A[i][k]
    return True


def forms(pd: Sequence[Sequence[int]]) -> Tuple[int, Matrix, Matrix]:
    """(sigma, P_+, P_-) of an alternating diagram; raises ValueError otherwise."""
    out = []
    for s in (0, 1):
        G, mu = goeritz(pd, s)
        neg = [[-x for x in row] for row in G]
        if _positive_definite(G):
            out.append((len(G) - mu, G, "+"))
        elif _positive_definite(neg):
            out.append((-len(G) - mu, neg, "-"))
        else:
            raise ValueError("a Goeritz form is indefinite: the diagram is not alternating")
    if out[0][0] != out[1][0] or {out[0][2], out[1][2]} != {"+", "-"}:
        raise ValueError("the two colourings disagree")
    Pp = next(P for _, P, t in out if t == "+")
    Pm = next(P for _, P, t in out if t == "-")
    return out[0][0], Pp, Pm


# --- embeddings in the standard lattice ----------------------------------------------------------

def _runs(n: int, parts: int, top: int) -> Iterator[tuple]:
    if n == 0:
        yield ()
        return
    if parts == 0:
        return
    for a in range(min(top, isqrt(n)), 0, -1):
        for rest in _runs(n - a * a, parts - 1, a):
            yield (a,) + rest


def _order(P: Matrix) -> List[int]:
    r = len(P)
    order = [max(range(r), key=lambda i: P[i][i])]
    while len(order) < r:
        order.append(max((i for i in range(r) if i not in order),
                         key=lambda i: (sum(1 for j in order if P[i][j]), -P[i][i])))
    return order


def embeddings(P: Matrix, N: int, budget: int = 20_000_000) -> Iterator[List[List[int]]]:
    """Every embedding of the Gram matrix P in Z^N, up to signed permutations of coordinates."""
    r = len(P)
    order = _order(P)
    vecs: List[List[int]] = []
    count = [0]

    def xs(i, t, n, k, partial, x):
        count[0] += 1
        if count[0] > budget:
            raise RuntimeError("search budget exhausted")
        if k == t:
            if all(partial[j] == P[order[i]][order[j]] for j in range(len(vecs))):
                yield list(x), n
            return
        for j in range(len(vecs)):
            rem = sum(vecs[j][m] ** 2 for m in range(k, t))
            if (partial[j] - P[order[i]][order[j]]) ** 2 > n * rem:
                return
        a = isqrt(n)
        for v in range(-a, a + 1):
            for j in range(len(vecs)):
                partial[j] += v * vecs[j][k]
            x.append(v)
            yield from xs(i, t, n - v * v, k + 1, partial, x)
            x.pop()
            for j in range(len(vecs)):
                partial[j] -= v * vecs[j][k]

    def rec(i, t):
        if i == r:
            out = [None] * r
            for pos, o in enumerate(order):
                out[o] = vecs[pos] + [0] * (N - len(vecs[pos]))
            yield out
            return
        n = P[order[i]][order[i]]
        for x, rem in list(xs(i, t, n, 0, [0] * len(vecs), [])):
            for y in _runs(rem, N - t, isqrt(rem)):
                for v in vecs:
                    v.extend([0] * len(y))
                vecs.append(x + list(y))
                yield from rec(i + 1, t + len(y))
                vecs.pop()
                for v in vecs:
                    del v[t:]

    yield from rec(0, 0)


def complement_norm(vecs: List[List[int]]) -> int:
    """|w|^2 for a primitive w spanning the orthogonal complement of r vectors in Z^{r+1}."""
    A = [[Fraction(x) for x in row] for row in vecs]
    n = len(A[0])
    piv, row = [], 0
    for col in range(n):
        p = next((i for i in range(row, len(A)) if A[i][col] != 0), None)
        if p is None:
            continue
        A[row], A[p] = A[p], A[row]
        A[row] = [x / A[row][col] for x in A[row]]
        for i in range(len(A)):
            if i != row and A[i][col] != 0:
                f = A[i][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[row])]
        piv.append(col)
        row += 1
    free = [c for c in range(n) if c not in piv]
    if len(free) != 1:
        raise ValueError("the vectors do not span a sublattice of corank one")
    w = [Fraction(0)] * n
    w[free[0]] = Fraction(1)
    for i, c in enumerate(piv):
        w[c] = -A[i][free[0]]
    den = 1
    for x in w:
        den = den * x.denominator // gcd(den, x.denominator)
    wi = [int(x * den) for x in w]
    g = 0
    for x in wi:
        g = gcd(g, abs(x))
    return sum((x // g) ** 2 for x in wi)


def admissible(l: int, det: int) -> bool:
    return det % l == 0 and isqrt(det // l) ** 2 == det // l


def blocked(P: Matrix, det: int, budget: int = 20_000_000) -> Tuple[bool, List[int]]:
    norms = sorted({complement_norm(v) for v in embeddings(P, len(P) + 1, budget)})
    for w2 in norms:
        k = 1
        while k * k * w2 <= det:
            if admissible(k * k * w2, det):
                return False, norms
            k += 1
    return True, norms


def lower_bound(pd: Sequence[Sequence[int]], arf: int, det: int,
                budget: int = 20_000_000, sign: int = 1) -> dict:
    """The Jabuka-Kelly bound for an alternating diagram (bound None: no conclusion).  sign = -1
    is the refuter: it reverses sigma without mirroring the forms, the convention error the
    verifier must catch (it claims gamma_4 >= 2 for the trefoil)."""
    sigma, Pp, Pm = forms(pd)
    sigma *= sign
    s = (sigma + 4 * arf) % 8
    out = {"sigma": sigma, "class": s}
    if s in (2, 6):
        b, w = blocked(Pm if s == 2 else Pp, det, budget)
        out.update(theorem="2.10", bound=2 if b else None, complement_norms=w)
    elif s == 0:
        b1, w1 = blocked(Pp, det, budget)
        b2, w2 = blocked(Pm, det, budget) if b1 else (False, [])
        out.update(theorem="2.12", bound=2 if b1 and b2 else None, complement_norms=[w1, w2])
    else:
        e = (any(True for _ in embeddings(Pp, len(Pp) + 2, budget))
             or any(True for _ in embeddings(Pm, len(Pm) + 2, budget)))
        out.update(theorem="2.11", bound=2 if e else 3)
    return out


# --- the stored fourth pass -----------------------------------------------------------------------

def _load() -> dict:
    with gzip.open(os.path.join(DATA, "crosscap4d_pass4.json.gz"), "rt") as f:
        return json.load(f)


def lower_bounds() -> List[dict]:
    return _load()["lower_bounds"]


def certificates() -> List[dict]:
    return _load()["certificates"]


def check_lower_bound(d: dict, budget: int = 20_000_000) -> Optional[str]:
    """None if the stored lower bound is reproduced and raises the KnotInfo lower end."""
    r = lower_bound(d["pd"], d["arf"], d["det"], budget)
    if r["bound"] != d["bound"] or r["theorem"] != d["theorem"] or r["sigma"] != d["sigma"]:
        return "recomputed %s, stored %s" % (r["bound"], d["bound"])
    lo, hi = d["knotinfo_range"]
    if not lo < d["bound"] <= hi:
        return "the bound does not raise the KnotInfo lower end"
    return None
