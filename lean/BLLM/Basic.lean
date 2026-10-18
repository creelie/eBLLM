import Mathlib

/-!
# Basic inequalities

The termwise Gibbs inequality and the logarithm of a power of the soundness error.
-/

open Real Finset

namespace BLLM

/-- Termwise Gibbs inequality: `x log(1/x) ≤ x log(1/y) + y - x` for `x, y > 0`. -/
theorem gibbs_term {x y : ℝ} (hx : 0 < x) (hy : 0 < y) :
    x * Real.log (1 / x) ≤ x * Real.log (1 / y) + y - x := by
  have h := Real.log_le_sub_one_of_pos (div_pos hy hx)
  have e : Real.log (y / x) = Real.log (1 / x) - Real.log (1 / y) := by
    rw [one_div, one_div, Real.log_inv, Real.log_inv, Real.log_div hy.ne' hx.ne']; ring
  rw [e] at h
  have : x * (Real.log (1 / x) - Real.log (1 / y)) ≤ x * (y / x - 1) :=
    mul_le_mul_of_nonneg_left h hx.le
  have h2 : x * (y / x - 1) = y - x := by field_simp
  linarith

/-- The term inequality behind the entropy lower bound. -/
theorem entropy_term {a b A θ : ℝ} (ha : 0 < a) (hb : 0 < b) (hA : 0 < A) (hθ : 0 < θ) :
    a * Real.log (A / a) + a * Real.log (1 / θ) ≤ a * Real.log (1 / b) + A * b / θ - a := by
  have hx : 0 < A * b / (θ * a) := by positivity
  have h := Real.log_le_sub_one_of_pos hx
  have e : Real.log (A * b / (θ * a)) =
      Real.log A + Real.log b - Real.log θ - Real.log a := by
    rw [Real.log_div (by positivity) (by positivity), Real.log_mul hA.ne' hb.ne',
      Real.log_mul hθ.ne' ha.ne']; ring
  rw [e] at h
  have h1 := mul_le_mul_of_nonneg_left h ha.le
  have h2 : a * (A * b / (θ * a) - 1) = A * b / θ - a := by field_simp
  rw [h2] at h1
  rw [Real.log_div hA.ne' ha.ne', one_div, one_div, Real.log_inv, Real.log_inv]
  linarith

/-- `log (1 / ε ^ r) = r log (1 / ε)`. -/
theorem log_inv_pow (ε : ℝ) (r : ℕ) :
    Real.log (1 / ε ^ r) = r * Real.log (1 / ε) := by
  rw [one_div, one_div, Real.log_inv, Real.log_inv, Real.log_pow]; ring

/-- `log (1/ε) > 0` for `0 < ε < 1`. -/
theorem log_inv_pos {ε : ℝ} (hε0 : 0 < ε) (hε1 : ε < 1) : 0 < Real.log (1 / ε) := by
  apply Real.log_pos; rw [one_div]; exact one_lt_inv_iff₀.2 ⟨hε0, hε1⟩

end BLLM
