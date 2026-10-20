"""The closing chain of Lemma 24 with K-invariant maps only (candidate C8, Lemma 25).

The chain is T -> T' -> L^-1 -> L -> L^3 -> L^5 -> T on E_0^6 (k = 7, k' = -3, J empty), with the skyscraper
factors written as Z_k = O_E2 (x) L^k (`e06_equivariant.Zk`), so that each factor carries the linearisation of its
parent line bundle. A pull-back from A_0 is a K-equivariant twisted complex: each summand has a linearisation, unique
up to a character of K, and the maps are invariant. On step s the pair (C_j, C'_j) then contributes an element of

    sum over chi of V_chi (x) V'_(chi eta),        eta = eta(s, j), the ratio of the characters of the two ends,

with the product of eta(s, j) over the six steps trivial for every j (the chain closes on the same T). Each
per-curve space of the chain is the regular representation of E[2] (four characters, one dimension each), so the
invariant maps of one step form a space of dimension 4^3 = 64, spanned by the pure tensors of eigenvectors.

The script fixes delta (a sum of r invariant pure tensors on each step), computes D(y) for y running over the 64
invariant basis tensors of each step (384 evaluations, the whole invariant tangent space of the adjacent arrows), and
prints the rank of the image and the dimension of the K-invariant targets t(M) with zero diagonal that it contains.

    python3 e06_invariant_rank.py [--eta trivial|SEED] [--delta-r 111111] [--delta-seed 1] [--jobs 4] [--prime P]
"""
import argparse, itertools, multiprocessing, random
from fractions import Fraction
import e0_twisted as T
import e06_tensor as M
import e06_points as Pt
import e06_equivariant as EQ
import e06_closing_rank as CR

N, P = 6, 3
K, KP, LS = 7, -3, [-1, 1, 3, 5]
CHARS = EQ.CHARS


def cmul(a, b):
    return (a[0] * b[0], a[1] * b[1])


def chain():
    """Objects of each curve, with their descriptors for the K-action."""
    cols, desc = [], []
    for c in range(N):
        if c < P:
            d = [("L", 2 * K), ("Z", KP)] + [("L", 2 * a) for a in LS] + [("L", 2 * K)]
        else:
            d = [("Z", K), ("L", 2 * KP)] + [("L", 2 * a) for a in LS] + [("Z", K)]
        desc.append(d)
        cols.append([T.L(x[1]) if x[0] == "L" else EQ.Zk(x[1]) for x in d])
    return cols, desc


def step_degree(A, B):
    R = M.rc(A, B)
    opts = [m for m in range(-1, 3) if R.dim(m)]
    assert len(opts) == 1, opts
    return opts[0], R


def eigen(cols, desc):
    """eig[s][c][chi] = an eigenvector of character chi in the step space of curve c (a list of Fractions)."""
    S = len(cols[0]) - 1
    eig = []
    for s in range(S):
        row = []
        for c in range(N):
            n, R = step_degree(cols[c][s], cols[c][s + 1])
            sp = EQ.character_spaces(desc[c][s], desc[c][s + 1], n)
            assert all(len(v) == 1 for v in sp.values()), (s, c, {k: len(v) for k, v in sp.items()})
            row.append((n, R, {chi: v[0] for chi, v in sp.items()}))
        eig.append(row)
    return eig


def etas(spec):
    """eta[s][j] with trivial product over s for each j."""
    S = len(LS) + 2
    if spec == "trivial":
        return [[(1, 1)] * P for _ in range(S)]
    rng = random.Random(int(spec))
    eta = [[rng.choice(CHARS) for _ in range(P)] for _ in range(S - 1)]
    last = []
    for j in range(P):
        prod = (1, 1)
        for s in range(S - 1):
            prod = cmul(prod, eta[s][j])
        last.append(prod)
    return eta + [last]


def pure(cols, eig, eta, s, chis, scale=1):
    A = tuple(cols[c][s] for c in range(N))
    B = tuple(cols[c][s + 1] for c in range(N))
    fs = []
    for c in range(N):
        n, R, ev = eig[s][c]
        j = c % P
        chi = chis[j] if c < P else cmul(chis[j], eta[s][j])
        fs.append(R.iota(n, ev[chi]))
    return M.TMor(A, B, [(Fraction(scale), tuple(fs))])


def delta_steps(cols, eig, eta, rs, seed):
    rng = random.Random(seed)
    out = []
    for s, r in enumerate(rs):
        t = None
        for _ in range(r):
            x = pure(cols, eig, eta, s, [rng.choice(CHARS) for _ in range(P)],
                     rng.choice([-1, 1]) * rng.randint(1, 10 ** 6))
            t = x if t is None else t + x
        out.append(t)
    return out


