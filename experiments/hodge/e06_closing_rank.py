"""The rank of y -> D(y)_TT along one closing chain of Lemma 22, on the cover T x B of Lemma 19 (candidate C8).

The chain is T -> T' -> L^{l0} -> ... -> L^{lm} -> T on E_0^6, with T = O_{Z_zeta} L^k, T' = O_{Z_x'} L^{k'} and
J = J(x'), in the model of Lemma 23 (the skyscraper O_E2 of all four points of order two on the curves where T or
T' is a point). The other maps delta of the chain are fixed (sums of r random pure tensors on step s, r = R[s]);
y runs over random pure tensors on one step at a time, and D(y) = sum over the steps of the transferred product
with y in place of delta on that step. The script

1. samples D(y) until the rank of the samples stops growing (rank mod a prime p, by default 2^31 - 1, a lower bound for the rank
   over Q), and prints the rank, by kind of output (H^2(O), H^1(N) diagonal and off-diagonal, Lambda^2 N);
2. computes the cokernel functionals of the sampled image;
3. builds the K-invariant targets t(M): H^1(O) on C_i, the translation class w of O_E2 on C'_j (the class that
   moves all four points of E[2] by the same tangent vector), the unit of Hom(O_E2, O_E2) on the other C' curves,
   for i != j; and prints each cokernel functional as a linear form in the six entries M_ij.

If the linear forms leave no nonzero M with zero diagonal, the image of this chain alone misses every deformation
target ev_T(v), v != 0. That is a statement about this chain and this delta, not about the arrangement: the other
chains through T add to the image, and delta here is not required to satisfy the Maurer-Cartan equation.

    python3 e06_closing_rank.py --samples 1100 --jobs 4 [--delta-r 111111] [--delta-seed 1] [--prime P] -- 7 -3 -1,1,3,5 ""
"""
import argparse, itertools, json, multiprocessing, random, sys
from fractions import Fraction
import e0_twisted as T
import e06_tensor as M
import e06_points as Pt

PR = 2147483647
N, P = 6, 3
Q = Pt.Z


def setup(k, kp, l, J):
    def T0(c):
        return T.L(2 * k) if c < P else Q

    def B0(c):
        if c % P in J:
            return T.L(2 * kp) if c < P else Q
        return Q if c < P else T.L(2 * kp)
    return [[T0(c), B0(c)] + [T.L(2 * a) for a in l] + [T0(c)] for c in range(N)]


def rand_step(cols, s, rng, r=1):
    A = tuple(cols[c][s] for c in range(N))
    B = tuple(cols[c][s + 1] for c in range(N))
    fs = []
    for c in range(N):
        R = M.rc(A[c], B[c])
        opts = [m for m in range(-1, 3) if R.dim(m)]
        if A[c] is Q and B[c] is Q:
            opts = [0]
        assert len(opts) == 1, (s, c, opts)
        fs.append(R.iota(opts[0], [Fraction(rng.choice([-1, 1]) * rng.randint(1, 10 ** 6))
                                   for _ in range(R.dim(opts[0]))]))
    t = M.TMor(A, B, [(Fraction(1), tuple(fs))])
    return t if r == 1 else t + rand_step(cols, s, rng, r - 1)


def modp(x):
    x = Fraction(x)
    return x.numerator % PR * pow(x.denominator % PR, PR - 2, PR) % PR


def proj_deg(x):
    """Class coordinates keyed by the output degree on each curve and the basis indices."""
    o = {}
    for c, fs in x.terms:
        vecs = []
        for f in fs:
            v = M.rc(f.X, f.Y).proj(f)
            vecs.append([(i, a) for i, a in enumerate(v) if a != 0])
            if not vecs[-1]:
                break
        else:
            pat = "".join(str(f.n) for f in fs)
            for combo in itertools.product(*vecs):
                key = pat + "|" + ",".join(str(i) for i, _ in combo)
                val = c
                for _, a in combo:
                    val *= a
                o[key] = o.get(key, 0) + val
    return {k: modp(v) for k, v in o.items() if v != 0 and modp(v)}


def _worker(job):
    global PR
    a, seed, ns = job
    PR = a["prime"]
    cols = setup(a["k"], a["kp"], a["l"], set(a["J"]))
    S = len(a["l"]) + 2
    drng = random.Random(a["delta_seed"])
    delta = [rand_step(cols, s, drng, a["delta_r"][s]) for s in range(S)]
    rng = random.Random(seed)
    out = []
    for _ in range(ns):
        s = rng.randrange(S)
        xs = list(delta)
        xs[s] = rand_step(cols, s, rng)
        _, tot = M.bn(xs)
        out.append(proj_deg(tot) if tot is not None else {})
    return out


def kind(p):
    c = [i for i in range(3) if p[i] == "1"]
    cp = [i for i in range(3) if p[3 + i] == "1"]
    if len(c) == 2:
        return "H2(O)"
    if len(cp) == 2:
        return "L2N"
    if len(c) == 1 and len(cp) == 1:
        return "H1N-diag" if c[0] == cp[0] else "H1N-off"
    return "other:" + p


