"""The crossing network aimed at the open steps of the two headline benchmarks, Yang-Mills and Hodge.

Every construction of the library is a typed node: it needs inputs of some types and gives an
output of one type.  Two nodes cross when the output of one is an input of the other; the offspring
gives the outer node's output and still needs whatever the outer node needed besides.  An offspring
with nothing left to need is *closed* and goes to its check.  A check is a computation (a neighbour
count on the lattice, a dimension count, a lattice-point test); it accepts, rejects with the
measurement that stopped it, or stops when no checkable form exists.  Checked offspring join the pool
and seed the next generation, so composites grow by chain reaction.

Three arms are run on the same library:

* ``network``: only typed crossings, each pair once, offspring checked;
* ``select``: random pairs, rejected unless the types fit (the type filter without the enumeration);
* ``random``: random pairs, crossed whatever the types; ill-typed offspring are counted and dropped.

An accepted check that bears on a node of the benchmark tree is reported with the node's id; the
tree records it as a proved step.  Nothing here proves an open leaf of either tree unless its check
does, and the checks say so.
"""
from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from fractions import Fraction
from math import gcd
from typing import Dict, FrozenSet, List, Optional, Tuple


# -- the lattice computations behind the Yang-Mills checks -----------------------------------------
# One fixed forward link per site, in direction SIG[x0 + 2 x1 + 4 x2 + 8 x3] (x read modulo 2).  The
# pattern was found by a SAT search (experiments/yangmills/onefixed.py) and is checked in Lean
# (lean/EBLLM/GaugeFix.lean).
SIG = [0, 0, 2, 3, 3, 1, 2, 1, 1, 2, 1, 3, 3, 2, 0, 0]


def _sig(x) -> int:
    return SIG[sum((c % 2) << i for i, c in enumerate(x))]


GAUGES = {
    "plain": lambda x, mu: False,
    "temporal": lambda x, mu: mu == 0,
    "one-per-plaquette": lambda x, mu: _sig(x) == mu,
}


def gauge_count(gauge: str, n: int = 4, d: int = 4) -> dict:
    """On the box {0..n-1}^d with free boundary: fixed links per plaquette, whether the fixed links form
    a forest, and the number of active partners of every active link all of whose 2(d-1) plaquettes
    lie in the box."""
    fixed = GAUGES[gauge]

    def sh(x, mu):
        y = list(x)
        y[mu] += 1
        return tuple(y)

    inbox = lambda x: all(0 <= c < n for c in x)
    plaq = []
    for x in itertools.product(range(n), repeat=d):
        for mu, nu in itertools.combinations(range(d), 2):
            if inbox(sh(x, mu)) and inbox(sh(x, nu)):
                plaq.append([(x, mu), (sh(x, mu), nu), (sh(x, nu), mu), (x, nu)])
    links = {l for p in plaq for l in p}
    F = {l for l in links if fixed(*l)}
    parent: Dict[tuple, tuple] = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    forest = True
    for (x, mu) in F:
        a, b = find(x), find(sh(x, mu))
        forest &= a != b
        parent[a] = b
    nb: Dict[tuple, int] = {}
    deg: Dict[tuple, int] = {}
    for p in plaq:
        act = [l for l in p if l not in F]
        for l in act:
            nb[l] = nb.get(l, 0) + len(act) - 1
            deg[l] = deg.get(l, 0) + 1
    full = sorted({nb[l] for l in nb if deg[l] == 2 * (d - 1)})
    per = sorted({sum(1 for l in p if l in F) for p in plaq})
    return dict(gauge=gauge, box=n, fixed_per_plaquette=per, forest=forest, neighbours=full)


def forest_lower_bound(d: int = 4) -> Fraction:
    """For every forest gauge fixing on Z^d the mean number of active partners of an active link is at
    least 2(d-1)(abar - 1), abar = 4(d-1)/d the mean number of active links of a plaquette."""
    abar = Fraction(4 * (d - 1), d)
    return 2 * (d - 1) * (abar - 1)


