"""Level colourings of 2^[n] from m-sequences, and lower bounds for their monochromatic sublattices.

The colour of S is s[|S| + offset], s the m-sequence of a primitive polynomial of degree p.  By the
weighted-poset lemma (levelmono.py) a weighted poset (P, w, t) whose down-set ranks t + w(I) all lie
in one colour class gives a monochromatic sublattice with |J(P)| members.  Two families are searched:
  cube:  P an antichain, weights w_1 <= ... <= w_k (repetition allowed): 2^k members;
  rect:  P two disjoint chains, rank sets A, B containing 0, A + B in the class minus t: |A||B|.
"""
import sys, random

PRIM = {4: [1, 0], 5: [2, 0], 6: [1, 0], 7: [1, 0], 8: [4, 3, 2, 0], 9: [4, 0], 10: [3, 0],
        11: [2, 0], 12: [6, 4, 1, 0], 13: [4, 3, 1, 0], 14: [10, 6, 1, 0]}


def mseq(p, length):
    taps = PRIM[p]                      # x^p + sum x^j, j in taps
    s = [1] + [0] * (p - 1)
    while len(s) < length:
        i = len(s) - p
        s.append(sum(s[i + j] for j in taps) & 1)
    return s[:length]


def masks(word):
    n = len(word) - 1
    m = [0, 0]
    for i, b in enumerate(word):
        m[b] |= 1 << i
    return n, m


def best_cube(word):
    """Largest k with t + (subset sums of w_1..w_k) inside one colour class and t + sum w <= n."""
    n, m = masks(word)
    full = (1 << (n + 1)) - 1
    best = [0, None]

    def dfs(S, k, wmin, top, c, gens):
        if k > best[0]:
            best[0] = k; best[1] = (c, gens)
        for w in range(wmin, n - top + 1):
            S2 = S | (S << w)
            if S2 & ~m[c] & full == 0 and S2 <= full:
                dfs(S2, k + 1, w, top + w, c, gens + [w])

    for c in (0, 1):
        for t in range(n + 1):
            if m[c] >> t & 1:
                dfs(1 << t, 0, 1, t, c, [t])
    return best


def best_rect(word, restarts=200, seed=0):
    """Greedy and randomised search for A, B containing 0 with t + A + B in one class; max |A||B|."""
    n, m = masks(word)
    rng = random.Random(seed)
    best = (0, None)
    for c in (0, 1):
        for t in range(n + 1):
            if not m[c] >> t & 1:
                continue
            L = m[c] >> t                    # bit x: t + x in class c
            room = n - t
            for r in range(max(1, restarts // (n + 1)) + 1):
                A = [0]
                B = L & ((1 << (room + 1)) - 1)   # B = {b : t + b in class}, a = 0
                maxa = 0
                while True:
                    prod = len(A) * bin(B).count("1")
                    if prod > best[0]:
                        best = (prod, (c, t, list(A), [i for i in range(room + 1) if B >> i & 1]))
                    cands = []
                    for a in range(maxa + 1, room + 1):
                        Bn = B & (L >> a) & ((1 << (room - a + 1)) - 1)
                        cnt = bin(Bn).count("1")
                        if cnt and (len(A) + 1) * cnt > 0:
                            cands.append(((len(A) + 1) * cnt, a, Bn))
                    if not cands:
                        break
                    cands.sort(reverse=True)
                    pick = cands[0] if r == 0 else cands[min(len(cands) - 1, int(rng.expovariate(0.7)))]
                    _, a, B = pick
                    A.append(a); maxa = a
    return best


if __name__ == "__main__":
    for p in map(int, sys.argv[1:]):
        n = 2 ** p - 2
        s = mseq(p, 2 * (n + 1))
        res = []
        for off in range(0, 2 ** p - 1, max(1, (2 ** p - 1) // 8)):
            word = s[off:off + n + 1]
            k, cw = best_cube(word)
            rp, rw = best_rect(word, restarts=0)
            ones = sum(word)
            res.append((off, k, 2 ** k, rp, max(ones, n + 1 - ones)))
            print(f"p={p} n={n} offset={off}: cube dim {k} ({2**k} members), rectangle {rp}, chain {max(ones, n+1-ones)}, n/2+1={n//2+1}", flush=True)