def rref(rows, n):
    piv, R = [], []
    for row in rows:
        row = row[:]
        for c, pr in zip(piv, R):
            if row[c]:
                f = row[c]
                row = [(x - f * y) % PR for x, y in zip(row, pr)]
        c = next((i for i, x in enumerate(row) if x), None)
        if c is None:
            continue
        inv = pow(row[c], PR - 2, PR)
        row = [x * inv % PR for x in row]
        for i in range(len(R)):
            if R[i][c]:
                f = R[i][c]
                R[i] = [(x - f * y) % PR for x, y in zip(R[i], row)]
        piv.append(c)
        R.append(row)
    return piv, R


def translation_class():
    """The class w in Ext^1(O_E2, O_E2) that moves every point of E[2] by the same tangent vector (dz = 1).

    A degree-1 class has a component s = (s0, s1), a section of O(4 oo) on the two charts, deforming the
    differential y to y + eps s; the zero of y at q moves by -s(q) / y'(q), read on U0 at the finite points
    (y' = 3x^2 - 1 there) and on U1 at oo (frame z^-4, where y z^4 = -z + ...)."""
    R = T.retract(Q, Q)
    d1 = R.dim(1)

    def disp(vec):
        el = R.iota(1, vec).c.get((0, 1))
        if el is None:
            return [Fraction(0)] * 4
        out = [Fraction(el.f1.get(4, 0))]       # oo: -(coefficient of x^2) / (-1)
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
    global PR
    ap = argparse.ArgumentParser()
    ap.add_argument("k", type=int)
    ap.add_argument("kp", type=int)
    ap.add_argument("l")
    ap.add_argument("J")
    ap.add_argument("--samples", type=int, default=1100)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--delta-seed", type=int, default=1)
    ap.add_argument("--delta-r", default=None)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--prime", type=int, default=PR, help="the prime of the rank computation (default 2^31 - 1)")
    ap.add_argument("--load", nargs="*", help="read samples from jsonl files instead of computing them")
    ap.add_argument("--save", help="write the computed samples to this jsonl file")
    a = ap.parse_args()
    PR = a.prime
    l = [int(x) for x in a.l.split(",")]
    S = len(l) + 2
    args = {"k": a.k, "kp": a.kp, "l": l, "J": [int(x) for x in a.J.split(",") if x],
            "prime": a.prime, "delta_seed": a.delta_seed, "delta_r": [int(x) for x in (a.delta_r or "1" * S)]}
    if a.load:
        vecs = [json.loads(line)["v"] for fn in a.load for line in open(fn) if line.strip() not in ("", "{}")]
    else:
        per = -(-a.samples // a.jobs)
        with multiprocessing.Pool(a.jobs) as pool:
            parts = pool.map(_worker, [(args, a.seed + 1000 * i, per) for i in range(a.jobs)])
        vecs = [v for p in parts for v in p]
        if a.save:
            with open(a.save, "w") as fh:
                for v in vecs:
                    fh.write(json.dumps({"v": v}) + "\n")
    keys = sorted({k for v in vecs for k in v})
    idx = {k: i for i, k in enumerate(keys)}
    rows = [[0] * len(keys) for _ in vecs]
    for r, v in zip(rows, vecs):
        for k, x in v.items():
            r[idx[k]] = x
    piv, R = rref(rows, len(keys))
    half = rref(rows[: len(rows) * 3 // 4], len(keys))[0]
    print(f"chain k={a.k} k'={a.kp} l={l} J={args['J']} delta_r={args['delta_r']} delta_seed={a.delta_seed} prime={PR}")
    print(f"samples {len(vecs)}, output coordinates {len(keys)}, rank {len(piv)} "
          f"(rank of the first three quarters {len(half)})")
    groups = {}
    for k in keys:
        groups.setdefault(kind(k.split("|")[0]), []).append(idx[k])
    for g, cs in sorted(groups.items()):
        print(f"  {g}: {len(cs)} coordinates, rank of the projection {len(rref([[r[c] for c in cs] for r in rows], len(cs))[0])}")
    pset = set(piv)
    free = [c for c in range(len(keys)) if c not in pset]
    funcs = []
    for f in free:
        lam = {keys[f]: 1}
        for c, r in zip(piv, R):
            if r[f]:
                lam[keys[c]] = (-r[f]) % PR
        funcs.append(lam)
    w = translation_class()
    unit = Pt.FunctionsOnE2().unit
    forms = []
    for lam in funcs:
        form = [[0] * 3 for _ in range(3)]
        for i, j in itertools.product(range(3), range(3)):
            pat = "".join("1" if c == i else "0" for c in range(3)) + "".join("1" if c == j else "0" for c in range(3))
            for key, lv in lam.items():
                p, ix = key.split("|")
                if p != pat:
                    continue
                ix = [int(x) for x in ix.split(",")]
                if any(ix[c] for c in range(3)):
                    continue
                coef = lv
                for c in range(3):
                    coef = coef * modp(w[ix[3 + c]] if c == j else unit[ix[3 + c]]) % PR
                form[i][j] = (form[i][j] + coef) % PR
        forms.append(form)
    # the six off-diagonal entries: which M with zero diagonal satisfy every form?
    off = [(i, j) for i in range(3) for j in range(3) if i != j]
    sys_rows = [[f[i][j] for (i, j) in off] for f in forms if any(f[i][j] for (i, j) in off)]
    r = len(rref(sys_rows, 6)[0]) if sys_rows else 0
    print(f"cokernel functionals {len(funcs)}; as forms in the six entries M_ij (i != j) they have rank {r}")
    print("K-invariant targets with zero diagonal in the image of this chain: a space of dimension", 6 - r)


if __name__ == "__main__":
    main()
