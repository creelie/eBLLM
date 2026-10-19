"""eBLLM: a verifier-gated engine for conjecture work (the VSI circuit of D. Bhattacharjee).

The engine does not prove anything by itself. It keeps the bookkeeping of an attempt honest:
a conjecture becomes a typed package, the attempt becomes an obligation graph, every failed
step becomes a recorded residue, and the release label comes only from verifier factors
(a Lean kernel check, a program with a checked output, a human referee).

Modules:
    package      the conjecture package C = (D, L, A, P, Q, E0, B0, R0)
    release      verifier factors, the multiplicative release product and the emitted label
    obligations  the obligation hypergraph, debt mass, release soundness, the six-gate vector
    playbook     Module 26: bullets, core failures, the collapse guard (paper and v1.1)
    sandtile     Section 10: toppling of proof burden, with the counterexamples to Thm 10.4
    scope        bridges as partial maps and their scope loss (Lemma 6.2 and its correction)
    failures     the 26 x 6 failure decomposition tensor and second-attempt routing
    accuracy     the Accuracy26 score of Section 21
    kappa        typed operator words and the Kappa generator of Section 4
    ledger       run ledgers and the Section 32 contract report
    controls     the calibration controls and the closures recorded with the package
    verifiers    Lean (source scan, #print axioms) and command verifiers
    engine       the Section 22 core loop with pluggable generators
"""

__version__ = "3.0.0"

from .release import Label, VERIFIERS, release_product, emit
from .package import ConjecturePackage

__all__ = ["Label", "VERIFIERS", "release_product", "emit", "ConjecturePackage", "__version__"]
