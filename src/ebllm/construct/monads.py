"""Positive monad bundles on the cyclic CICY threefolds (h^{1,1} = 1): the strings attack off the
standard embedding.

A positive monad is 0 -> V -> B -> C -> 0 with B = sum O(b_i), C = sum O(c_j), 1 <= b_i < c_j, and
rank V = |B| - |C| in {3, 4, 5} (Anderson, He, Lukas, hep-th/0702210, 0805.2875). With d = J^3:

    c1(V)    = sum b - sum c                      (must be 0)
    c2(V).J  = d (sum c^2 - sum b^2) / 2          (anomaly: c2(TX).J - c2(V).J >= 0)
    ind(V)   = d (sum b^3 - sum c^3) / 6          (net families = -ind; three on X/G needs ind = -3|G|)

Everything here is exact integer arithmetic. ``heisenberg_ok`` is the necessary condition for the
monad to carry a Z5 x Z5 equivariant structure on a quintic invariant under the Heisenberg group of
order 125 (the Dwork pencil is such a quintic): the centre acts on sections of O(k) by w^k, so every
O(k) with 5 not dividing k must occur with multiplicity divisible by 5 (tensor it with the
five-dimensional Schrodinger representation of the opposite central character).

What the scan settles, in agreement with the literature (Braun 0909.5682; Anderson, Gray, He, Lukas
0911.1569): on free quotients of the quintic, the positive monads with three net families are exactly
two, O(1)^6 -> O(2)^3 on X/Z5 (rank 3, E6) and O(1)^5 + O(2)^5 -> O(3)^5 on X/(Z5 x Z5) (rank 5,
SU(5), anomaly saturated). The second lives on the Dwork pencil itself, so it bypasses Prop.
dworkselect (ii) of creelie/strings at (C1)-(C2); but Z5 x Z5 Wilson lines cannot break SU(5) to the
Standard Model group, so (C3) fails, and positive two-term monads on CICYs are ruled out
phenomenologically (0911.1569). Label: proved for (C1)-(C2) modulo stability as cited; dead end at (C3).
"""
from itertools import combinations_with_replacement as _cwr
from collections import Counter
from typing import Dict, List, Sequence, Tuple

# name: (J^3, c2(TX).J, Euler number, orders of freely acting groups known in the literature)
CICY: Dict[str, Tuple[int, int, int, Tuple[int, ...]]] = {
    "P4[5]": (5, 50, -200, (1, 5, 25)),
    "P5[3,3]": (9, 54, -144, (1, 3, 9)),
    "P5[2,4]": (8, 56, -176, (1, 2, 4, 8)),
    "P6[3,2,2]": (12, 60, -144, (1, 2, 3, 4, 6, 8, 12)),
    "P7[2,2,2,2]": (16, 64, -128, (1, 2, 4, 8, 16, 32)),
}


def invariants(X: str, b: Sequence[int], c: Sequence[int]) -> Dict[str, int]:
    d, c2TX, _, _ = CICY[X]
    c2V2 = d * (sum(x * x for x in c) - sum(x * x for x in b))
    ind6 = d * (sum(x ** 3 for x in b) - sum(x ** 3 for x in c))
    if c2V2 % 2 or ind6 % 6:
        raise ValueError("non-integral characteristic class: not a vector bundle on X")
    return {"c1": sum(b) - sum(c), "c2V": c2V2 // 2, "anomaly_slack": c2TX - c2V2 // 2,
            "index": ind6 // 6, "rank": len(b) - len(c)}


def check(X: str, b: Sequence[int], c: Sequence[int]) -> List[str]:
    """Reasons the monad fails (C1); empty list means it passes c1 = 0, anomaly, positivity, rank."""
    why = []
    if not b or not c:
        why.append("empty B or C")
        return why
    if min(b) < 1:
        why.append("b_i < 1: not positive")
    if max(b) >= min(c):
        why.append("some b_i >= c_j: the map has a zero entry, stability is not covered")
    try:
        inv = invariants(X, b, c)
    except ValueError as e:
        return why + [str(e)]
    if inv["c1"] != 0:
        why.append(f"c1 = {inv['c1']} != 0")
    if inv["anomaly_slack"] < 0:
        why.append(f"anomaly: c2(V).J exceeds c2(TX).J by {-inv['anomaly_slack']}")
    if not 3 <= inv["rank"] <= 5:
        why.append(f"rank {inv['rank']} not in 3..5")
    return why


def heisenberg_ok(b: Sequence[int], c: Sequence[int], n: int = 5) -> bool:
    """Necessary condition for a Z_n x Z_n (Heisenberg) equivariant structure on the quintic."""
    return all(m % n == 0 for k, m in (Counter(b) + Counter(c)).items() if k % n)


def scan(X: str, max_rc: int = 6, max_c: int = 12) -> List[dict]:
    """Every positive monad on X passing ``check``, with its three-family groups."""
    groups = CICY[X][3]
    out = []
    for rc in range(1, max_rc + 1):
        for n in (3, 4, 5):
            rb = rc + n
            for c in _cwr(range(2, max_c), rc):
                if sum(c) < rb:
                    continue
                for b in _cwr(range(1, min(c)), rb):
                    if sum(b) != sum(c) or check(X, b, c):
                        continue
                    inv = invariants(X, b, c)
                    three = [g for g in groups if inv["index"] == -3 * g]
                    out.append({"X": X, "B": b, "C": c, **inv, "three_family_groups": three})
    return out


def three_family_quintic() -> List[dict]:
    """The positive monads giving three net families on a free quotient of the quintic, with the
    equivariance screen (Z5 acting by a cyclic permutation linearises every O(k); Z5 x Z5 needs
    ``heisenberg_ok``)."""
    rows = []
    for r in scan("P4[5]"):
        for g in r["three_family_groups"]:
            if g == 1:
                continue
            ok = True if g == 5 else heisenberg_ok(r["B"], r["C"])
            rows.append({**r, "group_order": g, "equivariant_screen": ok})
    return rows


def refute(X: str, b: Sequence[int], c: Sequence[int], group_order: int) -> List[str]:
    """Refuter for a claimed three-family positive-monad vacuum on X/G: every reason it is not one."""
    why = check(X, b, c)
    if not why:
        if invariants(X, b, c)["index"] != -3 * group_order:
            why.append("index is not -3|G|: not three net families")
        if X == "P4[5]" and group_order == 25 and not heisenberg_ok(b, c):
            why.append("no Z5 x Z5 equivariant structure (Heisenberg multiplicities)")
    return why
