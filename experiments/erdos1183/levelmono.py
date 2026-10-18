"""Largest monochromatic sublattice of a level colouring of 2^[n], by weighted posets.

Lemma.  Let the colour of S depend only on |S|, with colour classes L_0, L_1 of {0, ..., n}.  A
monochromatic sublattice of colour c with N members exists iff there are a finite poset P, weights
w: P -> {1, 2, ...} and t >= 0 with t + w(P) <= n, |J(P)| = N (J(P) the down-sets), and
t + w(I) in L_c for every down-set I.
Proof.  A sublattice D of 2^[n] is a finite distributive lattice, so D = J(P) for the poset P of its
join-irreducibles, and |.| restricted to D is a strictly increasing modular function, hence equal
to t + w(I) with t = |min D| and w(p) = |p| - |p_*| > 0 for p_* the lower cover of p.  Conversely,
given (P, w, t), assign to each p a block B_p of w(p) new elements and let T be t further elements;
I -> T u (union of B_p over p in I) is a lattice embedding of J(P) into 2^[n] with |image of I| =
t + w(I).

Search.  Elements are added in a linear extension ordered by the rank w(down-set of p), which is
nondecreasing along any linear extension sorted that way; each new element p has as strict
down-set some down-set D already present, and creates the down-sets I u {p} for I containing D.
The search answers whether N >= s is reachable.  Usage: python3 levelmono.py PATTERN s
"""
import sys
from functools import lru_cache


def reachable(Lc, n, s, t):
    """Is there (P, w) with base t, all down-set ranks t + w(I) in Lc, t + w(P) <= n and >= s down-sets?"""
    if t not in Lc:
        return False
    best = [1]

    def dfs(downs, last_rank, last_key):
        # downs: tuple of (mask, rank) for the down-sets so far, rank = w(I)
        if len(downs) >= s:
            return True
        k = max(m for m, _ in downs).bit_length()   # index of the next element
        j = 1 << k
        for di, (D, rD) in enumerate(downs):
            sup = [(m, r) for m, r in downs if m & D == D]
            top = max(r for _, r in sup)
            for w in range(1, n - t - top + 1):
                rp = rD + w
                if rp < last_rank or (rp == last_rank and di < last_key):
                    continue
                new = [(m | j, r + w) for m, r in sup]
                if all(t + r in Lc for _, r in new):
                    if dfs(downs + tuple(new), rp, di):
                        return True
        return False

    return dfs(((0, 0),), 0, -1)


def has_mono(pattern, s):
    n = len(pattern) - 1
    for c in (0, 1):
        Lc = frozenset(i for i, b in enumerate(pattern) if b == c)
        for t in sorted(Lc):
            if reachable(Lc, n, s, t):
                return True
    return False


def maxmono(pattern, cap=None):
    n = len(pattern) - 1
    s = (n + 2) // 2
    while (cap is None or s <= cap) and has_mono(pattern, s + 1):
        s += 1
    return s


if __name__ == "__main__":
    pat = [int(c) for c in sys.argv[1]]
    print(maxmono(pat, int(sys.argv[2]) if len(sys.argv) > 2 else None))
