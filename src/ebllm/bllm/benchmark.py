"""The Hodge and Yang-Mills benchmark: a goal tree, a move router, and a loop that learns from failure.

Each problem is a tree of statements.  An open leaf is attacked by one of the moves of `corpus.MOVES`
(reduction, lift, certificate, construction, counterexample, flow-surgery, descent, physics-first).
A *probe* is the executable form of one move at one leaf: a computation that either establishes a
checkable step (accepted), or stops with a residual statement and the measurement that stopped it.

A round races the router once for every open leaf among the moves not yet tried there, runs the
probe, and then

* records the attempt (move, outcome, residual, measurement, Lean status);
* updates the router: an accepted step potentiates the move, a failure depresses it;
* restructures the tree: a stopped probe may return residual sub-goals, which become new leaves.

Failures already recorded by earlier attempts outside this package (reports in the project's
Yang-Mills and Hodge folders) are entered in round 0 as known failures, so the loop does not repeat
them.  The loop ends when no open leaf has an untried move; the final report is the list of open
leaves with every move tried and where each stopped.

Lean is the judge for statements that have a faithful Lean form.  For the full Hodge conjecture and
the full Yang-Mills problem there is none: the formal statements in the Lean Millennium Prize
Problems repository are marked `statement_incomplete` (the Hodge one is vacuous, by a proof of
K. Buzzard), and a faithful statement needs parts of Hodge theory and of quantum field theory that
Mathlib does not contain.  Those nodes are reported as blocked at the statement, not as open.
"""
from __future__ import annotations

import json
import math
import os
import random
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from math import gcd
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .corpus import MOVES
from .neuro import SpikingSelector


# -- tree ---------------------------------------------------------------------------------------------
@dataclass
class Node:
    id: str
    problem: str
    statement: str
    status: str = "open"          # open | proved | blocked
    lean: str = "none"            # kernel-checked | finite parts | none | no faithful statement
    source: str = ""
    parent: Optional[str] = None
    kind: str = "and"             # and: proved when every part is proved
    children: List[str] = field(default_factory=list)
    rel: str = "part"             # part of the parent | route to the parent | step (a proved partial result)
    requires: List[str] = field(default_factory=list)   # attacked only once these are proved


@dataclass
class Result:
    outcome: str                  # accepted | rejected | stopped
    residual: str
    measurement: dict = field(default_factory=dict)
    lean: str = "none"
    closes: bool = False          # the accepted step proves the node itself
    new: List[dict] = field(default_factory=list)


@dataclass
class Attempt:
    round: int
    node: str
    move: str
    outcome: str
    residual: str
    measurement: dict
    lean: str
    source: str = "this package"


# -- probes -------------------------------------------------------------------------------------------
Probe = Callable[[dict], Result]
PROBES: Dict[Tuple[str, str], Probe] = {}


def probe(node: str, *moves: str):
    def wrap(f):
        for m in moves:
            PROBES[(node, m)] = f
        return f
    return wrap


_PROBE_CACHE: Dict[Tuple[str, str, str], "Result"] = {}


def run_probe(node: str, move: str, f, cfg: dict) -> "Result":
    """Probes are deterministic functions of the configuration, so their results are cached."""
    key = (node, move, json.dumps(cfg, sort_keys=True, default=str))
    if key not in _PROBE_CACHE:
        _PROBE_CACHE[key] = f(cfg)
    return _PROBE_CACHE[key]


def _registry_status(root: Optional[str], name: str) -> Optional[str]:
    if not root:
        return None
    path = os.path.join(root, "Problems", "Registry.lean")
    if not os.path.exists(path):
        return None
    text = open(path, encoding="utf-8").read()
    i = text.find(f'short_name := "{name}"')
    if i < 0:
        return None
    j = text.find("status :=", i)
    return text[j:text.find("\n", j)].split(":=")[1].strip() if j > 0 else None


