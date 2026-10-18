"""Checks: a cost per run, a soundness (the chance that one run passes an incorrect candidate),
and perfect completeness (a correct candidate always passes).

Exact checks have soundness 0: the Lean kernel, exact expansion of a polynomial identity, an
exhaustive finite computation.  Weak checks have soundness eps > 0: a randomized identity test,
a language model asked to find a flaw, a numerical test at random points.  A Cascade runs r weak
runs and then the exact check, so it keeps exactly the correct candidates whatever r is; the weak
runs only decide how often the exact check is paid.
"""
from __future__ import annotations

import os
import random
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from . import polys
from .schedules import optimal_cascade

STANDARD_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


@dataclass
class Candidate:
    """A proposed step: a statement of some kind, who proposed it and from what."""
    id: str
    kind: str                      # "identity", "lean", "command", "claim", ...
    statement: Dict[str, Any]
    agent: str = ""
    move: str = ""
    parents: List[str] = field(default_factory=list)
    rationale: str = ""


@dataclass
class Verdict:
    passed: bool
    detail: str = ""
    cost: float = 0.0


class Check:
    name = "check"
    cost = 1.0
    soundness = 0.0          # 0 for an exact check

    def cost_of(self, cand: "Candidate") -> float:
        return self.cost

    def applies(self, cand: Candidate) -> bool:
        return True

    def run(self, cand: Candidate, rng: random.Random) -> Verdict:
        raise NotImplementedError

    @property
    def exact(self) -> bool:
        return self.soundness == 0.0


def _sizes(cand: Candidate):
    return (polys.term_count(cand.statement["lhs"]), polys.term_count(cand.statement["rhs"]))


class ExactIdentityCheck(Check):
    """Expand both sides over the integers and compare: soundness 0.  Without a fixed cost, a run
    costs 1 + nl * nr / 20 for sides with nl and nr written terms."""
    name = "exact expansion"

    def __init__(self, cost: Optional[float] = None):
        self.fixed = cost
        self.cost = cost if cost is not None else 25.0

    def applies(self, cand):
        return cand.kind in ("identity", "univariate")

    def cost_of(self, cand) -> float:
        if self.fixed is not None:
            return self.fixed
        nl, nr = _sizes(cand)
        return 1 + nl * nr / 20

    def run(self, cand, rng):
        c = self.cost_of(cand)
        d = polys.add(polys.parse(cand.statement["lhs"]), polys.parse(cand.statement["rhs"]), -1)
        if not d:
            return Verdict(True, "both sides expand to the same polynomial", c)
        return Verdict(False, "lhs - rhs = " + polys.to_str(d), c)


class InterpolationCheck(Check):
    """Exact for one variable: two polynomials of degree at most d that agree at d + 1 points are
    equal.  The statement carries "var" and "degree"; the check evaluates exactly at 0, ..., d."""
    name = "evaluation at d + 1 points"

    def applies(self, cand):
        return cand.kind == "univariate"

    def cost_of(self, cand) -> float:
        return 0.05 * (cand.statement["degree"] + 1) * sum(_sizes(cand)) / 4

    def run(self, cand, rng):
        st = cand.statement
        l, r, d, x = polys.parse(st["lhs"]), polys.parse(st["rhs"]), st["degree"], st["var"]
        c = self.cost_of(cand)
        if (set(polys.variables(l)) | set(polys.variables(r))) - {x}:
            return Verdict(False, "not univariate", c)
        if polys.degree(l) > d or polys.degree(r) > d:
            return Verdict(False, "degree above the certificate", c)
        big = 2 ** 127 - 1
        for t in range(d + 1):
            if polys.evaluate(l, {x: t}, big) != polys.evaluate(r, {x: t}, big):
                return Verdict(False, f"differs at {x} = {t}", c)
        return Verdict(True, f"agrees at {d + 1} points, degree <= {d}", c)


class RandomIdentityCheck(Check):
    """Schwartz-Zippel: evaluate lhs - rhs at a uniform point modulo a prime p.  An identity that
    fails is caught except with probability at most deg / p."""
    name = "random evaluation"

    def __init__(self, prime: int = 2 ** 31 - 1, cost: Optional[float] = None, max_degree: int = 64):
        self.prime, self.fixed = prime, cost
        self.cost = cost if cost is not None else 1.0
        self.max_degree = max_degree
        self.soundness = max_degree / prime

    def applies(self, cand):
        return cand.kind in ("identity", "univariate")

    def cost_of(self, cand) -> float:
        """Without a fixed cost, a run costs (nl + nr) / 10 for sides with nl and nr written terms."""
        if self.fixed is not None:
            return self.fixed
        return sum(_sizes(cand)) / 10

    def run(self, cand, rng):
        l, r = polys.parse(cand.statement["lhs"]), polys.parse(cand.statement["rhs"])
        vs = polys.all_variables([l, r])
        pt = {v: rng.randrange(self.prime) for v in vs}
        if max(polys.degree(l), polys.degree(r)) > self.max_degree:
            return Verdict(False, "degree above the bound of the test", self.cost_of(cand))
        ok = polys.evaluate(l, pt, self.prime) == polys.evaluate(r, pt, self.prime)
        return Verdict(ok, f"agrees at a random point mod {self.prime}" if ok else f"differs mod {self.prime} at {pt}",
                       self.cost_of(cand))


