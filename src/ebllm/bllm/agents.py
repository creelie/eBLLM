"""Six subagents, one for each move by which hard proofs are found, and the coordinator.

    construction      build the object directly: enumerate or design candidates of a given shape
    strong-then-weak  aim at the strongest statement first, filter the many wrong guesses with
                      cheap checks, and fall back to weaker forms only when the strong one fails
    residual          take a near miss, compute exactly what is left over, and correct it
    trivialization    reduce the statement to a finite computation that an exact check settles
    bypass            find a result already kept in memory that implies the goal
    blow-up           rescale or substitute in a kept result to reach a larger statement

Each agent proposes Candidates.  A built-in deterministic proposer implements every move on
polynomial identities, so a full run needs no network and no key; a ModelAgent asks any
language model of `proposers` to carry out a move on any problem, and its proposals are checked
in exactly the same way.  The coordinator splits the soundness budget among the agents in
proportion to their checking cost (Theorem H), so one number per agent reaches the optimum.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

from . import polys
from .checks import Candidate
from .proposers import Proposer, extract_json_list

MOVES = ("construction", "strong-then-weak", "residual", "trivialization", "bypass", "blow-up")


@dataclass
class Problem:
    """Find rhs of a given shape with target == rhs identically."""
    id: str
    title: str
    target: str
    shape: str = ""                       # "product", "sum of squares", "linear factor", ...
    notes: str = ""
    lean: str = ""                        # a Lean proposition, for problems the kernel decides

    @property
    def kind(self) -> str:
        return "lean" if self.lean else "identity"

    @property
    def poly(self):
        return polys.parse(self.target)


class Agent:
    move = ""
    name = ""
    expected_wrong = 0.9                  # prior fraction of wrong proposals, used to tune cascades
    focus = False                         # an expensive search works on one problem per round
    kinds = ("identity",)                 # the kinds of problem the agent works on

    def propose(self, problem: Problem, memory, rng: random.Random, residues: Sequence[dict]) -> List[Candidate]:
        return []

    def _cand(self, problem, rhs, rationale, parents=(), kind="identity", extra=None):
        st = {"lhs": problem.target, "rhs": rhs, "problem": problem.id}
        st.update(extra or {})
        h = hashlib.sha256(f"{rhs}|{rationale}|{kind}|{extra}".encode()).hexdigest()[:8]
        cid = f"{problem.id}-{self.move}-{h}"
        return Candidate(cid, kind, st, agent=self.name, move=self.move, parents=list(parents),
                         rationale=rationale)


def _fmt(c: int, s: str) -> str:
    if c == 0:
        return ""
    if c == 1:
        return f"+{s}"
    if c == -1:
        return f"-{s}"
    return f"{c:+d}*{s}"


class ConstructionAgent(Agent):
    """Enumerates products of two quadratic forms, and sums of two squares of bilinear forms."""
    move, name, expected_wrong, focus = "construction", "Construction", 0.99, True

    def propose(self, problem, memory, rng, residues):
        out = []
        vs = polys.variables(problem.poly)
        if problem.shape == "product" and len(vs) == 2 and polys.degree(problem.poly) == 4:
            x, y = vs
            rng_c = range(-2, 3)
            for a, b, c, d in itertools.product(rng_c, rng_c, rng_c, rng_c):
                if b == 0 or d == 0:
                    continue
                f = f"({x}^2{_fmt(a, f'{x}*{y}')}{_fmt(b, f'{y}^2')})"
                g = f"({x}^2{_fmt(c, f'{x}*{y}')}{_fmt(d, f'{y}^2')})"
                out.append(self._cand(problem, f + "*" + g, f"product of quadratics a,b,c,d = {a},{b},{c},{d}"))
        if problem.shape == "sum of two squares" and len(vs) == 4:
            a, b, c, d = vs
            for s1, s2 in itertools.product((1, -1), repeat=2):
                for pair in (((a, c), (b, d)), ((a, d), (b, c))):
                    (p, q), (r, t) = pair
                    first = f"({p}*{q}{'+' if s1 > 0 else '-'}{r}*{t})"
                    other = ((a, d), (b, c)) if pair[0] == (a, c) else ((a, c), (b, d))
                    (p2, q2), (r2, t2) = other
                    second = f"({p2}*{q2}{'+' if s2 > 0 else '-'}{r2}*{t2})"
                    out.append(self._cand(problem, f"{first}^2+{second}^2", "two bilinear squares"))
        rng.shuffle(out)
        return out


class StrongThenWeakAgent(Agent):
    """Goes for Euler's four-square identity by sign patterns of the quaternion product."""
    move, name, expected_wrong, focus = "strong-then-weak", "StrongThenWeak", 0.998, True

    def propose(self, problem, memory, rng, residues):
        vs = polys.variables(problem.poly)
        if problem.shape != "sum of four squares" or len(vs) != 8:
            return []
        a, b, c, d, e, f, g, h = vs
        rows = [((a, e), (b, f), (c, g), (d, h)), ((a, f), (b, e), (c, h), (d, g)),
                ((a, g), (b, h), (c, e), (d, f)), ((a, h), (b, g), (c, f), (d, e))]
        out = []
        for signs in itertools.product((1, -1), repeat=12):
            sq = []
            for k, row in enumerate(rows):
                sg = (1,) + signs[3 * k:3 * k + 3]
                terms = "".join(("+" if s > 0 else "-") + f"{u}*{v}" for s, (u, v) in zip(sg, row))
                sq.append(f"({terms.lstrip('+')})^2")
            out.append(self._cand(problem, "+".join(sq), "quaternion sign pattern"))
        rng.shuffle(out)
        return out


