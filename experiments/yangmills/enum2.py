import itertools
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153
d, L = 4, 2
sites = list(itertools.product(range(L), repeat=d))
idx = {(s, mu): i + 1 for i, (s, mu) in enumerate(itertools.product(sites, range(d)))}
def add(s, mu):
    t = list(s); t[mu] = (t[mu] + 1) % L; return tuple(t)
cl = []
top = len(idx)
for s in sites:
    for mu, nu in itertools.combinations(range(d), 2):
        p = [(s, mu), (add(s, mu), nu), (add(s, nu), mu), (s, nu)]
        cl += CardEnc.equals([idx[e] for e in p], 1, top_id=top, encoding=EncType.pairwise).clauses
sols = []
with Cadical153(bootstrap_with=cl) as S:
    while S.solve():
        m = [v for v in S.get_model() if 0 < v <= top]
        F = frozenset(e for e, v in idx.items() if v in m)
        sols.append(F)
        S.add_clause([-v for v in m])
print("solutions", len(sols))
for F in sols[:8]:
    sig = {s: mu for (s, mu) in F}
    print(" ".join("".join(map(str, s)) + ":" + str(sig.get(s, '-')) for s in sites), "per-site", all(sum(1 for (t, mu) in F if t == s) == 1 for s in sites))
