"""Brain-style parts: a spiking selector that learns which agent to run, and real connectomes.

SpikingSelector
    One leaky integrate-and-fire neuron per agent, with escape noise: neuron k fires in a step of
    length dt with probability 1 - exp(-rho0 * exp((u_k - theta) / delta) * dt).  Its membrane
    relaxes to its synaptic weight w_k with time constant tau, so after a few tau it fires as a
    Poisson process of rate rho0 exp((w_k - theta)/delta).  The first neuron to spike chooses the
    agent; for independent Poisson neurons the first spike comes from k with probability equal to
    its share of the total rate, so the circuit samples agents with probability proportional to
    exp(w_k / delta).  A third factor, a reward signal sent when the checks keep a result,
    potentiates the synapse of the neuron that fired:
        w_k <- w_k + (delta / 2) log((c_k + 1 + alpha) / (c_k + alpha)),  c_k <- c_k + 1,
    and synaptic scaling then shifts every weight by the same amount so that the total rate stays
    rho0 (a shift that leaves the choice probabilities unchanged).  So w_k = (delta / 2) log(c_k +
    alpha) up to a common constant and the circuit samples agents with probability proportional
    to sqrt(c_k + alpha), up to an error of order rho0 * dt from the time step: square-root sampling of the needs it has
    learned, the optimum of the gap law (Theorem I).  Nothing in the circuit is trusted: it only
    decides which agent proposes next, and every proposal still goes through the checks.

Connectome
    A directed weighted graph loaded from published wiring data: the C. elegans hermaphrodite of
    Cook et al. (Nature 571, 2019; the edge list distributed by OpenWorm), the adult Drosophila
    brain of FlyWire (Dorkenwald et al., Nature 634, 2024; proofread_connections_783 from Zenodo
    10.5281/zenodo.10676866, CC BY 4.0), aggregated by neuropil, and the somas of the human
    cortical fragment H01 (Shapson-Coe et al., Science 384, 2024).  The files are not bundled;
    download them and pass their paths.  The graph gives its processing depth (the solution of
    L z = in-weight - out-weight of Varshney et al., PLoS Comput. Biol. 7, 2011), its Fiedler
    vector, and an echo-state reservoir whose recurrent weights are the wiring itself.

Everything is pure Python; the FlyWire feather file needs pyarrow, and CSV exports need nothing.
"""
from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# -- the spiking selector -----------------------------------------------------------------------
@dataclass
class SpikingSelector:
    names: Sequence[str]
    tau: float = 10.0            # membrane time constant, ms
    dt: float = 0.5              # integration step, ms
    theta: float = 1.0           # soft threshold
    delta: float = 0.25          # escape-noise width
    rho0: float = 0.02           # rate at threshold, per ms
    alpha: float = 0.5           # prior count (Jeffreys)
    max_steps: int = 200000
    w: List[float] = field(default_factory=list)
    counts: List[float] = field(default_factory=list)
    spikes: List[Tuple[int, float]] = field(default_factory=list)

    def __post_init__(self):
        n = len(self.names)
        if n == 0:
            raise ValueError("need at least one agent")
        if not self.w:
            self.w = [self.theta] * n
        if not self.counts:
            self.counts = [0.0] * n
        self._scale()

    def _scale(self) -> None:
        """Synaptic scaling: a common shift of the weights that keeps the total rate at rho0."""
        tot = sum(self.rates())
        shift = self.delta * math.log(self.rho0 / tot)
        self.w = [x + shift for x in self.w]

    def rates(self) -> List[float]:
        return [self.rho0 * math.exp((x - self.theta) / self.delta) for x in self.w]

    def probabilities(self) -> List[float]:
        """The stationary first-spike probabilities: each neuron's share of the total rate."""
        r = self.rates()
        s = sum(r)
        return [x / s for x in r]

    def race(self, rng: random.Random, exclude: Iterable[int] = (), settle: Optional[float] = None) -> int:
        """Integrate the membranes from rest until the first spike among the neurons not excluded;
        `settle` (default 5 tau) is the time the membranes relax before the race opens."""
        ex = set(exclude)
        live = [k for k in range(len(self.names)) if k not in ex]
        if not live:
            raise ValueError("every neuron is excluded")
        u = {k: 0.0 for k in live}
        decay = math.exp(-self.dt / self.tau)
        t, open_at = 0.0, 5 * self.tau if settle is None else settle
        for _ in range(self.max_steps):
            t += self.dt
            for k in live:
                u[k] = self.w[k] + (u[k] - self.w[k]) * decay
            if t < open_at:
                continue
            fired = [k for k in live
                     if rng.random() < 1 - math.exp(-self.rho0 * math.exp((u[k] - self.theta) / self.delta) * self.dt)]
            if fired:
                k = rng.choice(fired)                    # simultaneous spikes: a fair tie-break
                self.spikes.append((k, t))
                return k
        raise RuntimeError("no spike: raise rho0 or the weights")

    def order(self, rng: random.Random) -> List[int]:
        """An order of all agents by successive races without replacement."""
        out: List[int] = []
        while len(out) < len(self.names):
            out.append(self.race(rng, exclude=out))
        return out

    def reward(self, k: int, amount: float = 1.0) -> None:
        """The third factor: a kept result from agent k potentiates its synapse."""
        if amount <= 0:
            return
        c = self.counts[k]
        self.w[k] += 0.5 * self.delta * math.log((c + amount + self.alpha) / (c + self.alpha))
        self.counts[k] = c + amount
        self._scale()

    def target(self) -> List[float]:
        """Square-root sampling of the learned needs, which the probabilities equal exactly."""
        s = [math.sqrt(c + self.alpha) for c in self.counts]
        t = sum(s)
        return [x / t for x in s]