# -- the library ----------------------------------------------------------------------------------
@dataclass(frozen=True)
class Con:
    id: str
    problem: str
    gives: str
    needs: FrozenSet[str] = frozenset()
    source: str = ""
    parts: Tuple[str, ...] = ()

    @property
    def closed(self) -> bool:
        return not self.needs


def _c(i, p, gives, needs=(), source=""):
    return Con(i, p, gives, frozenset(needs), source, (i,))


LIBRARY: List[Con] = [
    # Yang-Mills
    _c("ym.vmf", "yang-mills", "link-law", (), "the single-link law of SU(2) is von Mises-Fisher on S^3"),
    _c("ym.quarter", "yang-mills", "influence", ("link-law",), "4Y-M, the sharp quarter W1 <= |b - b'|/4"),
    _c("ym.dobrushin", "yang-mills", "range", ("influence", "graph"), "Dobrushin 1968/70, Wasserstein form"),
    _c("ym.plain", "yang-mills", "graph", (), "no gauge fixing: 6(d - 1) partners"),
    _c("ym.temporal", "yang-mills", "graph", (), "temporal gauge U_0 = 1"),
    _c("ym.maxtree", "yang-mills", "graph", (), "Creutz's maximal-tree gauge, one fixed link per plaquette"),
    _c("ym.rp", "yang-mills", "gap", ("range",), "Osterwalder-Seiler reflection positivity, transfer matrix"),
    _c("ym.box", "yang-mills", "box", (), "a finite box with gauge-invariant boundary data"),
    _c("ym.gds", "yang-mills", "range", ("influence", "box"), "4Y-M gauge Dobrushin-Shlosman criterion"),
    _c("ym.bakry", "yang-mills", "range", ("link-law",), "Shen-Zhu-Zhu, Bakry-Emery on the link law"),
    _c("ym.polchinski", "yang-mills", "flow", (), "Polchinski renormalisation flow"),
    _c("ym.bblsi", "yang-mills", "range", ("flow",), "Bauerschmidt-Bodineau multiscale log-Sobolev"),
    _c("ym.balaban", "yang-mills", "effective-action", (), "Balaban's fine-scale renormalisation group"),
    _c("ym.crossover", "yang-mills", "range", ("effective-action", "box"), "Hypothesis R at a fixed physical scale"),
    _c("ym.finite", "yang-mills", "link-law", (), "a finite subgroup of SU(2) (Adhikari-Cao)"),
    # Hodge
    _c("h.markman", "hodge", "weil4", (), "Markman 2025: Weil classes on abelian fourfolds of Weil type"),
    _c("h.mz", "hodge", "F2-low", ("weil4",), "Moonen-Zarhin: dimension <= 5 reduces to Weil fourfolds"),
    _c("h.schoen", "hodge", "weil-higher", ("weil4",), "Schoen's product of Weil varieties"),
    _c("h.shioda", "hodge", "fermat-split", (), "Shioda's inductive structure of Fermat varieties"),
    _c("h.characters", "hodge", "fermat-characters", (), "Hodge characters of X^4_110 left by the census"),
    _c("h.block", "hodge", "coniveau", ("fermat-characters",), "block families: empty Fine interior (Batyrev)"),
    _c("h.buskin", "hodge", "k3-isometry", (), "Buskin 2019: rational Hodge isometries of K3 surfaces"),
    _c("h.rmclasses", "hodge", "k3-square", ("k3-isometry",), "classes of S x S from End_Hdg T(S) = K (RM)"),
    _c("h.openaicm", "hodge", "F2-cm", (), "OpenAI family 032, unrefereed, no Lean"),
]


def cross(a: Con, b: Con) -> Optional[Con]:
    """b fed into a: the output of b fills one input of a."""
    if b.gives in a.needs and a.problem == b.problem and a.id != b.id:
        return Con(f"({a.id}<-{b.id})", a.problem, a.gives, (a.needs - {b.gives}) | b.needs, "",
                   a.parts + b.parts)
    return None


