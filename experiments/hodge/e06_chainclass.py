"""Exhaustive check of the classification of closed chains through threefold pieces at A_0 = E_0^6
(the setting of prop:separated without the bound on the number of line bundles; see e06_orphans.py for the
node-by-node search on single configurations).

A closed chain alternates between line bundles and runs of threefold pieces.  Every step a -> b of Ext degree
k has excess k - 1, and a closed chain has total excess 0.  Threefold pieces enter only through the classes
(twist, shift): the Ext groups between a line bundle and O_Z (x) L^k do not depend on Z, and the 16
threefolds Z_zeta of one sign are permuted transitively by the multiplications by eta in mu_4^3 with
eta_1 eta_2 eta_3 = 1, which preserve the number of shared coordinates.  So a run from L_i to L_j exists with
excess b, through a class c, exactly when a path L_i -> c_1 -> ... -> c_r -> L_j of classes exists with an
edge for some admissible number of shared coordinates at each internal step.  This ignores that the
threefolds of a chain must be distinct, so the chains found are a superset of the true ones, and every
statement "no chain of this kind" proved below holds for the true ones.

The line bundles have distinct exponents, and the threefold pieces of sign (-1)^s sit at shifts s of the
parity eps * zeta_1 zeta_2 zeta_3, so two threefold pieces at one shift have the same sign and share at most
one coordinate (Ext^1 = 0 between them).

Checked, over every placement in the window:
  (A) every closed chain through a threefold piece has at least four line bundles;
  (B) with exactly four: shape L^{l1}[t] -> L^{l2}[t+1] -> L^{l3}[t+2] -> L^{l4}[t+3] -> run -> L^{l1}[t],
      l1 < l2 < l3 < l4, the run of two threefold pieces O_Z L^{k}[t+4] -> O_Z' L^{k'}[t+2] with
      k' <= l1, l4 <= k (so it needs two twists at least three apart);
  (C) with one threefold twist: at least five;
  (D) with one twist and exactly five: L^{l1}[t] -> ... -> L^{l5}[t+4] (exponents increasing) -> one threefold
      piece at shift t+2 with twist <= l1, or at shift t+5 with twist >= l5 -> L^{l1}[t];
  and the threefold pieces on some chain, by shift, to see when both signs occur.

    python3 e06_chainclass.py out.json
"""
import itertools, json, sys
from math import comb

CAP = 8


def ll_degrees(l, l2):
    if l2 > l:
        return {0}
    if l2 < l:
        return {6}
    return set(range(7))


def lz_degrees(l, k):          # Ext^*(L^l, O_Z L^k)
    if k > l:
        return {0}
    if k < l:
        return {3}
    return {0, 1, 2, 3}


def zl_degrees(k, l):          # Ext^*(O_Z L^k, L^l)
    if l > k:
        return {3}
    if l < k:
        return {6}
    return {3, 4, 5, 6}


def zz_degrees(k, k2, d):      # Ext^*(O_Z L^k, O_Z' L^k2), Z != Z' sharing d coordinates (E_2 ranges)
    c = 3 - d
    m = k2 - k
    if d == 0:
        return {3}
    if m > 0:
        return set(range(c, 4))
    if m < 0:
        return set(range(3, 4 + d))
    return set(range(c, 4 + d))


# numbers of shared coordinates between two of the 32 threefolds, by signs
D_SAME = (0, 1)        # e.g. (1,1,1), (1,i,-i)
D_OPP = (0, 1, 2)      # e.g. (1,1,1), (-1,-1,-1); (1,i,i); (1,1,-1)


def classes(twists, window, eps):
    """Threefold classes (twist, shift, sign), sign = eps * (-1)^shift."""
    return [(k, s, eps * (-1) ** (s % 2)) for k in twists for s in window]


def class_edges(cls):
    out = {c: [] for c in cls}
    for a in cls:
        for b in cls:
            k = 1 + a[1] - b[1]
            ds = D_SAME if a[2] == b[2] else D_OPP
            if any(k in zz_degrees(a[0], b[0], d) for d in ds):
                out[a].append((b, k))
    return out


