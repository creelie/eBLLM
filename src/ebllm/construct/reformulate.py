"""Two construction moves for definitions and conditional results: definition repair and the witness gate.

Definition repair. A definition D of a source text is compared with a proposed replacement D' on a
finite universe of examples and against a library of consequences, each a predicate Q. A
consequence is carried by a definition when every example satisfying the definition satisfies Q.
D' is accepted as a repair when

  (1) every example on which D and D' disagree has a stated reason (an example the old definition
      admits wrongly or misses), and
  (2) D' carries every consequence D carries and at least one more, or has the same extension as D
      with fewer clauses.

The criterion that a right definition is the one with the strongest consequences is Kontsevich's
(Leaders Talk, CGTN, 16 October 2026), where he also tells how an AI system shown the text of a talk
proposed a better definition without being asked. An accepted repair is a proposal: it passes the
usual gates (exact code or Lean) before anything downstream uses it.

The witness gate. A conditional result "H1 and ... and Hk imply C" is admitted only with a witness
that satisfies every Hi and every listed nondegeneracy condition; without one it stays a
conditional statement and is never counted as progress. A hypothesis bundle met only by a
degenerate datum, such as the zero solution, makes the implication empty. The rule comes from the
audit of Bedrossian's Lean formalization of Landau damping (arXiv:2609.16801), in which such a
bundle was closed by exhibiting a witness with its nondegeneracy facts.

PRACTICE lists the sources behind the two moves and the related formalizations
(data/practice.json); each row names the construction rule it supports.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

Pred = Callable[[object], bool]

PRACTICE: List[dict] = json.load(open(os.path.join(os.path.dirname(__file__), "data", "practice.json"),
                                      encoding="utf-8"))

RULES = {
    "R1": "a definition may be replaced only by a repair: every changed example has a reason and "
          "the replacement carries more consequences",
    "R2": "a conditional result is admitted only with a witness meeting every hypothesis and every "
          "nondegeneracy condition",
    "R3": "a proof is written in natural language first, then planned, formalized and audited "
          "against that text",
    "R4": "every place where the formal statement departs from the source is listed, with a "
          "restatement that uses the library only",
    "R5": "a heavy analytic step is first proved in a restricted range, then made elementary",
    "R6": "a withdrawn claim stays in the record, marked withdrawn",
}


@dataclass
class Definition:
    name: str
    test: Pred
    clauses: int = 1          # the size of the definition, for the tie-break


@dataclass
class RepairVerdict:
    accepted: bool
    disagreements: List[object]
    unexplained: List[object]
    carried_old: List[str]
    carried_new: List[str]
    reason: str


def carried(defn: Definition, universe: Iterable[object], library: Dict[str, Pred]) -> List[str]:
    """The consequences in the library that hold on every example satisfying the definition."""
    members = [x for x in universe if defn.test(x)]
    return sorted(q for q, pred in library.items() if members and all(pred(x) for x in members))


def repair(old: Definition, new: Definition, universe: Sequence[object],
           library: Dict[str, Pred], reasons: Dict[object, str]) -> RepairVerdict:
    dis = [x for x in universe if old.test(x) != new.test(x)]
    unexplained = [x for x in dis if x not in reasons]
    c_old, c_new = carried(old, universe, library), carried(new, universe, library)
    gains, losses = set(c_new) - set(c_old), set(c_old) - set(c_new)
    if unexplained:
        return RepairVerdict(False, dis, unexplained, c_old, c_new,
                             "the definitions differ on examples with no stated reason")
    if losses:
        return RepairVerdict(False, dis, [], c_old, c_new,
                             "the new definition loses consequences: " + ", ".join(sorted(losses)))
    if gains:
        return RepairVerdict(True, dis, [], c_old, c_new, "gains consequences: " + ", ".join(sorted(gains)))
    if not dis and new.clauses < old.clauses:
        return RepairVerdict(True, dis, [], c_old, c_new, "same extension, fewer clauses")
    return RepairVerdict(False, dis, [], c_old, c_new, "no gain")


@dataclass
class Conditional:
    name: str
    hypotheses: Dict[str, Pred]
    nondegenerate: Dict[str, Pred] = field(default_factory=dict)


def witness_gate(result: Conditional, witness: object) -> Tuple[bool, List[str]]:
    """(admitted, failures); the failures name each hypothesis or nondegeneracy check that fails."""
    if witness is None:
        return False, ["no witness exhibited"]
    fails = [h for h, p in result.hypotheses.items() if not p(witness)]
    fails += ["nondegenerate:" + h for h, p in result.nondegenerate.items() if not p(witness)]
    return not fails, fails
