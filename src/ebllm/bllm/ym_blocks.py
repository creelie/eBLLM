"""The block-of-links scout for the Yang-Mills forest ceiling (ledger barrier ym.forest-ceiling).

Scout for block-of-links Dobrushin in the forest gauge of 4D SU(2) lattice Yang-Mills.

Specification gamma^F of creelie/4Y-M (gauge-fixed/forest.md): links of the forest F set to 1,
each active link has conditional law vMF on S^3 with field b = 4 beta * sum of conjugated staples.
Single-link Dobrushin: alpha = 12 beta (sharp quarter, worst case b = 0), so beta_W = 4 beta < 1/3.

Block criterion (Dobrushin-Shlosman / Weitz, cover by translates of a block V):
    alpha_V = (1/|V|) * sum_{j not in V} kappa_{V,j},
    kappa_{V,j} = sup_eta W1^sum(mu_V^eta, mu_V^eta') / |eta_j - eta'_j|.
Here kappa is bounded ABOVE by a coupling: two block heat-bath chains with boundary conditions
eta and eta' (eta' = eta with link j rotated by eps), synchronous coupling (shared uniforms),
distance sum_x |u_x - u'_x| averaged at stationarity. Any coupling of the two stationary laws
gives an upper bound on W1, so this is an upper estimate, up to Monte Carlo error. The sup over
eta is replaced by a max over sampled boundary conditions: this is NOT a proof, it is a scout
deciding which block to certify with interval arithmetic.
"""
import itertools
import numpy as np

SIG = [0, 0, 2, 3, 3, 1, 2, 1, 1, 2, 1, 3, 3, 2, 0, 0]
def sigma(x): return SIG[(x[0] % 2) + 2 * (x[1] % 2) + 4 * (x[2] % 2) + 8 * (x[3] % 2)]
def is_F(link):
    x, mu = link
    return sigma(x) == mu
E = [tuple(int(i == k) for i in range(4)) for k in range(4)]
def add(x, k, s=1): return tuple(x[i] + s * E[k][i] for i in range(4))

def plaquettes_of(link):
    """The six plaquettes containing link, as lists of (link, inverted?) in path order."""
    x, mu = link; out = []
    for nu in range(4):
        if nu == mu: continue
        # plaquette based at x in plane (mu,nu): U_{x,mu} U_{x+mu,nu} U_{x+nu,mu}^-1 U_{x,nu}^-1
        out.append([((x, mu), False), ((add(x, mu), nu), False), ((add(x, nu), mu), True), ((x, nu), True)])
        y = add(x, nu, -1)  # plaquette based at x-nu: U_{y,nu} U_{y+nu,mu} U_{y+mu,nu}^-1 U_{y,mu}^-1, y+nu = x
        out.append([((y, nu), False), ((x, mu), False), ((add(y, mu), nu), True), ((y, mu), True)])
    return out

# quaternion helpers (w,x,y,z), unit quaternions = SU(2)
def qmul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2, w1*x2 + x1*w2 + y1*z2 - z1*y2,
                     w1*y2 - x1*z2 + y1*w2 + z1*x2, w1*z2 + x1*y2 - y1*x2 + z1*w2])
def qconj(a): return np.array([a[0], -a[1], -a[2], -a[3]])
ONE = np.array([1.0, 0, 0, 0])

def staple_field(link, val):
    """b/(4 beta) for link: sum over its plaquettes of the conjugated staple, so that
    ReTr(Q_p) = 2 <u, conj(staple)> (staple = product of the other three links in cyclic order)."""
    tot = np.zeros(4)
    for p in plaquettes_of(link):
        k = [i for i, (l, inv) in enumerate(p) if l == link][0]
        assert not p[k][1]
        # cyclic product starting after link: Q = U_link * S (cyclic), ReTr Q = ReTr(U S) = 2<u, conj(S)>
        S = ONE
        for i in range(1, 4):
            l, inv = p[(k + i) % 4]
            g = ONE if is_F(l) else val[l]
            S = qmul(S, qconj(g) if inv else g)
        tot += qconj(S)
    return tot

# inverse CDF tables for w = <u, bhat> with density ∝ sqrt(1-w^2) exp(kappa w)
WG = np.linspace(-1, 1, 4001)
KG = np.linspace(0, 12, 1201)
CDF = []
for kap in KG:
    f = np.sqrt(np.clip(1 - WG**2, 0, None)) * np.exp(kap * (WG - 1))
    c = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2)]); CDF.append(c / c[-1])
