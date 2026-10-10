# Review of the VSI paper's numbered results

Paper: D. Bhattacharjee, *Synthetic Neuromorphic Superintelligence for Verifier-Gated Conjecture
Closure: Sand-Tile Automata, K-Dot Circuits, and Phenomenological Proof Learning* (15 May 2026),
`paper/VSI-verifier-gated-conjecture-closure-2026-05-15.pdf`. Reviewed on 10 October 2026.

Every result below was read against its definitions. "Lean" means a theorem in `lean/EBLLM/`
(Lean 4 core, no Mathlib; `lean/Audit.lean` shows only the standard axioms), and "checks" means
the Python tests and the C, C++ and Julia programs in `checks/`.

## Results that are false as stated

| Result | What fails | Evidence |
|---|---|---|
| Proposition 10.2 (toppling exposes hidden debt) | Two sites joined by an edge, conservative kernel, heights (1, 1), θ = 1/2, Δ = 1: the run never stabilizes, and the graph is finite, so there is no infinite dependency path. The proof's "only finitely many topplings can occur at finite energy" is the error: with enough burden a closed conservative system topples forever. | Lean `SandTile.conservative_never_stable`; C `checks/c/sandtile.c` (10⁶ topplings) |
| Theorem 10.4 (sand-tile convergence rate) | The bound H₀·\|Λ\|·diam/θ_min is 4 for both two-site runs. The conservative run never stops. A dissipative run with Δ = 2 ≥ θ_min = 1 and share 1 − 1/N needs exactly N topplings. The proof assumes a sink and a uniform loss per toppling, neither of which is a hypothesis. A correct bound: if every toppling absorbs at least ε > 0 and the total burden stays ≥ −B, then k topplings need k·ε ≤ M₀ + B. | Lean `SandTile.dissipative_count`, `count_bound`; C for N up to 10⁴; Python tests |
| Lemma 6.2, second part (scope losses add) | ScopeLoss(g∘f) ≥ ScopeLoss(f) + ScopeLoss(g) fails when f misses the part of D_b that g loses: D_a = {0}, D_b = {0, 1}, f(0) = 0, g loses 1. The exact statement is ScopeLoss(g∘f) = ScopeLoss(f) + #{x : f(x) defined, g(f(x)) lost}, which is at most the sum when f is injective. | Lean `Scope.lemma_6_2_false`, `Scope.loss_comp`; C++ over all 9,710 pairs of small partial maps (2,976 violate the lemma) |
| Theorem 30.1 and Corollary 30.2 (no hidden context), with the guard of Section 18 | Collapse(P, P′) = 1 − \|Core P ∩ Core P′\|/\|Core P\| counts a failure that was *resolved* (its verifier now passes, so it leaves the core) as collapse. Under the hypothesis θ < 1/\|Core P\| the guard therefore rejects every update that records a successful repair, so the core never shrinks and Corollary 30.2's "shrinks only when a failure is resolved" cannot happen. The hypothesis θ < 1/\|Core P_t\| also lapses as the core grows: with θ = 1/3 and three core failures, deleting one unresolved failure is accepted. Collapse is undefined when the core is empty. | Lean `Playbook.paper_rejects_resolution`, `paper_guard_lapses`; C++ (1,880 of 1,880 resolving updates rejected) |
| Proposition 8.2 (positive information from failure) | With r(u) = r(v) = 0, Debt(v) = 100, TypeGain(v) = 1 and ScopeLoss(v) = 0, Definition 8.1 gives I = log(1/101) + 1 < 0, against the claimed I ≥ log(1 + 1/Debt) > 0. The proof's last step ("the TypeGain term guarantees positivity") does not follow. I > 0 exactly when TypeGain(v) > log((1 + r(v) + Debt(v))/(1 + r(u))). | arithmetic; Python test |
| Proposition 21.1 (accuracy monotonicity "if and only if") | The score at step t also contains Collapse(P_{t−1}, P_t), which the printed condition leaves out. The printed condition is sufficient but not necessary. | Julia (861 of 20,000 random steps where the score rises but the printed condition fails; none the other way); Python test |
| Proposition 25.4 and Theorem 35.2 (rates and summed descent) | Definition 25.1 bounds J below by −ζ·MaxCert, not by 0, but both results use J ≥ 0 when telescoping. The bounds should read J₀ + ζ·MaxCert + Σε (and Proposition 25.4's extra factor 1/ε is unexplained). In Theorem 35.2 the terms tend to 0 along the whole sequence, not only along a density-one subsequence, since the series converges. | by inspection |

## Results that are true but whose proof is wrong or incomplete

| Result | Comment |
|---|---|
| Corollary 6.4 (debt-monotone release blocking) | True, but the proof's claim that every increase of DebtMass adds a non-PASS leaf fails when only a weight changes. The right reason: a released state has DebtMass 0 (Lean `cor_6_4`, `debt_eq_zero_of_released`). |
| Lemma 18.1 (collapse guard sharpness) | The statement is right; the proof's last sentence has the direction reversed (increasing θ allows *more* deletion). |
| Theorem 18.2 (playbook utility convergence) | "E[U(b_k^t)] → αp_kT − βq_kT as T → ∞" is a limit equal to an expression in T; the intended statement is E[U]/t → αp_k − βq_k. The hypothesis αp_k > βq_k + λρ_k is never used. |
| Section 6.1, P(Rel = 1) ≤ min P(V_χ = 1) | True; "with equality only when all factors are maximally correlated" is not: equality also holds, for example, when the smallest probability is 0. |
| Lemma 10.3 (abelian property) | Holds for the classical sandpile with fixed Δ and K and a terminating run (tested on 200 random graphs in C and 40 in Python); the paper's version needs these hypotheses stated. |

## Results that hold by definition

Theorem 2.2, Theorem 3.1, Theorem 5.3 (first half), Theorem 6.3, Theorem 21.3 and Corollary 21.4
say that one zero factor in a product blocks release; Lean `rel_false_of_mem`, `no_shortcut`,
`released_only_if_all` prove this, and the Julia check runs all 2⁸ assignments. Lemma 4.1 and
Proposition 5.2 (finite coverage) hold: Lean `Kappa.length_words`, `typed_le`. Lemma 12.1 is the
standard descent lemma for L-smooth functions and is correct. Proposition 11.2 is correct.

## Statements that are not proofs

Lemma 25.2, Theorem 25.3, Theorem 25.5, Theorem 28.3, Theorem 33.1, Proposition 9.3,
Proposition 12.2 and Proposition 16.1 assert that some module "can identify" a direction or that
"other terms are bounded above by zero"; they depend on quantities the paper does not define
precisely enough to prove anything. They describe how the engine is meant to behave and should be
labelled as design principles rather than theorems.

## Labels the paper assigns

Section 27.3 records the Collatz conjecture as CAND-STRONG with V_model = 1. The section gives a
gate vector and a module sequence, but no argument, and its own defects (lower gate 1.00, formal
gate 1.00) say that the decisive step, a uniform stopping-time bound for every n, is missing. Under
the paper's own rules V_model = 1 needs a complete candidate argument, so the label the release
algebra gives is OPEN, as `ebllm controls` shows. The P versus NP sheet of Section 27.4 is in the
same position.

## What this means for the circuit

The release discipline at the core of the circuit is sound: no amount of context, presentation or
model confidence can raise a label while one verifier factor is zero. The faults are in the
supporting dynamics (sand-tile rate, scope-loss algebra) and in the memory guard, which as written
cannot record a success. `docs/CIRCUIT-v1.1.md` gives the corrected circuit implemented by this
package.
