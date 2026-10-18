"""Largest monochromatic sublattice of a colouring of 2^[n] that depends only on the sizes of S inside
the blocks of a fixed partition [n] = X_1 u ... u X_k (a grid colouring; k = 1 is a level colouring).

Lemma.  Let the colour of S depend only on v(S) = (|S n X_1|, ..., |S n X_k|), with colour classes
L_0, L_1 of the grid G = prod_i {0, ..., |X_i|}.  A monochromatic sublattice of colour c with N members
exists iff there are a finite poset P, weights w: P -> N^k \\ {0} and t in G with t + w(P) in G,
|J(P)| = N and t + w(I) in L_c for every down-set I.
Proof.  v is modular on 2^[n] and |v(A)| = |A| is strictly increasing, so on a sublattice D = J(P) it is
t + w(I) with t = v(min D) and w(p) = v(p) - v(p_*), nonzero because |p| > |p_*|.  Conversely, given
(P, w, t), give each p a block B_p meeting X_i in w(p)_i new points and let T meet X_i in t_i further
points; I -> T u (union of B_p, p in I) embeds J(P) as a sublattice with v = t + w(I).

The search is the one of levelmono.py with vector weights: elements are added in nondecreasing order
of the total size of their principal down-sets.  Usage: from gridmono import has_mono, maxmono.
"""
import itertools


def _reachable(Lc, dims, s, t):
    k = len(dims)
    if t not in Lc:
        return False
    room = tuple(d - x for d, x in zip(dims, t))
    weights = [w for w in itertools.product(*[range(r + 1) for r in room]) if any(w)]
    weights.sort(key=sum)

    def add(a, b):
        return tuple(x + y for x, y in zip(a, b))

    def fits(r):
        return all(x <= d for x, d in zip(r, room))

    def dfs(downs, last_rank, last_key):
        if len(downs) >= s:
            return True
        j = 1 << max(m for m, _ in downs).bit_length()
        for di, (D, rD) in enumerate(downs):
            sup = [(m, r) for m, r in downs if m & D == D]
            for w in weights:
                rp = sum(rD) + sum(w)
                if rp < last_rank or (rp == last_rank and di < last_key):
                    continue
                new = [(m | j, add(r, w)) for m, r in sup]
                if all(fits(r) and add(t, r) in Lc for _, r in new):
                    if dfs(downs + tuple(new), rp, di):
                        return True
        return False

    return dfs(((0, (0,) * k),), 0, -1)


def has_mono(colour, dims, s):
    """colour: dict from grid points (tuples) to 0/1; dims: block sizes."""
    for c in (0, 1):
        Lc = frozenset(p for p, x in colour.items() if x == c)
        for t in sorted(Lc, key=sum):
            if _reachable(Lc, dims, s, t):
                return True
    return False


def maxmono(colour, dims, cap):
    n = sum(dims)
    s = (n + 2) // 2
    while s <= cap and has_mono(colour, dims, s + 1):
        s += 1
    return s


def from_level(word, dims):
    return {p: int(word[sum(p)]) for p in itertools.product(*[range(d + 1) for d in dims])}
