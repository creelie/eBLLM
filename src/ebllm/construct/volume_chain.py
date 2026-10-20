"""The volume-chain bound: the pair-chain bound with the normalised volumes added as further keys.

If Q is a reflexive polytope strictly inside a reflexive P, then conv(Q) is strictly inside conv(P),
so the normalised volume of Q is strictly smaller than that of P, and the volume of the dual Q* is
strictly larger than that of P*. Along a reflexive descent the quadruple

    (|P|, |P*|, vol P, vol P*)

therefore falls strictly in the first and third entries and rises strictly in the second and fourth.
The longest chain of realised quadruples bounds every descent, and it is never longer than the
longest chain of realised pairs, because forgetting keys can only lengthen chains.

The volume is new information only from dimension four on. The h*-vector of a reflexive polytope is
palindromic (Hibi), so in dimension three h* = (1, h1, h1, 1) and vol P = 2|P| - 6 is fixed by the
point count, while in dimension four h* = (1, h1, h2, h1, 1) with |P| = 5 + h1, |2P| = 15 + 5 h1 + h2,
and

    vol P = 2 + 2 h1 + h2 = |2P| - 3|P| + 2,

which depends on h2. So the volume key can separate polytopes that the pair bound cannot.

``chain_bound3`` finds the longest chain in three keys by divide and conquer over the first key with a
Fenwick tree over the third (O(n log^2 n)); ``chain_bound_brute`` is the quadratic reference used by the
tests and for any number of keys.
"""
from .reflexive import is_reflexive, lattice_points


def normalised_volume4(points):
    """4! times the Euclidean volume of a reflexive 4-polytope, from |2P| - 3|P| + 2. Pass the vertices."""
    pts = [tuple(p) for p in points]           # vertices suffice, and keep the facet search small
    if len(pts[0]) != 4 or not is_reflexive(pts):
        raise ValueError("needs a reflexive 4-polytope")
    two = lattice_points([tuple(2 * c for c in p) for p in pts])
    return len(two) - 3 * len(lattice_points(pts)) + 2


def _orient(rows, signs):
    """Turn each key into one that rises strictly along a chain: sign -1 for keys that fall."""
    return sorted(set(tuple(s * x for s, x in zip(signs, r)) for r in rows))


def chain_bound_brute(rows, signs):
    """The most steps of a chain of the rows, key i rising strictly when signs[i] = 1 and falling
    strictly when signs[i] = -1."""
    pts = _orient(rows, signs)
    best = {}
    for p in pts:
        best[p] = max((best[q] + 1 for q in best if all(a < b for a, b in zip(q, p))), default=0)
    return max(best.values(), default=0)


def chain_bound3(rows, signs=(-1, 1, -1)):
    """The longest strict chain in three keys (points falling, dual points rising, volume falling)."""
    pts = _orient(rows, signs)
    if not pts:
        return 0
    cs = sorted(set(p[2] for p in pts))
    rank = {c: i + 1 for i, c in enumerate(cs)}
    groups = []
    for p in pts:
        if groups and groups[-1][0][0] == p[0]:
            groups[-1].append(p)
        else:
            groups.append([p])
    dp = {p: 0 for p in pts}
    tree = [-1] * (len(cs) + 2)

    def upd(i, v):
        while i < len(tree):
            if tree[i] < v:
                tree[i] = v
            i += i & -i

    def qry(i):
        m = -1
        while i > 0:
            if tree[i] > m:
                m = tree[i]
            i -= i & -i
        return m

    def clear(i):
        while i < len(tree):
            tree[i] = -1
            i += i & -i

    def solve(lo, hi):
        if lo == hi:
            return
        mid = (lo + hi) // 2
        solve(lo, mid)
        left = sorted((p for g in groups[lo:mid + 1] for p in g), key=lambda p: p[1])
        right = sorted((p for g in groups[mid + 1:hi + 1] for p in g), key=lambda p: p[1])
        j = 0
        for p in right:
            while j < len(left) and left[j][1] < p[1]:
                upd(rank[left[j][2]], dp[left[j]])
                j += 1
            m = qry(rank[p[2]] - 1)
            if m >= 0 and m + 1 > dp[p]:
                dp[p] = m + 1
        for q in left[:j]:
            clear(rank[q[2]])
        solve(mid + 1, hi)

    solve(0, len(groups) - 1)
    return max(dp.values())
