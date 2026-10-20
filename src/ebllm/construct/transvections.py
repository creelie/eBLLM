"""Bridge index = meridional rank for knots, from colourings by pseudo-reflections.

The meridional rank conjecture (Cappell and Shaneson; Kirby's problem list, Problem 1.11) says that
the bridge index b(K) of a knot equals its meridional rank mu(K), the least number of meridians
that generate the knot group.  Always mu(K) <= b(K).  This module settles the conjecture for a
given knot by matching the two bounds with certificates that a short program checks:

    upper bound   b(K) <= omega(D) for every diagram D, where omega(D) is the Wirtinger number:
                  the least number of arcs from which the colouring move (overarc and one underarc
                  coloured at a crossing => colour the other underarc) colours every arc
                  (Blair, Kjuchukova, Velazquez, Villanueva, Comm. Anal. Geom. 28 (2020) 243-262).
    lower bound   if rho: G -> GL(V), dim V = n, sends the meridian to a pseudo-reflection
                  (rank(rho(m) - 1) = 1), then mu(K) >= n - dim V^G.  Each of k meridians fixes a
                  hyperplane, so k of them fix a subspace of dimension at least n - k, and a
                  generating set fixes V^G; hence n - k <= dim V^G.

With n = 4, V^G = 0 and a diagram of Wirtinger number 4 the knot has b = mu = 4.  The
pseudo-reflections used are transvections t_v(x) = x + w(x, v) v of a symplectic form w over F_p
(order p) and reflections of a quadratic form (order 2; the Coxeter quotients used before are of
this kind).  Since g t_v g^-1 = t_{gv}, a transvection representation is a colouring of the arcs
by vectors, with v_c = +-t_{v_o}^{+-1}(v_a) at each crossing, and its fixed space is the
orthogonal of the span of the colours.  The colours of the seed arcs therefore form a basis, so
every such representation is found, up to a change of basis, by trying each nondegenerate Gram
matrix of the four seed vectors: p^6 cases (``search_sp4``).

What it settles (data/bridge13_certificates.json.gz, 243 certificates, from
https://github.com/creelie/conjecture-to-choose): KnotInfo 2026.10.5 lists the bridge index of
536 prime knots with 13 crossings as [3,4].  For 243 of them the KnotInfo diagram has Wirtinger
number 4 and there is a representation as above over F_3 (67 knots, Sp(4,3)), F_5 (161, Sp(4,5))
or F_5 with reflections (15, O(4,5)), so b = mu = 4 and the conjecture holds for them.  The other
293 (data/bridge13_open.json) stay open: exhaustive searches found no such representation with
transvections of Sp(4,q), q in {3, 4, 5, 7, 8, 9, 11}, reflections of O(4,q), q in {3, 5, 7}, or
pseudo-reflections of GL(4,2) and GL(4,3) with eigenvalue 1 or -1, and no diagram of Wirtinger
number 3 was found among 300 random diagrams of each.  This is a partial
result on a finite list, not refereed; the conjecture itself stays open.

Conventions (KnotInfo PD codes): [a, b, c, d] lists the edges at a crossing counterclockwise from
the incoming under-edge a, edges are numbered 1..2n along the orientation, so c = a + 1, and the
over strand runs b -> d when d = b + 1 (mod 2n).  The Wirtinger relation is
X_c = X_b^-1 X_a X_b in that case and X_c = X_b X_a X_b^-1 otherwise; the other choice describes
the mirror image, which has the same bridge index and meridional rank.  Everything here uses the
standard library only.
"""
from __future__ import annotations

import gzip
import itertools
import json
import os
from typing import Callable, Dict, List, Optional, Sequence, Tuple

DATA = os.path.join(os.path.dirname(__file__), "data")

PD = List[List[int]]
Matrix = List[List[int]]


# --- linear algebra over F_p -----------------------------------------------------------------

def is_prime(p: int) -> bool:
    return p > 1 and all(p % d for d in range(2, int(p ** 0.5) + 1))


def rank_mod(rows: Sequence[Sequence[int]], p: int) -> int:
    A = [[x % p for x in r] for r in rows]
    if not A:
        return 0
    r = 0
    for c in range(len(A[0])):
        piv = next((i for i in range(r, len(A)) if A[i][c]), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        iv = pow(A[r][c], -1, p)
        A[r] = [x * iv % p for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[r])]
        r += 1
    return r


def mat_mul(X: Matrix, Y: Matrix, p: int) -> Matrix:
    n = len(X)
    return [[sum(X[i][k] * Y[k][j] for k in range(n)) % p for j in range(n)] for i in range(n)]


def mat_inv(X: Matrix, p: int) -> Matrix:
    n = len(X)
    A = [[x % p for x in r] + [int(i == j) for j in range(n)] for i, r in enumerate(X)]
    for c in range(n):
        piv = next((i for i in range(c, n) if A[i][c]), None)
        if piv is None:
            raise ValueError("singular matrix")
        A[c], A[piv] = A[piv], A[c]
        iv = pow(A[c][c], -1, p)
        A[c] = [x * iv % p for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[c])]
    return [r[n:] for r in A]


