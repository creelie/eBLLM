"""Definition repair for the strings target: (C7)-(C9) of the Geometric Selection Conjecture as explicit
inequalities, with a checker.

creelie/strings states (C7) stabilised moduli, (C8) an acceptable rank and hierarchy of Yukawa masses and
(C9) consistent supersymmetry breaking, with thresholds "fixed by comparison with measurement". Until they
are inequalities, GSC is not a mathematical statement (atlas wall strings.c7-c9-undefined). This
module proposes them. EVERY NUMBER BELOW IS A PROPOSAL FOR DEEP TO ACCEPT OR EDIT; the defaults are
conventional physics choices, cited in each field, not results.

The checker is numeric: it takes a vacuum's computed data (mass matrix of the moduli, Yukawa matrices at
the stated scale, gravitino mass) and returns the violated conditions. A vacuum that passes is labelled
numeric-pass, never proved, unless its inputs carry certified error bounds.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple
import math

import numpy as np


@dataclass(frozen=True)
class Windows:
    # (C7) every modulus massive: all eigenvalues of the canonically normalised moduli mass matrix
    # at least m0^2. Default m0 = 30 TeV, above the cosmological moduli problem bound (moduli decaying
    # before nucleosynthesis need m >~ 10-50 TeV).
    m0_GeV: float = 3.0e4
    allow_flat_directions: int = 0            # number of exactly massless moduli tolerated (axions eaten etc.)
    # (C8) Yukawa matrices at the scale mu_GeV have rank 3 and singular-value ratios inside the windows,
    # each window = central value times or divided by `tolerance`. Central values: GUT-scale running
    # masses in the MSSM with tan(beta) = 10 (Xing, Zhang, Zhou, arXiv:0712.1419); check them before use.
    mu_GeV: float = 2.0e16
    central: Tuple[Tuple[str, float], ...] = (
        ("u/t", 6.5e-6), ("c/t", 3.2e-3),
        ("d/b", 8.7e-4), ("s/b", 1.6e-2),
        ("e/tau", 2.8e-4), ("mu/tau", 5.9e-2),
    )
    tolerance: float = 3.0
    vus_window: Tuple[float, float] = (0.15, 0.30)      # Cabibbo angle |V_us| (measured 0.225)
    # (C9) supersymmetry broken (some F-term nonzero) with gravitino mass in a window and a vacuum
    # energy no larger than |V0| <= v0_max in Planck units (0 disables the vacuum-energy test).
    m32_GeV: Tuple[float, float] = (1.0e3, 1.0e6)
    v0_max: float = 0.0


DEFAULT = Windows()


def _ratios(Y: np.ndarray) -> Tuple[int, List[float]]:
    sv = np.linalg.svd(np.asarray(Y, dtype=complex), compute_uv=False)   # descending
    rank = int(np.sum(sv > 1e-14 * max(sv[0], 1e-300)))
    return rank, [sv[2] / sv[0], sv[1] / sv[0]]


def check(vacuum: Dict, w: Windows = DEFAULT) -> List[str]:
    """Violated conditions of a vacuum. Keys: moduli_mass2_GeV2 (list of eigenvalues), Yu, Yd, Ye (3x3),
    vus, m32_GeV, F_nonzero (bool), V0 (Planck units, optional)."""
    bad = []
    m2 = sorted(vacuum["moduli_mass2_GeV2"])
    light = [x for x in m2 if x < w.m0_GeV ** 2]
    if len(light) > w.allow_flat_directions:
        bad.append(f"(C7) {len(light)} moduli below m0 = {w.m0_GeV:g} GeV (lightest m^2 = {m2[0]:.3g} GeV^2)")
    cen = dict(w.central)
    for name, key, lo, hi in (("up", "Yu", "u/t", "c/t"), ("down", "Yd", "d/b", "s/b"), ("lepton", "Ye", "e/tau", "mu/tau")):
        rank, (r1, r2) = _ratios(vacuum[key])
        if rank < 3:
            bad.append(f"(C8) {name} Yukawa has rank {rank} < 3")
            continue
        for tag, r in ((lo, r1), (hi, r2)):
            c = cen[tag]
            if not c / w.tolerance <= r <= c * w.tolerance:
                bad.append(f"(C8) {name} ratio {tag} = {r:.3g} outside [{c / w.tolerance:.3g}, {c * w.tolerance:.3g}]")
    if not w.vus_window[0] <= vacuum["vus"] <= w.vus_window[1]:
        bad.append(f"(C8) |V_us| = {vacuum['vus']:.3g} outside {w.vus_window}")
    if not vacuum.get("F_nonzero", False):
        bad.append("(C9) supersymmetry unbroken (all F-terms vanish)")
    if not w.m32_GeV[0] <= vacuum["m32_GeV"] <= w.m32_GeV[1]:
        bad.append(f"(C9) gravitino mass {vacuum['m32_GeV']:.3g} GeV outside {w.m32_GeV}")
    if w.v0_max and abs(vacuum.get("V0", 0.0)) > w.v0_max:
        bad.append(f"(C9) |V0| = {abs(vacuum['V0']):.3g} exceeds {w.v0_max:g}")
    return bad


def as_statement(w: Windows = DEFAULT) -> str:
    """The repaired conditions as text, for the atlas and for Deep to edit."""
    c = dict(w.central)
    return (f"(C7) every modulus has mass >= {w.m0_GeV:g} GeV (at most {w.allow_flat_directions} exactly flat). "
            f"(C8) at mu = {w.mu_GeV:g} GeV the up, down and lepton Yukawa matrices have rank 3 and singular-value "
            f"ratios within a factor {w.tolerance:g} of " + ", ".join(f"{k} = {v:g}" for k, v in c.items()) +
            f"; |V_us| in {w.vus_window}. (C9) some F-term is nonzero and the gravitino mass lies in {w.m32_GeV} GeV.")


def diag_yukawa(r_small: float, r_mid: float, phase: float = 0.0) -> np.ndarray:
    """A test Yukawa matrix with the given singular-value ratios (for tests and examples)."""
    return np.diag([1.0, r_mid, r_small]) * complex(math.cos(phase), math.sin(phase))
