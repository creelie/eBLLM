"""Target points, the attack channel, and one autonomous agent per target point.

*Target point.*  For each benchmark, the single statement that would cross its wall, with the type it
has in the crossing algebra.  A backward search from the target type over the library gives every type
a distance: 0 for the target type, and 1 + d for each input of a construction whose output is at
distance d.  Boosters are multiplied by exp(-distance of the composite's output), so crossings that
build towards the target point are drawn more often, and the forward search (crossing) meets the
backward search (distances) at the composites whose output type is at distance 0 or 1: the
candidate lemmas.

*Channel.*  ``bundle`` assembles, for one composite on one target, everything the engine holds about
it: the most similar past attempts in memory, the barrier x pattern cells of its constructions, the
booster weights of its synapses, the refuted offspring with their reasons, and the blocks recorded on
its benchmark.  Every proposer receives this bundle; its prior multiplies the booster weight
(cells that failed on this target lower it, past survivors raise it).  What flowed is logged in the
memory table ``channel``.

*Agents.*  ``TargetAgent`` holds one target point, its own booster weights, and a slice of the shared
memory (its benchmark).  Each step it attacks its library through the channel.  When a step adds no
survivor, it spawns a sub-attack whose target is the nearest open input type of its target point
(a lemma), and it trades: survivors of other agents with the same output type enter its library.
"""
from __future__ import annotations

import json
import math
from typing import Dict, List, Optional

from . import superbrain as S
from .memory import Memory
from .targets import Con

# benchmark -> (problem, target type, the target point)
TARGET_POINTS: Dict[str, tuple] = {
    "E1183": ("erdos1183", "linear-bound",
              "an explicit family of colourings of 2^[n] with largest monochromatic sublattice <= n/2 + C for "
              "every n (answers Question 9.3)"),
    "YM": ("yang-mills", "effective-action",
           "a crossover lemma: at one fixed beta_W > 1/3, a block-spin effective action whose blocked measure "
           "satisfies a Dobrushin-type condition, uniformly in the spacing"),
    "H": ("hodge", "fermat-split",
          "algebraicity of the Hodge class of the character (1,16,26,31,36) at level 55 on the Fermat fourfold "
          "of degree 110"),
    "Chowla": ("chowla", "local-gowers",
               "local U^2 uniformity of the Liouville function on almost all intervals of length "
               "exp((log X)^{2/5-delta}), one step below Pilatte's scale"),
    "B": ("standard-B", "inverse-L",
          "an algebraic inverse of L: H^2 -> H^4 for one named threefold of general type with h^{2,0} > 0 "
          "(a smooth quintic-type hypersurface section with transcendental H^2)"),
}

# barrier x pattern cells (MATRIX.md): (benchmark, construction) -> outcome
CELLS: Dict[tuple, str] = {}
for _b, _ids, _o in [
    ("E1183", ["e.level", "e.grid"], "partial"), ("E1183", ["e.compose", "k.e.xor", "k.e.random", "k.e.lll",
                                                            "k.e.berlekamp"], "fails"),
    ("YM", ["ym.maxtree", "ym.dsgf", "ym.gds"], "partial"),
    ("YM", ["ym.balaban", "ym.bblsi", "ym.finite", "k.ym.kp", "k.ym.gk", "k.ym.brydgesyau", "k.ym.bb21",
            "k.ym.adhikaricao", "ym.plaquettevars"], "fails"),
    ("H", ["h.similitude", "k.h.varesco"], "partial"),
    ("H", ["h.shioda", "h.symreduce", "h.buskin", "h.absolute", "h.andre", "h.schoen", "k.h.aoki"], "fails"),
    ("B", ["b.kleiman", "b.arapura", "b.ks", "b.hodge"], "fails"),
    ("Chowla", ["c.mrt", "k.c.mrtavg"], "partial"),
    ("Chowla", ["c.walk", "c.kwalk", "c.shorten", "k.c.fi", "k.c.hb", "k.c.selberg"], "fails")]:
    for _i in _ids:
        CELLS[(_b, _i)] = _o


def distances(lib: List[Con], target_type: str) -> Dict[str, int]:
    d = {target_type: 0}
    changed = True
    while changed:
        changed = False
        for c in lib:
            if c.gives in d:
                for n in c.needs:
                    if d.get(n, 99) > d[c.gives] + 1:
                        d[n] = d[c.gives] + 1
                        changed = True
    return d


