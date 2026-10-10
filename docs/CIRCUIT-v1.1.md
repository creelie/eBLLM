# The VSI circuit, version 1.1

Version 1.1 keeps the architecture of the paper (twenty-six modules, the B2/B3 critic ladder, the
six-gate residue synthesizer, sand-tile burden, Kappa generation, the Module 26 playbook) and
changes only what the review in `docs/REVIEW.md` found to be wrong. Each change is implemented in
the Python package and, where it is a theorem, proved in Lean.

## 1. The collapse guard counts deletions, not resolutions

    Collapse₁.₁(P, P′) = #{b ∈ Core(P) : b ∉ P′} / |Core(P)|   (0 when the core is empty)

A core failure whose verifier now passes has been resolved, not forgotten, and does not count.
Use θ = 0: no unresolved failure can be erased, and every resolution is accepted
(Lean `Playbook.v11_keeps_core`, `v11_accepts_resolution`; `ebllm.playbook.collapse_v11`).
The guarantee no longer depends on |Core| staying below 1/θ.

## 2. Sand-tile termination is a hypothesis, with an honest bound

Toppling is run with a toppling budget. A run that hits the budget is reported as non-terminating
burden (a residue), never as stable. When every toppling absorbs at least ε > 0 of burden and the
total stays ≥ −B, the number of topplings is at most (M₀ + B)/ε (Lean `SandTile.count_bound`).
Theorem 10.4's bound and Proposition 10.2 are dropped.

## 3. Scope loss of a composite bridge

    ScopeLoss(g ∘ f) = ScopeLoss(f) + #{x : f(x) defined and g(f(x)) lost}

(Lean `Scope.loss_comp`); the composite loses at most ScopeLoss(f) + ScopeLoss(g) when f is
injective where defined. A chain of bridges is released only if each link has zero scope loss,
as in Theorem 6.3, so nothing in the release depends on the false superadditivity.

## 4. Accuracy and information gain

Accuracy26 is non-decreasing from t to t + 1 iff the defects at t + 1, including
Collapse(P_t, P_{t+1}), sum to at most the defects at t, including Collapse(P_{t−1}, P_t)
(`ebllm.accuracy.monotone_step`). The typed-error gain of Definition 8.1 is positive iff
TypeGain(v) > log((1 + r(v) + Debt(v))/(1 + r(u))); it is not positive automatically.

## 5. Energy bounds

The descent sums of Proposition 25.4 and Theorem 35.2 are bounded by J₀ + ζ·MaxCert + Σε, since
J ≥ −ζ·MaxCert.

## 6. Labels

The emitted label is one of THEOREM, COUNTEREXAMPLE, CONDITIONAL, INDEPENDENCE, CANDIDATE, BUJ,
and OPEN for a run that has no candidate yet but still has a repair route (the paper leaves this
state unnamed). A result that has not been refereed is a CANDIDATE, however strong the formal
evidence; `ebllm controls` shows this for every closure recorded so far.

## 7. Verifiers are programs

The formal factor is computed, not asserted: a static scan of the Lean sources (no `sorry`,
`axiom`, `native_decide`, `implemented_by`, `unsafe`, `opaque`, debug options or environment
commands) and an audit of `#print axioms` (only `propext`, `Classical.choice`, `Quot.sound`).
The code factor is a program run with its expected output. These are the checks used for the
sphere packing, Navier–Stokes, Poincaré and Morley formalizations recorded in this project.