def divide_linear(p, x: str, y: str):
    """Divide p by (x - y) as a polynomial in x; returns (quotient, remainder) with exact
    integer coefficients (remainder = p evaluated at x = y)."""
    n = max((dict(m).get(x, 0) for m in p), default=0)
    coeff = [dict() for _ in range(n + 1)]       # coefficient of x^k, a polynomial without x
    for m, c in p.items():
        k = dict(m).get(x, 0)
        rest = tuple((v, e) for v, e in m if v != x)
        coeff[k] = polys.add(coeff[k], {rest: c})
    q = [dict() for _ in range(n)]
    carry: dict = {}
    for k in range(n, 0, -1):
        carry = polys.add(coeff[k], polys.mul(carry, polys.var(y)))
        q[k - 1] = carry
    rem = polys.add(coeff[0], polys.mul(carry, polys.var(y)))
    quot: dict = {}
    for k, ck in enumerate(q):
        quot = polys.add(quot, polys.mul(ck, polys.power(polys.var(x), k)))
    return quot, rem


class ResidualAgent(Agent):
    """Starts from the naive guess (x - y)(x^4 + y^4), computes the exact residual, and divides
    it by the linear factor to correct the guess."""
    move, name, expected_wrong = "residual", "Residual", 0.5

    def propose(self, problem, memory, rng, residues):
        vs = polys.variables(problem.poly)
        if problem.shape != "linear factor" or len(vs) != 2:
            return []
        x, y = vs
        n = polys.degree(problem.poly)
        guess = f"({x}-{y})*({x}^{n - 1}+{y}^{n - 1})"
        out = [self._cand(problem, guess, "naive guess")]
        for r in residues:
            if r.get("move") == self.move and r.get("problem") == problem.id:
                cur = polys.parse(r["rhs"])
                res = polys.add(problem.poly, cur, -1)
                quot, rem = divide_linear(res, x, y)
                if not rem:
                    base = polys.parse(r["rhs"].split("*", 1)[1])
                    out = [self._cand(problem, f"({x}-{y})*({polys.to_str(polys.add(base, quot))})",
                                      "residual divided by the linear factor", parents=[r["id"]])]
                break
        return out


class TrivializationAgent(Agent):
    """A univariate identity of degree d is decided by d + 1 evaluations: it proposes the
    binomial expansion with that finite certificate."""
    move, name, expected_wrong = "trivialization", "Trivialization", 0.1

    def propose(self, problem, memory, rng, residues):
        vs = polys.variables(problem.poly)
        if problem.shape != "expansion" or len(vs) != 1:
            return []
        x = vs[0]
        p = problem.poly
        d = polys.degree(p)
        from math import comb
        # read the base (x + c)^d from the target: c = coefficient of x^(d-1) / d
        c = p.get(((x, d - 1),), 0) // d
        rhs = "+".join(f"{comb(d, k) * c ** (d - k)}*{x}^{k}" for k in range(d + 1))
        return [self._cand(problem, rhs, f"binomial theorem, certified at {d + 1} points",
                           kind="univariate", extra={"var": x, "degree": d})]


