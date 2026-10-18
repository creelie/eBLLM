"""Amplifiers of the crossing network of ``targets``: second-generation library nodes, pattern transfer,
an adversarial refuter, booster synapses and the gap numbers of the two headline benchmarks.

*Library.*  ``LIBRARY2`` adds to ``targets.LIBRARY`` the crosses aimed at the assumption of each proved
ceiling (other variables than links after a forest gauge fixing), the second-generation partners of the
gauge-fixed specification (finite-box Dobrushin-Shlosman, Bakry-Emery, path coupling) and the nodes made
by transferring the pattern of the one step that moved: *remove redundant variables by a symmetry, then
apply a local criterion*.

*Refuter.*  Before an accepted offspring counts as a survivor, ``refute`` tries to break it: it rechecks
every lattice count on a second box, rejects claims that rest on an unrefereed import or on a periodic
box, rejects claims that a stronger accepted result dominates, and marks reproductions of published
theorems as known.  Refuted offspring are kept as negative data.

*Boosters.*  The synapse between two data points (a pair of pool members that cross) has a weight.
When a crossing fires and its offspring survives the check and the refuter, the weight of that edge is
raised by ``eta`` and the edges that built its parents are raised by ``eta * gamma**k`` at distance k;
a refuted or rejected offspring lowers the edge by ``eta / 2``.  After each generation the out-weights
of every node are rescaled to mean one, so no hub runs away, and a share ``eps`` of the crosses is drawn
uniformly (exploration).  The boosted arm draws its crosses with probability proportional to the weight.

*Gap numbers.*  For Yang-Mills, the largest Wilson coupling below which the strong-coupling gap is
proved, and its share of the interval up to 2.2, the crossover of four-dimensional SU(2) seen by Monte
Carlo (Creutz 1980), which is a physical marker and not a threshold of any proof.  For Hodge, for each
open family, the largest dimension of a family on whose general member the classes are known to be
algebraic, against the dimension of the largest family of that kind.
"""
from __future__ import annotations

import itertools
import json
import math
import random
from fractions import Fraction
from math import gcd
from typing import Dict, List, Optional, Tuple

from . import targets as T
from .targets import Check, Con, _c, cross

# -- the second library ---------------------------------------------------------------------------
NEW_NODES: List[Con] = [
    # ceiling-targeted: change the variables, not the gauge
    _c("ym.plaquettevars", "yang-mills", "graph", (), "Batrouni 1982: plaquette variables with Bianchi constraints"),
    _c("ym.blocks", "yang-mills", "graph", (), "blocks of active links (block Dobrushin)"),
    # second generation: partners of the gauge-fixed specification
    _c("ym.pathcoupling", "yang-mills", "range", ("influence", "graph"), "path coupling of single-link Glauber"),
    _c("ym.bakrygf", "yang-mills", "range", ("link-law", "graph"), "Bakry-Emery after a forest gauge fixing"),
    _c("ym.dsgf", "yang-mills", "range", ("range", "box"), "Dobrushin-Shlosman on a box of the gauge-fixed spec"),
    # pattern transfer: remove redundant variables by a symmetry, then check locally
    _c("h.symreduce", "hodge", "coniveau", ("fermat-characters",),
       "pattern transfer: quotient by mu_m^6 x| S_6 and the Galois group, then Shioda's local test"),
    _c("h.similitude", "hodge", "k3-square", ("k3-isometry",),
       "pattern transfer: composites T(S) -> T(S') -> T(S) through K3 surfaces with T(S') = T(S)(d)"),
]
LIBRARY2: List[Con] = list(T.LIBRARY) + NEW_NODES

PATTERN = {"ym.maxtree": "symmetry-reduce-then-local", "h.symreduce": "symmetry-reduce-then-local",
           "h.similitude": "symmetry-reduce-then-local", "ym.plaquettevars": "change-of-variables",
           "ym.blocks": "change-of-variables"}


def _decomposable(a: Tuple[int, ...], m: int) -> bool:
    """Whether the multiset a splits into blocks of sizes two and three, each summing to 0 mod m."""
    a = list(a)
    if not a:
        return True
    x, rest = a[0], a[1:]
    for k in (1, 2):
        for idx in itertools.combinations(range(len(rest)), k):
            if (x + sum(rest[i] for i in idx)) % m == 0:
                if _decomposable(tuple(r for i, r in enumerate(rest) if i not in idx), m):
                    return True
    return False


