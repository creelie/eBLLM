import BLLM.Basic

/-!
# Contamination in a branching takeoff

With mean offspring `m > 1` the expected number of false accepts is a multiple of
`∑ m ^ k δ k`. A fixed false-accept rate makes this series diverge; checks amplified to
`r k log (1/ε) ≥ k log (2 m)` make it converge.
-/

open Real

namespace BLLM

/-- A fixed positive false-accept rate with `m ≥ 1` gives a divergent contamination series. -/
theorem contamination_diverges {m δ : ℝ} (hm : 1 ≤ m) (hδ : 0 < δ) :
    ¬ Summable fun k : ℕ => m ^ k * δ := by
  intro h
  have ht := h.tendsto_atTop_zero
  have hlow : ∀ k : ℕ, δ ≤ m ^ k * δ := fun k => by
    have := one_le_pow₀ hm (n := k); nlinarith
  have : δ ≤ 0 := ge_of_tendsto ht (Filter.Eventually.of_forall hlow)
  linarith

/-- Amplified checks: if `r k log (1/ε) ≥ k log (2m)` then `m ^ k ε ^ r k ≤ (1/2) ^ k`. -/
theorem amplified_term {m ε : ℝ} (hm : 0 < m) (hε0 : 0 < ε) (r : ℕ → ℕ)
    (hr : ∀ k : ℕ, (k : ℝ) * Real.log (2 * m) ≤ r k * Real.log (1 / ε)) (k : ℕ) :
    m ^ k * ε ^ r k ≤ (1 / 2) ^ k := by
  have hpos : 0 < m ^ k * ε ^ r k := by positivity
  rw [← Real.log_le_log_iff hpos (by positivity)]
  rw [Real.log_mul (by positivity) (by positivity), Real.log_pow, Real.log_pow, Real.log_pow]
  have e1 : Real.log (2 * m) = Real.log 2 + Real.log m := Real.log_mul (by norm_num) hm.ne'
  have e2 : Real.log ε = - Real.log (1 / ε) := by rw [one_div, Real.log_inv]; ring
  have e3 : Real.log (1 / 2) = - Real.log 2 := by rw [one_div, Real.log_inv]
  rw [e2, e3]
  have := hr k
  rw [e1] at this
  nlinarith

/-- Amplified checks give a convergent contamination series. -/
theorem amplified_summable {m ε : ℝ} (hm : 0 < m) (hε0 : 0 < ε) (r : ℕ → ℕ)
    (hr : ∀ k : ℕ, (k : ℝ) * Real.log (2 * m) ≤ r k * Real.log (1 / ε)) :
    Summable fun k => m ^ k * ε ^ r k :=
  Summable.of_nonneg_of_le (fun k => by positivity) (amplified_term hm hε0 r hr)
    (summable_geometric_of_lt_one (by norm_num) (by norm_num))

/-- The amplification `r k = ⌈k log (2m) / log (1/ε)⌉₊` satisfies the hypothesis. -/
theorem amplified_schedule_ok {m ε : ℝ} (hε0 : 0 < ε) (hε1 : ε < 1) (k : ℕ) :
    (k : ℝ) * Real.log (2 * m)
      ≤ (⌈(k : ℝ) * Real.log (2 * m) / Real.log (1 / ε)⌉₊ : ℕ) * Real.log (1 / ε) := by
  have hL := log_inv_pos hε0 hε1
  rw [← div_le_iff₀ hL]; exact Nat.le_ceil _

end BLLM
