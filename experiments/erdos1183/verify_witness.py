"""Independent check of a colouring of the Boolean lattice 2^[n]: a SAT query, with no code shared
with findmono.c, asks whether either colour class contains a sublattice (a set closed under union and
intersection) with at least s members. UNSAT for both classes certifies the colouring."""
import sys
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType


def has_sublattice(cls, s):
    idx = {v: i + 1 for i, v in enumerate(cls)}
    top = len(cls)
    card = CardEnc.atleast(lits=list(idx.values()), bound=s, top_id=top, encoding=EncType.seqcounter)
    with Cadical153(bootstrap_with=card.clauses) as S:
        for a in cls:
            for b in cls:
                if a < b:
                    for c in (a | b, a & b):
                        if c in idx:
                            S.add_clause([-idx[a], -idx[b], idx[c]])
                        else:
                            S.add_clause([-idx[a], -idx[b]])
        return S.solve()


def check(n, s, red):
    pts = range(1 << n)
    R = [v for v in pts if red >> v & 1]
    B = [v for v in pts if not red >> v & 1]
    return [has_sublattice(R, s), has_sublattice(B, s)]


if __name__ == "__main__":
    n, s, red = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3], 16)
    r = check(n, s, red)
    print(f"n={n} s={s}: red class contains a sublattice of size >= {s}: {r[0]}; blue: {r[1]}")
    sys.exit(0 if not any(r) else 1)
