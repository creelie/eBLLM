import BLLM.Basic

/-!
# Randomised and adaptive schedules

If a check is repeated a random number `R` of times, the probability that a wrong item survives
is `E ε ^ R ≥ ε ^ (E R)`.
-/

open Real Finset

namespace BLLM

variable {ι : Type*}

/-- **Jensen step.** For weights `w ≥ 0` summing to one and repetition counts `r`,
`ε ^ (∑ w r) ≤ ∑ w ε ^ r`. -/
theorem jensen_repetition (s : Finset ι) (w : ι → ℝ) (r : ι → ℕ) {ε : ℝ} (hε0 : 0 < ε)
    (hw : ∀ i ∈ s, 0 ≤ w i) (hw1 : ∑ i ∈ s, w i = 1) :
    ε ^ (∑ i ∈ s, w i * r i) ≤ ∑ i ∈ s, w i * ε ^ r i := by
  have h := Real.geom_mean_le_arith_mean_weighted s w (fun i => ε ^ r i) hw hw1
    (fun i _ => (pow_pos hε0 _).le)
  refine le_trans (le_of_eq ?_) h
  rw [Real.rpow_sum_of_pos hε0]
  refine Finset.prod_congr rfl fun i _ => ?_
  rw [← Real.rpow_natCast, ← Real.rpow_mul hε0.le, mul_comm]

/-- Consequently a randomised schedule whose expected false-accept count is at most `θ` has
expected repetition counts `m i = ∑ w r` satisfying `∑ ε ^ m i ≤ θ`, so the entropy lower bound
applies to its expected cost. -/
theorem randomised_budget {κ : Type*} (s : Finset ι) (t : Finset κ) (w : κ → ℝ)
    (r : κ → ι → ℕ) {ε θ : ℝ} (hε0 : 0 < ε) (hw : ∀ j ∈ t, 0 ≤ w j)
    (hw1 : ∑ j ∈ t, w j = 1) (hθ : ∑ j ∈ t, w j * ∑ i ∈ s, ε ^ r j i ≤ θ) :
    ∑ i ∈ s, ε ^ (∑ j ∈ t, w j * r j i) ≤ θ := by
  calc ∑ i ∈ s, ε ^ (∑ j ∈ t, w j * r j i)
      ≤ ∑ i ∈ s, ∑ j ∈ t, w j * ε ^ r j i :=
        Finset.sum_le_sum fun i _ => jensen_repetition t w (fun j => r j i) hε0 hw hw1
    _ = ∑ j ∈ t, w j * ∑ i ∈ s, ε ^ r j i := by
        rw [Finset.sum_comm]; refine Finset.sum_congr rfl fun j _ => ?_; rw [Finset.mul_sum]
    _ ≤ θ := hθ

end BLLM
