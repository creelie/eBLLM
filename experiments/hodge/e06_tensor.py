"""Exact A-infinity products on products of copies of E_0 (candidate C8, Lemmas 19, 20 and 22).

An object of E_0^N is an N-tuple of objects of e0_twisted (line bundles O(a oo) and the skyscraper O_oo), meaning
their external product. Hom complexes are tensor products of the Hom complexes of the factors (Kunneth), with
the Koszul sign rule; the special deformation retract of each factor onto its cohomology (e0_twisted.Retract)
gives the one of the tensor product by the tensor trick,

    i = (x) i_c,   p = (x) p_c,   h = sum_f (i p)^{(x)(f-1)} (x) h_f (x) 1^{(x)(N-f)},

and the transferred products are the tree formula of e0_twisted with these. A morphism is a sum of pure tensors
(coefficient, (phi_1, ..., phi_N)), phi_c a morphism of e0_twisted.

    python3 e06_tensor.py        # checks the A-infinity relations on E_0 x E_0 and E_0^3
"""
from fractions import Fraction
import itertools, random, sys
import e0_twisted as T


class TMor:
    __slots__ = ("X", "Y", "terms")

    def __init__(self, X, Y, terms=None):
        self.X, self.Y = X, Y          # tuples of e0_twisted objects
        self.terms = [(c, fs) for c, fs in (terms or []) if c != 0 and not any(f.iszero() for f in fs)]

    @property
    def n(self):
        return sum(f.n for f in self.terms[0][1]) if self.terms else None

    def iszero(self):
        return not self.terms

    def __add__(self, o):
        return TMor(self.X, self.Y, self.terms + o.terms)

    def scale(self, s):
        return TMor(self.X, self.Y, [(c * s, fs) for c, fs in self.terms])


def mu(x, y):
    out = []
    for c1, fs in x.terms:
        for c2, gs in y.terms:
            sgn = 0
            for c in range(len(fs)):
                for c2_ in range(c):
                    sgn += gs[c2_].n * fs[c].n
            prods = []
            ok = True
            for f, g in zip(fs, gs):
                z = T.mu(f, g)
                if z.iszero():
                    ok = False
                    break
                prods.append(z)
            if ok:
                out.append((c1 * c2 * (1 - 2 * (sgn % 2)), tuple(prods)))
    return TMor(x.X, y.Y, out)


def b2(x, y):
    if x.iszero() or y.iszero():
        return TMor(x.X, y.Y)
    r = mu(x, y)
    return r.scale(-1) if x.n % 2 else r


def rc(X, Y):
    return T.retract(X, Y)


def ip1(f):
    R = rc(f.X, f.Y)
    cls = R.proj(f)
    if not any(cls):
        return None
    return R.iota(f.n, cls)


def h(x):
    out = []
    for c, fs in x.terms:
        N = len(fs)
        pre = []
        sgn = 0
        for fidx in range(N):
            hf = rc(fs[fidx].X, fs[fidx].Y).h(fs[fidx])
            if not hf.iszero():
                out.append((c * (1 - 2 * (sgn % 2)), tuple(pre) + (hf,) + tuple(fs[fidx + 1:])))
            ipf = ip1(fs[fidx])
            if ipf is None:
                break
            pre.append(ipf)
            sgn += fs[fidx].n
    return TMor(x.X, x.Y, out)


def proj(x):
    """Class coordinates: dict {tuple of basis indices: coefficient}."""
    out = {}
    for c, fs in x.terms:
        vecs = []
        for f in fs:
            v = rc(f.X, f.Y).proj(f)
            vecs.append([(k, a) for k, a in enumerate(v) if a != 0])
            if not vecs[-1]:
                break
        else:
            for combo in itertools.product(*vecs):
                key = tuple(k for k, _ in combo)
                val = c
                for _, a in combo:
                    val *= a
                out[key] = out.get(key, 0) + val
    return {k: v for k, v in out.items() if v != 0}


def degs(x):
    return tuple(f.n for f in x.terms[0][1]) if x.terms else None


def iota(X, Y, ns, cls):
    """ns: per-factor degrees; cls: dict {tuple of basis indices: coefficient}."""
    terms = []
    for key, a in cls.items():
        fs = []
        for c, k in enumerate(key):
            R = rc(X[c], Y[c])
            v = [Fraction(0)] * R.dim(ns[c])
            v[k] = Fraction(1)
            fs.append(R.iota(ns[c], v))
        terms.append((Fraction(a), tuple(fs)))
    return TMor(X, Y, terms)


def phi(xs, memo=None):
    if memo is None:
        memo = {}
    key = (id(xs[0]), len(xs))
    if len(xs) == 1:
        return xs[0]
    tot = None
    for k in range(1, len(xs)):
        t = b2(phi(xs[:k]), phi(xs[k:]))
        tot = t if tot is None else tot + t
    return h(tot)