class SmallPrimeCheck(RandomIdentityCheck):
    """A deliberately weak test: evaluation modulo a small prime (soundness about deg / p)."""
    name = "evaluation mod a small prime"

    def __init__(self, prime: int = 101, cost: Optional[float] = None, max_degree: int = 10):
        super().__init__(prime, cost, max_degree)


class CallableCheck(Check):
    def __init__(self, name: str, fn: Callable[[Candidate, random.Random], bool], cost: float = 1.0,
                 soundness: float = 0.0, kinds: Optional[Sequence[str]] = None):
        self.name, self.fn, self.cost, self.soundness, self.kinds = name, fn, cost, soundness, kinds

    def applies(self, cand):
        return self.kinds is None or cand.kind in self.kinds

    def run(self, cand, rng):
        return Verdict(bool(self.fn(cand, rng)), self.name, self.cost)


class CommandCheck(Check):
    """Run a program; pass on exit status 0 and an output line matching `expect`."""
    name = "command"

    def __init__(self, cost: float = 10.0, timeout: int = 3600):
        self.cost, self.timeout = cost, timeout

    def applies(self, cand):
        return cand.kind == "command"

    def run(self, cand, rng):
        st = cand.statement
        try:
            p = subprocess.run(st["argv"], cwd=st.get("cwd"), capture_output=True, text=True,
                               timeout=self.timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return Verdict(False, str(exc), self.cost)
        out = p.stdout + p.stderr
        ok = p.returncode == 0 and (st.get("expect") is None or re.search(st["expect"], out, re.M))
        return Verdict(bool(ok), out[-400:], self.cost)


class LeanCheck(Check):
    """The Lean kernel.  The candidate statement is {"theorem": "name", "source": "..."}; the
    source is compiled with `lean` (or `lake env lean` inside `project`), and the check passes only
    if it compiles, contains no sorry, and the theorem depends on the standard axioms alone."""
    name = "Lean kernel"
    soundness = 0.0

    def __init__(self, project: Optional[str] = None, cost: float = 100.0, timeout: int = 1800,
                 lean: str = "lean"):
        self.project, self.cost, self.timeout, self.lean = project, cost, timeout, lean

    def applies(self, cand):
        return cand.kind == "lean"

    def run(self, cand, rng):
        src = cand.statement["source"]
        thm = cand.statement["theorem"]
        if re.search(r"\bsorry\b|\badmit\b|^\s*axiom\s|native_decide", src, re.M):
            return Verdict(False, "the source uses sorry, admit, axiom or native_decide", self.cost)
        text = src + f"\n#print axioms {thm}\n"
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "Candidate.lean")
            open(path, "w", encoding="utf-8").write(text)
            argv = ["lake", "env", self.lean, path] if self.project else [self.lean, path]
            try:
                p = subprocess.run(argv, cwd=self.project, capture_output=True, text=True,
                                   timeout=self.timeout)
            except (OSError, subprocess.TimeoutExpired) as exc:
                return Verdict(False, f"Lean not run: {exc}", self.cost)
        out = (p.stdout + p.stderr).replace(path, "Candidate.lean")
        if p.returncode != 0 or "error" in out:
            return Verdict(False, out[-600:], self.cost)
        m = re.search(r"depends on axioms: \[([^\]]*)\]", out)
        axioms = {a.strip() for a in m.group(1).split(",")} if m else set()
        if "does not depend on any axioms" not in out and not m:
            return Verdict(False, "no axiom report", self.cost)
        extra = axioms - STANDARD_AXIOMS
        if extra:
            return Verdict(False, f"nonstandard axioms {sorted(extra)}", self.cost)
        return Verdict(True, "kernel accepted; axioms " + (", ".join(sorted(axioms)) or "none"), self.cost)


@dataclass
class CascadeResult:
    kept: bool
    cost: float
    weak_runs_used: int
    detail: str
    reached_strong: bool


@dataclass
class Cascade:
    """r weak runs, then the exact check.  `tune(rho)` sets r by the optimal-cascade rule."""
    weak: Optional[Check]
    strong: Check
    r: int = 0

    def tune(self, rho: float) -> int:
        if self.weak is None or self.weak.soundness <= 0:
            self.r = 0
        else:
            self.r = optimal_cascade(self.weak.cost, self.strong.cost, rho, self.weak.soundness).weak_runs
        return self.r

    def run(self, cand: Candidate, rng: random.Random) -> CascadeResult:
        spent = 0.0
        if self.weak is not None and self.weak.applies(cand):
            for j in range(self.r):
                v = self.weak.run(cand, rng)
                spent += v.cost
                if not v.passed:
                    return CascadeResult(False, spent, j + 1, f"{self.weak.name}: {v.detail}", False)
        v = self.strong.run(cand, rng)
        spent += v.cost
        return CascadeResult(v.passed, spent, self.r, f"{self.strong.name}: {v.detail}", True)