def bundle(mem: Memory, bench: str, c: Con, weights: Dict[str, float], k: int = 5) -> dict:
    hits = mem.retrieve(c.parts, k=k, log=False)
    cells = {p: CELLS[(bench, p)] for p in c.parts if (bench, p) in CELLS}
    syn = {key: round(v, 3) for key, v in weights.items() if key.split("|")[0] in c.parts}
    refuted = [h for h in hits if h["survived"] == 0]
    blocks = [dict(step=s, assumption=a[:120]) for s, a in mem.db.execute(
        "SELECT step, assumption FROM blocks WHERE target = ? LIMIT 5", (S.LIB5[bench][0].problem,))]
    return dict(composite=c.id, retrieved=hits, cells=cells, synapses=syn, refuted=refuted, blocks=blocks)


def channel_prior(b: dict) -> float:
    x = 1.0
    x *= 0.5 ** sum(1 for o in b["cells"].values() if o == "fails")
    x *= 1.5 ** sum(1 for o in b["cells"].values() if o == "partial")
    x *= 1.0 + sum(h["sim"] for h in b["retrieved"] if h["survived"] == 1)
    return max(0.05, min(5.0, x))


class TargetAgent:
    def __init__(self, bench: str, mem: Memory, channel: bool = True, target_weight: bool = True):
        self.bench = bench
        self.problem, self.ttype, self.point = TARGET_POINTS[bench]
        self.mem = mem
        self.lib: List[Con] = list(S.LIB5[bench])
        self.w: Dict[str, float] = {}
        self.channel, self.target_weight = channel, target_weight
        self.dist = distances(self.lib, self.ttype)
        self.history: List[dict] = []
        self.known: set = set()
        self.sub: List[dict] = []
        mem.db.execute("CREATE TABLE IF NOT EXISTS channel(round INTEGER, bench TEXT, composite TEXT, items INTEGER, "
                       "prior REAL, bundle TEXT)")

    def prior(self, round_):
        def f(c: Con) -> float:
            x = 1.0
            if self.target_weight:
                x *= math.exp(-self.dist.get(c.gives, 6))
            if self.channel:
                b = bundle(self.mem, self.bench, c, self.w)
                p = channel_prior(b)
                n = len(b["retrieved"]) + len(b["cells"]) + len(b["synapses"]) + len(b["blocks"])
                self.mem.db.execute("INSERT INTO channel VALUES (?,?,?,?,?,?)",
                                    (round_, self.bench, c.id, n, p, json.dumps(b, default=str)[:2000]))
                x *= p
            return x
        return f

    def step(self, round_: int, seed: int, llm=None, generations: int = 6, per_gen: int = 8) -> dict:
        rec = S.attack("full", memory=self.mem, weights=self.w, seed=seed, round_=round_, library=self.lib,
                       prior_fn=self.prior(round_), known_boost=0.25, llm=llm, generations=generations,
                       per_gen=per_gen)
        self.w = rec["weights"]
        new = set(rec["survivors"]) - self.known
        self.known |= new
        # distance reached: the least distance to the target type of any checked composite's output
        reached = min([self.dist.get(S.LIB5[self.bench][0].gives, 6)] +
                      [self.dist.get(v["node"], 6) for v in rec["survivors"].values()] or [6])
        out = dict(round=round_, bench=self.bench, checks=rec["checks"], new=len(new), known=len(self.known),
                   refuted=len(rec["refuted"]), skipped=rec["skipped"], target_reached=self.reached(rec))
        if not new:
            # sub-attack on the nearest open input of the target point: a lemma
            lemma = min((t for t, d in self.dist.items() if d == 1), default=None)
            if lemma:
                sub = S.attack("full", memory=self.mem, seed=seed + 7, round_=round_, library=self.lib,
                               prior_fn=lambda c, L=lemma: 3.0 if c.gives == L else 0.5, generations=3, per_gen=6)
                out["sub"] = dict(lemma=lemma, checks=sub["checks"], new=len(set(sub["survivors"]) - self.known))
                self.known |= set(sub["survivors"])
        self.history.append(out)
        return out

    def reached(self, rec) -> bool:
        """Did a survivor reach the target point?  Only a composite whose output is the target type and
        whose check accepts it as the target point counts; no check in the package does so yet."""
        return any(v["node"] in ("E.lin", "YM.lattice", "H.F3p.fermat110", "C.even.log", "B.3.gt")
                   for v in rec["survivors"].values())

    def trade(self, others: List["TargetAgent"]) -> List[str]:
        """Pass results between benchmarks where one benchmark is an input of another: B needs the Hodge
        conjecture on X x X (the H agent's target), and the H agent's (F2) side feeds nothing else.  A
        dependency is passed only when the other agent reached its target point."""
        got = []
        for o in others:
            if self.bench == "B" and o.bench == "H" and any(h.get("target_reached") for h in o.history):
                got.append("H -> B: Hodge on X x X")
        return got