def transvection(v: Sequence[int], form: Callable[[Sequence[int], Sequence[int]], int], p: int) -> Matrix:
    """The matrix of x -> x + form(x, v) v (column j is the image of e_j)."""
    n = len(v)
    M = [[0] * n for _ in range(n)]
    for j in range(n):
        e = [int(k == j) for k in range(n)]
        c = form(e, v) % p
        for i in range(n):
            M[i][j] = (e[i] + c * v[i]) % p
    return M


def reflection(v: Sequence[int], gram: Matrix, p: int) -> Matrix:
    """The matrix of x -> x - 2 B(x, v)/B(v, v) v for the symmetric form B with Gram matrix gram."""
    n = len(v)
    B = lambda x, y: sum(x[i] * gram[i][j] * y[j] for i in range(n) for j in range(n)) % p
    iq = pow(B(v, v), -1, p)
    M = [[0] * n for _ in range(n)]
    for j in range(n):
        e = [int(k == j) for k in range(n)]
        c = 2 * B(e, v) * iq % p
        for i in range(n):
            M[i][j] = (e[i] - c * v[i]) % p
    return M


def meridional_rank_lower_bound(mats: Sequence[Matrix], p: int) -> int:
    """n - dim of the common fixed space of the given pseudo-reflections (the lemma above).

    The matrices are the images of the meridians (one per arc); each must fix a hyperplane."""
    n = len(mats[0])
    stack = []
    for M in mats:
        D = [[(M[i][j] - int(i == j)) % p for j in range(n)] for i in range(n)]
        if rank_mod(D, p) != 1:
            raise ValueError("not a pseudo-reflection")
        stack += D
    return rank_mod(stack, p)


# --- diagrams --------------------------------------------------------------------------------

def check_pd(pd: PD) -> Optional[str]:
    n2 = 2 * len(pd)
    if sorted(e for c in pd for e in c) != sorted(list(range(1, n2 + 1)) * 2):
        return "each edge 1..2n must occur exactly twice"
    for a, b, c, d in pd:
        if c != a % n2 + 1:
            return f"under strand not consecutive at {[a, b, c, d]}"
        if not (d == b % n2 + 1 or b == d % n2 + 1):
            return f"over strand not consecutive at {[a, b, c, d]}"
    return None


def arcs(pd: PD) -> List[List[int]]:
    """The arcs as lists of edges, by walking the knot: an arc ends at the edge that runs under."""
    n2 = 2 * len(pd)
    ends_under = {c[0] for c in pd}
    e = pd[0][2]
    out, cur = [], []
    for _ in range(n2):
        cur.append(e)
        if e in ends_under:
            out.append(cur)
            cur = []
        e = e % n2 + 1
    if cur:
        out[0] = cur + out[0]
    return out


def crossing_arcs(pd: PD) -> Tuple[int, List[Tuple[int, int, int, int]]]:
    """(number of arcs, [(over, under in, under out, eps)]) with eps = +1 when the over strand
    runs d -> b, so that the colour of the outgoing arc is t_{v_over}^{eps}(v_in)."""
    n2 = 2 * len(pd)
    A = arcs(pd)
    of = {e: i for i, arc in enumerate(A) for e in arc}
    cr = [(of[b], of[a], of[c], 1 if b == d % n2 + 1 else -1) for a, b, c, d in pd]
    return len(A), cr


def wirtinger_closure(pd: PD, seeds: Sequence[int]) -> set:
    """The arcs coloured from the seed arcs (given as arc indices) by the colouring move."""
    _, cr = crossing_arcs(pd)
    coloured = set(seeds)
    changed = True
    while changed:
        changed = False
        for o, u, v, _ in cr:
            if o in coloured and (u in coloured) != (v in coloured):
                coloured |= {u, v}
                changed = True
    return coloured


def wirtinger_seeds(pd: PD, k: int) -> Optional[Tuple[int, ...]]:
    """k arcs from which the colouring move reaches every arc, if there are any, else None.
    So the Wirtinger number of the diagram is at most k exactly when this is not None."""
    n, _ = crossing_arcs(pd)
    for s in itertools.combinations(range(n), k):
        if len(wirtinger_closure(pd, s)) == n:
            return s
    return None


# --- certificates ----------------------------------------------------------------------------

