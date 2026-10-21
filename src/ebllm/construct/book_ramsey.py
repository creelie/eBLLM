"""Two-block circulant graphs for the book Ramsey numbers R(B_{n-1}, B_n).

The graph Gamma(A, B) lives on Z_v x {0, 1} with v = 2n - 1: inside block 0
the edges are differences in a symmetric set A, inside block 1 the nonzero
differences outside A, and (x, 0) ~ (y, 1) when y - x lies in B. For the even
shape |A| = n, |B| = n - 1 both book conditions (no B_{n-1}, complement free
of B_n) reduce to one inequality per nonzero residue d,

    N_AA(d) + N_BB(d) <= n + 1 - 3 [d in A],

where N_XX(d) = #{x in X : x + d in X}. With the Rousseau-Sheehan bound
R(B_{n-1}, B_n) <= 4n - 1 such a graph gives R(B_{n-1}, B_n) = 4n - 1.

  N58          the sets for n = 58 (creelie/Breakthrough-problems-2, data/n58.json)
  star_ok      the residue inequality
  book_ok      direct count over all pairs of vertices, sharing nothing with star_ok
"""

N58 = {
    "n": 58,
    "v": 115,
    "A": [3, 10, 11, 14, 16, 18, 21, 23, 24, 25, 26, 27, 28, 29, 30, 32, 36, 37, 38, 43, 44, 46, 47,
          48, 49, 52, 54, 55, 56, 59, 60, 61, 63, 66, 67, 68, 69, 71, 72, 77, 78, 79, 83, 85, 86, 87,
          88, 89, 90, 91, 92, 94, 97, 99, 101, 104, 105, 112],
    "B": [0, 2, 5, 6, 7, 9, 10, 11, 15, 17, 20, 21, 22, 23, 24, 26, 30, 34, 38, 43, 44, 46, 47, 50,
          52, 53, 54, 56, 59, 65, 66, 67, 69, 71, 72, 73, 74, 75, 80, 81, 83, 84, 85, 88, 90, 92, 93,
          97, 100, 102, 105, 106, 107, 109, 110, 111, 114],
}


def _auto(X, d, v):
    S = set(X)
    return sum(1 for x in S if (x + d) % v in S)


def star_ok(n, A, B):
    """The residue inequality for every nonzero d (even shape |A| = n, |B| = n - 1)."""
    v = 2 * n - 1
    S = set(A)
    if len(S) != n or len(set(B)) != n - 1 or any((-a) % v not in S for a in S) or 0 in S:
        return False
    return all(_auto(A, d, v) + _auto(B, d, v) <= n + 1 - 3 * (d in S) for d in range(1, v))


def graph(n, A, B):
    v = 2 * n - 1
    SA, SB = set(A), set(B)
    adj = [[False] * (2 * v) for _ in range(2 * v)]
    for p in range(2 * v):
        for q in range(2 * v):
            if p == q:
                continue
            (x, i), (y, j) = (p % v, p // v), (q % v, q // v)
            if i == j:
                d = (y - x) % v
                adj[p][q] = (d in SA) if i == 0 else (d != 0 and d not in SA)
            else:
                adj[p][q] = ((y - x) % v in SB) if i == 0 else ((x - y) % v in SB)
    return adj


def book_ok(n, A, B):
    """No edge in more than n - 2 triangles, no non-edge with more than n - 1 common non-neighbours."""
    adj = graph(n, A, B)
    N = len(adj)
    rows = [sum(1 << r for r in range(N) if adj[p][r]) for p in range(N)]
    full = (1 << N) - 1
    for p in range(N):
        for q in range(p + 1, N):
            if adj[p][q] != adj[q][p]:
                return False
            if adj[p][q]:
                if bin(rows[p] & rows[q]).count("1") > n - 2:
                    return False
            else:
                both = full & ~rows[p] & ~rows[q] & ~(1 << p) & ~(1 << q)
                if bin(both).count("1") > n - 1:
                    return False
    return True