# -- the checks -----------------------------------------------------------------------------------
@dataclass
class Check:
    outcome: str
    node: str
    statement: str
    measurement: dict = field(default_factory=dict)


def check(c: Con) -> Check:
    p = set(c.parts)
    if c.problem == "yang-mills":
        if c.gives in ("range", "gap") and {"ym.dobrushin", "ym.quarter"} <= p:
            if "ym.finite" in p:
                return Check("rejected", "YM.window", "a finite subgroup has no von Mises-Fisher law, and no finite "
                             "subgroup approximates SU(2) uniformly (Jordan): the quarter bound does not apply")
            if "ym.vmf" not in p:
                return Check("stopped", "YM.strong", "the quarter bound needs the single-link law")
            g = next(x for x in ("ym.maxtree", "ym.temporal", "ym.plain") if x in p)
            name = {"ym.maxtree": "one-per-plaquette", "ym.temporal": "temporal", "ym.plain": "plain"}[g]
            m = gauge_count(name)
            k = m["neighbours"][0]
            if not m["forest"] or len(m["neighbours"]) != 1:
                return Check("rejected", "YM.strong", "the fixed links are not a forest", m)
            beta_w = Fraction(4, k)                    # alpha = k |beta| < 1, beta_W = 4 beta
            m.update(alpha=f"{k}|beta| = {Fraction(k, 4)} beta_W", range=f"beta_W < {beta_w}",
                     ceiling_for_forests=str(forest_lower_bound()))
            what = "lattice gap m >= -log(%s beta_W)" % Fraction(k, 4) if c.gives == "gap" else \
                   "unique gauge-invariant state with exponential decay"
            return Check("accepted", "YM.window.lower" if name == "one-per-plaquette" else "YM.strong",
                         f"4D SU(2): {what} for beta_W < {beta_w} ({name} gauge, {k} partners per link)", m)
        if "ym.bakry" in p and c.gives in ("range", "gap"):
            if "ym.finite" in p:
                return Check("rejected", "YM.window", "Bakry-Emery needs Ricci curvature; a finite group has none")
            return Check("accepted", "YM.strong", "uniqueness for |beta| < 1/(16(d-1)) (Shen-Zhu-Zhu), weaker than "
                         "the Dobrushin ranges", dict(range="beta_W < 1/12 at d = 4"))
        if "ym.gds" in p:
            return Check("stopped", "YM.window.box", "the gauge Dobrushin-Shlosman test needs a box of side about 90 "
                         "in 4D (4Y-M); no exact computation over SU(2)^{4 n^4} at that size exists",
                         dict(side=90, links=4 * 90 ** 4))
        if "ym.bblsi" in p:
            return Check("stopped", "YM.window.lsi", "the multiscale log-Sobolev inequality needs a Polchinski flow "
                         "with uniformly convex effective potentials; for gauge fields at order-one coupling no "
                         "convexity is known, and gauge invariance removes the Gaussian reference measure")
        if "ym.crossover" in p:
            return Check("stopped", "YM.lattice", "Hypothesis R: Balaban's effective action at a fixed physical "
                         "scale must land in a region where a convergent method gives a gap, uniformly in the "
                         "spacing; this is the Clay problem on the lattice")
        return Check("stopped", "YM", "no check is implemented for this composite")
    # Hodge
    if "h.mz" in p and "h.markman" in p:
        return Check("accepted", "H.F2.dim5", "(F2) in dimension at most five (Markman 2025 with Moonen-Zarhin); "
                     "known before this package", dict(known=True))
    if "h.schoen" in p and "h.markman" in p:
        n = 3
        products = 2 ** 2 + 1 ** 2                    # moduli of a Weil fourfold (n = 2) and surface (n = 1)
        return Check("rejected", "H.F2.weil6", "products of Weil fourfolds and Weil surfaces fill a family of "
                     f"dimension {products} inside the {n * n}-dimensional moduli of Weil sixfolds: meagre, and a "
                     "very general Weil sixfold is simple", dict(product_dim=products, moduli_dim=n * n))
    if "h.block" in p and "h.characters" in p:
        mm, a = 55, (1, 16, 26, 31, 36)
        shadows = [t for t in range(1, mm) if gcd(t, mm) > 1 and all((t * x) % mm for x in a)
                   and sum((t * x) % mm for x in a) == mm]
        return Check("rejected", "H.F3p.fermat110", "no block family: the character (1,16,26,31,36) at level 55 has "
                     "a shadow, a lattice point of the Fine interior", dict(shadows=shadows))
    if "h.rmclasses" in p and "h.buskin" in p:
        # The Hodge isometries of T(S) itself, S very general with real multiplication by K, are the
        # x in K with x = x* and x x* = 1, so x = +-1.  Buskin's theorem therefore gives the classes of
        # K beyond Q only through other K3 surfaces S' with T(S') = T(S)(c) over Q, which is how
        # Varesco (Math. Z. 305, 2023) proves the classes on the square of the general member of
        # certain four-dimensional families this way.
        return Check("stopped", "H.F3p.K3RM", "Buskin's theorem on S alone reaches only the isometries +-1 of T(S); "
                     "the classes of K need Hodge isometries through K3 surfaces S' with T(S') = T(S)(c) over Q, "
                     "known for the general member of certain four-dimensional families (Varesco 2023) and not for "
                     "the very general member of the eight-dimensional family of real quadratic multiplication", dict(self_isometries="+-1"))
    if "h.openaicm" in p:
        return Check("rejected", "H.F2.cm", "the import is an unrefereed theorem with no Lean form")
    return Check("stopped", "H", "no check is implemented for this composite")


