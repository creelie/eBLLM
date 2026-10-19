"""Closed chains and restricted Euler bounds for the open E_0^6 configurations of
Bhattacharjee-Bhattacharya 2026 (prop:separated and the paragraph after it).

For a configuration of pieces O_Z (x) L^k [s], L^l [t] the terms of d_E that can reach a diagonal
block Ext^2(F_a, F_a) run along closed chains a_0, ..., a_m = a_0 of distinct pieces with a nonzero
component in Ext^{k_i}(F_{a_{i-1}}, F_{a_i}), k_i = 1 + s_{a_{i-1}} - s_{a_i}, sum k_i = m.  A chain
of length m carries the A_infinity product m_m.  This script lists the chains of the least-bound
configurations of e06_count.py, their lengths and the groups they pass through, and computes the
restricted Euler bound

    dim Ext^2 >= C2_exact - (degree-1 blocks that reach some degree-2 block) - (degree-3 blocks reached
                 from some degree-2 block),

which is the Euler bound with the blocks that cannot interact removed.

    python3 e06_chains.py out.json
"""
import itertools, json, sys
from e06_count import (ZETAS, Piece, base, ext_dims, configuration_ch, bounds, zsign, zmeet)


def blocks(pieces):
    n = len(pieces)
    B = {}  # (a, b) -> {total degree: (dim, exact)}
    for a, pa in enumerate(pieces):
        for b, pb in enumerate(pieces):
            dims, exact = ext_dims(pa, pb)
            for k, dim in dims.items():
                t = k + pb.shift - pa.shift
                d, e = B.setdefault((a, b), {}).get(t, (0, True))
                B[(a, b)][t] = (d + dim, e and exact)
    return B


def closed_chains(pieces, max_len=8, start_kinds=("L", "Z")):
    """Closed chains of distinct pieces with every step of total degree one (Ext degree
    k = 1 + s_a - s_b), up to rotation; returns (length, [piece reprs], [Ext degrees])."""
    n = len(pieces)
    B = blocks(pieces)
    step = {a: [b for b in range(n) if b != a and B.get((a, b), {}).get(1, (0,))[0] > 0] for a in range(n)}
    out = []
    for a0 in range(n):
        if pieces[a0].kind not in start_kinds:
            continue
        stack = [(a0, [a0])]
        while stack:
            cur, path = stack.pop()
            for b in step[cur]:
                if b == a0 and len(path) >= 2:
                    if min(path) == a0:  # one representative per rotation
                        degs = [1 + pieces[x].shift - pieces[y].shift for x, y in zip(path, path[1:] + [a0])]
                        out.append((len(path), [repr(pieces[x]) for x in path], degs))
                elif b not in path and len(path) < max_len:
                    stack.append((b, path + [b]))
    return out


def restricted_euler(pieces):
    n = len(pieces)
    B = blocks(pieces)
    edge = [[B.get((a, b), {}).get(1, (0,))[0] > 0 and a != b for b in range(n)] for a in range(n)]
    reach = [[a == b or edge[a][b] for b in range(n)] for a in range(n)]
    for k in range(n):
        for a in range(n):
            if reach[a][k]:
                for b in range(n):
                    if reach[k][b]:
                        reach[a][b] = True
    deg = {t: [(ab, v[t]) for ab, v in B.items() if t in v] for t in (1, 2, 3)}
    c2 = sum(d for _, (d, e) in deg[2] if e)
    deg2 = [ab for ab, _ in deg[2]]
    c1 = sum(d for (a2, b2), (d, _) in deg[1]
             if any(reach[a][a2] and reach[b2][b] and (a2, b2) != (a, b) for (a, b) in deg2))
    c3 = sum(d for (a2, b2), (d, _) in deg[3]
             if any(reach[a2][a] and reach[b][b2] and (a2, b2) != (a, b) for (a, b) in deg2))
    return dict(C2_exact=c2, C1_reaching=c1, C3_reached=c3, restricted_euler=c2 - c1 - c3)


def report(name, pieces, out):
    ok, N = configuration_ch(pieces)
    b = bounds(pieces)
    r = restricted_euler(pieces)
    ch = closed_chains(pieces)
    lengths = {}
    for m, _, _ in ch:
        lengths[m] = lengths.get(m, 0) + 1
    sample = ch[:3]
    rec = dict(polarised=ok, N=N, **b, **r, chains_by_length=lengths, chain_samples=sample)
    out[name] = rec
    print(name, "polarised" if ok else "NOT polarised", "N =", N)
    print("  ", {k: rec[k] for k in ("C1", "C2", "C3", "euler", "safe", "restricted_euler")})
    print("   closed chains by length:", lengths)
    for m, p, d in sample:
        print("   chain", m, p, "degrees", d)


def main():
    out = {}
    # the least-bound configurations found by e06_count.py
    report("(a) L^1..4 at shifts -2..1", base() + [Piece("L", None, l, t) for l, t in zip((1, 2, 3, 4), (-2, -1, 0, 1))], out)
    report("(0) base35 L^1,2,3 at shifts 2,3,4", base() + [Piece("L", None, l, t) for l, t in zip((1, 2, 3), (2, 3, 4))], out)
    z = ZETAS[0]
    report("(c) Z111 at L^1[-1],L^1[0],L^2[1],L^2[2]",
           base() + [Piece("Z", z, 1, -1), Piece("Z", z, 1, 0), Piece("Z", z, 2, 1), Piece("Z", z, 2, 2)]
           + [Piece("L", None, l, 0) for l in (1, 2, 3)], out)
    partners = [z2 for z2 in ZETAS if zmeet(z, z2)[0] == 2]
    report("(d) partner Z11- at shifts 0,1",
           base() + [Piece("Z", partners[0], 0, 0), Piece("Z", partners[0], 0, 1)]
           + [Piece("L", None, l, 0) for l in (1, 2, 3)], out)
    # (a) over the window again, now with the restricted Euler bound as well
    best = None
    count = 0
    for nL in (4, 5):
        for ls in itertools.combinations(range(1, 5), nL):
            for ts in itertools.product(range(-3, 4), repeat=nL):
                pcs = base() + [Piece("L", None, l, t) for l, t in zip(ls, ts)]
                ok, N = configuration_ch(pcs)
                if not ok:
                    continue
                count += 1
                b = bounds(pcs)
                r = restricted_euler(pcs)
                lo = max(b["lower"], r["restricted_euler"])
                if best is None or lo < best[0]:
                    best = (lo, ls, ts, b, r)
    print(f"(a) {count} polarised configurations; least max(safe, restricted Euler):", best)
    out["family_a_restricted"] = dict(count=count, least=best)
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
