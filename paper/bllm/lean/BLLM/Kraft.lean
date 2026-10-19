import BLLM.Basic

/-!
# Integer soundness and Kraft lengths

For `ε = 1/D` with an integer `D ≥ 2` and budget `θ = D ^ (-k)`, a schedule meets the budget
exactly when its repetition counts are `r i = ℓ i + k` for lengths `ℓ` satisfying Kraft's
inequality `∑ D ^ (-ℓ i) ≤ 1`; its cost is `k ∑ a + ∑ a ℓ`.
-/

open Real Finset

namespace BLLM

variable {ι : Type*}

/-- A schedule meeting the budget `D^(-k)` repeats every check at least `k` times and its
shifted counts satisfy Kraft's inequality. -/
theorem kraft_of_schedule (s : Finset ι) (r : ι → ℕ) {D : ℝ} (hD : 1 < D) (k : ℕ)
    (h : ∑ i ∈ s, (1 / D) ^ r i ≤ (1 / D) ^ k) :
    (∀ i ∈ s, k ≤ r i) ∧ ∑ i ∈ s, (1 / D) ^ (r i - k) ≤ 1 := by
  have hb0 : 0 < 1 / D := by positivity
  have hb1 : 1 / D < 1 := by rw [div_lt_one (by linarith)]; exact hD
  have hk : ∀ i ∈ s, k ≤ r i := by
    intro i hi
    have hle : (1 / D) ^ r i ≤ (1 / D) ^ k :=
      le_trans (Finset.single_le_sum (fun j _ => (pow_pos hb0 (r j)).le) hi) h
    exact (pow_le_pow_iff_right_of_lt_one₀ hb0 hb1).1 hle
  refine ⟨hk, ?_⟩
  have e : ∑ i ∈ s, (1 / D) ^ r i = (1 / D) ^ k * ∑ i ∈ s, (1 / D) ^ (r i - k) := by
    rw [Finset.mul_sum]; refine Finset.sum_congr rfl fun i hi => ?_
    rw [← pow_add, Nat.add_sub_cancel' (hk i hi)]
  rw [e] at h
  have hp : 0 < (1 / D) ^ k := pow_pos hb0 k
  by_contra hc
  push Not at hc
  have : (1 / D) ^ k * 1 < (1 / D) ^ k * ∑ i ∈ s, (1 / D) ^ (r i - k) :=
    mul_lt_mul_of_pos_left hc hp
  linarith

/-- Kraft lengths shifted by `k` give a schedule meeting the budget `D^(-k)`. -/
theorem schedule_of_kraft (s : Finset ι) (ℓ : ι → ℕ) {D : ℝ} (hD : 1 < D) (k : ℕ)
    (h : ∑ i ∈ s, (1 / D) ^ ℓ i ≤ 1) :
    ∑ i ∈ s, (1 / D) ^ (ℓ i + k) ≤ (1 / D) ^ k := by
  have hb0 : 0 < 1 / D := by positivity
  have e : ∑ i ∈ s, (1 / D) ^ (ℓ i + k) = (1 / D) ^ k * ∑ i ∈ s, (1 / D) ^ ℓ i := by
    rw [Finset.mul_sum]; refine Finset.sum_congr rfl fun i _ => ?_; rw [pow_add, mul_comm]
  rw [e]
  calc (1 / D) ^ k * ∑ i ∈ s, (1 / D) ^ ℓ i ≤ (1 / D) ^ k * 1 :=
        mul_le_mul_of_nonneg_left h (pow_pos hb0 k).le
    _ = (1 / D) ^ k := mul_one _

/-- The cost of the shifted schedule. -/
theorem shifted_cost (s : Finset ι) (a : ι → ℝ) (ℓ : ι → ℕ) (k : ℕ) :
    ∑ i ∈ s, a i * ((ℓ i + k : ℕ) : ℝ) = k * ∑ i ∈ s, a i + ∑ i ∈ s, a i * ℓ i := by
  rw [Finset.mul_sum, ← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl fun i _ => ?_; push_cast; ring

end BLLM
