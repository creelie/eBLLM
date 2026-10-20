"""The barrier ledger: no-go theorems as data, and the bypass search they drive.

A barrier is a proved statement of the form "every argument with hypotheses H_1, ..., H_k stops at
X".  The crossing network meets barriers all the time (the forest ceiling of the Dobrushin route,
the missing convexity of the Polchinski flow, the relocation of a Hodge defect by surgery), but until
now each one lived inside the stop branch of a check, as prose.  Here each barrier is a record:

* ``hypotheses``: named predicates on the parts of a composite.  The barrier applies to a composite
  exactly when every hypothesis holds for it;
* ``breakers``: for each hypothesis, the library nodes whose presence makes it fail, each with the
  reason it fails.

Two things follow.  A composite that a barrier applies to is pruned before its check runs, with the
barrier as the reason (the check is not asked to rediscover a theorem).  And the bypass search
reads the barrier backwards: to get past it, a composite must break at least one hypothesis, so the
search proposes, for every blocked composite, the crossings with a breaker of each hypothesis.
A hypothesis with no breaker in the library is reported as a *gap*: the place where a new
construction is needed, stated as the negation of that hypothesis.

Nothing here proves anything.  A bypass proposal is a crossing to try; it still has to pass its check,
the refuter and Lean.  The ledger only records which theorems stand in the way and which of their
hypotheses the library can already break.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Tuple

from .targets import Con, cross


Parts = FrozenSet[str]


@dataclass(frozen=True)
class Hyp:
    id: str
    text: str
    holds: Callable[[Parts], bool]
    breakers: Tuple[Tuple[str, str], ...] = ()      # (library node id, why its presence breaks the hypothesis)


@dataclass(frozen=True)
class Barrier:
    id: str
    problem: str
    statement: str
    source: str
    hypotheses: Tuple[Hyp, ...]
    status: str = "proved"           # proved | proved-here | observed (a measured stop, not a theorem)

    def applies(self, c: Con) -> bool:
        p = frozenset(c.parts)
        return c.problem == self.problem and all(h.holds(p) for h in self.hypotheses)

    def failing(self, c: Con) -> List[str]:
        p = frozenset(c.parts)
        return [h.id for h in self.hypotheses if not h.holds(p)]


def _has(*ids: str) -> Callable[[Parts], bool]:
    return lambda p: all(i in p for i in ids)


def _none_of(*ids: str) -> Callable[[Parts], bool]:
    return lambda p: not any(i in p for i in ids)


def _any_of(*ids: str) -> Callable[[Parts], bool]:
    return lambda p: any(i in p for i in ids)


SINGLE_SITE_BREAKERS = (
    ("ym.blocks", "updates a block of active links at once, so influences are measured block to block"),
    ("ym.gds", "Dobrushin-Shlosman on a box: the criterion is a finite-volume contraction, not a sum of single-link influences"),
    ("ym.dsgf", "Dobrushin-Shlosman on a box of the gauge-fixed specification"),
)

BARRIERS: List[Barrier] = [
    Barrier(
        "ym.forest-ceiling", "yang-mills",
        "every single-link Dobrushin argument after a forest gauge fixing in 4D has at least "
        "2(d-1)(abar-1) = 12 active partners per active link on average, so with the quarter influence "
        "bound it cannot pass beta_W = 1/3, which the one-per-plaquette gauge attains",
        "4Y-M, the forest lower bound (targets.forest_lower_bound)",
        (
            Hyp("single-site", "the specification updates one link at a time",
                _none_of("ym.blocks", "ym.gds", "ym.dsgf"), SINGLE_SITE_BREAKERS),
            Hyp("forest-gauge", "the fixed links form a forest (any gauge fixing does)",
                _any_of("ym.maxtree", "ym.temporal", "ym.plain"),
                (("ym.plaquettevars", "plaquette variables are not links; the Bianchi constraints replace the gauge"),)),
            Hyp("quarter-influence", "the influence of one link on another is bounded by |b - b'|/4",
                _has("ym.quarter"), ()),
        ),
    ),
    Barrier(
        "ym.no-convexity", "yang-mills",
        "the multiscale log-Sobolev route needs uniformly convex effective potentials along the "
        "Polchinski flow; for gauge fields at order-one coupling none is known, and gauge invariance "
        "removes the Gaussian reference measure",
        "Bauerschmidt-Bodineau-Dagallier, Probab. Surveys 21 (2024); 4Y-M strong-coupling/OPEN.md",
        (
            Hyp("flow", "the argument runs a Polchinski flow", _has("ym.polchinski"), ()),
            Hyp("gauge-invariant-reference", "no gauge fixing before the flow",
                _none_of("ym.maxtree", "ym.temporal"),
                (("ym.maxtree", "a maximal-tree gauge fixing restores a product reference measure on the "
                  "active links (convexity still has to be proved)"),)),
        ),
        status="observed",
    ),
    Barrier(
        "hodge.surgery-relocates", "hodge",
        "specialisation, blow-ups, degenerations and Fourier-Mukai equivalences move the defect of a "
        "Hodge class between varieties but never reduce it",
        "fermat-hodge-, paper/sec8_status.tex (Props. bypass and surgery)",
        (
            Hyp("surgery", "the argument moves the class by specialisation, a blow-up, a degeneration or "
                "a derived equivalence", _any_of("h.specialise", "h.blowup", "h.degenerate", "h.fm"), ()),
            Hyp("no-new-cycle", "no cycle is constructed outright on the variety that carries the class",
                _none_of("h.markman", "h.buskin", "h.shioda"),
                (("h.markman", "an algebraic cycle constructed outright (Markman's secant sheaves) is new input"),
                 ("h.buskin", "an algebraic correspondence from a rational Hodge isometry is new input"),
                 ("h.shioda", "Shioda's inductive structure produces cycles on Fermat varieties directly"))),
        ),
    ),
    Barrier(
        "hodge.chain-multipliers", "hodge",
        "a chain of quotients by finite groups of symplectic automorphisms between K3 surfaces with "
        "totally real endomorphism field has multiplier in {1, 2, 3, 6} modulo squares, so it makes no "
        "real multiplication outside Q(sqrt 2), Q(sqrt 3), Q(sqrt 6) algebraic (sqrt 10, 14, 15, 21 and "
        "every cubic field are out of reach)",
        "fermat-hodge-, Proposition sqrt10 (Nikulin's ranks 16 and 18 of the order-5 and order-7 coinvariants)",
        (
            Hyp("symplectic-quotients", "every correspondence of the chain is a quotient by symplectic automorphisms",
                _has("h.similitude"), ()),
            Hyp("no-new-correspondence", "no correspondence outside the chain acts on T(S)",
                _none_of("h.markman"), ()),
        ),
    ),
    Barrier(
        "hodge.hk-carriers-trivial", "hodge",
        "composites of rational Hodge isometries between hyper-Kahler carriers of K3^[n] type with "
        "transcendental space (T, r q_lambda) return to a carrier by +-1, and composites of similarities by "
        "a rational number, so the algebraic isometries of Buskin and Markman never give an irrational "
        "element of a cubic field",
        "fermat-hodge-, Proposition hk",
        (
            Hyp("isometries-only", "the correspondences are Hodge isometries or similarities between carriers",
                _any_of("h.buskin", "h.rmclasses"), ()),
            Hyp("cubic-field", "the endomorphism field of T is a totally real cubic field",
                _none_of("h.symreduce"), ()),
        ),
    ),
]


@dataclass
class Bypass:
    composite: str
    barrier: str
    hypothesis: str
    breaker: str
    reason: str
    offspring: Optional[str] = None      # the crossing that adds the breaker, when the types allow it


@dataclass
class Report:
    pruned: Dict[str, str] = field(default_factory=dict)          # composite id -> barrier id
    bypasses: List[Bypass] = field(default_factory=list)
    gaps: List[Tuple[str, str, str]] = field(default_factory=list)  # (barrier, hypothesis, what is needed)


def blocking(c: Con, barriers: Iterable[Barrier] = BARRIERS) -> Optional[Barrier]:
    return next((b for b in barriers if b.applies(c)), None)


def bypass_search(pool: Iterable[Con], library: Iterable[Con], barriers: Iterable[Barrier] = BARRIERS) -> Report:
    """Prune every composite of the pool that a barrier applies to, and for each one propose the
    crossings that would break a hypothesis of that barrier."""
    barriers = list(barriers)
    lib = {c.id: c for c in library}
    rep = Report()
    seen_gaps = set()
    for c in pool:
        b = blocking(c, barriers)
        if b is None:
            continue
        rep.pruned[c.id] = b.id
        for h in b.hypotheses:
            if not h.breakers and (b.id, h.id) not in seen_gaps:
                seen_gaps.add((b.id, h.id))
                rep.gaps.append((b.id, h.id, "a construction with the negation of: " + h.text))
            for node, why in h.breakers:
                if node not in lib:
                    continue
                n = lib[node]
                child = cross(n, c) or cross(c, n)
                rep.bypasses.append(Bypass(c.id, b.id, h.id, node, why, child.id if child else None))
    return rep


def ledger() -> List[dict]:
    """The barriers as rows, for ``anaxia barriers``."""
    return [dict(id=b.id, problem=b.problem, status=b.status, statement=b.statement, source=b.source,
                 hypotheses=[dict(id=h.id, text=h.text, breakers=[n for n, _ in h.breakers])
                             for h in b.hypotheses])
            for b in BARRIERS]