class BypassAgent(Agent):
    """Looks in memory for a kept identity whose left side becomes the target under a renaming
    of variables, and transports it."""
    move, name, expected_wrong = "bypass", "Bypass", 0.3

    def propose(self, problem, memory, rng, residues):
        out = []
        tv = polys.variables(problem.poly)
        for note in memory.search_identities():
            lv = polys.variables(polys.parse(note["lhs"]))
            if len(lv) != len(tv) or note["problem"] == problem.id:
                continue
            for perm in itertools.permutations(tv):
                mp = {u: polys.var(v) for u, v in zip(lv, perm)}
                if polys.substitute(polys.parse(note["lhs"]), mp) == problem.poly:
                    ren = dict(zip(lv, perm))           # rename in the text, keeping the shape
                    rhs = re.sub(r"[A-Za-z_][A-Za-z_0-9]*", lambda m: ren.get(m.group(0), m.group(0)),
                                 note["rhs"])
                    out.append(self._cand(problem, rhs, f"transport of {note['id']} by renaming",
                                          parents=[note["id"]]))
                    break
        return out


class BlowUpAgent(Agent):
    """Substitutes x -> x^k in every variable of a kept identity to reach a target of higher
    degree, keeping the shape."""
    move, name, expected_wrong = "blow-up", "BlowUp", 0.3

    def propose(self, problem, memory, rng, residues):
        out = []
        tv = polys.variables(problem.poly)
        for note in memory.search_identities():
            lp = polys.parse(note["lhs"])
            lv = polys.variables(lp)
            if lv != tv or note["problem"] == problem.id:
                continue
            for k in (2, 3, 4):
                mp = {v: polys.power(polys.var(v), k) for v in lv}
                if polys.substitute(lp, mp) == problem.poly:
                    rhs = note["rhs"]
                    for v in lv:
                        rhs = rhs.replace(v, f"({v}^{k})")
                    out.append(self._cand(problem, rhs, f"substitution of degree {k} in {note['id']}",
                                          parents=[note["id"]]))
        return out


PROMPT = """You are the {move} subagent of a verifier-gated research system.
Problem {pid}: {title}
Statement: {statement}
Move: {move_doc}
Earlier failures recorded for this problem (do not repeat them):
{residues}
Propose up to {k} candidate steps. Answer with a JSON list; each item has "kind" and the fields of
that kind ("identity": "lhs", "rhs"; "lean": "theorem", "source"; "claim": "text"), and "rationale".
Every candidate will be checked; anything unchecked is recorded as a proposal, never as a result."""

MOVE_DOCS = {
    "construction": "build the object directly",
    "strong-then-weak": "aim at the strongest form first; give weaker forms only as fallbacks",
    "residual": "take a near miss, compute what is left over exactly, and correct it",
    "trivialization": "reduce the statement to a finite computation an exact check can settle",
    "bypass": "find a known result that implies the goal and transport it",
    "blow-up": "rescale or substitute in a known result to reach the larger statement",
}


TACTICS = ("rfl", "decide", "omega", "simp", "intro n hn; omega", "intro n; omega",
           "intro n hn; simp; omega", "constructor <;> decide", "simp_arith", "native_decide")


@dataclass
class LeanTacticAgent(Agent):
    """Tactic search with no language model: each tactic of a fixed list closes the goal or not,
    and the Lean kernel decides.  native_decide is listed so that the check visibly refuses it."""
    tactics: Sequence[str] = TACTICS
    move = "trivialization"
    name = "LeanTactics"
    kinds = ("lean",)
    expected_wrong = 0.8

    def propose(self, problem, memory, rng, residues):
        tried = {r.get("tactic") for r in residues if r.get("problem") == problem.id}
        thm = "goal_" + "".join(ch if ch.isalnum() else "_" for ch in problem.id)
        out = []
        for t in self.tactics:
            if t in tried:
                continue
            src = f"theorem {thm} : {problem.lean} := by\n  {t}\n"
            out.append(self._cand(problem, "", f"tactic `{t}`", kind="lean",
                                  extra={"source": src, "theorem": thm, "tactic": t,
                                         "lhs": problem.lean}))
        return out


