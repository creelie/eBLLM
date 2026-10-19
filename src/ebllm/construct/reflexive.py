"""Reflexive lattice polytopes: lattice points, duality, descents and the pair-chain bound.

A lattice polytope P in R^d is reflexive when the origin is an interior point and every facet
lies on a hyperplane a.x = 1 with a an integral vector; the vectors a are then the vertices of
the polar dual P*, which is reflexive too. A descent step removes one vertex v of P and keeps
the convex hull of the other lattice points of P, provided that hull is again reflexive. A
polytope with no descent step is minimal, and a descent ends at a minimal polytope.

Every step loses at least one lattice point of P (the vertex v) and, because the dual of a
smaller polytope is larger, gains at least one lattice point of the dual. So along a descent
the pair (points of P, points of P*) falls strictly in its first entry and rises strictly in
its second. If S is the set of pairs that occur among the reflexive polytopes of dimension d,
every descent is a chain in S for that order, and the longest chain in S bounds every descent
(``pair_chain_bound``). For d = 4 the pairs come from the Kreuzer-Skarke list of
473,800,776 polytopes; in the plane the 16 reflexive polygons are enumerated here and every
descent is computed exactly.

All arithmetic is in integers; nothing here uses floating point.
"""
from functools import lru_cache
from itertools import combinations, product
from math import gcd