def fermat_orbit(a=(1, 16, 26, 31, 36), m=55) -> dict:
    units = [t for t in range(1, m) if gcd(t, m) == 1]
    orbit = sorted({tuple(sorted((t * x) % m for x in a)) for t in units})
    return dict(character=list(a), level=m, orbit=len(orbit), decomposable=sum(_decomposable(o, m) for o in orbit))


def check2(c: Con) -> Check:
    p = set(c.parts)
    if c.problem == "yang-mills":
        if c.parts[0] == "ym.dsgf":
            return Check("stopped", "YM.window.box", "Dobrushin-Shlosman on the gauge-fixed specification needs the "
                         "Kantorovich sensitivity of a box law to its boundary, which at order-one coupling is an "
                         "integral over SU(2)^{3 n^4}; the 4Y-M estimate puts the box side near 90")
        if "ym.finite" in p and ({"ym.quarter", "ym.bakrygf", "ym.bakry"} & p):
            return Check("rejected", "YM.window", "a finite subgroup has no von Mises-Fisher law and no Ricci "
                         "curvature, and no finite subgroup approximates SU(2) uniformly (Jordan)")
        if "ym.plaquettevars" in p:
            return Check("rejected", "YM.window.lower", "in plaquette variables the Bianchi identity of a cube fixes "
                         "each plaquette variable, up to parallel transport, by the other five plaquettes of the "
                         "cube: the single-variable kernels are point masses and Dobrushin's coefficients are 1")
        if "ym.blocks" in p:
            return Check("stopped", "YM.window.lower", "a block coefficient needs the Kantorovich sensitivity of the "
                         "joint law of a block at finite beta; the single-link bound of the sharp quarter does not "
                         "control it and the package has no rigorous bound for it", dict(block_sizes_tried=[2, 3]))
        if c.parts[0] == "ym.pathcoupling" and "ym.quarter" in p:
            m = T.gauge_count("one-per-plaquette") if "ym.maxtree" in p else T.gauge_count(
                "temporal" if "ym.temporal" in p else "plain")
            k = m["neighbours"][0]
            return Check("accepted", "YM.strong", f"path coupling of single-link Glauber contracts for beta_W < "
                         f"{Fraction(4, k)}: the same range as Dobrushin, no gain", dict(neighbours=k, gain=False))
        if c.parts[0] == "ym.bakrygf":
            g = "ym.maxtree" if "ym.maxtree" in p else ("ym.temporal" if "ym.temporal" in p else "ym.plain")
            act = {"ym.maxtree": 3, "ym.temporal": 4, "ym.plain": 4}[g]
            # Hess ReTr of a product of k active links is bounded by N (sum |Y_e|)^2 <= N k sum |Y_e|^2;
            # with 2(d-1) plaquettes per link the curvature condition (N+2)/4 > 2(d-1) N k |beta| at N = 2.
            beta = Fraction(1, 2 * 3 * 2 * act)      # 1 > 2 (d-1) N k |beta| / ((N+2)/4) with d = 4, N = 2
            return Check("accepted", "YM.strong", f"Bakry-Emery after the {g[3:]} gauge: beta_W < {4 * beta}, "
                         "weaker than Dobrushin", dict(active_per_plaquette=act, range=f"beta_W < {4 * beta}"))
        r = T.check(c)
        return r
    if "h.symreduce" in p:
        o = fermat_orbit()
        return Check("rejected", "H.F3p.fermat110", "Shioda's test is invariant under mu_m^6 x| S_6 and the Galois "
                     f"group: the orbit of the leftover character has {o['orbit']} members and "
                     f"{o['decomposable']} split, so the quotient gives nothing new", o)
    if "h.similitude" in p:
        return Check("stopped", "H.F3p.K3RM", "sqrt(d) in the RM field is a Hodge similitude T(S) -> T(S)(d); "
                     "Buskin covers isometries only, and the algebraicity of Hodge similitudes is reduced by "
                     "Varesco (2023) to the Kuga-Satake Hodge conjecture, open for the very general member",
                     dict(known_route="Varesco 2023"))
    return T.check(c)


