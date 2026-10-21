"""An explicit point where the Prym map of etale triple covers of genus-four curves is etale.

The curve is B_lambda : x^3 + y^3 + 1 + lambda x^3 y^3 = 0 in P^1 x P^1, of bidegree (3, 3) and
genus 4, smooth for lambda not in {0, 1}, with eta = O(1, -1)|_B of order three
(div(y^3 + 1/lambda) = 3 F_x - 3 F_y).  Then H^0(K + eta) = <1, x, x^2>, H^0(K - eta) = <1, y, y^2>
and H^0(2K) = H^0(O(2, 2)|_B), of dimension 3g - 3 = 9.  The codifferential of the Prym map of
the etale cyclic triple cover given by eta is the multiplication map

    H^0(K + eta) (x) H^0(K - eta) -> H^0(2K),

and it sends x^i (x) y^j to the restriction of x^i y^j.  No form of bidegree (2, 2) vanishes on a
curve of bidegree (3, 3), so the nine products are independent and the map is an isomorphism: the
period map is a local isomorphism onto the nine-dimensional domain of abelian sixfolds of Weil type
for Q(sqrt -3) at n = 3.  This is the statement of Faber (1988) for a general triple cover, here at
an explicit curve (fermat-hodge-, Proposition VI.40).

``check`` certifies the independence by evaluating the nine products at points of B over a prime
field and computing the rank there: independence modulo p implies independence over Q.
``refute`` runs the same test on the products x^i x^j, which is what the map would be if eta were
replaced by K + eta on both sides; they span only five functions, so the test can fail.
Nothing here bears on (F2) or (F3'): the sixfolds reached are those of Weil type for one field.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple


def points(lam: int, p: int) -> List[Tuple[int, int]]:
    """The affine points of B_lambda over F_p."""
    out = []
    for x in range(p):
        for y in range(p):
            if (x ** 3 + y ** 3 + 1 + lam * x ** 3 * y ** 3) % p == 0:
                out.append((x, y))
    return out


def rank_mod_p(rows: Sequence[Sequence[int]], p: int) -> int:
    m = [list(r) for r in rows]
    rank = 0
    cols = len(m[0]) if m else 0
    for c in range(cols):
        piv = next((i for i in range(rank, len(m)) if m[i][c] % p), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        inv = pow(m[rank][c], p - 2, p)
        m[rank] = [v * inv % p for v in m[rank]]
        for i in range(len(m)):
            if i != rank and m[i][c] % p:
                f = m[i][c]
                m[i] = [(a - f * b) % p for a, b in zip(m[i], m[rank])]
        rank += 1
    return rank


def product_rank(lam: int, p: int, pairs: Sequence[Tuple[Tuple[int, int], Tuple[int, int]]]) -> int:
    """Rank over F_p of the products x^a y^b x^c y^d, one column for each pair, on B_lambda."""
    pts = points(lam, p)
    rows = [[pow(x, a + c, p) * pow(y, b + d, p) % p for (a, b), (c, d) in pairs] for x, y in pts]
    return rank_mod_p(rows, p)


def weil_pairs() -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    return [((i, 0), (0, j)) for i in range(3) for j in range(3)]


def check(lam: int = 2, p: int = 101) -> Dict[str, object]:
    assert lam % p not in (0, 1)
    r = product_rank(lam, p, weil_pairs())
    return {"lambda": lam, "p": p, "points": len(points(lam, p)), "rank": r, "isomorphism": r == 9}


def refute(lam: int = 2, p: int = 101) -> Dict[str, object]:
    pairs = [((i, 0), (j, 0)) for i in range(3) for j in range(3)]
    r = product_rank(lam, p, pairs)
    return {"rank": r, "isomorphism": r == 9}
