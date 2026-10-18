"""Monte Carlo estimate of the Dobrushin-Shlosman block condition for gauge-fixed 4D SU(2).

The specification is gamma^F of the paper: Wilson action exp(2 beta sum_p Re Tr U_p), beta_W = 4 beta,
with the links of the forest F (one per plaquette, the table of verify_gauge.py) set to 1.  Spins are unit
quaternions with the chordal metric |U - U'| of R^4, the metric of the sharp-quarter inequality.  For a
block V of active links and an active boundary link y, the influence k_y is the least constant with
W_1(gamma_V^w, gamma_V^w') <= k_y |w_y - w'_y| for boundary conditions w, w' that differ only at y, W_1 taken
for the metric sum_{x in V} |U_x - U'_x|.  The Dobrushin-Shlosman condition in this form is
sum_y k_y < |V|; for a single link it is Dobrushin's condition sum_y k_y < 1, which the paper proves for
beta_W < 1/3 (k_y <= beta_W/4 for each of the 12 active partners).

Estimate, not a proof.  W_1 is bounded above by the stationary mean distance of a coupled heat-bath chain
(at every update: reflection-maximal coupling of the change of mean direction, then the monotone transport
of the concentration), which is a coupling of the two conditional laws, so its time average estimates an
upper bound for that boundary condition.  The supremum over boundary conditions and over the size of the
change at y is replaced by a maximum over sampled ones (random Haar and ordered boundaries; antipodal and
small changes at y), which can miss the worst case.  The printed ratio sum_y k_y / |V| is a statistical
estimate; ratio < 1 with a clear margin says the block route is worth a proof, nothing more.

    python3 ds_block.py --beta-w 0.30 0.40 0.50 --side 0 1 --replicas 64 --sweeps 400 [--workers N]

side 0 is the single-link block.  Output: one JSON line per (beta_W, side, offset) and ds_block.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

SIG = {"0000": 0, "0001": 1, "0010": 3, "0011": 3, "0100": 2, "0101": 1, "0110": 2, "0111": 0,
       "1000": 0, "1001": 2, "1010": 1, "1011": 2, "1100": 3, "1101": 3, "1110": 1, "1111": 0}
D = 4


def sigma(x):
    return SIG["".join(str(c % 2) for c in x)]


def shift(x, mu, s=1):
    y = list(x); y[mu] += s; return tuple(y)


def is_fixed(link):
    x, mu = link
    return sigma(x) == mu


def staples(link):
    """The six staples of link (x, mu): lists of (link, dagger) whose ordered product S gives Re Tr(U S)."""
    x, mu = link
    out = []
    for nu in range(D):
        if nu == mu:
            continue
        # forward: U(x+mu,nu) U(x+nu,mu)^+ U(x,nu)^+
        out.append([((shift(x, mu), nu), False), ((shift(x, nu), mu), True), ((x, nu), True)])
        # backward: U(x+mu-nu,nu)^+ U(x-nu,mu)^+ U(x-nu,nu)
        xm = shift(x, nu, -1)
        out.append([((shift(xm, mu), nu), True), ((xm, mu), True), ((xm, nu), False)])
    return out


# ---- quaternions (a0, a1, a2, a3) = a0 + i a1 + j a2 + k a3 ; SU(2) = unit quaternions, Re Tr U = 2 a0
def qmul(p, q):
    a0, a1, a2, a3 = p[..., 0], p[..., 1], p[..., 2], p[..., 3]
    b0, b1, b2, b3 = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    return np.stack([a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
                     a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
                     a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
                     a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0], axis=-1)


def qconj(p):
    return p * np.array([1.0, -1.0, -1.0, -1.0])


def haar(rng, n):
    v = rng.normal(size=(n, 4))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def log_z(kappa):
    """log of Z(k) = int exp(k a0) dHaar = 2 I_1(k)/k, by its series (k <= 40 here)."""
    k = np.asarray(kappa, dtype=float)
    h = (k / 2.0) ** 2
    term = np.ones_like(k)
    s = np.ones_like(k)
    for j in range(1, 80):
        term = term * h / (j * (j + 1))
        s = s + term
    return np.log(s)          # 2 I_1(k)/k = sum_j (k/2)^{2j} / (j! (j+1)!)


def sample_a0(rng, kappa):
    """x in [-1,1] with density proportional to sqrt(1-x^2) exp(kappa x)."""
    n = kappa.shape[0]
    x = np.empty(n)
    todo = np.arange(n)
    while todo.size:
        k = kappa[todo]
        u = rng.random(todo.size)
        small = k < 1e-9
        xs = np.where(small, 2 * u - 1, 1 + np.log1p(-u * (-np.expm1(-2 * np.maximum(k, 1e-9)))) / np.maximum(k, 1e-9))
        ok = rng.random(todo.size) < np.sqrt(np.clip(1 - xs * xs, 0, 1))
        x[todo[ok]] = xs[ok]
        todo = todo[~ok]
    return x


def heatbath(rng, A, beta_w):
    """Sample U with density exp(beta_W (U A)_0) wrt Haar; A is a sum of staples (n,4)."""
    r = np.linalg.norm(A, axis=1)
    W = A / np.maximum(r, 1e-300)[:, None]
    x = sample_a0(rng, beta_w * r)
    v = rng.normal(size=(A.shape[0], 3))
    v = v / np.linalg.norm(v, axis=1, keepdims=True) * np.sqrt(np.clip(1 - x * x, 0, 1))[:, None]
    V = np.concatenate([x[:, None], v], axis=1)
    U = qmul(V, qconj(W))
    tiny = r < 1e-12
    if tiny.any():
        U[tiny] = haar(rng, int(tiny.sum()))
    return U, r


def logp(U, A, r, beta_w):
    return beta_w * qmul(U, A)[:, 0] - log_z(beta_w * r)


GRID = np.linspace(-1.0, 1.0, 4001)


def cdf_rows(kappa):
    """CDF of the density sqrt(1-x^2) exp(kappa x) on GRID, one row per kappa."""
    g = np.sqrt(np.clip(1 - GRID ** 2, 0, 1))[None, :] * np.exp(kappa[:, None] * (GRID[None, :] - 1.0))
    c = np.concatenate([np.zeros((len(kappa), 1)), np.cumsum((g[:, 1:] + g[:, :-1]) * 0.5, axis=1)], axis=1)
    return c / c[:, -1:]


def transport_a0(a, k1, k2):
    """Monotone map of the a0-law at concentration k1 to the one at k2 (vectorised)."""
    c1, c2 = cdf_rows(k1), cdf_rows(k2)
    dx = GRID[1] - GRID[0]
    pos = np.clip((a + 1.0) / dx, 0, len(GRID) - 1.000001)
    i = pos.astype(int); f = pos - i
    rows = np.arange(len(a))
    u = c1[rows, i] * (1 - f) + c1[rows, i + 1] * f
    j = np.clip((c2 < u[:, None]).sum(axis=1), 1, len(GRID) - 1)
    lo, hi = c2[rows, j - 1], c2[rows, j]
    t = np.where(hi > lo, (u - lo) / np.maximum(hi - lo, 1e-300), 0.0)
    return GRID[j - 1] + t * dx


def coupled_step(rng, A1, A2, beta_w, U1=None):
    """A coupling of the two heat-bath laws of one link, chosen to be good in the chordal metric:
    reflection-maximal coupling for the change of mean direction (exact at equal concentration),
    then the monotone transport of the a0 coordinate for the change of concentration."""
    if U1 is None:
        U1, r1 = heatbath(rng, A1, beta_w)
    else:
        r1 = np.linalg.norm(A1, axis=1)
    r2 = np.linalg.norm(A2, axis=1)
    same = np.all(A1 == A2, axis=1)
    m1 = qconj(A1 / np.maximum(r1, 1e-300)[:, None])
    m2 = qconj(A2 / np.maximum(r2, 1e-300)[:, None])
    k1, k2 = beta_w * r1, beta_w * r2
    # step 1: vMF(m1,k1) -> vMF(m2,k1)
    diff = m1 - m2
    nd = np.linalg.norm(diff, axis=1)
    n = diff / np.maximum(nd, 1e-300)[:, None]
    stay = np.log(rng.random(len(r1))) < np.minimum(0.0, k1 * ((U1 * m2).sum(1) - (U1 * m1).sum(1)))
    refl = U1 - 2 * (U1 * n).sum(1)[:, None] * n
    Y = np.where((stay | (nd < 1e-15))[:, None], U1, refl)
    # step 2: vMF(m2,k1) -> vMF(m2,k2)
    a = np.clip((Y * m2).sum(1), -1, 1)
    P = Y - a[:, None] * m2
    move = np.abs(k1 - k2) > 1e-12
    Z = Y.copy()
    if move.any():
        a2 = transport_a0(a[move], k1[move], k2[move])
        pn = np.linalg.norm(P[move], axis=1)
        Z[move] = a2[:, None] * m2[move] + P[move] * (np.sqrt(np.clip(1 - a2 ** 2, 0, 1)) / np.maximum(pn, 1e-300))[:, None]
    Z[same] = U1[same]
    return U1, Z


def coupled_update(rng, A1, A2, beta_w, steps=1):
    """Path coupling: split the straight segment from A1 to A2 into equal steps, couple each pair of
    neighbouring laws by coupled_step, and glue.  One step is the default: on single links it stays
    within about 30 percent of the sharp Lipschitz constant beta_W/4, and more steps did worse."""
    U1, _ = heatbath(rng, A1, beta_w)
    same = np.all(A1 == A2, axis=1)
    X = U1
    for s_ in range(1, steps + 1):
        a = A1 + (A2 - A1) * ((s_ - 1) / steps)
        b = A1 + (A2 - A1) * (s_ / steps)
        _, X = coupled_step(rng, a, b, beta_w, U1=X)
    X[same] = U1[same]
    return U1, X


def block(side, offset):
    if side == 0:
        x = tuple(offset)
        for mu in range(D):
            if not is_fixed((x, mu)):
                return [(x, mu)]
    lo = offset
    box = [tuple(lo[i] + c[i] for i in range(D)) for c in itertools.product(range(side + 1), repeat=D)]
    S = set(box)
    return [(x, mu) for x in box for mu in range(D) if shift(x, mu) in S and not is_fixed((x, mu))]


def influence(args):
    beta_w, side, offset, y_index, replicas, sweeps, burn, seed, mode, pert = args
    rng = np.random.default_rng(seed)
    V = block(side, offset)
    Vset = set(V)
    st = {l: staples(l) for l in V}
    bd = sorted({lk for l in V for s in st[l] for lk, _ in s if lk not in Vset and not is_fixed(lk)})
    y = bd[y_index]
    R = replicas
    delta = 2.0 if pert == "antipodal" else 0.2
    th = 2 * math.asin(delta / 2)               # rotation by angle th moves a unit quaternion by delta
    rot = np.array([math.cos(th), math.sin(th), 0.0, 0.0])
    cfg1, cfg2 = {}, {}
    for lk in bd:
        if mode == "ordered":
            u = np.tile([1.0, 0, 0, 0], (R, 1))
        else:
            u = np.tile(haar(rng, 1), (R, 1))     # one boundary condition, R independent chains
        cfg1[lk] = u
        cfg2[lk] = u if lk != y else (-u if delta >= 2 else qmul(u, rot))
    for l in V:
        u = haar(rng, R)
        cfg1[l] = u; cfg2[l] = u.copy()
    one = np.tile([1.0, 0, 0, 0], (R, 1))

    def get(cfg, lk, dag):
        u = one if is_fixed(lk) else cfg[lk]
        return qconj(u) if dag else u

    def A(cfg, l):
        tot = np.zeros((R, 4))
        for s in st[l]:
            p = get(cfg, *s[0])
            for lk, dag in s[1:]:
                p = qmul(p, get(cfg, lk, dag))
            tot += p
        return tot

    acc = np.zeros(R)
    for t in range(burn + sweeps):
        for l in V:
            cfg1[l], cfg2[l] = coupled_update(rng, A(cfg1, l), A(cfg2, l), beta_w)
        if t >= burn:
            acc += sum(np.linalg.norm(cfg1[l] - cfg2[l], axis=1) for l in V)
    d = acc / sweeps / delta                     # Wasserstein bound per unit change at y
    return dict(y=str(y), mode=mode, pert=pert, mean=float(d.mean()), max=float(d.mean() + 2 * d.std(ddof=1) / math.sqrt(R)),
                se=float(d.std(ddof=1) / math.sqrt(R)) if R > 1 else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--beta-w", type=float, nargs="+", default=[0.30, 0.40])
    ap.add_argument("--side", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--offsets", type=int, default=1, help="how many of the 16 offsets mod 2 to test")
    ap.add_argument("--replicas", type=int, default=32, help="chains per boundary condition")
    ap.add_argument("--omegas", type=int, default=3, help="random boundary conditions per boundary link")
    ap.add_argument("--sweeps", type=int, default=200)
    ap.add_argument("--burn", type=int, default=50)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--perts", nargs="+", default=["small", "antipodal"], choices=["small", "antipodal"],
                    help="small: local Lipschitz constant; antipodal: largest change, coupling is looser")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ds_block.json"))
    a = ap.parse_args()
    offs = [tuple(c) for c in itertools.product((0, 1), repeat=D)][: a.offsets]
    results = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for bw in a.beta_w:
            for side in a.side:
                for off in offs:
                    V = block(side, off)
                    Vset = set(V)
                    bd = sorted({lk for l in V for s in staples(l) for lk, _ in s
                                 if lk not in Vset and not is_fixed(lk)})
                    jobs = [(bw, side, off, i, a.replicas, a.sweeps, a.burn, 7919 * i + 104729 * j + 13 * len(pt), m, pt)
                            for i in range(len(bd)) for j, m in enumerate(["ordered"] + ["random"] * a.omegas) for pt in a.perts]
                    res = list(ex.map(influence, jobs))
                    ks = {}
                    for r in res:
                        ks[r["y"]] = max(ks.get(r["y"], 0.0), r["max"])
                    ksum = sum(ks.values())
                    per = {}
                    for pt in a.perts:
                        kp = {}
                        for r in res:
                            if r["pert"] == pt:
                                kp[r["y"]] = max(kp.get(r["y"], 0.0), r["max"])
                        per[pt] = round(sum(kp.values()) / len(V), 4)
                    row = dict(beta_w=bw, side=side, offset=off, block_links=len(V), boundary_links=len(bd),
                               sum_k=round(ksum, 4), ratio=round(ksum / len(V), 4), ratio_by_pert=per,
                               mean_ratio=round(sum(max(r["mean"] for r in res if r["y"] == yy) for yy in ks) / len(V), 4),
                               seconds=round(time.time() - t0, 1))
                    results.append(row)
                    print(json.dumps(row), flush=True)
    json.dump(dict(note="Monte Carlo estimate, not a proof; see the module docstring", rows=results),
              open(a.out, "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