# -- the arms -------------------------------------------------------------------------------------
def run(arm: str, generations: int = 4, per_gen: int = 40, seed: int = 0) -> dict:
    rng = random.Random(seed)
    pool: List[Con] = list(LIBRARY)
    seen = {c.parts for c in pool}
    tried: set = set()
    out = dict(arm=arm, generations=[], accepted={})
    for g in range(1, generations + 1):
        made = ill = checked = acc = 0
        new: List[Con] = []
        if arm == "network":
            pairs = [(a, b) for a in pool for b in pool if cross(a, b) and (a.parts, b.parts) not in tried]
            pairs = pairs[:per_gen] if len(pairs) > per_gen else pairs
        else:
            pairs = [(rng.choice(pool), rng.choice(pool)) for _ in range(per_gen)]
        for a, b in pairs:
            tried.add((a.parts, b.parts))
            c = cross(a, b)
            if c is None:
                if arm == "random":
                    made += 1
                    ill += 1
                continue
            made += 1
            if c.parts in seen:
                continue
            seen.add(c.parts)
            new.append(c)
            if c.closed:
                r = check(c)
                checked += 1
                if r.outcome == "accepted":
                    acc += 1
                    out["accepted"].setdefault(r.statement, dict(node=r.node, generation=g, parts=list(c.parts),
                                                                 measurement=r.measurement))
        pool += new
        out["generations"].append(dict(generation=g, offspring=made, ill_typed=ill, new=len(new),
                                       checked=checked, accepted=acc))
    return out


def compare(seeds: int = 5, **kw) -> dict:
    res = {}
    for arm in ("network", "select", "random"):
        runs = [run(arm, seed=s, **kw) for s in range(seeds)]
        found = [any("one-per-plaquette" in s for s in r["accepted"]) for r in runs]
        res[arm] = dict(offspring=sum(g["offspring"] for r in runs for g in r["generations"]) / seeds,
                        ill_typed=sum(g["ill_typed"] for r in runs for g in r["generations"]) / seeds,
                        checked=sum(g["checked"] for r in runs for g in r["generations"]) / seeds,
                        accepted=sum(len(r["accepted"]) for r in runs) / seeds,
                        found_one_third=sum(found), runs=seeds)
    return res