def run_tables(lines, cls, cedges):
    """F[i][c]: excesses of paths L_i -> ... -> c (entry and internal steps);
    G[j][c]: excesses of paths c -> ... -> L_j (internal steps and exit)."""
    order = sorted(cls, key=lambda c: -c[1])          # internal edges lower the shift
    F, G = [], []
    for (l, t) in lines:
        f = {c: set() for c in cls}
        for c in order:
            k = 1 + t - c[1]
            if k in lz_degrees(l, c[0]):
                f[c].add(k - 1)
            for b, kk in cedges[c]:
                f[b] |= {x + kk - 1 for x in f[c] if x + kk - 1 <= CAP}
        F.append(f)
    for (l, t) in lines:
        g = {c: set() for c in cls}
        for c in reversed(order):                        # targets of edges first
            k = 1 + c[1] - t
            if k in zl_degrees(c[0], l):
                g[c].add(k - 1)
            for b, kk in cedges[c]:
                g[c] |= {x + kk - 1 for x in g[b] if x + kk - 1 <= CAP}
        G.append(g)
    return F, G


def runs(F, G, i, j, cls):
    """{excess b: set of classes on some run L_i -> L_j of excess b}."""
    out = {}
    for c in cls:
        for x in F[i][c]:
            for y in G[j][c]:
                if x + y <= CAP:
                    out.setdefault(x + y, set()).add(c)
    return out


def cycles(lines, cls, cedges, full=False):
    """Closed chains at the level of line bundles: cyclic sequences of distinct line bundles (starting at the
    least index), each move direct or a run; returns [(sequence, moves)], moves[i] = ('L', exc) or
    ('Z', b, classes).  With full=True only the chains through every line bundle."""
    n = len(lines)
    F, G = run_tables(lines, cls, cedges)
    R = {(i, j): runs(F, G, i, j, cls) for i in range(n) for j in range(n)}
    direct = {}
    for i, (l, t) in enumerate(lines):
        for j, (l2, t2) in enumerate(lines):
            if i != j:
                k = 1 + t - t2
                if k in ll_degrees(l, l2):
                    direct[(i, j)] = k - 1
    found = []

    def moves(i, j):
        if (i, j) in direct:
            yield ("L", direct[(i, j)])
        for b, cs in R[(i, j)].items():
            yield ("Z", b, cs)

    def dfs(seq, mv, exc):
        cur = seq[-1]
        # close
        for m in moves(cur, seq[0]):
            if full and len(seq) < n:
                break
            if exc + m[1] == 0 and (len(seq) >= 2 or m[0] == "Z") and any(x[0] == "Z" for x in mv + [m]):
                found.append((list(seq), mv + [m]))
        for j in range(seq[0] + 1, n):
            if j in seq:
                continue
            for m in moves(cur, j):
                e2 = exc + m[1]
                # every later move starts at a line bundle and has excess >= -1
                if e2 > n - len(seq):
                    continue
                dfs(seq + [j], mv + [m], e2)

    for i in (range(1) if full else range(n)):
        dfs([i], [], 0)
    return found


def check(lines, twists, window, eps, full=False):
    cls = classes(twists, window, eps)
    cedges = class_edges(cls)
    found = cycles(lines, cls, cedges, full)
    bad, onchain = [], set()
    for seq, mv in found:
        nl = len(seq)
        ls = [lines[i] for i in seq]
        zruns = [(p, m) for p, m in enumerate(mv) if m[0] == "Z"]
        for _, m in zruns:
            onchain |= {(c[0], c[1]) for c in m[2]}
        if nl <= 3:
            bad.append(("A", ls, mv))
            continue
        if nl == 4:
            ok = len(twists) > 1 and len(zruns) == 1 and zruns[0][1][1] == 3
            if ok:
                p = zruns[0][0]
                rot = seq[p + 1:] + seq[:p + 1]                  # starts after the run
                L = [lines[i] for i in rot]
                t = L[0][1]
                ok = [x[1] for x in L] == [t, t + 1, t + 2, t + 3] and all(L[a][0] < L[a + 1][0] for a in range(3))
                ok = ok and all((c[1] == t + 4 and c[0] >= L[3][0]) or (c[1] == t + 2 and c[0] <= L[0][0])
                                for c in zruns[0][1][2])
            if not ok:
                bad.append(("B/C", ls, mv))
        if nl == 5 and len(twists) == 1:
            ok = len(zruns) == 1 and zruns[0][1][1] == 4
            if ok:
                p = zruns[0][0]
                rot = seq[p + 1:] + seq[:p + 1]
                L = [lines[i] for i in rot]
                t = L[0][1]
                ok = [x[1] for x in L] == [t + a for a in range(5)] and all(L[a][0] < L[a + 1][0] for a in range(4))
                ok = ok and all((c[1] == t + 2 and c[0] <= L[0][0]) or (c[1] == t + 5 and c[0] >= L[4][0])
                                for c in zruns[0][1][2])
            if not ok:
                bad.append(("D", ls, mv))
    return found, bad, onchain