def _statement_probe(name: str, missing: str):
    def run(cfg: dict) -> Result:
        st = _registry_status(cfg.get("millennium_root"), name)
        return Result("stopped", f"no faithful Lean statement: the registry marks {name} as {st}; "
                                 f"a faithful one needs {missing}", dict(registry_status=st),
                      lean="no faithful statement")
    return run


for _m in MOVES:
    PROBES[("YM.lean", _m)] = _statement_probe(
        "YangMills", "a Wightman or Osterwalder-Schrader framework tied to SU(N) gauge fields, absent from Mathlib")
    PROBES[("H.lean", _m)] = _statement_probe(
        "Hodge", "the analytic topology on X(C), the Hodge decomposition and the cycle class map, absent from Mathlib")


def dobrushin_coefficient(beta_w: float, d: int = 4) -> float:
    """Single-link Dobrushin coefficient 6 (d - 1) |beta| for SU(2), beta = beta_W / 4 (4Y-M, Thresholds.lean)."""
    return 6 * (d - 1) * abs(beta_w / 4)


@probe("YM.strong", "certificate")
def _ym_strong(cfg: dict) -> Result:
    grid = [Fraction(k, 100) for k in range(1, 23)]
    ok = [b for b in grid if dobrushin_coefficient(float(b)) < 1]
    gaps = {str(b): round(-math.log(9 * float(b) / 2), 4) for b in (Fraction(1, 10), Fraction(1, 5), Fraction(22, 100))}
    return Result("accepted", "gap m >= -log(9 beta_W / 2) for beta_W < 2/9 in 4D SU(2)",
                  dict(largest_grid_beta=str(max(ok)), gaps=gaps, ceiling="2/9"),
                  lean="finite parts (creelie/4Y-M, YangMills/StrongCoupling/Thresholds.lean: gap_pos, gap_d4)",
                  closes=True)


@probe("YM.window", "certificate")
def _ym_window_cert(cfg: dict) -> Result:
    c = {b: dobrushin_coefficient(b) for b in (2 / 9, 0.3, 0.5, 1.0, 2.0)}
    return Result("rejected", "single-link Dobrushin certificates end at beta_W = 2/9: the coefficient is >= 1 "
                              "beyond it, so no single-link certificate exists in the window",
                  dict(coefficients={str(round(k, 4)): round(v, 4) for k, v in c.items()}),
                  new=[dict(id="YM.window.box", statement="a finite-box gauge-invariant mixing certificate "
                            "(Conjecture G of subgap3) at one coupling in the window", source="subgap3-finite-box.md")])


@probe("YM.window", "lift")
def _ym_lift(cfg: dict) -> Result:
    # two dimensions: exact gap from the character expansion of the heat kernel, at every beta
    from math import exp
    def bessel_ratio(n, beta, terms=60):
        def I(k):
            return sum((beta / 2) ** (2 * j + k) / (math.factorial(j) * math.factorial(j + k)) for j in range(terms))
        return I(n + 1) / I(1)
    sigma = {b: round(-math.log(bessel_ratio(1, b) / 1), 4) for b in (1.0, 4.0, 16.0)}
    return Result("stopped", "the gap exists at every coupling in two dimensions (string tension "
                             "-log(I_2/I_1) > 0), but there is no deformation from d = 2 to d = 4: "
                             "2D gauge fields have no local degrees of freedom",
                  dict(string_tension_2d=sigma), lean="none",
                  new=[dict(id="YM.window.lift", statement="a lift of the two-dimensional gap through a "
                            "family of theories interpolating in dimension", source="this package")])


@probe("YM.window.box", "certificate", "construction")
def _ym_box(cfg: dict) -> Result:
    side = 90
    links = 4 * side ** 4
    return Result("stopped", "the gauge finite-box test needs a box of side about 90 in 4D; the check is "
                             "over SU(2)^{links} with boundary conditions, far beyond any exact computation",
                  dict(side=side, links=links), lean="none")