def bn(xs):
    tot = None
    for k in range(1, len(xs)):
        t = b2(phi(xs[:k]), phi(xs[k:]))
        tot = t if tot is None else tot + t
    return proj(tot), tot


def dims(X, Y):
    return [[rc(X[c], Y[c]).dim(n) for n in range(-1, 3)] for c in range(len(X))]


def random_class(X, Y, ns, rng):
    keys = [range(rc(X[c], Y[c]).dim(ns[c])) for c in range(len(X))]
    allk = list(itertools.product(*keys))
    if not allk:
        return None
    cls = {k: Fraction(rng.randint(-2, 2)) for k in allk if rng.random() < 0.7}
    cls = {k: v for k, v in cls.items() if v != 0}
    return cls or {allk[0]: Fraction(1)}


def relation(xs):
    """Shifted A-infinity relation sum b(.., b(..), ..) on inputs iota(class); returns the defect (a dict)."""
    n = len(xs)
    total = {}
    for j in range(2, n):
        for i in range(0, n - j + 1):
            cls, tot = bn(xs[i:i + j])
            if not cls:
                continue
            inner = iota(tot.X, tot.Y, degs(tot), cls)
            out, _ = bn(xs[:i] + [inner] + xs[i + j:])
            sgn = 1 - 2 * (sum(x.n - 1 for x in xs[:i]) % 2)
            for k, v in out.items():
                total[k] = total.get(k, 0) + sgn * v
    return {k: v for k, v in total.items() if v != 0}


def check(N, trials, seed):
    rng = random.Random(seed)
    Q = T.skyscraper_oo()
    done = bad = 0
    while done < trials:
        n = rng.randint(3, 4)
        # a chain of objects; each factor is a line bundle of even degree or O_oo
        objs = []
        for _ in range(n + 1):
            objs.append(tuple(Q if rng.random() < 0.3 else T.L(2 * rng.randint(-1, 2)) for _ in range(N)))
        xs = []
        ok = True
        for A, B in zip(objs, objs[1:]):
            # choose per-factor degrees with nonzero cohomology
            ns = []
            for c in range(N):
                opts = [m for m in range(-1, 3) if rc(A[c], B[c]).dim(m)]
                if not opts:
                    ok = False
                    break
                ns.append(rng.choice(opts))
            if not ok:
                break
            cls = random_class(A, B, ns, rng)
            xs.append(iota(A, B, ns, cls))
        if not ok:
            continue
        done += 1
        if relation(xs):
            bad += 1
    return bad




def chain_inputs(N, n, rng):
    """Inputs along (Q,..,Q) -> line bundles of increasing degree on each factor -> (Q,..,Q): the class X of
    Ext^1(O_oo, O(a)), n - 2 random sections, and the evaluation; on some factors the skyscraper is replaced by
    a line bundle and X by an H^1 class or a section."""
    Q = T.skyscraper_oo()
    cols = []
    for c in range(N):
        degs_ = sorted(rng.sample([0, 2, 4, 6, 8], n - 1))
        end = Q if rng.random() < 0.7 else T.L(degs_[0] + 2 * rng.randint(-2, 0) - 2)
        cols.append([end] + [T.L(a) for a in degs_] + [end])
    xs = []
    for t in range(n):
        A = tuple(cols[c][t] for c in range(N))
        B = tuple(cols[c][t + 1] for c in range(N))
        ns = []
        for c in range(N):
            opts = [m for m in range(-1, 3) if rc(A[c], B[c]).dim(m)]
            ns.append(max(opts) if t == 0 else min(opts))
        xs.append(iota(A, B, ns, random_class(A, B, ns, rng)))
    return xs


def check_chains(N, trials, seed):
    rng = random.Random(seed)
    bad = nontriv = 0
    for _ in range(trials):
        xs = chain_inputs(N, rng.randint(3, 4), rng)
        terms = 0
        n = len(xs)
        for j in range(2, n):
            for i in range(0, n - j + 1):
                cls, tot = bn(xs[i:i + j])
                if cls and bn(xs[:i] + [iota(tot.X, tot.Y, degs(tot), cls)] + xs[i + j:])[0]:
                    terms += 1
        nontriv += terms >= 2
        bad += bool(relation(xs))
    return bad, nontriv


if __name__ == "__main__":
    ok = True
    for N, trials in ((2, 40), (3, 12)):
        bad = check(N, trials, seed=N)
        ok &= bad == 0
        print(f"A-infinity relations on E_0^{N}, random objects, n = 3 and 4:", "hold" if bad == 0 else f"{bad} failures")
    for N, trials in ((1, 30), (2, 30), (3, 10)):
        bad, nontriv = check_chains(N, trials, seed=10 + N)
        ok &= bad == 0
        print(f"A-infinity relations on E_0^{N}, chains through O_oo: {trials - bad} of {trials} hold,"
              f" {nontriv} with at least two nonzero terms")
    sys.exit(0 if ok else 1)
