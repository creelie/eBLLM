"""Supersymmetric Yang-Mills theories with several times reduce to ten dimensions.

Uploaded by a second agent on Tubai's command.  Rios, Marrani and Chester (Phys. Rev. D 99 (2019)
046004, Sec. III A) state that Nishino's existence proofs for super Yang-Mills theories in the
signatures (9+m)+(1+m) (Nucl. Phys. B 523 (1998) 450) "can be successfully repeated" in

    (9+8n)+1,   (10+8n)+2,   (11+8n)+3,   (12+8n)+4,

because these share D = s+t and s-t mod 8 with Nishino's signatures.  The paper of creelie/cs-grav
("Supersymmetric Yang-Mills theories with several times reduce to ten dimensions", release v1.0.0,
doi:10.5281/zenodo.23558751) refutes the claim.  This module rebuilds its three constructions and
checks them:

1. The Witt bound (Lemmas 2.2, 2.3).  If k mutually orthogonal null vectors annihilate a real
   (Majorana) gaugino, they lie in the complexification of a real totally isotropic subspace of
   R^{s,t}, so k <= min(s,t).  The residual space of the frame has dimension D' = s+t-2k.

2. The dimension count (Theorem 3.3).  If symmetric gamma matrices on a d-dimensional space satisfy
   (1/2)(g^mu_ab g_mu,cd + g^mu_ac g_mu,bd) = j g^s_ad g_s,bc for some j, then N = 2(d-2) and
   j = -1/2.  A Weyl spinor has N divisible by 2^(ceil(d/2)-1), and the two conditions together
   leave exactly d in {3, 4, 6, 10}.  The cubic gaugino terms of a theory built in Nishino's manner
   (axioms N1-N5) reduce to this identity on the residual spinors, so D' is 10 (or 2, degenerate).

3. The Main Theorem.  With Majorana-Weyl spinors (s-t = 0 mod 8) the two give s-t in {8, 0, -8}:
   no theory in the four families for n >= 1, none in 27+3 or 19+3.  For a single time,
   (9+8n)+1 with n >= 1, a massless multiplet without tensor charges has at least 2^(2^(2+4n))
   states (Theorem 6.1), against 8+8n bosonic states of a vector field.

The refuters are the two shortcuts that the paper rules out: the mod-8 rule of the claim itself
(existence decided by D and s-t mod 8 alone), and complex null frames (which allow k > min(s,t) but
give no real form of the theory).  Both predict theories that the checks reject.

The numerical part (numpy) builds explicit gamma matrices and tests the cubic identity, which holds
in (9,1), (5,5), (1,9) and fails in (17,1), (13,5), (9,9).  Every statement is proved in the paper;
the numbers are an independent check, not a proof.  Label: proved, under the axioms N1-N5; the
single-time bound assumes that tensor charges vanish on the multiplet (hypothesis H).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

FAMILIES = ("(9+8n)+1", "(10+8n)+2", "(11+8n)+3", "(12+8n)+4")


def family(name: str, n: int) -> Tuple[int, int]:
    """The signature (s, t) of a family of the claim for a given n."""
    base = {"(9+8n)+1": (9, 1), "(10+8n)+2": (10, 2), "(11+8n)+3": (11, 3), "(12+8n)+4": (12, 4)}[name]
    return base[0] + 8 * n, base[1]


def nishino(m: int) -> Tuple[int, int]:
    """Nishino's signature (9+m)+(1+m), with its frame of k = m null vectors."""
    return 9 + m, 1 + m


def majorana_weyl(s: int, t: int) -> bool:
    """Majorana-Weyl spinors exist in R^{s,t} exactly when s - t = 0 mod 8."""
    return (s - t) % 8 == 0


def witt_bound(s: int, t: int) -> int:
    """The largest number of mutually orthogonal null vectors in a real totally isotropic subspace."""
    return min(s, t)


def residual_dimensions(s: int, t: int) -> List[int]:
    """D' = s + t - 2k for every admissible real frame, k = 0, ..., min(s, t)."""
    return [s + t - 2 * k for k in range(witt_bound(s, t) + 1)]


