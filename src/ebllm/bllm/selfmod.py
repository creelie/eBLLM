"""Learning from failure: every failed attempt is logged, changes one rule of the engine, and is retried.

A *rule* is a named setting that a run reads: the representation of the object searched for, a hard
filter, the search strategy, the check, the library, the retrieval, the budget, the mode.  One
attempt on a target ends in one of four outcomes:

    closed     the target is settled and the result passed every check;
    partial    a weaker statement or a piece of the target passed;
    failed     the attempt ran and produced nothing that passed;
    stopped    no checkable form of the next step exists under the current rules.

After a failure the loop writes one record:

    target, attempt     what was attacked, and the how-many-th time;
    rules_version       the version of the rule book the attempt ran under;
    failed_part         the part of the engine that failed, with the evidence (a measurement);
    diagnosis           one of the failure kinds of KINDS;
    change              the rule it alters, its kind, the old and the new value;
    retry               the outcome of the next attempt, which runs under the changed rules.

The change is chosen from the diagnosis by a playbook (failure kind -> rule kinds that address it).
The playbook ranks the rule kinds by how often a change of that kind has turned a failure of that
kind into a closed or partial retry in the log so far, with a prior from the table PLAYBOOK, so the
log trains the playbook as it grows.  A success changes nothing.  Two guards keep the loop honest:
a change must name a measurement that it is meant to improve, and the same change is never applied
twice to the same target, so a retry is never the same attempt again.

With a skill memory (module ``skills``) the loop ranks the kinds by the whole runs a change belonged
to, and the playbook only breaks ties; the memory is rebuilt from the log.

The bundled log (data/modlog.json) holds the records of the runs from which the rules of the engine
were changed: the construction-mode runs on planar colouring gadgets and the run on the Calabi-Yau
seed conjecture.  ``patterns`` turns any log into the failure-to-change matrix and the success of the
retries, which is what the paper draws.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

DATA = os.path.join(os.path.dirname(__file__), "data")

OUTCOMES = ("closed", "partial", "failed", "stopped")

# Failure kinds, each with the question the diagnosis answers.
KINDS: Dict[str, str] = {
    "missing-mode": "the engine has no mode that can even state the object the target needs",
    "filter-cost": "a hard filter takes almost all of the budget (most cuts or checks are spent on it)",
    "generator": "candidates are produced and checked, and none survives",
    "rules-silent": "no rule of the current rule set can fire on the target",
    "arrangement": "the argument is found but cannot be arranged as the target requires",
    "retrieval": "the target was already settled, or a needed result was in the literature and missed",
    "overclaim": "the statement aimed at is stronger than what the run can prove",
    "scale": "the exact computation is larger than the hardware can finish",
    "representation": "the object is searched in a form in which the property is not visible",
}

# Rule kinds a change can alter.
RULE_KINDS: Dict[str, str] = {
    "mode": "add a mode of work (a new object type with its filter, its property and its check)",
    "representation": "change how candidates are written, so that a filter holds by construction",
    "strategy": "change how candidates are generated (goal-directed instead of random, a new order)",
    "library": "add stored results as rules or lemmas",
    "retrieval": "change what is searched before an attack",
    "scope": "replace the target by the statement the evidence supports",
    "reduction": "reduce the target to a finite profile or to counts that are already known",
    "check": "add or replace a check",
    "budget": "change the budget or the hardware a step runs on",
}

# Prior: which rule kinds address which failure kind, best first.
PLAYBOOK: Dict[str, Tuple[str, ...]] = {
    "missing-mode": ("mode", "representation"),
    "filter-cost": ("representation", "strategy", "budget"),
    "generator": ("strategy", "library", "representation"),
    "rules-silent": ("library", "strategy"),
    "arrangement": ("representation", "strategy"),
    "retrieval": ("retrieval", "scope"),
    "overclaim": ("scope", "reduction"),
    "scale": ("reduction", "representation", "budget"),
    "representation": ("representation", "reduction", "strategy"),
}


@dataclass
class Change:
    rule: str
    kind: str
    old: str
    new: str
    improves: str  # the measurement the change is meant to improve

    def key(self) -> Tuple[str, str]:
        return (self.rule, self.new)


@dataclass
class Record:
    target: str
    attempt: int
    rules_version: int
    outcome: str
    failed_part: str = ""
    evidence: str = ""
    diagnosis: str = ""
    change: Optional[Change] = None
    retry: str = ""
    note: str = ""

    def as_dict(self) -> dict:
        d = asdict(self)
        if self.change is None:
            d["change"] = None
        return d

    @staticmethod
    def from_dict(d: dict) -> "Record":
        c = d.get("change")
        return Record(target=d["target"], attempt=int(d["attempt"]), rules_version=int(d.get("rules_version", 0)),
                      outcome=d["outcome"], failed_part=d.get("failed_part", ""), evidence=d.get("evidence", ""),
                      diagnosis=d.get("diagnosis", ""), change=Change(**c) if c else None,
                      retry=d.get("retry", ""), note=d.get("note", ""))


class RuleBook:
    """The rules a run reads, with every change kept in order."""

    def __init__(self, rules: Optional[Dict[str, str]] = None):
        self.rules: Dict[str, str] = dict(rules or {})
        self.history: List[Change] = []

    @property
    def version(self) -> int:
        return len(self.history)

    def get(self, name: str, default: str = "") -> str:
        return self.rules.get(name, default)

    def apply(self, change: Change) -> "RuleBook":
        if change.kind not in RULE_KINDS:
            raise ValueError(f"unknown rule kind {change.kind!r}")
        if not change.improves:
            raise ValueError("a change must name the measurement it is meant to improve")
        if self.rules.get(change.rule, "") != change.old:
            raise ValueError(f"rule {change.rule!r} is {self.rules.get(change.rule, '')!r}, not {change.old!r}")
        new = RuleBook(self.rules)
        new.history = self.history + [change]
        new.rules[change.rule] = change.new
        return new

    def to_json(self) -> dict:
        return dict(rules=self.rules, history=[asdict(c) for c in self.history])


class Playbook:
    """Ranks the rule kinds for a diagnosis: prior order, then the record of retries in the log."""

    def __init__(self, prior: Optional[Dict[str, Tuple[str, ...]]] = None):
        self.prior = dict(prior or PLAYBOOK)
        self.wins: Dict[Tuple[str, str], int] = {}
        self.tries: Dict[Tuple[str, str], int] = {}

    def learn(self, records: Iterable[Record]) -> "Playbook":
        for r in records:
            if r.change is None or not r.diagnosis or not r.retry:
                continue
            k = (r.diagnosis, r.change.kind)
            self.tries[k] = self.tries.get(k, 0) + 1
            if r.retry in ("closed", "partial"):
                self.wins[k] = self.wins.get(k, 0) + 1
        return self

    def score(self, diagnosis: str, kind: str) -> float:
        order = self.prior.get(diagnosis, ())
        prior = 1.0 / (2 + order.index(kind)) if kind in order else 0.1
        w, t = self.wins.get((diagnosis, kind), 0), self.tries.get((diagnosis, kind), 0)
        return (w + 2 * prior) / (t + 2)  # Laplace-style smoothing toward the prior

    def rank(self, diagnosis: str) -> List[str]:
        if diagnosis not in KINDS:
            raise ValueError(f"unknown failure kind {diagnosis!r}")
        return sorted(RULE_KINDS, key=lambda k: (-self.score(diagnosis, k), k))


AttemptFn = Callable[[str, RuleBook], Tuple[str, str, str]]          # -> (outcome, failed_part, evidence)
DiagnoseFn = Callable[[str, str, str], str]                           # (outcome, part, evidence) -> kind
ProposeFn = Callable[[str, List[str], RuleBook, List[Record]], Optional[Change]]


class FailLoop:
    """Attempt, and on failure log, diagnose, change one rule and retry, until closed or out of moves."""

    def __init__(self, attempt: AttemptFn, diagnose: DiagnoseFn, propose: ProposeFn,
                 book: Optional[RuleBook] = None, playbook: Optional[Playbook] = None, memory=None,
                 max_attempts: int = 12, skills=None, area: str = ""):
        self.attempt, self.diagnose, self.propose = attempt, diagnose, propose
        self.book = book or RuleBook()
        self.playbook = playbook or Playbook()
        self.memory = memory
        self.max_attempts = max_attempts
        self.skills, self.area = skills, area   # a skills.SkillMemory, and the run the targets belong to
        self.log: List[Record] = []

    def _write(self, r: Record) -> None:
        self.log.append(r)
        if self.memory is not None:
            self.memory.record_attempt(r.as_dict())

    def rank(self, diagnosis: str) -> List[str]:
        if self.skills is not None:
            return self.skills.rank(diagnosis, self.area, self.playbook)
        return self.playbook.rank(diagnosis)

    def run(self, target: str) -> List[Record]:
        used = set()
        prev: Optional[Record] = None
        start = len(self.log)
        for n in range(1, self.max_attempts + 1):
            outcome, part, evidence = self.attempt(target, self.book)
            if outcome not in OUTCOMES:
                raise ValueError(f"unknown outcome {outcome!r}")
            if prev is not None:
                prev.retry = outcome
                self.playbook.learn([prev])
            rec = Record(target, n, self.book.version, outcome, part, evidence)
            if outcome == "closed":
                self._write(rec)
                break
            rec.diagnosis = self.diagnose(outcome, part, evidence)
            change = self.propose(rec.diagnosis, self.rank(rec.diagnosis), self.book, self.log)
            if change is not None and (change.key() in used or
                                       (self.skills is not None and self.skills.refused(change))):
                change = None
            if change is None:
                rec.note = "no change left for this diagnosis"
                self._write(rec)
                break
            used.add(change.key())
            self.book = self.book.apply(change)
            rec.change = change
            self._write(rec)
            prev = rec
        if self.skills is not None:
            self.skills.add(self.area, self.log[start:])
        if self.memory is not None:
            self.memory.commit()
        return self.log


def load_log(path: Optional[str] = None) -> Dict[str, List[Record]]:
    """The bundled log, one list of records per run."""
    with open(path or os.path.join(DATA, "modlog.json")) as f:
        raw = json.load(f)
    return {run["run"]: [Record.from_dict(r) for r in run["records"]] for run in raw["runs"]}


def check_log(runs: Dict[str, List[Record]]) -> List[str]:
    """Consistency of a log: known kinds, a change on every failed record that names what it improves,
    attempts numbered 1, 2, ... per target, and the retry of a record equal to the next outcome."""
    errors = []
    for run, recs in runs.items():
        by_target: Dict[str, List[Record]] = {}
        for r in recs:
            by_target.setdefault(r.target, []).append(r)
            if r.outcome not in OUTCOMES:
                errors.append(f"{run}: outcome {r.outcome!r}")
            if r.outcome != "closed" and r.diagnosis not in KINDS:
                errors.append(f"{run}/{r.target}#{r.attempt}: diagnosis {r.diagnosis!r}")
            if r.change is not None:
                if r.change.kind not in RULE_KINDS:
                    errors.append(f"{run}/{r.target}#{r.attempt}: rule kind {r.change.kind!r}")
                if not r.change.improves:
                    errors.append(f"{run}/{r.target}#{r.attempt}: change names no measurement")
        for t, rs in by_target.items():
            if [r.attempt for r in rs] != list(range(1, len(rs) + 1)):
                errors.append(f"{run}/{t}: attempts {[r.attempt for r in rs]}")
            for a, b in zip(rs, rs[1:]):
                if a.change is not None and a.retry != b.outcome:
                    errors.append(f"{run}/{t}#{a.attempt}: retry {a.retry!r} but next outcome {b.outcome!r}")
    return errors


def patterns(records: Iterable[Record]) -> dict:
    """Failure kind x rule kind: how many changes, and how many retries closed or advanced."""
    count: Dict[Tuple[str, str], int] = {}
    won: Dict[Tuple[str, str], int] = {}
    outcomes: Dict[str, int] = {o: 0 for o in OUTCOMES}
    for r in records:
        outcomes[r.outcome] += 1
        if r.change is None:
            continue
        k = (r.diagnosis, r.change.kind)
        count[k] = count.get(k, 0) + 1
        if r.retry in ("closed", "partial"):
            won[k] = won.get(k, 0) + 1
    rows = sorted({d for d, _ in count})
    cols = sorted({c for _, c in count})
    return dict(rows=rows, cols=cols,
                count=[[count.get((d, c), 0) for c in cols] for d in rows],
                won=[[won.get((d, c), 0) for c in cols] for d in rows],
                outcomes=outcomes, changes=sum(count.values()), advanced=sum(won.values()))


def summary(runs: Dict[str, List[Record]]) -> List[str]:
    lines = []
    for run, recs in runs.items():
        p = patterns(recs)
        lines.append(f"{run}: {len(recs)} attempts, {p['changes']} rule changes, "
                     f"{p['advanced']} retries closed or advanced; outcomes {p['outcomes']}")
        for r in recs:
            if r.change is not None:
                lines.append(f"  {r.target} #{r.attempt}: {r.diagnosis} -> {r.change.kind} "
                             f"({r.change.rule}: {r.change.new}) -> {r.retry or 'not yet built'}")
            else:
                lines.append(f"  {r.target} #{r.attempt}: {r.outcome}" + (f" ({r.note})" if r.note else ""))
    return lines