# -- connectomes ---------------------------------------------------------------------------------
@dataclass
class Connectome:
    nodes: List[str]
    edges: Dict[Tuple[int, int], float]
    kinds: Dict[Tuple[int, int], str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)
    source: str = ""

    @property
    def index(self) -> Dict[str, int]:
        return {n: i for i, n in enumerate(self.nodes)}

    def add(self, a: str, b: str, w: float, kind: str = "") -> None:
        idx = self._idx
        for n in (a, b):
            if n not in idx:
                idx[n] = len(self.nodes)
                self.nodes.append(n)
        e = (idx[a], idx[b])
        self.edges[e] = self.edges.get(e, 0.0) + w
        if kind:
            self.kinds[e] = kind

    def __post_init__(self):
        self._idx = {n: i for i, n in enumerate(self.nodes)}

    def degrees(self) -> Tuple[List[float], List[float]]:
        n = len(self.nodes)
        win, wout = [0.0] * n, [0.0] * n
        for (a, b), w in self.edges.items():
            wout[a] += w
            win[b] += w
        return win, wout

    def symmetric(self) -> List[Dict[int, float]]:
        """The adjacency of (W + W^T)/2 as sparse rows, without self-loops."""
        rows: List[Dict[int, float]] = [dict() for _ in self.nodes]
        for (a, b), w in self.edges.items():
            if a == b:
                continue
            rows[a][b] = rows[a].get(b, 0.0) + w / 2
            rows[b][a] = rows[b].get(a, 0.0) + w / 2
        return rows

    def processing_depth(self, iters: int = 5000, tol: float = 1e-10) -> List[float]:
        """Varshney et al.: solve L z = b with L the Laplacian of (W + W^T)/2 and b = in - out
        weight, by conjugate gradients on each connected component (z has mean 0 on it); a high z
        means far from the senses, deep in the processing."""
        rows = self.symmetric()
        n = len(rows)
        deg = [sum(r.values()) for r in rows]
        win, wout = self.degrees()
        b = [x - y for x, y in zip(win, wout)]
        comp = _components(rows)
        z = [0.0] * n
        for members in comp:
            if len(members) < 2:
                continue
            m = set(members)
            bb = {i: b[i] for i in members}
            mean = sum(bb.values()) / len(members)
            bb = {i: v - mean for i, v in bb.items()}
            x = {i: 0.0 for i in members}
            r = dict(bb)
            p = dict(r)
            rs = sum(v * v for v in r.values())
            for _ in range(iters):
                Ap = {i: deg[i] * p[i] - sum(w * p[j] for j, w in rows[i].items() if j in m) for i in members}
                pAp = sum(p[i] * Ap[i] for i in members)
                if pAp <= 0:
                    break
                a = rs / pAp
                for i in members:
                    x[i] += a * p[i]
                    r[i] -= a * Ap[i]
                rs2 = sum(v * v for v in r.values())
                if rs2 < tol * tol:
                    break
                for i in members:
                    p[i] = r[i] + rs2 / rs * p[i]
                rs = rs2
            mx = sum(x.values()) / len(members)
            for i in members:
                z[i] = x[i] - mx
        return z

    def fiedler(self, iters: int = 3000, seed: int = 3) -> List[float]:
        """The Fiedler vector of the normalised Laplacian of the largest component, by power
        iteration on 2I - L_norm with the constant direction (D^1/2 1) projected out."""
        rows = self.symmetric()
        comp = max(_components(rows), key=len)
        m = set(comp)
        deg = {i: sum(w for j, w in rows[i].items() if j in m) for i in comp}
        sq = {i: math.sqrt(deg[i]) for i in comp}
        nrm = math.sqrt(sum(d for d in deg.values()))
        e0 = {i: sq[i] / nrm for i in comp}
        rng = random.Random(seed)
        v = {i: rng.random() - 0.5 for i in comp}
        for _ in range(iters):
            dot = sum(v[i] * e0[i] for i in comp)
            v = {i: v[i] - dot * e0[i] for i in comp}
            # (2I - L_norm) v = v + D^-1/2 W D^-1/2 v
            v = {i: v[i] + sum(w * v[j] / (sq[i] * sq[j]) for j, w in rows[i].items() if j in m) for i in comp}
            s = math.sqrt(sum(x * x for x in v.values()))
            v = {i: x / s for i, x in v.items()}
        out = [0.0] * len(rows)
        for i in comp:
            out[i] = v[i] / sq[i]
        return out


