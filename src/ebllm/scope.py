"""Bridges as partial maps, and their scope loss (Lemma 6.2).

A bridge B : D_a -> D_b transports each point of D_a to a verifier-coherent point of D_b, or
loses it.  Model it as a partial map f : D_a -> D_b + {lost}; its scope loss is the measure of
the lost set (here the counting measure on a finite D_a).

Lemma 6.2 of the paper claims ScopeLoss(g o f) >= ScopeLoss(f) + ScopeLoss(g).  That is false:
if f misses the part of D_b that g loses, the composite loses nothing extra
(`counterexample_superadditivity`).  The exact statement is

    ScopeLoss(g o f) = ScopeLoss(f) + #{x : f(x) = y defined and g(y) lost},

so ScopeLoss(g o f) <= ScopeLoss(f) + ScopeLoss(g) when f is injective where defined, with
equality when in addition f maps onto the part of D_b that g loses.  `lean/EBLLM/Scope.lean`
proves the decomposition and checks the counterexample.
"""
from __future__ import annotations

from typing import List, Optional, Sequence

PartialMap = Sequence[Optional[int]]  # f[x] is the image of x, or None if x is lost


def loss(f: PartialMap) -> int:
    return sum(1 for y in f if y is None)


def compose(g: PartialMap, f: PartialMap) -> List[Optional[int]]:
    return [None if y is None else g[y] for y in f]


def pulled_back_loss(g: PartialMap, f: PartialMap) -> int:
    return sum(1 for y in f if y is not None and g[y] is None)


def counterexample_superadditivity():
    """D_a = {0}, D_b = {0, 1}; f(0) = 0; g loses 1.  loss(f) = 0, loss(g) = 1, loss(g o f) = 0."""
    f = [0]
    g = [0, None]
    return f, g


def is_injective_where_defined(f: PartialMap) -> bool:
    ys = [y for y in f if y is not None]
    return len(ys) == len(set(ys))
