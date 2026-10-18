"""Exact multivariate polynomials over the integers, with a small expression parser.

Used by the exact check (expand both sides and compare) and by the randomized identity test
(evaluate at random points modulo a prime), the two ends of a weak-before-strong cascade.
Expressions use integers, variables, + - * ^ (or **) and parentheses, e.g. "(a^2+b^2)*(c^2+d^2)".
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, Tuple

Monomial = Tuple[Tuple[str, int], ...]
Poly = Dict[Monomial, int]

_TOKEN = re.compile(r"\s*(?:(\d+)|([A-Za-z_][A-Za-z_0-9]*)|(\*\*|[-+*^()]))")


def _mono_mul(m1: Monomial, m2: Monomial) -> Monomial:
    d = dict(m1)
    for v, e in m2:
        d[v] = d.get(v, 0) + e
    return tuple(sorted((v, e) for v, e in d.items() if e))


def add(p: Poly, q: Poly, sign: int = 1) -> Poly:
    out = dict(p)
    for m, c in q.items():
        out[m] = out.get(m, 0) + sign * c
        if out[m] == 0:
            del out[m]
    return out


def mul(p: Poly, q: Poly) -> Poly:
    out: Poly = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = _mono_mul(m1, m2)
            out[m] = out.get(m, 0) + c1 * c2
            if out[m] == 0:
                del out[m]
    return out


def power(p: Poly, n: int) -> Poly:
    out: Poly = {(): 1}
    for _ in range(n):
        out = mul(out, p)
    return out


def const(c: int) -> Poly:
    return {(): c} if c else {}


def var(name: str) -> Poly:
    return {((name, 1),): 1}


def degree(p: Poly) -> int:
    return max((sum(e for _, e in m) for m in p), default=0)


def variables(p: Poly) -> Tuple[str, ...]:
    return tuple(sorted({v for m in p for v, _ in m}))


class _Parser:
    def __init__(self, text: str):
        self.toks = []
        pos = 0
        text = text.strip()
        while pos < len(text):
            m = _TOKEN.match(text, pos)
            if not m or m.end() == pos:
                raise ValueError(f"cannot parse {text[pos:]!r}")
            self.toks.append(m.group(1) or m.group(2) or ("^" if m.group(3) == "**" else m.group(3)))
            pos = m.end()
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self):
        t = self.peek()
        self.i += 1
        return t

    def expr(self) -> Poly:
        p = self.term()
        while self.peek() in ("+", "-"):
            sign = 1 if self.take() == "+" else -1
            p = add(p, self.term(), sign)
        return p

    def term(self) -> Poly:
        p = self.factor()
        while self.peek() == "*" or (self.peek() is not None and self.peek() not in ("+", "-", ")", "^")):
            if self.peek() == "*":
                self.take()
            p = mul(p, self.factor())
        return p

    def factor(self) -> Poly:
        if self.peek() == "-":
            self.take()
            return mul(const(-1), self.factor())
        p = self.atom()
        if self.peek() == "^":
            self.take()
            e = self.take()
            if e is None or not e.isdigit():
                raise ValueError("exponents must be nonnegative integers")
            p = power(p, int(e))
        return p

    def atom(self) -> Poly:
        t = self.take()
        if t is None:
            raise ValueError("unexpected end of expression")
        if t == "(":
            p = self.expr()
            if self.take() != ")":
                raise ValueError("missing )")
            return p
        if t.isdigit():
            return const(int(t))
        if re.match(r"[A-Za-z_]", t):
            return var(t)
        raise ValueError(f"unexpected token {t!r}")


def parse(text: str) -> Poly:
    p = _Parser(text)
    out = p.expr()
    if p.peek() is not None:
        raise ValueError(f"trailing input at {p.peek()!r}")
    return out


def evaluate(p: Poly, point: Dict[str, int], modulus: int) -> int:
    total = 0
    for m, c in p.items():
        t = c % modulus
        for v, e in m:
            t = t * pow(point[v] % modulus, e, modulus) % modulus
        total = (total + t) % modulus
    return total


def to_str(p: Poly) -> str:
    if not p:
        return "0"
    parts = []
    for m, c in sorted(p.items(), key=lambda kv: (-sum(e for _, e in kv[0]), kv[0])):
        mono = "*".join(v if e == 1 else f"{v}^{e}" for v, e in m)
        if not mono:
            parts.append(str(c))
        elif c == 1:
            parts.append(mono)
        elif c == -1:
            parts.append("-" + mono)
        else:
            parts.append(f"{c}*{mono}")
    return " + ".join(parts).replace("+ -", "- ")


def substitute(p: Poly, mapping: Dict[str, Poly]) -> Poly:
    out: Poly = {}
    for m, c in p.items():
        t = const(c)
        for v, e in m:
            t = mul(t, power(mapping.get(v, var(v)), e))
        out = add(out, t)
    return out


def all_variables(polys: Iterable[Poly]) -> Tuple[str, ...]:
    return tuple(sorted({v for p in polys for v in variables(p)}))


def term_count(text: str) -> int:
    """Number of written terms of an expression: a crude, monotone measure of its size."""
    return max(1, len(re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+", text)))