# -- the refuter ----------------------------------------------------------------------------------
KNOWN_BEST = {"YM.strong": Fraction(2, 9)}


def refute(c: Con, r: Check, best: Dict[str, Fraction]) -> Tuple[bool, str]:
    """(survives, reason).  Only accepted checks are tried."""
    p = set(c.parts)
    if "h.openaicm" in p:
        return False, "rests on an unrefereed import"
    if r.measurement.get("gain") is False:
        return False, "reproduces an accepted range with no gain"
    if "neighbours" in r.measurement and "gauge" in r.measurement:
        again = T.gauge_count(r.measurement["gauge"], n=5)
        if again["neighbours"] != r.measurement["neighbours"] or not again["forest"]:
            return False, "the lattice count changes on a second box"
        if again["fixed_per_plaquette"] != r.measurement["fixed_per_plaquette"]:
            return False, "the fixed-link count changes on a second box"
    rng = r.measurement.get("range", "")
    if rng.startswith("beta_W < "):
        v = Fraction(rng.split("< ")[1].split()[0])
        if any(v < b for b in best.values()):
            return False, f"dominated: a survivor already covers beta_W < {max(best.values())}"
    if r.measurement.get("known"):
        return True, "known result"
    return True, "survives"


# -- the arms with boosters -----------------------------------------------------------------------
def run_boosted(arm: str, generations: int = 6, per_gen: int = 6, seed: int = 0, eta: float = 1.0,
                gamma: float = 0.5, eps: float = 0.2, weights: Optional[Dict[str, float]] = None,
                library: Optional[List[Con]] = None, synapse: str = "head") -> dict:
    """arm: 'boosted' (weights steer and learn), 'unboosted' (uniform over typed pairs), 'random' (any pair).
    Returns the full record: every crossing with its parents, check, refuter verdict and edge weight."""
    rng = random.Random(seed)
    lib = list(library or LIBRARY2)
    pool: List[Con] = list(lib)
    seen = {c.parts for c in pool}
    tried: set = set()
    w: Dict[str, float] = dict(weights or {})
    made_by: Dict[Tuple[str, ...], Tuple[Con, Con]] = {}       # offspring parts -> the parents of the cross
    best = dict(KNOWN_BEST)
    rec = dict(arm=arm, seed=seed, crossings=[], generations=[], survivors={}, refuted=[], first={})

    def key(a, b):
        # 'edge': one synapse per pair of pool members; 'head': one per pair of outer library nodes, so
        # that what is learned on one composite carries to every composite with the same heads
        return f"{a.id}|{b.id}" if synapse == "edge" else f"{a.parts[0]}|{b.parts[0]}"

    for g in range(1, generations + 1):
        typed = [(a, b) for a in pool for b in pool if (a.parts, b.parts) not in tried and cross(a, b)]
        if arm == "random":
            cand = [(rng.choice(pool), rng.choice(pool)) for _ in range(per_gen)]
        elif not typed:
            cand = []
        elif arm == "unboosted":
            cand = rng.sample(typed, min(per_gen, len(typed)))
        else:
            cand, left = [], list(typed)
            for _ in range(min(per_gen, len(typed))):
                if rng.random() < eps:
                    i = rng.randrange(len(left))
                else:
                    ws = [w.get(key(a, b), 1.0) for a, b in left]
                    i = rng.choices(range(len(left)), weights=ws)[0]
                cand.append(left.pop(i))
        stats = dict(generation=g, offspring=0, ill_typed=0, checked=0, accepted=0, survived=0, refuted=0)
        new = []
        for a, b in cand:
            tried.add((a.parts, b.parts))
            c = cross(a, b)
            stats["offspring"] += 1
            if c is None:
                stats["ill_typed"] += 1
                continue
            if c.parts in seen:
                continue
            seen.add(c.parts)
            made_by[c.parts] = (a, b)
            new.append(c)
            row = dict(generation=g, child=c.id, a=a.id, b=b.id, closed=c.closed, weight=w.get(key(a, b), 1.0))
            if c.closed:
                r = check2(c)
                stats["checked"] += 1
                row.update(outcome=r.outcome, node=r.node, statement=r.statement)
                fired = 0.0
                if r.outcome == "accepted":
                    stats["accepted"] += 1
                    ok, why = refute(c, r, best)
                    row.update(refuter=why, survived=ok)
                    if ok:
                        stats["survived"] += 1
                        fired = eta
                        rec["survivors"].setdefault(r.statement, dict(node=r.node, generation=g, parts=list(c.parts)))
                        rec["first"].setdefault(r.node, g)
                        v = r.measurement.get("range", "")
                        if v.startswith("beta_W < "):
                            best[r.node] = max(best.get(r.node, Fraction(0)), Fraction(v.split("< ")[1].split()[0]))
                    else:
                        stats["refuted"] += 1
                        fired = -eta / 2
                        rec["refuted"].append(dict(child=c.id, statement=r.statement, reason=why))
                elif r.outcome == "rejected":
                    fired = -eta / 2
                if arm == "boosted" and fired:
                    w[key(a, b)] = max(0.05, w.get(key(a, b), 1.0) + fired)
                    if fired > 0:                    # boost the path that built the parents
                        frontier, k = [a.parts, b.parts], 1
                        while frontier and k <= 4:
                            nxt = []
                            for parts in frontier:
                                if parts in made_by:
                                    pa, pb = made_by[parts]
                                    w[key(pa, pb)] = w.get(key(pa, pb), 1.0) + eta * gamma ** k
                                    nxt += [pa.parts, pb.parts]
                            frontier, k = nxt, k + 1
                row["boost"] = fired if arm == "boosted" else 0.0
            rec["crossings"].append(row)
        pool += new
        if arm == "boosted":                          # per-node normalisation of the out-weights
            outs: Dict[str, List[str]] = {}
            for k in w:
                outs.setdefault(k.split("|")[0], []).append(k)
            for ks in outs.values():
                mean = sum(w[k] for k in ks) / len(ks)
                for k in ks:
                    w[k] /= mean
        rec["generations"].append(stats)
    rec["weights"] = w
    rec["best"] = {k: str(v) for k, v in best.items()}
    return rec


