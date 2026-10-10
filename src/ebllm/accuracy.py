"""The Accuracy26 score of Section 21.  It measures the quality of an attempt, not truth:
Corollary 21.4 notes that Accuracy26 -> 1 is compatible with Rel = 0."""
from __future__ import annotations

from fractions import Fraction


def accuracy26(R_T, Mstar_T, MapDef_T, Collapse_T, NMDef_T, R_0, Mstar_0, MapDef_0, NMDef_0):
    """1 - (R_T + M*_T + MapDef_T + Collapse + NMDef_T) / (1 + R_0 + M*_0 + MapDef_0 + NMDef_0).
    Exact (a Fraction) when every input is an int or a Fraction."""
    vals = (R_T, Mstar_T, MapDef_T, Collapse_T, NMDef_T, R_0, Mstar_0, MapDef_0, NMDef_0)
    if all(isinstance(x, (int, Fraction)) for x in vals):
        vals = tuple(Fraction(x) for x in vals)
    num = sum(vals[:5])
    den = 1 + sum(vals[5:])
    return 1 - num / den


def monotone_step(prev: dict, new: dict) -> bool:
    """The score does not decrease from step t to t+1 iff
    R' + M*' + MapDef' + Collapse' + NMDef' <= R + M* + MapDef + Collapse + NMDef,
    where Collapse is Collapse(P_{t-1}, P_t) and Collapse' is Collapse(P_t, P_{t+1})."""
    lhs = new["R"] + new["Mstar"] + new["MapDef"] + new["Collapse"] + new["NMDef"]
    rhs = prev["R"] + prev["Mstar"] + prev["MapDef"] + prev.get("Collapse", 0) + prev["NMDef"]
    return lhs <= rhs


def monotone_step_paper(prev: dict, new: dict) -> bool:
    """Proposition 21.1 as printed: the right side leaves out Collapse at step t.  This is
    sufficient for a non-decreasing score but not necessary when Collapse(P_{t-1}, P_t) > 0."""
    lhs = new["R"] + new["Mstar"] + new["MapDef"] + new["Collapse"] + new["NMDef"]
    rhs = prev["R"] + prev["Mstar"] + prev["MapDef"] + prev["NMDef"]
    return lhs <= rhs
