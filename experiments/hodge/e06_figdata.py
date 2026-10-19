"""Data for the figures of the Hodge-only round of the BLLM paper: the Ext block matrix of the pieces of
candidate C1 (the 32 threefold pieces of prop:separated and the four line bundles of configuration (a)),
by total degree, and the distribution of the lower bounds over the configurations of families (a) and (c)
of e06_count.py.

    python3 e06_figdata.py out.json
"""
import itertools, json, sys
from e06_count import ZETAS, Piece, base, configuration_ch, bounds, ext_dims
from e06_chains import blocks, restricted_euler


def block_matrix(pieces):
    B = blocks(pieces)
    n = len(pieces)
    out = {}
    for t in (0, 1, 2, 3, 4, 5, 6):
        M = [[B.get((a, b), {}).get(t, (0, True))[0] for b in range(n)] for a in range(n)]
        if any(any(row) for row in M):
            out[t] = M
    return dict(pieces=[repr(p) for p in pieces], shifts=[p.shift for p in pieces],
                kinds=[p.kind for p in pieces], twists=[p.twist for p in pieces],
                zetas=[[str(c) for c in p.zeta] if p.zeta else None for p in pieces], by_degree=out)


def main():
    out = {}
    c1 = base() + [Piece("L", None, l, t) for l, t in zip((1, 2, 3, 4), (-2, -1, 0, 1))]
    out["C1_blocks"] = block_matrix(c1)
    out["C1_bounds"] = dict(**bounds(c1), **restricted_euler(c1))
    b35 = base() + [Piece("L", None, l, t) for l, t in zip((1, 2, 3), (2, 3, 4))]
    out["base35_blocks"] = block_matrix(b35)
    # family (a): every polarised configuration with its bounds
    rows = []
    for nL in (4, 5):
        for ls in itertools.combinations(range(1, 5), nL):
            for ts in itertools.product(range(-3, 4), repeat=nL):
                pcs = base() + [Piece("L", None, l, t) for l, t in zip(ls, ts)]
                ok, N = configuration_ch(pcs)
                if not ok:
                    continue
                b = bounds(pcs)
                rows.append(dict(ls=ls, ts=ts, C1=b["C1"], C2=b["C2"], C3=b["C3"], euler=b["euler"], safe=b["safe"]))
        print("family a", nL, len(rows), flush=True)
    out["family_a_rows"] = rows
    # family (c)
    rows = []
    z = ZETAS[0]
    for k1, k2 in itertools.combinations(range(1, 4), 2):
        for s1, s2 in itertools.product(range(-2, 3), repeat=2):
            for s1b, s2b in itertools.product(range(-2, 3), repeat=2):
                extra = [Piece("Z", z, k1, s1), Piece("Z", z, k1, s1b), Piece("Z", z, k2, s2), Piece("Z", z, k2, s2b)]
                pcs = base() + extra + [Piece("L", None, l, 0) for l in (1, 2, 3)]
                ok, N = configuration_ch(pcs)
                if not ok:
                    continue
                b = bounds(pcs)
                rows.append(dict(k=(k1, k2), s=(s1, s1b, s2, s2b), C1=b["C1"], C2=b["C2"], C3=b["C3"],
                                 euler=b["euler"], safe=b["safe"]))
    print("family c", len(rows), flush=True)
    out["family_c_rows"] = rows
    json.dump(out, open(sys.argv[1], "w"), default=str)
    print("written", sys.argv[1])


if __name__ == "__main__":
    main()