def patterns(nl, nt):
    """Exponents and twists up to order: the Ext groups depend only on the relative order of the exponents of
    the line bundles and the twists of the threefold pieces.  A pattern is a word in the slots L, Z, LZ (a
    line bundle, a twist, or a line bundle whose exponent equals a twist) with nl slots containing L and nt
    containing Z; the slot index is the value."""
    def words(a, b):
        if a == 0 and b == 0:
            yield ()
            return
        if a:
            for w in words(a - 1, b):
                yield ("L",) + w
        if b:
            for w in words(a, b - 1):
                yield ("Z",) + w
        if a and b:
            for w in words(a - 1, b - 1):
                yield ("LZ",) + w
    for w in words(nl, nt):
        yield [v for v, s in enumerate(w) if "L" in s], tuple(v for v, s in enumerate(w) if "Z" in s)


def _survey(args):
    """Every placement of the line bundles of one pattern at shifts 0..nl with least shift 0 (a closed
    chain through m line bundles rises by at most one at each step that starts at a line bundle, so their
    shifts span at most m), both parity conventions; only the chains through all the line bundles."""
    nl, ls, twists, W = args
    tot = dict(configs=0, with_chain=0, chains=0, bad=0, mixed_sign=0, onchain_rel=[], bad_examples=[],
               mixed_examples=[], examples=[])
    rel = set()
    for ts in itertools.product(range(0, nl + 1), repeat=nl):
        if min(ts) != 0:
            continue
        lines = list(zip(ls, ts))
        for eps in (1, -1):
            found, bad, onchain = check(lines, twists, W, eps, full=True)
            tot["configs"] += 1
            if found:
                tot["with_chain"] += 1
                tot["chains"] += len(found)
                if len(tot["examples"]) < 2:
                    tot["examples"].append(dict(lines=lines, eps=eps, onchain=sorted(onchain)))
                if len({s % 2 for _, s in onchain}) > 1:
                    tot["mixed_sign"] += 1
                    if len(tot["mixed_examples"]) < 2:
                        tot["mixed_examples"].append(dict(lines=lines, eps=eps, onchain=sorted(onchain)))
            if bad:
                tot["bad"] += 1
                if len(tot["bad_examples"]) < 2:
                    tot["bad_examples"].append(dict(lines=lines, eps=eps, bad=[str(b) for b in bad[:2]]))
    return tot


def merge(a, b):
    for k in ("configs", "with_chain", "chains", "bad", "mixed_sign"):
        a[k] += b[k]
    for k in ("bad_examples", "mixed_examples", "examples"):
        a[k] = (a[k] + b[k])[:3]


def main():
    from multiprocessing import Pool
    out = {}
    plan = [(nl, 1) for nl in range(1, 7)] + [(nl, 2) for nl in range(1, 6)] + [(nl, 3) for nl in range(1, 5)] + [(4, 4)]
    with Pool(4) as pool:
        for nl, nt in plan:
            tot = dict(configs=0, with_chain=0, chains=0, bad=0, mixed_sign=0, bad_examples=[], mixed_examples=[],
                       examples=[])
            pats = list(patterns(nl, nt))
            W = range(-6, 2 * nl + 8)
            jobs = [(nl, ls, tw, W) for ls, tw in pats]
            for part in pool.imap_unordered(_survey, jobs):
                merge(tot, part)
            name = f"{nl} line bundles on the chain, {nt} twists, {len(pats)} order patterns"
            print(name, {k: v for k, v in tot.items() if k in ("configs", "with_chain", "chains", "bad",
                                                               "mixed_sign")}, flush=True)
            out[name] = tot
            if len(sys.argv) > 1:
                json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