def admissible_frames(s: int, t: int) -> List[int]:
    """The ranks k <= min(s, t) whose residual dimension is 10 or 2 (Theorem 5.6)."""
    if not majorana_weyl(s, t):
        return []
    return [k for k in range(witt_bound(s, t) + 1) if s + t - 2 * k in (2, 10)]


def theory_allowed(s: int, t: int) -> bool:
    """The Main Theorem: a theory built in Nishino's manner can exist only if this is True."""
    return bool(admissible_frames(s, t))


def weyl_dimension(d: int) -> int:
    """The least dimension of a Weyl (or, for odd d, Dirac) spinor on a d-dimensional space."""
    return 2 ** (math.ceil(d / 2) - 1)


def vector_structure_dimensions(dmax: int = 200) -> List[int]:
    """The d <= dmax for which N = 2(d - 2) is a multiple of the Weyl dimension (Theorem 3.3)."""
    return [d for d in range(3, dmax + 1) if (2 * (d - 2)) % weyl_dimension(d) == 0]


def sym2_forms(r: int) -> List[int]:
    """Form degrees in Sym^2 of a Weyl spinor of so(2r): r, r-4, r-8, ... (Proposition 2.1)."""
    return list(range(r, -1, -4))


def sym2_count_ok(r: int) -> bool:
    """dim Sym^2 Delta_+ = sum of the dimensions of the forms, half of the middle one."""
    n = 2 ** (r - 1)
    rhs = sum(math.comb(2 * r, p) // (2 if p == r else 1) for p in sym2_forms(r))
    anti = sum(math.comb(2 * r, p) for p in range(r - 2, -1, -4))
    return n * (n + 1) // 2 == rhs and n * (n - 1) // 2 == anti


def single_time_bound(n: int) -> Dict[str, int]:
    """Theorem 6.1 in (9+8n)+1: log2 of the least number of states of a massless multiplet without
    tensor charges, against the bosonic and fermionic states of a vector multiplet."""
    supercharges = 2 ** (4 + 4 * n)
    return {"supercharges": supercharges, "log2_states": supercharges // 4,
            "vector_bosons": 8 + 8 * n, "gaugino_states": 2 ** (3 + 4 * n)}


def certificate(nmax: int = 6) -> Dict[str, object]:
    """Everything the paper asserts that can be recomputed exactly."""
    return {
        "nishino_allowed": [nishino(m) for m in range(0, 12) if theory_allowed(*nishino(m))],
        "families": {f: [(n, family(f, n), admissible_frames(*family(f, n))) for n in range(0, nmax + 1)]
                     for f in FAMILIES},
        "division_dimensions": vector_structure_dimensions(),
        "excluded_named": {"27+3": theory_allowed(27, 3), "19+3": theory_allowed(19, 3)},
        "single_time": [single_time_bound(n) for n in range(0, 4)],
        "sym2": all(sym2_count_ok(r) for r in range(2, 21)),
    }


def check(cert: Optional[Dict[str, object]] = None) -> List[str]:
    """Independent check of a certificate; returns the list of failures (empty when it holds)."""
    cert = cert or certificate()
    bad = []
    # Nishino's own signatures are allowed, with k = m giving D' = 10
    for m in range(0, 12):
        s, t = nishino(m)
        if (s, t) not in cert["nishino_allowed"] or s + t - 2 * m != 10 or m > min(s, t):
            bad.append(f"Nishino signature ({s},{t}) not allowed")
    # every family signature with n >= 1 has D' >= 16 for every real frame
    for f, rows in cert["families"].items():
        for n, (s, t), frames in rows:
            least = s + t - 2 * min(s, t)
            if n >= 1 and (frames or least < 16 or (s - t) not in (8 + 8 * n,)):
                bad.append(f"{f} at n={n} is not excluded")
            if n == 0 and 10 not in [s + t - 2 * k for k in frames]:
                bad.append(f"{f} at n=0 should be Nishino's")
    if cert["division_dimensions"] != [3, 4, 6, 10]:
        bad.append(f"vector structures in d = {cert['division_dimensions']}")
    if any(cert["excluded_named"].values()):
        bad.append("27+3 or 19+3 allowed")
    for n, row in enumerate(cert["single_time"]):
        fits = row["log2_states"] <= math.log2(2 * row["vector_bosons"])
        if fits != (n == 0):
            bad.append(f"single-time bound wrong at n={n}")
    if not cert["sym2"]:
        bad.append("Sym^2 decomposition")
    return bad


# ----------------------------------------------------------------------------------- refuters
def mod8_rule(s: int, t: int) -> bool:
    """The shortcut of the claim: a theory exists whenever the reality and symmetry data agree with
    a signature of Nishino's list, that is s - t = 0 mod 8 and D = s + t >= 10 even."""
    return (s - t) % 8 == 0 and (s + t) % 2 == 0 and s + t >= 10


def complex_frames(s: int, t: int) -> List[int]:
    """Frames of complex null vectors, which need not lie in a real isotropic subspace: k <= D/2."""
    return [k for k in range((s + t) // 2 + 1) if s + t - 2 * k in (2, 10)]


def refuter() -> Dict[str, List[Tuple[int, int]]]:
    """Run the two shortcuts on the families; each signature they accept is a claimed theory that
    the checks reject.  Returns the signatures each shortcut wrongly admits (n = 1, 2)."""
    out = {"mod8_rule": [], "complex_frames": []}
    for f in FAMILIES:
        for n in (1, 2):
            s, t = family(f, n)
            if mod8_rule(s, t) and not theory_allowed(s, t):
                out["mod8_rule"].append((s, t))
            if complex_frames(s, t) and not theory_allowed(s, t):
                out["complex_frames"].append((s, t))
    return out


# --------------------------------------------------------------------- numbers (numpy, optional)
def _gammas(s: int, t: int):
    """Dense gamma matrices of Cl(s, t), s + t even, timelike first; chirality is diagonal."""
    import numpy as np
    r = (s + t) // 2
    s1 = np.array([[0, 1], [1, 0]], dtype=complex)
    s2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
    s3 = np.array([[1, 0], [0, -1]], dtype=complex)
    i2 = np.eye(2, dtype=complex)

    def kron(ms):
        out = np.array([[1.0 + 0j]])
        for m in ms:
            out = np.kron(out, m)
        return out

    e = []
    for j in range(r):
        e.append(kron([s3] * j + [s1] + [i2] * (r - j - 1)))
        e.append(kron([s3] * j + [s2] + [i2] * (r - j - 1)))
    eta = [-1.0] * t + [1.0] * s
    gam = [(1j * e[a] if a < t else e[a]) for a in range(s + t)]
    chi = kron([np.diag([1.0, -1.0])] * r).diagonal().real
    return np.array(eta), gam, e, chi


def fierz_residual(s: int, t: int, seed: int = 20261022) -> float:
    """|sum_mu eta_mu (x g^mu x) g^mu x| / |x|^3 for a random Weyl spinor x, with g^mu the symmetric
    vector bilinear on one Weyl module: zero exactly when the cubic identity holds."""
    import numpy as np
    eta, gam, e, chi = _gammas(s, t)
    plus = np.where(chi > 0)[0]
    best = None
    for parity in (0, 1):
        C = np.eye(len(chi), dtype=complex)
        for a in range(s + t):
            if a % 2 == parity:
                C = C @ e[a]
        blocks = [(C @ g)[np.ix_(plus, plus)] for g in gam]
        if max(abs(b).max() for b in blocks) < 1e-9:
            continue
        if max(abs(b - b.T).max() for b in blocks) > 1e-9:
            continue
        best = blocks
        break
    if best is None:
        raise ValueError(f"no symmetric same-chirality vector bilinear in ({s},{t})")
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(len(plus)) + 1j * rng.standard_normal(len(plus))
    y = sum(eta[m] * (x @ (best[m] @ x)) * (best[m] @ x) for m in range(s + t))
    return float(np.linalg.norm(y) / np.linalg.norm(x) ** 3)


def summary() -> Dict[str, object]:
    cert = certificate()
    return {"failures": check(cert), "division_dimensions": cert["division_dimensions"],
            "refuter": refuter(), "excluded_named": cert["excluded_named"]}