def all_checks() -> List[dict]:
    """Every closed composite of the library up to depth four, with its check."""
    pool = list(LIBRARY)
    seen = {c.parts for c in pool}
    rows = []
    for _ in range(4):
        new = []
        for a in pool:
            for b in pool:
                c = cross(a, b)
                if c and c.parts not in seen:
                    seen.add(c.parts)
                    new.append(c)
                    if c.closed:
                        k = check(c)
                        rows.append(dict(parts=list(c.parts), gives=c.gives, outcome=k.outcome, node=k.node,
                                         statement=k.statement))
        pool += new
    return rows


# -- per-step closure -----------------------------------------------------------------------------
def closure(tree: Dict[str, object], root: str) -> dict:
    """Leaves of the subtree at root, by status.  A leaf is a node without children; proved partial
    steps count as leaves."""
    def sub(n):
        yield n
        for c in tree[n].children:
            yield from sub(c)
    leaves = [n for n in sub(root) if not tree[n].children]
    st = {"proved": [], "open": [], "blocked": []}
    for n in leaves:
        st[tree[n].status].append(n)
    total = len(leaves)
    return dict(root=root, leaves=total, proved=len(st["proved"]), open=st["open"], blocked=st["blocked"],
                share=round(len(st["proved"]) / total, 3) if total else 0.0)


# -- the headline tree ----------------------------------------------------------------------------
EXTRA = [
    # id, parent, statement, rel, source
    ("YM.window.lsi", "YM.window", "a multiscale log-Sobolev inequality (Bauerschmidt-Bodineau) for gauge fields "
     "at order-one coupling", "route", "Bauerschmidt-Bodineau 2019; Bauerschmidt-Bodineau-Dagallier 2024"),
    ("H.F2.weil6", "H.F2", "Weil classes on abelian sixfolds of Weil type, in general", "part", ""),
    ("H.F3p.fermat220", "H.F3p.fermat", "X^4_220: the classes lifted from the leftover class of X^4_110", "part",
     "creelie/e84hc"),
]

STEP = {"YM.window.lower": ("YM.window", "lattice gap of 4D SU(2) for beta_W < 1/3, m >= -log(3 beta_W): gauge-fixed "
                            "single-link Dobrushin with one fixed link in every plaquette",
                            "this package (targets.py; lean/EBLLM/GaugeFix.lean)",
                            "finite parts (lean/EBLLM/GaugeFix.lean: one_fixed_per_plaquette, twelve_neighbours)")}


def headline_tree(state_path: Optional[str] = None):
    """The benchmark tree of the saved state, with the leaves named for the headline round added."""
    import json
    import os
    from .benchmark import Node, build_tree
    path = state_path or os.path.join(os.path.dirname(__file__), "..", "..", "..", "experiments",
                                      "benchmark_state.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            tree = {k: Node(**v) for k, v in json.load(fh)["tree"].items()}
    else:
        tree = build_tree()
    for i, par, st, rel, src in EXTRA:
        if i not in tree:
            tree[i] = Node(i, tree[par].problem, st, source=src, parent=par, rel=rel)
            tree[par].children.append(i)
    return tree


def apply(tree, accepted: Dict[str, dict]) -> List[str]:
    """Enter the accepted checks that bear on a step of STEP as proved steps."""
    from .benchmark import Node
    changes = []
    for st, v in accepted.items():
        nid = v["node"]
        if nid in STEP and nid not in tree:
            par, stmt, src, lean = STEP[nid]
            tree[nid] = Node(nid, tree[par].problem, stmt, "proved", lean, src, par, rel="step")
            tree[par].children.append(nid)
            changes.append(f"{nid}: proved step ({st})")
    return changes