CDF = np.array(CDF)
def sample_w(kap, U):
    x = min(kap / (KG[1] - KG[0]), len(KG) - 1.000001); i = int(x); t = x - i
    return (1 - t) * np.interp(U, CDF[i], WG) + t * np.interp(U, CDF[i + 1], WG)

def heat_bath(b, z):
    """Transport map T_b from Haar to vMF_b applied to a shared Haar point z: the component of z
    along bhat is moved by the monotone 1D map F_kappa^{-1} o F_0, the orthogonal direction is kept.
    T_b -> identity as b -> 0, so the synchronous coupling is Lipschitz in b."""
    kap = np.linalg.norm(b)
    if kap < 1e-12:
        return z.copy()
    bh = b / kap; w0 = float(np.dot(z, bh))
    w = sample_w(kap, np.interp(w0, WG, CDF[0]))
    v = z - w0 * bh; nv = np.linalg.norm(v)
    if nv < 1e-14:
        return bh * np.sign(w)
    return w * bh + np.sqrt(max(0.0, 1 - w * w)) * v / nv

def random_su2(rng):
    q = rng.normal(size=4); return q / np.linalg.norm(q)

def block_and_boundary(V):
    V = [l for l in V if not is_F(l)]
    bd = set()
    for l in V:
        for p in plaquettes_of(l):
            for m, _ in p:
                if m not in V and not is_F(m): bd.add(m)
    return V, sorted(bd)

def kappa(V, j, beta, rng, n_eta=6, sweeps=400, burn=100, eps=1e-3):
    """max over sampled eta of the coupled-chain estimate of W1^sum / eps."""
    best = 0.0
    Vs, bd = block_and_boundary(V)
    for _ in range(n_eta):
        eta = {m: random_su2(rng) for m in bd}
        eta2 = dict(eta); ax = rng.normal(size=3); ax /= np.linalg.norm(ax)
        rot = np.concatenate([[np.cos(eps / 2)], np.sin(eps / 2) * ax])
        eta2[j] = qmul(eta[j], rot); dj = np.linalg.norm(eta2[j] - eta[j])
        A = dict(eta); B = dict(eta2)
        for l in Vs: A[l] = B[l] = random_su2(rng)
        acc = 0.0; n = 0
        for s in range(sweeps):
            for l in Vs:
                z = random_su2(rng)
                A[l] = heat_bath(4 * beta * staple_field(l, A), z)
                B[l] = heat_bath(4 * beta * staple_field(l, B), z)
            if s >= burn:
                acc += sum(np.linalg.norm(A[l] - B[l]) for l in Vs); n += 1
        best = max(best, acc / n / dj)
    return best

def alpha_block(V, beta, rng, **kw):
    Vs, bd = block_and_boundary(V)
    ks = {j: kappa(Vs, j, beta, rng, **kw) for j in bd}
    return sum(ks.values()) / len(Vs), len(Vs), len(bd), ks


# Measured with this module (n_eta=2..3, 120-150 sweeps, seeds 7 and 11), as upper estimates of alpha_V;
# the coupling overhead at b = 0 is 1.13 (0.283 against the optimal 1/4), so divide by 1.13 for a
# calibrated estimate. Single-link worst case is 12 beta = 3 beta_W.
SCOUT = {
    "single link": {0.3: 1.017, 0.3333: 1.126, 0.4: 1.342, 0.5: 1.654},
    "plaquette (3 active links)": {0.3: 0.959, 0.3333: 1.075, 0.4: 1.312, 0.5: 1.673},
    "unit 3-cube (9 active links)": {0.3: 0.873, 0.3333: 0.992, 0.4: 1.240, 0.5: 1.639},
    "unit 4-cube (24 active links)": {0.3333: 0.871, 0.37: 1.006, 0.4: 1.123},
}
COUPLING_OVERHEAD = 1.13


def scout_crossing(block: str, calibrated: bool = True):
    """Smallest measured beta_W at which the (calibrated) estimate reaches 1, or None. Not a proof."""
    rows = sorted(SCOUT[block].items())
    f = COUPLING_OVERHEAD if calibrated else 1.0
    prev = None
    for bw, a in rows:
        a = a / f
        if a >= 1:
            if prev is None:
                return bw
            (b0, a0) = prev
            return b0 + (1 - a0) * (bw - b0) / (a - a0)
        prev = (bw, a)
    return None


def unit_cube4():
    o = (0, 0, 0, 0)
    return [(c, mu) for c in itertools.product((0, 1), repeat=4) for mu in range(4) if c[mu] == 0]