def _components(rows: List[Dict[int, float]]) -> List[List[int]]:
    seen, out = set(), []
    for s in range(len(rows)):
        if s in seen:
            continue
        stack, comp = [s], []
        seen.add(s)
        while stack:
            i = stack.pop()
            comp.append(i)
            for j in rows[i]:
                if j not in seen:
                    seen.add(j)
                    stack.append(j)
        out.append(comp)
    return out


def load_edge_list(path: str, source: str = "", kinds: Optional[Sequence[str]] = None) -> Connectome:
    """A CSV with columns Source, Target, Weight and optionally Type (the OpenWorm edge lists of
    Cook et al. 2019: chemical and electrical synapses); padded fields are stripped."""
    g = Connectome([], {}, source=source or path)
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        head = [h.strip().lower() for h in next(rd)]
        ia, ib, iw = head.index("source"), head.index("target"), head.index("weight")
        it = head.index("type") if "type" in head else None
        for row in rd:
            if not row or len(row) <= max(ia, ib, iw):
                continue
            t = row[it].strip() if it is not None else ""
            if kinds is not None and t not in kinds:
                continue
            g.add(row[ia].strip(), row[ib].strip(), float(row[iw]), t)
    return g


def load_flywire_neuropils(path: str, min_syn: int = 5) -> Connectome:
    """FlyWire connections aggregated to the graph of neuropils: a neuron whose input synapses lie
    mostly in neuropil P and which makes a connection in neuropil Q adds that connection's synapses
    to the edge P -> Q, the flow of information through the neuron.  The file is
    proofread_connections_783 (feather needs pyarrow; a CSV export needs nothing), with columns
    pre_pt_root_id, post_pt_root_id, neuropil and syn_count; connections of fewer than min_syn
    synapses are dropped, as in the FlyWire analyses."""
    rows = _read_table(path, ["pre_pt_root_id", "post_pt_root_id", "neuropil", "syn_count"])
    in_np: Dict[str, Dict[str, int]] = {}
    conns = []
    for pre, post, npl, n in rows:
        n = int(n)
        if n < min_syn:
            continue
        d = in_np.setdefault(post, {})
        d[npl] = d.get(npl, 0) + n
        conns.append((pre, npl, n))
    home = {k: max(v, key=v.get) for k, v in in_np.items()}
    g = Connectome([], {}, source=path)
    for pre, npl, n in conns:
        if pre in home:
            g.add(home[pre], npl, float(n))
    return g