def compare_boosters(seeds: int = 40, **kw) -> dict:
    out = {}
    for arm in ("boosted", "unboosted", "random"):
        runs = [run_boosted(arm, seed=s, **kw) for s in range(seeds)]
        first = [r["first"].get("YM.window.lower") for r in runs]
        hit = [f for f in first if f is not None]
        out[arm] = dict(runs=seeds,
                        survivors=sum(len(r["survivors"]) for r in runs) / seeds,
                        refuted=sum(len(r["refuted"]) for r in runs) / seeds,
                        checked=sum(g["checked"] for r in runs for g in r["generations"]) / seeds,
                        ill_typed=sum(g["ill_typed"] for r in runs for g in r["generations"]) / seeds,
                        found_one_third=len(hit),
                        mean_generation_one_third=(sum(hit) / len(hit)) if hit else None,
                        best_ym=max((Fraction(r["best"].get("YM.window.lower", "0")) for r in runs), default=0))
        out[arm]["best_ym"] = str(out[arm]["best_ym"])
    return out


# -- gap numbers ----------------------------------------------------------------------------------
CROSSOVER = 2.2       # Monte Carlo crossover of 4D SU(2) (Creutz 1980), a marker, not a proof threshold

HODGE_FAMILIES = [
    # family, dimension of the largest family of the kind, largest dimension of a family on whose
    # general member the classes are known to be algebraic, source
    ("Weil sixfolds (CM field K quadratic)", 9, 5, "products of Weil fourfolds (Markman) and Weil surfaces"),
    ("Weil eightfolds of nontrivial discriminant", 16, 0, "none refereed"),
    ("S x S, S a K3 with real quadratic multiplication", 8, 4, "Varesco 2023: the first four-dimensional families (rank T = 12); the largest family has rank T = 20"),
    ("Abelian varieties with CM by a field of degree >= 4, off CM points", None, 0, "CM points only"),
    ("Fermat fourfold of degree 110", 0, 0, "one orbit of Hodge characters left"),
]


