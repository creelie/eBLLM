"""The layer tower B^n over construction mode.

Layer 1 is the goal-directed builder: it grows a gadget from the rules (and from
library gadgets used as lemmas) until the contacts can no longer share a colour.
Layer 2 acts on layer 1, not on the target: it keeps a population of builder
strategies (move priorities, noise, how often to try a lemma), runs each one for
a slice of checks, keeps the strategies that reach gadgets in fewer checks and
mutates them (the evolve-and-evaluate loop of FunSearch and AlphaEvolve, with a
fixed strategy space in place of program text), and it sets a curriculum: an
easier contact profile is attacked first and the gadget it yields joins the
library as a lemma for the harder one (as AlphaProof trains on easier variants
before the statement it wants). Layer k >= 3 acts on layer k - 1 the same way:
it runs several copies of layer k - 1 with different settings and keeps the
better half after each round (successive halving).

Two wirings. In the ladder each layer sees only what the layer directly below
returns: every copy of a layer has its own library. In the mesh every layer
reads and writes one library, so a gadget found at the bottom of one branch is
a lemma everywhere at once, and Hebbian synapses on the move kinds (strengthened
by the moves of every gadget found, decaying otherwise) bias the strategies of
all layers.

Whatever path it took, a gadget counts only when the independent checks of
graphcheck accept it: planar with the contacts on one face, no cycle of a
forbidden length, the contact distances, and no 3-colouring with the contacts
equal, found by backtracking, which shares no code with the SAT search.
Budgets and costs are counted in exact SAT checks (proof_builder.CHECKS).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
import time
from dataclasses import asdict, dataclass, field

import networkx as nx

from . import gadget
from . import graphcheck as gc
from . import proof_builder as pb


@dataclass(frozen=True)
class Target:
    name: str
    forbid: tuple
    goal: tuple                 # minimum distances of the contact pairs (0,1), (0,2), (1,2)
    ladder: tuple = ()          # easier profiles a curriculum solves first
    max_n: int = 60
    max_steps: int = 300
    seeds: tuple = ()           # stored gadgets the library starts with
    note: str = ""


TARGETS = {
    "steinberg-g1": Target("steinberg-g1", (4, 5), (3, 3, 4), (), 40, 200, (),
                           "the profile of Steinberg's 15-vertex gadget G1, from the rules alone"),
    "steinberg-g2": Target("steinberg-g2", (4, 5), (4, 4, 4), ((3, 3, 4),), 80, 400, ("T",),
                           "the profile of Steinberg's 42-vertex gadget G2, from the rules and the triangle gadget T"),
    "erdos-k6": Target("erdos-k6", (4, 5, 6), (3, 3, 5), ((3, 3, 4),), 100, 400, ("T", "G1prime"),
                       "a gadget that would answer Erdos's question (no 4-, 5-, 6-cycles); open"),
}

DEFAULT_POLICY = {"pri": dict(pb.PRI), "noise": 2.5, "lemma_tries": 4}


def need(profile):
    return {(0, 1): profile[0], (0, 2): profile[1], (1, 2): profile[2]}


def meets(G, forbid, profile):
    """The gate: independent of the search code."""
    contacts = [0, 1, 2]
    if not gc.planar_with_face(G, contacts):
        return False
    if gc.cycle_lengths_present(G, max(forbid)) & set(forbid):
        return False
    d = gc.contact_distances(G, contacts)
    if any(d[p] is not None and d[p] < k for p, k in need(profile).items()):
        return False
    return not gc.three_colourable(G, {c: 0 for c in contacts})


def fingerprint(G):
    H = G.copy()
    nx.set_node_attributes(H, {v: ("c" if v in (0, 1, 2) else "") for v in H}, "r")
    return nx.weisfeiler_lehman_graph_hash(H, node_attr="r")


def distances(G):
    d = gc.contact_distances(G, [0, 1, 2])
    return tuple(d[p] if d[p] is not None else 99 for p in ((0, 1), (0, 2), (1, 2)))


def covers(dist, profile):
    """Some relabelling of the contacts meets the profile (lemmas are used in every role)."""
    pairs = ((0, 1), (0, 2), (1, 2))
    dd = dict(zip(pairs, dist))
    for s in itertools.permutations(range(3)):
        got = [dd[tuple(sorted((s[i], s[j])))] for i, j in pairs]
        if all(g >= k for g, k in zip(got, profile)):
            return True
    return False


class Library:
    def __init__(self, names=()):
        self.items = []          # (name, graph, contact distances)
        self.keys = set()
        for nm in names:
            G, _ = gadget(nm)
            self.add(G, nm)

    def add(self, G, name):
        k = fingerprint(G)
        if k in self.keys:
            return False
        self.keys.add(k)
        self.items.append((name, G, distances(G)))
        return True

    def solved(self, profile):
        return any(covers(d, profile) for _, _, d in self.items)

    def lemmas(self):
        return [{"G": G, "name": nm} for nm, G, _ in self.items]


class Mesh:
    """Cross-layer synapses on the move kinds and the shared library."""
    ETA, DECAY, LAMBDA = 1.0, 0.05, 1.5

    def __init__(self, on, seeds=()):
        self.on, self.seeds = on, seeds
        self.w = {k: 0.0 for k in pb.PRI}
        self.library = Library(seeds) if on else None

    def bias(self, policy):
        if not self.on:
            return policy
        pri = {k: v - self.LAMBDA * self.w[k] for k, v in policy["pri"].items()}
        return dict(policy, pri=pri)

    def reinforce(self, used):
        if not self.on or not used:
            return
        for k in self.w:
            self.w[k] *= 1 - self.DECAY
        for k in used:
            self.w[k] += self.ETA / len(used)


@dataclass
class Record:
    budget: int
    start: int = 0
    found: list = field(default_factory=list)       # (checks so far, profile, n, m, layer path)
    goal_at: int = None
    tries: int = 0
    rejected: int = 0                                 # forcers the gate refused
    t0: float = 0.0
    seconds: float = 0.0

    def used(self):
        return pb.CHECKS[0] - self.start

    def left(self):
        return self.budget - self.used()


class Ctx:
    def __init__(self, target, rng, mesh, rec):
        self.target, self.rng, self.mesh, self.rec = target, rng, mesh, rec

    def library(self):
        return self.mesh.library if self.mesh.on else Library(self.target.seeds)


def search(ctx, profile, policy, library, budget, path):
    """Layer 1 work: builder tries until a gated gadget or the budget is spent."""
    tg = ctx.target
    pol = ctx.mesh.bias(policy)
    lemmas = library.lemmas()
    a = argparse.Namespace(contacts=3, forbid=set(tg.forbid), need=need(profile), max_n=tg.max_n,
                           max_steps=tg.max_steps, noise=pol["noise"],
                           lemma_tries=pol["lemma_tries"] if lemmas else 0, lib=lemmas, pri=pol["pri"],
                           tri_disjoint=False, tri_free_contacts=[])
    start = pb.CHECKS[0]
    while pb.CHECKS[0] - start < budget and ctx.rec.left() > 0:
        b = pb.Builder(a, ctx.rng)
        G = b.run()
        ctx.rec.tries += 1
        if G is None:
            continue
        G = pb.minimise(G, [0, 1, 2], a.forbid)
        if not meets(G, tg.forbid, profile):
            ctx.rec.rejected += 1
            continue
        ctx.mesh.reinforce(b.used)
        library.add(G, f"found_{len(library.items)}")
        ctx.rec.found.append((ctx.rec.used(), list(profile), G.number_of_nodes(), G.number_of_edges(), path))
        if covers(distances(G), tg.goal) and ctx.rec.goal_at is None:
            ctx.rec.goal_at = ctx.rec.used()
        return G
    return None


class Layer1:
    """The builder with one fixed strategy, aimed at the goal."""

    def __init__(self, ctx, library, cfg=None, path="1"):
        self.ctx, self.library, self.path = ctx, library, path
        self.policy = (cfg or {}).get("policy", DEFAULT_POLICY)

    def progress(self):
        return int(self.library.solved(self.ctx.target.goal))

    def step(self, budget):
        search(self.ctx, self.ctx.target.goal, self.policy, self.library, budget, self.path)


LAYER2_SPACE = {"pop": (2, 4, 6), "sigma": (0.3, 0.8, 1.5), "slice": (300, 800, 2000), "curriculum": (True, False)}
LAYER2_DEFAULT = {"pop": 4, "sigma": 0.8, "slice": 800, "curriculum": True}
LAYERK_SPACE = {"arms": (3, 4, 6), "slice": (1000, 3000)}
LAYERK_DEFAULT = {"arms": 4, "slice": 2000}


def mutate(policy, sigma, rng):
    pri = {k: v + rng.gauss(0, sigma) for k, v in policy["pri"].items()}
    noise = min(8.0, max(0.2, policy["noise"] * math.exp(rng.gauss(0, sigma / 2))))
    lt = min(8, max(0, policy["lemma_tries"] + rng.choice((-1, 0, 1))))
    return {"pri": pri, "noise": noise, "lemma_tries": lt}


class Layer2:
    """Evolve-and-evaluate over builder strategies, with a curriculum of profiles."""

    def __init__(self, ctx, library, cfg=None, path="2"):
        self.ctx, self.library, self.path = ctx, library, path
        self.cfg = dict(LAYER2_DEFAULT, **(cfg or {}))
        rng = ctx.rng
        self.pop = [dict(DEFAULT_POLICY)] + [mutate(DEFAULT_POLICY, self.cfg["sigma"], rng)
                                             for _ in range(self.cfg["pop"] - 1)]
        self.fit = [[0, 0] for _ in self.pop]      # gadgets found, checks spent

    def profile(self):
        tg = self.ctx.target
        if self.cfg["curriculum"]:
            for p in tg.ladder:
                if not self.library.solved(p):
                    return p
        return tg.goal

    def progress(self):
        tg = self.ctx.target
        return sum(self.library.solved(p) for p in tg.ladder + (tg.goal,))

    def step(self, budget):
        ctx, start = self.ctx, pb.CHECKS[0]
        while pb.CHECKS[0] - start < budget and ctx.rec.left() > 0 and ctx.rec.goal_at is None:
            for i, pol in enumerate(self.pop):
                c0 = pb.CHECKS[0]
                G = search(ctx, self.profile(), pol, self.library,
                           min(self.cfg["slice"], budget - (pb.CHECKS[0] - start)), f"{self.path}.{i}")
                self.fit[i][1] += pb.CHECKS[0] - c0
                self.fit[i][0] += G is not None
                if ctx.rec.goal_at is not None or pb.CHECKS[0] - start >= budget or ctx.rec.left() <= 0:
                    return
            # keep the better half, refill with mutations of the kept strategies
            order = sorted(range(len(self.pop)), key=lambda i: -(self.fit[i][0] + 1) / (self.fit[i][1] + self.cfg["slice"]))
            keep = order[: max(1, len(order) // 2)]
            pop = [self.pop[i] for i in keep]
            fit = [self.fit[i] for i in keep]
            while len(pop) < self.cfg["pop"]:
                pop.append(mutate(ctx.rng.choice(pop), self.cfg["sigma"], ctx.rng))
                fit.append([0, 0])
            self.pop, self.fit = pop, fit


def sample(space, rng):
    return {k: rng.choice(v) for k, v in space.items()}


class LayerK:
    """Successive halving over copies of the layer below with sampled settings."""

    def __init__(self, k, ctx, library, cfg=None, path=None):
        self.k, self.ctx = k, ctx
        self.path = path or str(k)
        self.cfg = dict(LAYERK_DEFAULT, **(cfg or {}))
        space, default = (LAYER2_SPACE, LAYER2_DEFAULT) if k == 3 else (LAYERK_SPACE, LAYERK_DEFAULT)
        cfgs = [default] + [sample(space, ctx.rng) for _ in range(self.cfg["arms"] - 1)]
        # the ladder gives every copy its own library; the mesh shares one
        self.arms = [make(k - 1, ctx, ctx.library(), c, f"{self.path}.{j}") for j, c in enumerate(cfgs)]
        self.library = library
        self.score = [0.0 for _ in self.arms]

    def progress(self):
        return max(a.progress() for a in self.arms)

    def step(self, budget):
        ctx, start = self.ctx, pb.CHECKS[0]
        while pb.CHECKS[0] - start < budget and ctx.rec.left() > 0 and ctx.rec.goal_at is None:
            for j, arm in enumerate(self.arms):
                c0 = pb.CHECKS[0]
                arm.step(min(self.cfg["slice"], budget - (pb.CHECKS[0] - start)))
                self.score[j] = arm.progress() / max(1, pb.CHECKS[0] - c0)
                if ctx.rec.goal_at is not None or pb.CHECKS[0] - start >= budget or ctx.rec.left() <= 0:
                    return
            if len(self.arms) > 1:
                order = sorted(range(len(self.arms)), key=lambda j: (-self.arms[j].progress(), -self.score[j]))
                keep = sorted(order[: max(1, len(order) // 2)])
                self.arms = [self.arms[j] for j in keep]
                self.score = [self.score[j] for j in keep]


def make(k, ctx, library, cfg=None, path=None):
    if k == 1:
        return Layer1(ctx, library, cfg, path or "1")
    if k == 2:
        return Layer2(ctx, library, cfg, path or "2")
    return LayerK(k, ctx, library, cfg, path)


def run(target, depth, mesh=False, budget=20000, seed=1):
    """One run of the depth-n tower until the goal gadget or the budget; returns the record."""
    tg = TARGETS[target] if isinstance(target, str) else target
    rec = Record(budget=budget, start=pb.CHECKS[0], t0=time.time())
    ctx = Ctx(tg, random.Random(seed), Mesh(mesh, tg.seeds), rec)
    top = make(depth, ctx, ctx.library())
    while rec.left() > 0 and rec.goal_at is None:
        before = pb.CHECKS[0]
        top.step(rec.left())
        if pb.CHECKS[0] == before:      # nothing left to try at this setting
            break
    rec.seconds = time.time() - rec.t0
    out = asdict(rec)
    out.update(target=tg.name, depth=depth, wiring="mesh" if mesh else "ladder", seed=seed,
               checks=rec.used(), synapses=dict(ctx.mesh.w) if mesh else None)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="anaxia construct tower",
                                 description="run the depth-n tower B^n on a construction target")
    ap.add_argument("target", choices=sorted(TARGETS))
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--mesh", action="store_true", help="shared library and cross-layer synapses")
    ap.add_argument("--budget", type=int, default=20000, help="exact SAT checks")
    ap.add_argument("--seeds", default="1", help="comma-separated seeds")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    if a.depth < 1:
        ap.error("depth is an integer at least 1")
    rows = []
    for s in (int(x) for x in a.seeds.split(",")):
        r = run(a.target, a.depth, a.mesh, a.budget, s)
        rows.append(r)
        print(json.dumps({k: r[k] for k in ("target", "depth", "wiring", "seed", "goal_at", "checks",
                                            "tries", "rejected", "seconds")} | {"found": len(r["found"])}),
              flush=True)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
