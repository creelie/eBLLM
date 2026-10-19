"""The live chains of the eight rank +-2 configurations of eight line bundles (C8_chains.md, Lemma 22).

For each configuration of e06_six_n8.json with rank sum (-1)^s = +-2 and each admissible set Z0 of zero up
edges whose live chains carry threefold pieces of both parities (e06_six.refine), every live chain is split
into its up steps and its runs through threefold pieces, and every run is matched against all realisations
by threefold pieces with the degrees of Lemma 3 (at most three threefolds; a run of excess b uses at most b + 1).

    python3 e06_runs.py
"""
import json, os, sys
import e06_six as E

HERE = os.path.dirname(os.path.abspath(__file__))
REL = {-1: "<", 0: "=lo", 5: "mid", 10: "=hi", 11: ">"}


def realisations(b, dec):
    """Runs L^A -> threefolds -> L^B of excess b; A = top exponent 10, B = 0 if dec, else A = 0, B = 10."""
    A, B = (10, 0) if dec else (0, 10)
    ks = sorted(REL)
    out = set()

    def go(seq, k, x):
        for d in E.zl_degrees(k, B):
            if x + d - 1 == b:
                out.add(tuple(seq) + (("L", d),))
        if len(seq) < 3:
            for k2 in ks:
                for d in E.zz_degrees(k, k2):
                    if x + d - 1 < b:
                        go(seq + [(REL[k2], d)], k2, x + d - 1)

    for k in ks:
        for d in E.lz_degrees(A, k):
            go([(REL[k], d)], k, d - 1)
    return sorted(out, key=lambda r: (len(r), r))


def main():
    d = json.load(open(os.path.join(HERE, "e06_six_n8.json")))
    confs = [tuple(c) for c in d["both"] if sum((-1) ** s for s in c)]
    assert len(confs) == 8
    excesses = set()
    nchains = 0
    for c in confs:
        up, good = E.refine(c)
        for z0, used in good:
            for path, par in used:
                cyc = list(path) + [path[0]]
                for a, b in zip(cyc, cyc[1:]):
                    if c[b] == c[a] + 1 and b > a:
                        continue
                    excesses.add((c[a] - c[b], b < a))
                nchains += 1
    print("rank +-2 configurations:", len(confs), " live chains over all admissible Z0:", nchains)
    print("runs that occur (excess, decreasing):", sorted(excesses))
    ok = True
    for (b, dec) in sorted(excesses):
        rs = realisations(b, dec)
        print(f"excess {b} {'decreasing' if dec else 'increasing'}: {len(rs)} realisations")
        for r in rs:
            print("   ", r)
        if dec and b == 3:
            # each one: Hom (degree 0) into a threefold T of twist >= top, Ext^3 into T' of twist <= bottom, Ext^3 out
            ok &= all(len(r) == 3 and r[0][1] == 0 and r[0][0] in (">", "=hi") and r[1][1] == 3
                      and r[1][0] in ("<", "=lo") and r[2] == ("L", 3) for r in rs)
        if not dec and b == 1:
            ok &= all(len(r) == 2 and r[0][1] == 0 and r[1] == ("L", 3) for r in rs)
    ok &= excesses <= {(3, True), (1, False)}
    print("Lemma 22:", "holds" if ok else "FAILS")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