@dataclass
class ModelAgent(Agent):
    """Any language model, asked to carry out one move on one problem."""
    move: str = "construction"
    proposer: Optional[Proposer] = None
    k: int = 8
    expected_wrong: float = 0.9
    kinds = ("identity", "lean")

    def __post_init__(self):
        if self.move not in MOVES:
            raise ValueError(f"unknown move {self.move!r}")
        self.name = f"{self.move}@{getattr(self.proposer, 'name', 'model')}"

    def prompt(self, problem: Problem, residues: Sequence[dict]) -> str:
        res = "\n".join(f"- {r.get('rhs', r.get('text', ''))}: {r.get('detail', '')}" for r in residues[-10:]
                        if r.get("problem") == problem.id) or "- none"
        return PROMPT.format(move=self.move, pid=problem.id, title=problem.title,
                             statement=f"{problem.target}  ({problem.shape or 'any form'})",
                             move_doc=MOVE_DOCS[self.move], residues=res, k=self.k)

    def propose(self, problem, memory, rng, residues):
        items = extract_json_list(self.proposer.complete(self.prompt(problem, residues)))
        out = []
        for it in items[: self.k]:
            kind = it.get("kind", "identity")
            if kind == "identity" and "rhs" in it:
                out.append(self._cand(problem, str(it["rhs"]), str(it.get("rationale", ""))))
            elif kind == "lean" and "source" in it and "theorem" in it:
                c = self._cand(problem, "", str(it.get("rationale", "")), kind="lean",
                               extra={"source": it["source"], "theorem": it["theorem"]})
                out.append(c)
            elif kind == "claim":
                out.append(self._cand(problem, "", str(it.get("rationale", "")), kind="claim",
                                      extra={"text": str(it.get("text", ""))}))
        return out


def default_agents(lean: bool = False) -> List[Agent]:
    """Memory first (bypass, blow-up), then the cheap moves, then the searches; with `lean`, also
    tactic search on the problems that carry a Lean statement."""
    agents: List[Agent] = [BypassAgent(), BlowUpAgent(), TrivializationAgent(), ResidualAgent(),
                           ConstructionAgent(), StrongThenWeakAgent()]
    return agents + [LeanTacticAgent()] if lean else agents


DEMO_PROBLEMS = [
    Problem("germain", "Sophie Germain's identity", "x^4+4*y^4", "product",
            "x^4 + 4y^4 factors over the integers"),
    Problem("brahmagupta", "Brahmagupta-Fibonacci identity", "(a^2+b^2)*(c^2+d^2)", "sum of two squares",
            "a product of sums of two squares is a sum of two squares"),
    Problem("quintic", "x^5 - y^5 has the factor x - y", "x^5-y^5", "linear factor"),
    Problem("binomial", "the tenth binomial expansion", "(x+2)^10", "expansion"),
    Problem("germain8", "x^8 + 4y^8 factors", "x^8+4*y^8", "product"),
    Problem("euler", "Euler's four-square identity",
            "(a^2+b^2+c^2+d^2)*(e^2+f^2+g^2+h^2)", "sum of four squares"),
    Problem("brahmagupta2", "two squares again, in other letters", "(p^2+q^2)*(r^2+s^2)", "sum of two squares"),
    Problem("euler2", "four squares again, in other letters",
            "(p^2+q^2+r^2+s^2)*(t^2+u^2+v^2+w^2)", "sum of four squares"),
]

LEAN_PROBLEMS = [
    Problem("evenproducts", "n(n+1) is even for n < 40", "", "Lean kernel",
            "a bounded statement that a kernel decides", lean="∀ n, n < 40 → n * (n + 1) % 2 = 0"),
    Problem("mersenne", "2^13 - 1 = 8191", "", "Lean kernel", lean="2 ^ 13 - 1 = 8191"),
    Problem("linear", "a linear inequality over the naturals", "", "Lean kernel",
            lean="∀ n : Nat, 3 * n + 7 ≤ 5 * n + 7"),
]
