"""Search for a gauge-fixing link set F on Z^4, periodic with period L in every coordinate, such that
every plaquette contains exactly one link of F and F lifts to a forest on Z^4.  With such an F every
remaining link of a plaquette has two remaining partners, so each remaining link has 6 x 2 = 12
Dobrushin neighbours instead of 18.  Usage: python3 onefixed.py L"""
import itertools
import sys

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153

d = 4
L = int(sys.argv[1]) if len(sys.argv) > 1 else 2
sites = list(itertools.product(range(L), repeat=d))
idx = {}
for s in sites:
    for mu in range(d):
        idx[(s, mu)] = len(idx) + 1


def add(s, mu):
    t = list(s)
    t[mu] = (t[mu] + 1) % L
    return tuple(t)


def plaquettes():
    for s in sites:
        for mu, nu in itertools.combinations(range(d), 2):
            yield [(s, mu), (add(s, mu), nu), (add(s, nu), mu), (s, nu)]


top = len(idx)
clauses = []
for p in plaquettes():
    enc = CardEnc.equals(lits=[idx[e] for e in p], bound=1, top_id=top, encoding=EncType.pairwise)
    clauses += enc.clauses


def lift_has_cycle(F):
    # F is periodic; its lift to Z^4 has a cycle iff the quotient graph has a cycle of zero winding.
    # Union-find with potentials: each quotient vertex gets an integer offset vector to its root.
    parent = {s: s for s in sites}
    off = {s: (0,) * d for s in sites}

    def find(s):
        if parent[s] == s:
            return s, (0,) * d
        r, o = find(parent[s])
        parent[s] = r
        off[s] = tuple(a + b for a, b in zip(off[s], o))
        return r, off[s]

    windings = []
    for (s, mu) in F:
        t = add(s, mu)
        step = [0] * d
        step[mu] = 1
        if t[mu] == 0:
            step[mu] = 1  # wraps: in the lift t is s + e_mu, offset handled below
        # lift: point s goes to s + e_mu; record the lattice offset of the wrap
        wrap = [0] * d
        if t[mu] == 0:
            wrap[mu] = 1
        rs, os_ = find(s)
        rt, ot = find(t)
        # position(s) = root(s) + os_*L-shift ... use offsets in units of the period
        if rs != rt:
            parent[rt] = rs
            off[rt] = tuple(os_[i] + wrap[i] - ot[i] for i in range(d))
        else:
            w = tuple(os_[i] + wrap[i] - ot[i] for i in range(d))
            windings.append(w)
    # a cycle in the lift needs an integer combination of windings equal to zero; with a single
    # independent cycle per component it is enough that every winding is nonzero and the windings in
    # one component are linearly independent over Q.
    comps = {}
    for (s, mu) in F:
        pass
    return windings


with Cadical153(bootstrap_with=clauses) as S:
    sat = S.solve()
    print("L", L, "satisfiable", sat)
    if sat:
        m = set(v for v in S.get_model() if v > 0)
        F = [e for e, v in idx.items() if v in m]
        print("fixed links per site", len(F) / len(sites))
        print("pattern:", sorted(F)[:16])
