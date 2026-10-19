import Mathlib

/-!
# The soundness dichotomy

Wrong proposals pass their checks independently, the `n`-th with probability between
`b q n` and `C q n`. If `∑ q < ∞` only finitely many wrong items are accepted almost surely;
if `∑ q = ∞` infinitely many are accepted almost surely.
-/

open MeasureTheory ProbabilityTheory Filter ENNReal

namespace BLLM

variable {Ω : Type*} {m0 : MeasurableSpace Ω} {μ : Measure Ω}

/-- Finitely many false accepts when the error series converges. -/
theorem false_accepts_finite (E : ℕ → Set Ω) (q : ℕ → ℝ≥0∞) {C : ℝ≥0∞} (hC : C ≠ ∞)
    (hup : ∀ n, μ (E n) ≤ C * q n) (hq : ∑' n, q n ≠ ∞) :
    μ (limsup E atTop) = 0 := by
  apply measure_limsup_atTop_eq_zero
  refine ne_top_of_le_ne_top (ENNReal.mul_ne_top hC hq) ?_
  rw [← ENNReal.tsum_mul_left]; exact ENNReal.tsum_le_tsum hup

/-- Infinitely many false accepts when the error series diverges. -/
theorem false_accepts_infinite [IsProbabilityMeasure μ] (E : ℕ → Set Ω) (q : ℕ → ℝ≥0∞)
    {b : ℝ≥0∞} (hb : b ≠ 0) (hm : ∀ n, MeasurableSet (E n)) (hind : iIndepSet E μ)
    (hlow : ∀ n, b * q n ≤ μ (E n)) (hq : ∑' n, q n = ∞) :
    μ (limsup E atTop) = 1 := by
  apply measure_limsup_eq_one hm hind
  apply eq_top_iff.2
  calc ∞ = b * ∑' n, q n := by rw [hq, ENNReal.mul_top hb]
    _ = ∑' n, b * q n := (ENNReal.tsum_mul_left).symm
    _ ≤ ∑' n, μ (E n) := ENNReal.tsum_le_tsum hlow

/-- Union bound: the probability of any false accept is at most `C ∑ q`. -/
theorem any_false_accept_le (E : ℕ → Set Ω) (q : ℕ → ℝ≥0∞) {C : ℝ≥0∞}
    (hup : ∀ n, μ (E n) ≤ C * q n) :
    μ (⋃ n, E n) ≤ C * ∑' n, q n := by
  calc μ (⋃ n, E n) ≤ ∑' n, μ (E n) := measure_iUnion_le _
    _ ≤ ∑' n, C * q n := ENNReal.tsum_le_tsum hup
    _ = C * ∑' n, q n := ENNReal.tsum_mul_left

end BLLM