def gap_numbers(best_ym: Fraction) -> dict:
    return dict(yang_mills=dict(covered_beta_w=str(best_ym), share_to_crossover=round(float(best_ym) / CROSSOVER, 4),
                                crossover=CROSSOVER),
                hodge=[dict(family=f, dimension=d, covered=c, source=s) for f, d, c, s in HODGE_FAMILIES])


# -- cross-thread map -----------------------------------------------------------------------------
CROSS_THREAD = [
    # source thread or repository, what it gives, the nodes it feeds
    ("creelie/4Y-M (Yang-Mills)", "sharp quarter, gauge Dobrushin-Shlosman, reflection positivity, gap from decay",
     ["ym.quarter", "ym.gds", "ym.rp", "YM.strong"]),
    ("creelie/fermat-hodge- and creelie/H8 (Hodge)", "the (F2)/(F3') split, Schoen products, the open families",
     ["H.F2", "H.F3p", "h.schoen", "H.F2.weil6", "H.F2.weil8", "H.F2.E06"]),
    ("creelie/e84hc (Fermat varieties)", "the census of Hodge characters, the classes left at 110 and 220",
     ["h.characters", "H.F3p.fermat110", "H.F3p.fermat220"]),
    ("Erdos 1183 (creelie/D7)", "change of representation (level colourings to weighted posets)",
     ["ym.plaquettevars", "ym.blocks", "h.symreduce"]),
    ("creelie/eD424 (D4 and the 24-cell)", "finite certificates of a symmetric configuration",
     ["ym.dsgf", "YM.window.box"]),
    ("creelie/eLhmr (Lehmer)", "no input to either headline tree", []),
    ("creelie/silver-system (Earth-Moon)", "no input to either headline tree", []),
    ("OpenAI math corpus (family 032)", "an unrefereed claim of (F2) for CM abelian varieties", ["h.openaicm"]),
]


def graph_export(records: List[dict]) -> dict:
    """The construction graph of a set of runs: nodes (library and offspring), crossing edges and their
    outcomes, the learned synapses, and the cross-thread map."""
    nodes = {c.id: dict(id=c.id, problem=c.problem, gives=c.gives, needs=sorted(c.needs), source=c.source,
                        pattern=PATTERN.get(c.id, ""), library=True) for c in LIBRARY2}
    edges = []
    for r in records:
        for x in r["crossings"]:
            nodes.setdefault(x["child"], dict(id=x["child"], library=False))
            edges.append(dict(arm=r["arm"], seed=r["seed"], **x))
    return dict(nodes=list(nodes.values()), edges=edges,
                synapses={r["arm"] + ":" + str(r["seed"]): r.get("weights", {}) for r in records},
                cross_thread=[dict(source=s, gives=g, feeds=f) for s, g, f in CROSS_THREAD])


def to_json(obj) -> str:
    return json.dumps(obj, indent=1, default=str)


def compare_rounds(seeds: int = 150, rounds: int = 4, generations: int = 8, per_gen: int = 6,
                   synapse: str = "head") -> dict:
    """The boosted arm keeps its synapses from one round to the next; the unboosted arm starts afresh.
    For each round: runs that reach beta_W < 1/3, the mean generation at which they reach it, and the
    standard error of the share."""
    out = {}
    for arm in ("boosted", "unboosted"):
        hits = [[] for _ in range(rounds)]
        surv = [0.0] * rounds
        for s in range(seeds):
            w: Dict[str, float] = {}
            for r in range(rounds):
                rec = run_boosted(arm, generations=generations, per_gen=per_gen, seed=1000 * r + s, weights=w,
                                  synapse=synapse)
                if arm == "boosted":
                    w = rec["weights"]
                f = rec["first"].get("YM.window.lower")
                if f:
                    hits[r].append(f)
                surv[r] += len(rec["survivors"]) / seeds
        rows = []
        for r in range(rounds):
            q = len(hits[r]) / seeds
            rows.append(dict(round=r + 1, share=round(q, 4), se=round(math.sqrt(q * (1 - q) / seeds), 4),
                             mean_generation=round(sum(hits[r]) / len(hits[r]), 2) if hits[r] else None,
                             survivors=round(surv[r], 3)))
        out[arm] = rows
    return out
