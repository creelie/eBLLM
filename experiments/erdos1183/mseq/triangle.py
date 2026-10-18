"""Triangle configurations in m-sequence level colourings.

s_i = Tr(beta alpha^i).  If d has Zech partner e (alpha^e = 1 + alpha^d), the ranks t + a d + b e span
the same space as t + j d, so j chains {0, d, e} and i antichain elements of weight d give a
monochromatic sublattice with 3^j 2^i members as soon as the ranks t + a d + b e (a + b <= i + j,
b <= j) lie in one colour class and t + j max(d, e) + i d <= n.  This searches that family directly.
"""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from mseq import mseq

for p in map(int, sys.argv[1:]):
    N = 2 ** p - 1
    s = mseq(p, 3 * N)
    # alpha^i as the state vector of the LFSR: use the sequence itself; Zech: find e with s_{x+e} = s_x + s_{x+d} for all x
    def zech(d):
        for e in range(1, N):
            if all(s[x + e] == (s[x] ^ s[x + d]) for x in range(p + 2)):
                return e
        return None
    Z = {d: zech(d) for d in range(1, N)}
    for off in (0, N // 3, 2 * N // 3):
        n = N - 1
        word = s[off:off + n + 1]
        best = (0, None)
        for d in range(1, n + 1):
            e = Z[d]
            if e is None:
                continue
            for t in range(n + 1):
                c = word[t]
                for j in range(0, p + 2):
                    for i in range(0, p + 2):
                        top = t + j * max(d, e) + i * d
                        if top > n:
                            break
                        ok = all(word[t + a * d + b * e] == c for b in range(j + 1) for a in range(i + j - b + 1)
                                 if t + a * d + b * e <= n) and all(t + a * d + b * e <= n
                                 for b in range(j + 1) for a in range(i + j - b + 1))
                        if not ok:
                            break
                        val = 3 ** j * 2 ** i
                        if val > best[0]:
                            best = (val, dict(c=c, t=t, d=d, e=e, chains=j, antichain=i))
        print(f"p={p} n={n} offset={off}: best triangle family {best[0]} members ({best[0]/(n+2):.2f} (n+2)), {best[1]}", flush=True)