def check_certificate(cert: Dict) -> Optional[str]:
    """None if the certificate proves bridge index = meridional rank = 4, else the reason it fails.

    cert has the format of https://github.com/creelie/conjecture-to-choose: name, pd, field (a
    prime p), matrices (one 4x4 matrix over F_p per edge 1..2n) and wirtinger_seeds (four edges)."""
    pd, p, mats = cert["pd"], cert["field"], cert["matrices"]
    if not is_prime(p):
        return "field size must be prime"
    err = check_pd(pd)
    if err:
        return err
    n2 = 2 * len(pd)
    if len(mats) != n2:
        return "one matrix per edge is needed"
    M = {e: [[x % p for x in r] for r in mats[e - 1]] for e in range(1, n2 + 1)}
    if any(len(X) != 4 or any(len(r) != 4 for r in X) for X in M.values()):
        return "the matrices must be 4 x 4"
    A = arcs(pd)
    if any(M[e] != M[arc[0]] for arc in A for e in arc):
        return "matrix not constant along an arc"
    for a, b, c, d in pd:
        O = M[b]
        try:
            Oi = mat_inv(O, p)
        except ValueError:
            return "a matrix is singular"
        lhs = mat_mul(mat_mul(Oi, M[a], p), O, p) if d == b % n2 + 1 else mat_mul(mat_mul(O, M[a], p), Oi, p)
        if lhs != M[c]:
            return f"Wirtinger relation fails at {[a, b, c, d]}"
    try:
        if meridional_rank_lower_bound([M[arc[0]] for arc in A], p) != 4:
            return "the common fixed space is not zero"
    except ValueError:
        return "an arc matrix is not a pseudo-reflection"
    of = {e: i for i, arc in enumerate(A) for e in arc}
    seeds = {of[e] for e in cert["wirtinger_seeds"] if e in of}
    if len(seeds) != 4 or len(cert["wirtinger_seeds"]) != 4:
        return "the seeds must lie on four distinct arcs"
    if len(wirtinger_closure(pd, sorted(seeds))) != len(A):
        return "the seed colouring does not reach every arc"
    return None


PAIRS = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]


def search_sp4(pd: PD, p: int, seeds: Optional[Sequence[int]] = None) -> Optional[Dict]:
    """A certificate over Sp(4, p), meridians to transvections, or None if there is none.

    The search is complete for the given seed arcs (the first set of four found by
    ``wirtinger_seeds`` by default): the seed colours are the standard basis and the symplectic
    form runs over every nondegenerate Gram matrix W (p^6 cases, Pfaffian nonzero); the colours of
    the other arcs follow from the colouring moves, and the colouring is kept when every crossing
    agrees up to sign.  The certificate is returned as matrices and should be checked with
    ``check_certificate``, which shares nothing with this search but the arcs."""
    n, cr = crossing_arcs(pd)
    if seeds is None:
        seeds = wirtinger_seeds(pd, 4)
    if seeds is None:
        return None
    known, steps, changed = set(seeds), [], True
    while changed:
        changed = False
        for o, u, v, e in cr:
            if o in known and u in known and v not in known:
                steps.append((v, o, u, e)); known.add(v); changed = True
            elif o in known and v in known and u not in known:
                steps.append((u, o, v, -e)); known.add(u); changed = True
    if len(known) != n:
        return None
    for W in itertools.product(range(p), repeat=6):
        if (W[0] * W[5] - W[1] * W[4] + W[2] * W[3]) % p == 0:
            continue
        form = lambda x, y, W=W: sum(w * (x[i] * y[j] - x[j] * y[i]) for w, (i, j) in zip(W, PAIRS)) % p
        col: List[Optional[List[int]]] = [None] * n
        for i, s in enumerate(seeds):
            col[s] = [int(k == i) for k in range(4)]
        for t, o, src, e in steps:
            c = e * form(col[src], col[o])
            col[t] = [(x + c * y) % p for x, y in zip(col[src], col[o])]
        ok = True
        for o, u, v, e in cr:
            c = e * form(col[u], col[o])
            w = [(x + c * y) % p for x, y in zip(col[u], col[o])]
            if w != col[v] and w != [(-x) % p for x in col[v]]:
                ok = False
                break
        if ok:
            A = arcs(pd)
            per = [transvection(col[i], form, p) for i in range(n)]
            mats = [None] * (2 * len(pd))
            for i, arc in enumerate(A):
                for e in arc:
                    mats[e - 1] = per[i]
            return {"pd": pd, "field": p, "group": f"Sp(4,{p}) transvections", "gram": list(W),
                    "matrices": mats, "wirtinger_seeds": [A[s][0] for s in seeds]}
    return None


def certificates() -> List[Dict]:
    """The 243 certificates for 13-crossing knots (bridge index 4 = meridional rank)."""
    with gzip.open(os.path.join(DATA, "bridge13_certificates.json.gz"), "rt", encoding="utf-8") as f:
        return json.load(f)


def still_open() -> List[str]:
    """The 293 knots with 13 crossings whose KnotInfo bridge index [3,4] these methods leave open."""
    with open(os.path.join(DATA, "bridge13_open.json"), encoding="utf-8") as f:
        return json.load(f)