# Hodge: Fermat fourfolds of degree m by Shioda's inductive structure
def fermat_hodge_characters(m: int, n: int = 4):
    """Sorted Hodge characters a in ((Z/m) - 0)^{n+2} of X^n_m with sum 0 and <t a> summing to (n/2 + 1) m."""
    k = n + 2
    units = [t for t in range(1, m) if gcd(t, m) == 1]
    out = []

    def rec(prefix, start, s):
        if len(prefix) == k - 1:
            last = (-s) % m
            if last == 0 or last < prefix[-1]:
                return
            a = prefix + [last]
            if all(sum((t * x) % m for x in a) == (k // 2) * m for t in units):
                out.append(tuple(a))
            return
        for x in range(start, m):
            rec(prefix + [x], x, s + x)
    rec([], 1, 0)
    return out


def decomposes(a: Sequence[int], m: int) -> bool:
    """A zero-sum pair or triple splits the class into products of lower Fermat varieties
    (Shioda's inductive structure), whose Hodge classes are algebraic by Lefschetz (1,1)."""
    k = len(a)
    for i in range(k):
        for j in range(i + 1, k):
            if (a[i] + a[j]) % m == 0:
                return True
            for l in range(j + 1, k):
                if (a[i] + a[j] + a[l]) % m == 0:
                    return True
    return False


@probe("H.F3p.fermat", "lift", "reduction")
def _fermat_census(cfg: dict) -> Result:
    top = int(cfg.get("fermat_max", 24))
    clean, bad = [], {}
    for m in range(3, top + 1):
        ex = [a for a in fermat_hodge_characters(m) if not decomposes(a, m)]
        if ex:
            bad[m] = len(ex)
        else:
            clean.append(m)
    return Result("accepted" if clean else "rejected",
                  "HC for X^4_m whenever every Hodge character splits by a zero-sum pair or triple "
                  "(Shioda 1979); degrees with leftover characters need other cycles",
                  dict(degrees_checked=f"3..{top}", all_split=clean, leftover_counts=bad),
                  lean="none (finite census computed here; the geometric step is Shioda's)",
                  new=[dict(id="H.F3p.fermat110", statement="X^4_110: the class 2_* xi_55 left by the census and "
                            "by Aoki's cycles", source="creelie/e84hc", rel="part")])


@probe("H.F3p.fermat110", "certificate", "construction")
def _fermat110(cfg: dict) -> Result:
    m, a = 55, (1, 16, 26, 31, 36)
    shadows = [t for t in range(1, m) if gcd(t, m) > 1 and all((t * x) % m for x in a)
               and sum((t * x) % m for x in a) == m]
    return Result("rejected", "a block-pattern certificate (Fine interior empty, so the quotient is uniruled) "
                              "cannot exist: the character has a shadow, a non-unit t with sum <t a_k> = m, "
                              "which is a lattice point of the Fine interior",
                  dict(character=list(a), level=m, shadows=shadows), lean="none")


@probe("H.F3p.K3RM", "reduction", "lift")
def _k3rm(cfg: dict) -> Result:
    root = cfg.get("openai_root")
    formal = None
    if root and os.path.exists(os.path.join(root, "lean", "formalization.yaml")):
        y = open(os.path.join(root, "lean", "formalization.yaml"), encoding="utf-8").read().lower()
        formal = ("products of k3" in y) or ("hodge conjecture" in y)
    return Result("rejected", "the reduction would import OpenAI's unrefereed theorem on products of K3 surfaces "
                              "(family 032); it has no Lean formalisation, so the judge rejects the import",
                  dict(openai_hodge_in_lean_catalogue=formal), lean="none")


@probe("H.F2.cm", "reduction")
def _f2cm(cfg: dict) -> Result:
    r = _k3rm(cfg)
    r.residual = ("the CM case would import OpenAI's unrefereed theorem for CM abelian varieties (family 032); "
                  "no Lean formalisation, so the judge rejects the import")
    return r


@probe("H.F2.E06", "construction")
def _e06(cfg: dict) -> Result:
    return Result("rejected", "convolutions of Weil line bundles on E_0^6 have dim Ext^2 >= 69 > 57, so they do not "
                              "meet the polarised semiregularity criterion (n = 3, trivial discriminant)",
                  dict(ext2_lower=69, needed=57), lean="finite parts (creelie/H8 Lean Section 42)")


# -- known failures from earlier reports --------------------------------------------------------------
KNOWN = [
    ("YM.window", "flow-surgery", "t^2 E(t) along the Wilson flow is not monotone on a finite torus; no sup-norm "
                                  "control at order-one coupling", "yang-mills/agents2/crossover.md"),
    ("YM.window", "reduction", "Tomboulis decimations: refuted as written (Kanazawa's U(1) reductio)",
     "yang-mills/agents/route-tomboulis.md"),
    ("YM.window", "physics-first", "large-N master loop: needs a weak-coupling a priori estimate nobody has",
     "yang-mills/agents/route-largeN.md"),
    ("YM.window", "descent", "Balaban's multiscale induction is controlled only at small coupling",
     "yang-mills/agents/route-balaban.md"),
    ("YM.window.box", "lift", "Knabe-type gap certificate needs relaxation rates beyond the measured ones",
     "yang-mills/agents2/code/crossover/glauber_relax.py"),
    ("H.F3p", "construction", "det T sign obstruction: canonical cycles have zero det T component",
     "hodge-full-attack/ideas.md"),
    ("H.F2.weil8", "construction", "Pryms of cyclic triple covers: family dimension <= 3n < n^2",
     "memory: hodge-closure-attempts"),
    ("H.F2.weil8", "lift", "deforming Schoen's cycle: rigid along the Prym locus", "memory: hodge-closure-attempts"),
]


def build_tree() -> Dict[str, Node]:
    nodes = [
        Node("YM", "yang-mills", "Clay: quantum SU(N) Yang-Mills on R^4 exists with a mass gap", kind="and"),
        Node("YM.lean", "yang-mills", "a faithful Lean statement of the Clay problem", parent="YM"),
        Node("YM.lattice", "yang-mills", "Hypothesis R: a lattice gap uniform in the spacing", parent="YM"),
        Node("YM.continuum", "yang-mills", "continuum limit with the Wightman axioms", parent="YM",
             requires=["YM.lattice"]),
        Node("YM.strong", "yang-mills", "lattice gap at strong coupling", parent="YM.lattice"),
        Node("YM.weak", "yang-mills", "fine-scale control at weak coupling", parent="YM.lattice", status="proved",
             source="Balaban 1984-89", lean="none"),
        Node("YM.window", "yang-mills", "the crossover window: order-one coupling, uniformly in the spacing",
             parent="YM.lattice"),
        Node("H", "hodge", "Hodge conjecture", kind="and"),
        Node("H.lean", "hodge", "a faithful Lean statement of the Hodge conjecture", parent="H"),
        Node("H.F2", "hodge", "(F2): the Hodge conjecture for abelian varieties", parent="H"),
        Node("H.F3p", "hodge", "(F3'): no Hodge classes off the part reached from abelian varieties", parent="H"),
        Node("H.F2.dim5", "hodge", "(F2) in dimension at most five", parent="H.F2", status="proved",
             source="Markman 2025; Moonen-Zarhin", lean="none"),
        Node("H.F2.cm", "hodge", "(F2) for CM abelian varieties", parent="H.F2"),
        Node("H.F2.weil8", "hodge", "Weil classes on split Weil eightfolds of nontrivial discriminant", parent="H.F2"),
        Node("H.F2.E06", "hodge", "a semiregular object on E_0^6 meeting the polarised criterion", parent="H.F2"),
        Node("H.F3p.K3RM", "hodge", "(F3') for S x S, S a very general K3 in the 8-dimensional RM family",
             parent="H.F3p"),
        Node("H.F3p.fermat", "hodge", "(F3') and HC for Fermat fourfolds", parent="H.F3p"),
    ]
    tree = {n.id: n for n in nodes}
    for n in nodes:
        if n.parent:
            tree[n.parent].children.append(n.id)
    return tree


# -- router -------------------------------------------------------------------------------------------
class RoutingSelector(SpikingSelector):
    """A spiking selector whose synapses encode successes and failures: the weight of move k is
    theta + (delta/2) log((s_k + alpha)/(s_k + f_k + 2 alpha)) up to the common scaling shift, so the
    first-spike probabilities are proportional to sqrt of the posterior success rate."""

    def __init__(self, names, successes=None, failures=None, **kw):
        super().__init__(names=list(names), **kw)
        self.counts = list(successes or [0.0] * len(self.names))
        self.fails = list(failures or [0.0] * len(self.names))
        self._set()

    def _set(self):
        a = self.alpha
        self.w = [self.theta + 0.5 * self.delta * math.log((s + a) / (s + f + 2 * a))
                  for s, f in zip(self.counts, self.fails)]
        self._scale()

    def reward(self, k: int, amount: float = 1.0) -> None:
        self.counts[k] += amount
        self._set()

    def depress(self, k: int, amount: float = 1.0) -> None:
        self.fails[k] += amount
        self._set()

    def target(self) -> List[float]:
        a = self.alpha
        r = [math.sqrt((s + a) / (s + f + 2 * a)) for s, f in zip(self.counts, self.fails)]
        t = sum(r)
        return [x / t for x in r]


ERDOS_TO_MOVE = {"counterexample": "counterexample", "construction": "construction",
                 "probabilistic": "construction", "known-machinery": "reduction",
                 "density-increment": "descent", "induction-descent": "descent",
                 "computer-search": "certificate", "lp-sdp-certificate": "certificate"}


def erdos_rates(harvest: Optional[dict]) -> Dict[str, Tuple[int, int]]:
    """(settled problems, those with a Lean solution) per move, from the Erdos harvest."""
    out: Dict[str, List[int]] = {}
    if not harvest or "strategies" not in harvest:
        return {}
    for v in harvest["strategies"]["per_problem"].values():
        for m in {ERDOS_TO_MOVE[s] for s in v["strategies"] if s in ERDOS_TO_MOVE}:
            c = out.setdefault(m, [0, 0])
            c[0] += 1
            c[1] += int(v["lean"])
    return {m: (a, b) for m, (a, b) in out.items()}


def corpus_prior(stats: Optional[dict], pseudo: float = 10.0,
                 harvest: Optional[dict] = None) -> Tuple[List[float], List[float]]:
    """Success and failure pseudo-counts per move: the Lean-formalised share of the OpenAI manuscripts
    using the move, averaged with the Lean-solved share of the settled Erdos problems using it when
    the harvest is given and names the move."""
    if not stats or "openai" not in stats:
        return [1.0] * len(MOVES), [1.0] * len(MOVES)
    mv = stats["openai"]["moves"]
    er = erdos_rates(harvest)
    rate = []
    for m in MOVES:
        r = mv[m]["rate"] or 0.0
        if m in er and er[m][0]:
            r = (r + er[m][1] / er[m][0]) / 2
        rate.append(r)
    s = [pseudo * r for r in rate]
    return s, [pseudo - x for x in s]


# -- the loop -----------------------------------------------------------------------------------------
@dataclass
class Benchmark:
    tree: Dict[str, Node]
    router: RoutingSelector
    attempts: List[Attempt] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)
    round: int = 0

    @classmethod
    def new(cls, stats: Optional[dict] = None, harvest: Optional[dict] = None) -> "Benchmark":
        s, f = corpus_prior(stats, harvest=harvest)
        b = cls(build_tree(), RoutingSelector(MOVES, s, f))
        for node, move, residual, src in KNOWN:
            b.attempts.append(Attempt(0, node, move, "known failure", residual, {}, "none", src))
            b.router.depress(MOVES.index(move), 0.5)
        b.history.append(dict(round=0, changes=[f"entered {len(KNOWN)} known failures"],
                              probabilities=dict(zip(MOVES, [round(x, 4) for x in b.router.probabilities()]))))
        return b

    def tried(self, node: str) -> set:
        return {a.move for a in self.attempts if a.node == node}

    def leaves(self) -> List[str]:
        out = []
        for n in self.tree.values():
            if n.status != "open":
                continue
            if any(self.tree[c].status == "open" and self.tree[c].rel == "part" for c in n.children):
                continue
            if any(self.tree[r].status != "proved" for r in n.requires):
                continue
            out.append(n.id)
        return out

    def _propagate(self) -> None:
        changed = True
        while changed:
            changed = False
            for n in self.tree.values():
                if n.status != "open":
                    continue
                parts = [self.tree[c] for c in n.children if self.tree[c].rel == "part"]
                routes = [self.tree[c] for c in n.children if self.tree[c].rel == "route"]
                if (parts and all(c.status == "proved" for c in parts)) or any(c.status == "proved" for c in routes):
                    n.status, changed = "proved", True

    def step(self, cfg: dict, rng: random.Random, mix: Optional[Callable[[Node, List[str]], List[float]]] = None,
             lam: float = 0.5) -> dict:
        self.round += 1
        changes, ran = [], []
        for nid in self.leaves():
            node = self.tree[nid]
            untried = [m for m in MOVES if m not in self.tried(nid)]
            if not untried:
                continue
            ex = [MOVES.index(m) for m in MOVES if m not in untried]
            if mix is None:
                k = self.router.race(rng, exclude=ex)
                move = MOVES[k]
            else:                                         # the BLLM mixture: router and language model
                p = self.router.probabilities()
                q = mix(node, list(MOVES))
                w = [0.0 if i in ex else (1 - lam) * p[i] + lam * q[i] for i in range(len(MOVES))]
                k = rng.choices(range(len(MOVES)), weights=w)[0]
                move = MOVES[k]
            f = PROBES.get((nid, move))
            if f is None:
                r = Result("stopped", f"no checkable formulation of '{move}' at this node is implemented")
            else:
                r = run_probe(nid, move, f, cfg)
            self.attempts.append(Attempt(self.round, nid, move, r.outcome, r.residual, r.measurement, r.lean))
            ran.append((nid, move, r.outcome))
            if r.outcome == "accepted":
                self.router.reward(k)
                if r.closes:
                    node.status, node.lean = "proved", r.lean
                    changes.append(f"{nid} proved by {move}")
                else:
                    cid = f"{nid}.{move}"
                    self.tree[cid] = Node(cid, node.problem, r.residual, "proved", r.lean, "this package", nid,
                                          rel="step")
                    node.children.append(cid)
                    changes.append(f"{nid}: proved step {cid}")
            else:
                self.router.depress(k)
                if r.lean == "no faithful statement":
                    node.status, node.lean = "blocked", r.lean
                    changes.append(f"{nid} blocked at the statement")
            for d in r.new:
                if d["id"] not in self.tree:
                    self.tree[d["id"]] = Node(d["id"], node.problem, d["statement"], source=d.get("source", ""),
                                              parent=nid, rel=d.get("rel", "route"))
                    node.children.append(d["id"])
                    changes.append(f"new leaf {d['id']} under {nid}")
        self._propagate()
        rec = dict(round=self.round, ran=ran, changes=changes,
                   accepted=sum(1 for _, _, o in ran if o == "accepted"),
                   open_leaves=len(self.leaves()),
                   proved=sorted(n.id for n in self.tree.values() if n.status == "proved"),
                   probabilities=dict(zip(MOVES, [round(x, 4) for x in self.router.probabilities()])))
        self.history.append(rec)
        return rec

    def exhausted(self) -> bool:
        return all(not [m for m in MOVES if m not in self.tried(n)] for n in self.leaves())

    def run(self, cfg: dict, rounds: int = 50, seed: int = 1, state: Optional[str] = None, **kw) -> List[dict]:
        rng = random.Random(seed + self.round)
        out = []
        for _ in range(rounds):
            if self.exhausted():
                break
            out.append(self.step(cfg, rng, **kw))
            if state:
                self.save(state)
        return out

    def report(self) -> dict:
        blocked = {}
        waiting = [n.id for n in self.tree.values() if n.status == "open" and n.requires
                   and any(self.tree[r].status != "proved" for r in n.requires)]
        for nid in self.leaves() + waiting + [n.id for n in self.tree.values() if n.status == "blocked"]:
            blocked[nid] = dict(statement=self.tree[nid].statement, status=self.tree[nid].status,
                                attempts=[dict(move=a.move, outcome=a.outcome, residual=a.residual, source=a.source)
                                          for a in self.attempts if a.node == nid])
        top = {p: self.tree[p].status for p in ("YM", "H")}
        return dict(top=top, rounds=self.round, attempts=len(self.attempts),
                    accepted=[asdict(a) for a in self.attempts if a.outcome == "accepted"], stopped_at=blocked)

    # persistence: the state after every round, so a restarted session resumes
    def save(self, path: str) -> None:
        d = dict(round=self.round, tree={k: asdict(v) for k, v in self.tree.items()},
                 attempts=[asdict(a) for a in self.attempts], history=self.history,
                 router=dict(successes=self.router.counts, failures=self.router.fails))
        tmp = path + ".tmp"
        with open(tmp, "w") as h:
            json.dump(d, h, indent=1)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path: str) -> "Benchmark":
        d = json.load(open(path))
        b = cls({k: Node(**v) for k, v in d["tree"].items()},
                RoutingSelector(MOVES, d["router"]["successes"], d["router"]["failures"]),
                [Attempt(**a) for a in d["attempts"]], d["history"], d["round"])
        return b

    def write_vault(self, root: str) -> None:
        """One Obsidian note per node and per round, linked by [[ids]]."""
        os.makedirs(os.path.join(root, "nodes"), exist_ok=True)
        os.makedirs(os.path.join(root, "rounds"), exist_ok=True)
        for n in self.tree.values():
            lines = ["---", f"id: {n.id}", f"status: {n.status}", f"lean: {n.lean}", "---", "",
                     f"# {n.id}", "", n.statement, ""]
            if n.parent:
                lines.append(f"Part of [[{n.parent}]].")
            for c in n.children:
                lines.append(f"- [[{c}]] ({self.tree[c].status})")
            lines.append("")
            for a in self.attempts:
                if a.node == n.id:
                    lines.append(f"- round {a.round}, **{a.move}**: {a.outcome}. {a.residual}"
                                 + (f" (source: {a.source})" if a.source != "this package" else ""))
            open(os.path.join(root, "nodes", f"{n.id}.md"), "w").write("\n".join(lines) + "\n")
        for h in self.history:
            r = h["round"]
            lines = ["---", f"round: {r}", f"accepted: {h.get('accepted', 0)}", "---", "", f"# Round {r}", ""]
            for nid, move, out in h.get("ran", []):
                lines.append(f"- [[{nid}]]: {move} -> {out}")
            lines += ["", "Changes:"] + [f"- {c}" for c in h.get("changes", [])]
            lines += ["", "Router: " + ", ".join(f"{k} {v}" for k, v in h["probabilities"].items())]
            open(os.path.join(root, "rounds", f"round-{r:02d}.md"), "w").write("\n".join(lines) + "\n")
