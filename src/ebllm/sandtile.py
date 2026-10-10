"""Section 10: sand-tile toppling of proof burden, in exact rational arithmetic.

Each obligation site v carries a height h(v) (debt + risk + residue - certification).  A site
with h(v) > theta(v) topples: it loses Delta(v) and each neighbour u gains K[u][v] * Delta(v).
With sum_u K[u][v] = 1 the toppling conserves burden; with sum < 1 the rest is absorbed into
the typed-residue ledger.

The paper states (Theorem 10.4) that the number of topplings is at most
H0 * |Lambda| * diam(Lambda) / theta_min, and (Proposition 10.2) that on a locally finite graph
a finite-energy conservative run either stabilizes or exposes an infinite dependency path.
Both are false as stated; `counterexample_conservative` and `counterexample_dissipative` give
the counterexamples, and `lean/EBLLM/SandTile.lean` checks them in the kernel.  What does hold
is the classical abelian property when Delta and K are fixed (a toppling never makes another
unstable site stable), which `abelian_check` tests.
"""
from __future__ import annotations

import random
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

Num = Fraction


class SandTile:
    def __init__(self, n: int, edges: Sequence[Tuple[int, int]], theta, delta, kernel=None):
        """n sites 0..n-1; undirected edges; theta[v], delta[v]; kernel[(u, v)] = K_uv (the
        share of Delta(v) that goes to u).  The default kernel splits Delta(v) equally among the
        neighbours of v (conservative)."""
        self.n = n
        self.adj: List[List[int]] = [[] for _ in range(n)]
        for a, b in edges:
            self.adj[a].append(b)
            self.adj[b].append(a)
        self.theta = [Num(x) for x in theta]
        self.delta = [Num(x) for x in delta]
        if any(d <= 0 for d in self.delta):
            raise ValueError("topple amounts must be positive")
        if kernel is None:
            kernel = {(u, v): Num(1, len(self.adj[v])) for v in range(n) for u in self.adj[v]}
        self.K = {k: Num(x) for k, x in kernel.items()}
        for v in range(n):
            s = sum(self.K.get((u, v), 0) for u in self.adj[v])
            if s > 1 or any(self.K.get((u, v), 0) < 0 for u in self.adj[v]):
                raise ValueError("kernel shares must be nonnegative with sum at most 1")

    def unstable(self, h) -> List[int]:
        return [v for v in range(self.n) if h[v] > self.theta[v]]

    def topple(self, h, v) -> Tuple[list, Num]:
        """Topple site v; returns the new heights and the burden absorbed into the residue ledger."""
        h = list(h)
        d = self.delta[v]
        h[v] -= d
        passed = Num(0)
        for u in self.adj[v]:
            share = self.K.get((u, v), 0) * d
            h[u] += share
            passed += share
        return h, d - passed

    def stabilize(self, h0, order: str = "lowest", max_topples: int = 100000, seed: int = 0):
        """Topple until stable.  Returns (final heights, number of topplings, absorbed residue),
        or None if `max_topples` topplings did not stabilize the configuration."""
        h = [Num(x) for x in h0]
        rng = random.Random(seed)
        absorbed = Num(0)
        for count in range(max_topples + 1):
            u = self.unstable(h)
            if not u:
                return h, count, absorbed
            if count == max_topples:
                return None
            v = u[0] if order == "lowest" else rng.choice(u)
            h, a = self.topple(h, v)
            absorbed += a
        return None

    def bound_theorem_10_4(self, h0) -> Num:
        """The bound H0 * |Lambda| * diam(Lambda) / theta_min claimed by Theorem 10.4."""
        return Num(max(h0)) * self.n * self.diameter() / min(self.theta)

    def diameter(self) -> int:
        best = 0
        for s in range(self.n):
            dist = {s: 0}
            frontier = [s]
            while frontier:
                nxt = []
                for x in frontier:
                    for y in self.adj[x]:
                        if y not in dist:
                            dist[y] = dist[x] + 1
                            nxt.append(y)
                frontier = nxt
            if len(dist) < self.n:
                raise ValueError("graph is disconnected")
            best = max(best, max(dist.values()))
        return best


def counterexample_conservative():
    """Two sites joined by an edge, conservative kernel, theta = 1/2, Delta = 1, heights (1, 1).
    Every toppling moves one unit across the edge and leaves one site above 1/2, so the run never
    stabilizes; the graph is finite, so there is no infinite dependency path either
    (against Proposition 10.2), and Theorem 10.4's bound is (1 * 2 * 1) / (1/2) = 4."""
    st = SandTile(2, [(0, 1)], theta=[Num(1, 2)] * 2, delta=[1, 1])
    return st, [Num(1), Num(1)]


def counterexample_dissipative(eps=Num(1, 100)):
    """Two sites, theta = 1, Delta = 2, kernel share 1 - eps (eps is absorbed), heights (2, 2).
    Every toppling satisfies Delta >= theta_min, as the proof of Theorem 10.4 assumes, yet the run
    needs about 1/eps topplings, while the bound is (2 * 2 * 1) / 1 = 4."""
    k = 1 - Num(eps)
    st = SandTile(2, [(0, 1)], theta=[1, 1], delta=[2, 2], kernel={(0, 1): k, (1, 0): k})
    return st, [Num(2), Num(2)]


def chip_firing(n: int, edges, sink: int):
    """Classical chip-firing with a sink: a site with at least deg(v) chips sends one chip along
    each edge; chips sent to the sink disappear.  In the threshold form above, theta(v) =
    deg(v) - 1 and Delta(v) = deg(v), with the share to the sink absorbed."""
    st_edges = [(a, b) for a, b in edges]
    adj = [[] for _ in range(n)]
    for a, b in st_edges:
        adj[a].append(b)
        adj[b].append(a)
    theta = [len(adj[v]) - 1 for v in range(n)]
    delta = [max(1, len(adj[v])) for v in range(n)]
    kernel = {}
    for v in range(n):
        for u in adj[v]:
            kernel[(u, v)] = Num(0) if u == sink else Num(1, len(adj[v]))
    theta[sink] = 10 ** 18  # the sink never topples
    return SandTile(n, st_edges, theta, delta, kernel)


def abelian_check(trials: int = 50, seed: int = 1) -> bool:
    """On random connected graphs with a sink, the stable configuration and the number of
    topplings do not depend on the order of topplings (the abelian property)."""
    rng = random.Random(seed)
    for t in range(trials):
        n = rng.randint(4, 9)
        edges = [(i, rng.randrange(i)) for i in range(1, n)]
        for _ in range(rng.randint(0, n)):
            a, b = rng.sample(range(n), 2)
            if (a, b) not in edges and (b, a) not in edges:
                edges.append((a, b))
        st = chip_firing(n, edges, sink=0)
        h0 = [0] + [rng.randint(0, 3 * len(st.adj[v])) for v in range(1, n)]
        results = set()
        for s in range(5):
            r = st.stabilize(h0, order="random", seed=s, max_topples=10 ** 6)
            if r is None:
                return False
            h, c, _ = r
            results.add((tuple(h[1:]), c))
        if len(results) != 1:
            return False
    return True