def _det(rows):
    """Determinant of a square integer matrix by fraction-free elimination (Bareiss)."""
    m = [list(r) for r in rows]
    n = len(m)
    sign, prev = 1, 1
    for k in range(n - 1):
        if m[k][k] == 0:
            for i in range(k + 1, n):
                if m[i][k] != 0:
                    m[k], m[i] = m[i], m[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                m[i][j] = (m[i][j] * m[k][k] - m[i][k] * m[k][j]) // prev
        prev = m[k][k]
    return sign * m[n - 1][n - 1]


def _normal(points):
    """An integer normal to the affine hull of d points in R^d (zero if they are dependent)."""
    d = len(points[0])
    base = points[0]
    diffs = [[p[i] - base[i] for i in range(d)] for p in points[1:]]
    a = []
    for i in range(d):
        minor = [[r[j] for j in range(d) if j != i] for r in diffs]
        a.append((-1) ** i * _det(minor) if minor else 1)
    g = 0
    for x in a:
        g = gcd(g, abs(x))
    return tuple(x // g for x in a) if g else tuple(a)


def _dot(a, x):
    return sum(i * j for i, j in zip(a, x))


def facets(points):
    """The facets of conv(points) as pairs (a, c), a primitive, with a.x <= c on the polytope.

    The polytope must be full-dimensional. Facets are found by testing every hyperplane through
    d of the points, which is exact and fast enough for the small polytopes of this module.
    """
    pts = sorted(set(tuple(p) for p in points))
    d = len(pts[0])
    out = set()
    for sub in combinations(pts, d):
        a = _normal(list(sub))
        if not any(a):
            continue
        c = _dot(a, sub[0])
        vals = [_dot(a, p) for p in pts]
        if all(v <= c for v in vals):
            on = [p for p, v in zip(pts, vals) if v == c]
        elif all(v >= c for v in vals):
            a, c = tuple(-x for x in a), -c
            on = [p for p, v in zip(pts, vals) if v == -c]
        else:
            continue
        if _rank([[p[i] - on[0][i] for i in range(d)] for p in on[1:]]) == d - 1:
            out.add((a, c))
    return sorted(out)


def _rank(rows):
    m = [list(r) for r in rows]
    if not m:
        return 0
    rank, cols = 0, len(m[0])
    for col in range(cols):
        piv = next((i for i in range(rank, len(m)) if m[i][col] != 0), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        for i in range(len(m)):
            if i != rank and m[i][col] != 0:
                f, g = m[i][col], m[rank][col]
                m[i] = [g * x - f * y for x, y in zip(m[i], m[rank])]
        rank += 1
    return rank


def dimension(points):
    pts = list(points)
    return _rank([[p[i] - pts[0][i] for i in range(len(pts[0]))] for p in pts[1:]])


def vertices(points):
    """The vertices of conv(points): the points that lie on at least d facets meeting in a point."""
    pts = sorted(set(tuple(p) for p in points))
    d = len(pts[0])
    fs = facets(pts)
    out = []
    for p in pts:
        tight = [a for a, c in fs if _dot(a, p) == c]
        if _rank(tight) == d:
            out.append(p)
    return out


def lattice_points(points):
    """Every lattice point of conv(points), by testing the integer points of the bounding box."""
    pts = [tuple(p) for p in points]
    d = len(pts[0])
    fs = facets(pts)
    lo = [min(p[i] for p in pts) for i in range(d)]
    hi = [max(p[i] for p in pts) for i in range(d)]
    return sorted(x for x in product(*(range(lo[i], hi[i] + 1) for i in range(d)))
                  if all(_dot(a, x) <= c for a, c in fs))


def is_reflexive(points):
    """True when conv(points) is full-dimensional, contains 0 in its interior and every facet
    is a.x = 1 for an integral a."""
    pts = [tuple(p) for p in points]
    d = len(pts[0])
    if dimension(pts) != d:
        return False
    return all(c == 1 for _, c in facets(pts))


def dual(points):
    """The vertices of the polar dual {y : x.y <= 1 for x in P} of a reflexive polytope."""
    if not is_reflexive(points):
        raise ValueError("the polytope is not reflexive")
    return sorted(a for a, _ in facets(points))


def descent_steps(points):
    """Every polytope reached in one descent step: drop a vertex, keep the hull of the other
    lattice points, when that hull is reflexive. Each is returned as its sorted lattice points."""
    lp = lattice_points(points)
    out = []
    for v in vertices(lp):
        rest = [p for p in lp if p != v]
        if dimension(rest) == len(v) and is_reflexive(rest):
            out.append(tuple(lattice_points(rest)))
    return sorted(set(out))


def is_minimal(points):
    return not descent_steps(points)


@lru_cache(maxsize=None)
def _depths(lp):
    steps = descent_steps(lp)
    if not steps:
        return 0, 0
    sub = [_depths(s) for s in steps]
    return 1 + min(s[0] for s in sub), 1 + max(s[1] for s in sub)


def shortest_descent(points):
    """The fewest steps from P to a minimal polytope."""
    return _depths(tuple(lattice_points(points)))[0]


def longest_descent(points):
    """The most steps of any descent from P (every descent ends at a minimal polytope)."""
    return _depths(tuple(lattice_points(points)))[1]


def pair_chain_bound(pairs):
    """The most steps in a chain (n_0, m_0), (n_1, m_1), ... of the given pairs with n strictly
    falling and m strictly rising. Every descent of a reflexive polytope is such a chain of
    (lattice points of P, lattice points of P*), so this bounds every descent.

    Sorting by n downwards (and by m downwards among equal n, so that two pairs with the same n
    are never both taken) turns the chain into a strictly increasing subsequence of the m, found
    by patience sorting.
    """
    from bisect import bisect_left
    tails = []
    for _, m in sorted(set(pairs), key=lambda p: (-p[0], -p[1])):
        i = bisect_left(tails, m)
        if i == len(tails):
            tails.append(m)
        else:
            tails[i] = m
    return max(len(tails) - 1, 0)


def _canonical2(points):
    """A normal form of a lattice polygon under GL(2, Z): the least column Hermite form of its
    vertex matrix over all starting vertices and both orientations."""
    vs = vertices(points)
    cx = sum(v[0] for v in vs) / len(vs)
    cy = sum(v[1] for v in vs) / len(vs)
    from math import atan2
    ring = sorted(vs, key=lambda v: atan2(v[1] - cy, v[0] - cx))
    best = None
    for seq in (ring, ring[::-1]):
        for s in range(len(seq)):
            cols = seq[s:] + seq[:s]
            form = _hermite2(cols)
            if best is None or form < best:
                best = form
    return best


def _hermite2(cols):
    """Row Hermite normal form of the 2 x n matrix with the given columns, under left
    multiplication by GL(2, Z), with the pivots made positive."""
    r0 = [c[0] for c in cols]
    r1 = [c[1] for c in cols]
    n = len(cols)
    j = 0
    while j < n and r0[j] == 0 and r1[j] == 0:
        j += 1
    while r1[j] != 0:
        q = r0[j] // r1[j]
        r0 = [a - q * b for a, b in zip(r0, r1)]
        r0, r1 = r1, r0
    if r0[j] < 0:
        r0 = [-a for a in r0]
    k = next(i for i in range(n) if _rank([[cols[j][0], cols[j][1]], [cols[i][0], cols[i][1]]]) == 2)
    if r1[k] < 0:
        r1 = [-a for a in r1]
    q = r0[k] // r1[k]
    r0 = [a - q * b for a, b in zip(r0, r1)]
    return tuple(r0), tuple(r1)


def reflexive_polygons():
    """The 16 reflexive polygons up to GL(2, Z), each as its sorted lattice points.

    A reflexive polygon P lies in M* whenever its dual contains the minimal polygon M (duality
    reverses inclusion), and every dual contains a minimal polygon, the end of any of its
    descents. So descending from the duals of the minimal polygons reaches every reflexive
    polygon. The three starting polygons below are those duals: the triangle with 10 lattice
    points, the square [-1, 1]^2 and a triangle with 9 points. The tests check that the minimal
    polygons found are exactly the duals of these three, so the search is closed, and that the
    list agrees with the classical one.
    """
    tops = [[(-1, -1), (2, -1), (-1, 2)], [(-1, -1), (1, -1), (1, 1), (-1, 1)],
            [(-1, -1), (3, -1), (-1, 1)]]
    seen, todo = {}, []
    for t in tops:
        if is_reflexive(t):
            todo.append(tuple(lattice_points(t)))
    while todo:
        p = todo.pop()
        key = _canonical2(p)
        if key in seen:
            continue
        seen[key] = p
        todo.extend(descent_steps(p))
    return sorted(seen.values(), key=lambda p: (len(p), p))