def _worker(job):
    a, tasks = job
    CR.PR = a["prime"]
    cols, desc = chain()
    eig = eigen(cols, desc)
    eta = etas(a["eta"])
    delta = delta_steps(cols, eig, eta, a["delta_r"], a["delta_seed"])
    out = []
    for s, chis in tasks:
        xs = list(delta)
        xs[s] = pure(cols, eig, eta, s, list(chis))
        _, tot = M.bn(xs)
        out.append(CR.proj_deg(tot) if tot is not None else {})
    return out


def zk_unit(Z):
    R = T.retract(Z, Z)
    d = R.dim(0)
    basis = [[Fraction(int(i == j)) for j in range(d)] for i in range(d)]
    table = [[Pt.mul_cls(Z, Z, Z, basis[a], basis[b], 0, 0) for b in range(d)] for a in range(d)]
    rows, rhs = [], []
    for b in range(d):
        for c in range(d):
            rows.append([table[a][b][c] for a in range(d)])
            rhs.append(basis[b][c])
    u = Pt.rank_solve(rows, rhs)
    assert u is not None
    return u


def translation_class(Z):
    """As `e06_closing_rank.translation_class`, for Z_k: the component (0, 1) is a section of O(4 oo) in every case."""
    R = T.retract(Z, Z)
    d1 = R.dim(1)

    def disp(vec):
        el = R.iota(1, vec).c.get((0, 1))
        if el is None:
            return [Fraction(0)] * 4
        out = [Fraction(el.f1.get(4, 0))]
        for e in (0, 1, -1):
            v = sum((Fraction(c) * Fraction(e) ** (n // 2) for n, c in el.f0.items() if n % 2 == 0), Fraction(0))
            out.append(-v / (3 * e * e - 1))
        return out
    basis = [[Fraction(int(i == j)) for j in range(d1)] for i in range(d1)]
    D = [disp(b) for b in basis]
    w = Pt.rank_solve([[D[a][q] for a in range(d1)] for q in range(4)], [Fraction(1)] * 4)
    assert disp(w) == [Fraction(1)] * 4
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eta", default="trivial")
    ap.add_argument("--delta-r", default="111111")
    ap.add_argument("--delta-seed", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--prime", type=int, default=2147483647)
    a = ap.parse_args()
    PR = CR.PR = a.prime
    S = len(LS) + 2
    args = {"eta": a.eta, "delta_r": [int(x) for x in a.delta_r], "delta_seed": a.delta_seed, "prime": a.prime}
    tasks = [(s, chis) for s in range(S) for chis in itertools.product(CHARS, repeat=P)]
    parts = [tasks[i::a.jobs] for i in range(a.jobs)]
    with multiprocessing.Pool(a.jobs) as pool:
        res = pool.map(_worker, [(args, p) for p in parts])
    vecs = [v for r in res for v in r]
    # targets t(M), i != j
    Z = EQ.Zk(K)
    w = translation_class(Z)
    unit = zk_unit(Z)
    targets = []
    for i, j in itertools.product(range(P), range(P)):
        if i == j:
            continue
        pat = "".join("1" if c == i else "0" for c in range(P)) + "".join("1" if c == j else "0" for c in range(P))
        dz = len(unit)
        t = {}
        for ix in itertools.product(range(dz), repeat=P):
            val = Fraction(1)
            for c in range(P):
                val *= w[ix[c]] if c == j else unit[ix[c]]
            if val:
                t[pat + "|" + ",".join(["0"] * P + [str(x) for x in ix])] = CR.modp(val)
        targets.append(t)
    keys = sorted({k for v in vecs + targets for k in v})
    idx = {k: i for i, k in enumerate(keys)}

    def row(v):
        r = [0] * len(keys)
        for k, x in v.items():
            r[idx[k]] = x % PR
        return r
    img = [row(v) for v in vecs]
    rimg = len(CR.rref(img, len(keys))[0])
    rall = len(CR.rref(img + [row(t) for t in targets], len(keys))[0])
    groups = {}
    for k in keys:
        groups.setdefault(CR.kind(k.split("|")[0]), []).append(idx[k])
    print(f"invariant chain k={K} k'={KP} l={LS} eta={a.eta} delta_r={a.delta_r} delta_seed={a.delta_seed} prime={PR}")
    print(f"evaluations {len(vecs)}, output coordinates {len(keys)}, rank of the image {rimg}")
    for g, cs in sorted(groups.items()):
        print(f"  {g}: {len(cs)} coordinates, rank of the projection {len(CR.rref([[r[c] for c in cs] for r in img], len(cs))[0])}")
    print("K-invariant targets with zero diagonal in the image:", 6 + rimg - rall, "of 6")


if __name__ == "__main__":
    main()