def _read_table(path: str, cols: Sequence[str]):
    if path.endswith(".feather") or path.endswith(".arrow"):
        try:
            import pyarrow.feather as feather            # optional
        except ImportError as exc:
            raise RuntimeError("reading a feather file needs pyarrow; or pass a CSV export") from exc
        t = feather.read_table(path, columns=list(cols))
        arrays = [t.column(c).to_pylist() for c in cols]
        return [tuple(str(a) if i < 3 else a for i, a in enumerate(r)) for r in zip(*arrays)]
    with open(path, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        return [tuple(r[c] for c in cols) for r in rd]


def load_h01_somas(path: str) -> List[dict]:
    """The somas of the human temporal-cortex fragment H01: x, y, z in voxels of 8 x 8 x 33 nm,
    cell type and cortical layer.  Coordinates are returned in micrometres."""
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                out.append(dict(x=float(r["x"]) * 0.008, y=float(r["y"]) * 0.008, z=float(r["z"]) * 0.033,
                                celltype=r.get("celltype", ""), layer=r.get("layer", "")))
            except (KeyError, ValueError):
                continue
    return out


# -- a reservoir wired like a brain --------------------------------------------------------------
@dataclass
class Reservoir:
    """An echo-state network x <- (1 - leak) x + leak tanh(W x + U u) whose recurrent matrix W is
    a connectome scaled to spectral radius `radius`; a ridge readout is fitted on the states."""
    graph: Connectome
    radius: float = 0.9
    leak: float = 0.5
    inputs: int = 1
    seed: int = 7
    W: List[Dict[int, float]] = field(default_factory=list)
    U: List[List[float]] = field(default_factory=list)

    def __post_init__(self):
        n = len(self.graph.nodes)
        rows: List[Dict[int, float]] = [dict() for _ in range(n)]
        rng = random.Random(self.seed)
        sign: Dict[int, float] = {}
        for (a, b), w in self.graph.edges.items():
            s = sign.setdefault(a, 1.0 if rng.random() < 0.8 else -1.0)    # Dale's law: one sign per neuron
            rows[b][a] = rows[b].get(a, 0.0) + s * math.log1p(w)
        rho = _spectral_radius(rows)
        k = self.radius / rho if rho > 0 else 0.0
        self.W = [{j: k * w for j, w in r.items()} for r in rows]
        self.U = [[rng.uniform(-1, 1) for _ in range(self.inputs)] for _ in range(n)]

    def states(self, us: Sequence[Sequence[float]]) -> List[List[float]]:
        n = len(self.W)
        x = [0.0] * n
        out = []
        for u in us:
            pre = [sum(w * x[j] for j, w in self.W[i].items()) + sum(a * b for a, b in zip(self.U[i], u))
                   for i in range(n)]
            x = [(1 - self.leak) * xi + self.leak * math.tanh(p) for xi, p in zip(x, pre)]
            out.append(x)
        return out

    @staticmethod
    def ridge(X: Sequence[Sequence[float]], y: Sequence[float], lam: float = 1e-3) -> List[float]:
        """Least squares with a ridge penalty, by the normal equations (with a bias column)."""
        Z = [list(r) + [1.0] for r in X]
        d = len(Z[0])
        A = [[sum(Z[k][i] * Z[k][j] for k in range(len(Z))) + (lam if i == j else 0.0) for j in range(d)]
             for i in range(d)]
        b = [sum(Z[k][i] * y[k] for k in range(len(Z))) for i in range(d)]
        return _solve(A, b)

    @staticmethod
    def predict(beta: Sequence[float], X: Sequence[Sequence[float]]) -> List[float]:
        return [sum(a * b for a, b in zip(beta, list(r) + [1.0])) for r in X]


def _spectral_radius(rows: List[Dict[int, float]], iters: int = 300) -> float:
    """|lambda_max| by power iteration on W^T W (the largest singular value, an upper bound for
    the spectral radius, which is what keeps the echo-state property)."""
    n = len(rows)
    v = [1.0 / math.sqrt(n)] * n
    s = 0.0
    for _ in range(iters):
        wv = [sum(w * v[j] for j, w in r.items()) for r in rows]
        wtw = [0.0] * n
        for i, r in enumerate(rows):
            for j, w in r.items():
                wtw[j] += w * wv[i]
        s = math.sqrt(sum(x * x for x in wtw))
        if s == 0:
            return 0.0
        v = [x / s for x in wtw]
    return math.sqrt(s)


def _solve(A: List[List[float]], b: List[float]) -> List[float]:
    n = len(b)
    M = [row[:] + [bb] for row, bb in zip(A, b)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-300:
            raise ValueError("singular system")
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            if f:
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (M[r][n] - sum(M[r][k] * x[k] for k in range(r + 1, n))) / M[r][r]
    return x


def memory_capacity(res: Reservoir, delays: Sequence[int] = (1, 2, 4, 8), steps: int = 600,
                    washout: int = 100, seed: int = 11, readout: int = 60) -> Dict[int, float]:
    """The squared correlation between the input k steps back and its best linear readout from
    `readout` reservoir units: the short-term memory of a circuit wired like the given brain."""
    rng = random.Random(seed)
    u = [rng.uniform(-1, 1) for _ in range(steps)]
    S = res.states([[x] for x in u])
    units = list(range(min(readout, len(S[0]))))
    half = washout + (steps - washout) // 2
    out = {}
    for k in delays:
        Xtr = [[S[t][i] for i in units] for t in range(washout, half)]
        ytr = [u[t - k] for t in range(washout, half)]
        beta = Reservoir.ridge(Xtr, ytr, 1e-4)
        Xte = [[S[t][i] for i in units] for t in range(half, steps)]
        yte = [u[t - k] for t in range(half, steps)]
        p = Reservoir.predict(beta, Xte)
        out[k] = _corr2(p, yte)
    return out


def _corr2(a: Sequence[float], b: Sequence[float]) -> float:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    return cov * cov / (va * vb) if va > 0 and vb > 0 else 0.0
