"""The lattice degree of a Delsarte hypersurface, and the census it lets the Fermat results close.

A Delsarte hypersurface in P^{N-1} is x^{A} = sum_i prod_j x_j^{a_ij} = 0 for an N x N exponent
matrix A with constant row sums m.  Shioda's monomial cover exhibits it as a quotient of the Fermat
hypersurface of degree e, the *lattice degree*: the exponent of the group M / L', where M is the
lattice {x in Z^N : sum x_j = 0} and L' is spanned by the differences of the rows of A.  The Hodge
conjecture descends along dominant maps, so the conjecture for the Fermat variety of degree e in
the same dimension gives it for the Delsarte hypersurface (for smooth members; H8, thm:simplextype,
with the classical Shioda reduction).

This module computes e without any dependency: e is the largest invariant factor of the
(N-1) x (N-1) integer matrix R of row differences in the coordinates of M, that is
e = |det R| / gcd(all (N-2)-minors of R).  ``census`` enumerates every shape of a Delsarte
hypersurface built from Fermat terms, chains and loops (the 29 shapes of H8 in six variables), for
each degree m, and classifies the fourfolds by which Fermat result closes them:

    published     e <= 20 (Shioda 1979), e prime (Shioda), e coprime to 6 with e <= 100 and e in
                  {21, 27} (da Silva 2021, published): unconditional, and in substance a corollary
                  of Shioda's reduction, so recorded as closed instances, not as new theorems;
    jumagulov     e odd <= 199 otherwise: conditional on the machine census of Jumagulov
                  (arXiv 2608.18134, Lean certificates, unrefereed);
    open          every other e.

Nothing here is new mathematics; it is the bookkeeping that turns two published theorems and one
preprint into an explicit list of fourfolds with a closed Hodge conjecture, with the degree that
closes each one.
"""
from __future__ import annotations

import math
from fractions import Fraction
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Tuple


def kinds(total: int) -> List[Tuple[str, int]]:
    return [("F", 1)] + [(t, k) for k in range(2, total + 1) for t in "CL"]


def multisets(total: int, ks: Sequence[Tuple[str, int]], start: int = 0) -> Iterable[List[Tuple[str, int]]]:
    if total == 0:
        yield []
        return
    for i in range(start, len(ks)):
        t, k = ks[i]
        if k <= total:
            for rest in multisets(total - k, ks, i):
                yield [ks[i]] + rest


def shape_matrix(shape: Sequence[Tuple[str, int]], m: int) -> List[List[int]]:
    """The exponent matrix of a sum of Fermat terms x^m, chains x_1^{m-1} x_2 + ... + x_k^m and
    loops x_1^{m-1} x_2 + ... + x_k^{m-1} x_1."""
    nv = sum(k for _, k in shape)
    rows = []
    pos = 0
    for t, k in shape:
        v = list(range(pos, pos + k))
        pos += k
        if t == "F":
            rows.append({v[0]: m})
        elif t == "C":
            for a in range(k - 1):
                rows.append({v[a]: m - 1, v[a + 1]: 1})
            rows.append({v[-1]: m})
        else:
            for a in range(k):
                rows.append({v[a]: m - 1, v[(a + 1) % k]: 1})
    return [[r.get(j, 0) for j in range(nv)] for r in rows]


def name(shape: Sequence[Tuple[str, int]]) -> str:
    return "".join(t + str(k) for t, k in shape)


def det(M: Sequence[Sequence[int]]) -> int:
    """Exact integer determinant by fraction-free elimination."""
    n = len(M)
    a = [list(map(Fraction, row)) for row in M]
    d = Fraction(1)
    for i in range(n):
        p = next((r for r in range(i, n) if a[r][i] != 0), None)
        if p is None:
            return 0
        if p != i:
            a[i], a[p] = a[p], a[i]
            d = -d
        d *= a[i][i]
        for r in range(i + 1, n):
            f = a[r][i] / a[i][i]
            if f:
                a[r] = [x - f * y for x, y in zip(a[r], a[i])]
    assert d.denominator == 1
    return int(d)


def lattice_degree(A: Sequence[Sequence[int]]) -> Tuple[int, int]:
    """(e, index): the exponent and the order of M / L' for the exponent matrix A.
    R is the matrix of row differences A_i - A_0 in the coordinates (entries 1..N-1) of M."""
    N = len(A)
    R = [[A[i][j] - A[0][j] for j in range(1, N)] for i in range(1, N)]
    n = N - 1
    index = abs(det(R))
    if index == 0:
        raise ValueError("the rows of A are affinely dependent")
    g = 0
    for rows in combinations(range(n), n - 1):
        for cols in combinations(range(n), n - 1):
            g = math.gcd(g, abs(det([[R[r][c] for c in cols] for r in rows])))
            if g == 1:
                return index, index
    return index // g, index


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % p for p in range(2, int(n ** 0.5) + 1))


def closed_by(e: int) -> str:
    """Which Fermat result settles the Hodge conjecture for the Fermat fourfold of degree e."""
    if e <= 20 or is_prime(e) or (math.gcd(e, 6) == 1 and e <= 100) or e in (21, 27):
        return "published"
    if e % 2 == 1 and e <= 199:
        return "jumagulov"
    return "open"


def census(degrees: Iterable[int], variables: int = 6) -> List[Dict]:
    """Every shape in the given number of variables, for each degree, with its lattice degree and
    the Fermat result that closes it (fourfolds for six variables)."""
    out = []
    shapes = list(multisets(variables, kinds(variables)))
    for m in degrees:
        for sh in shapes:
            A = shape_matrix(sh, m)
            e, index = lattice_degree(A)
            out.append(dict(degree=m, shape=name(sh), e=e, index=index, closed_by=closed_by(e),
                            fermat=all(t == "F" for t, _ in sh)))
    return out


def summary(rows: Sequence[Dict]) -> Dict[str, int]:
    out = {"shapes": len(rows), "published": 0, "jumagulov": 0, "open": 0, "non_fermat_closed": 0}
    for r in rows:
        out[r["closed_by"]] += 1
        if not r["fermat"] and r["closed_by"] != "open":
            out["non_fermat_closed"] += 1
    return out
