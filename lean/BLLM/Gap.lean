import Mathlib

/-!
# The search gap

Ideas fall into finitely many classes. The idea a problem needs lies in class `i` with
probability `π i`, and a proposer draws the class of each proposal independently from a
distribution `q`, so it needs `∑ π i / q i` proposals in expectation to reach the right class.
Writing `π i = a i ^ 2` with `a i = √(π i)`, the least expected number is `(∑ a i) ^ 2`, the
exponential of the Rényi entropy of order one half of `π`, attained at `q ∝ a`; every other
proposer pays exactly the factor `1 + χ²(a / S ‖ q)`, and mixing any proposer with weight `λ`
of the square-root profile costs at most `(∑ a i) ^ 2 / λ`.
-/

open Finset

namespace BLLM

variable {ι : Type*}

/-- The least expected number of proposals is `(∑ a) ^ 2`. -/
theorem search_lower (s : Finset ι) (a q : ι → ℝ) (hq : ∀ i ∈ s, 0 < q i)
    (hsum : ∑ i ∈ s, q i = 1) :
    (∑ i ∈ s, a i) ^ 2 ≤ ∑ i ∈ s, a i ^ 2 / q i := by
  have h := sq_sum_div_le_sum_sq_div s a hq
  rwa [hsum, div_one] at h

/-- The square-root profile attains it. -/
theorem search_optimal (s : Finset ι) (a : ι → ℝ) (ha : ∀ i ∈ s, 0 < a i) :
    ∑ i ∈ s, a i ^ 2 / (a i / ∑ j ∈ s, a j) = (∑ i ∈ s, a i) ^ 2 := by
  rcases s.eq_empty_or_nonempty with rfl | hne
  · simp
  have hS : 0 < ∑ j ∈ s, a j := sum_pos ha hne
  have h : ∀ i ∈ s, a i ^ 2 / (a i / ∑ j ∈ s, a j) = (∑ j ∈ s, a j) * a i := by
    intro i hi
    have := (ha i hi).ne'
    field_simp
  rw [sum_congr rfl h, ← mul_sum, sq]

/-- Every proposer pays the optimum times `1 + χ²(r ‖ q)`, with `r = a / S`. -/
theorem search_chi2 (s : Finset ι) (a q : ι → ℝ) (hq : ∀ i ∈ s, 0 < q i)
    (hsum : ∑ i ∈ s, q i = 1) (hS : ∑ i ∈ s, a i ≠ 0) :
    ∑ i ∈ s, a i ^ 2 / q i =
      (∑ i ∈ s, a i) ^ 2 * (1 + ∑ i ∈ s, (a i / ∑ j ∈ s, a j - q i) ^ 2 / q i) := by
  set S := ∑ j ∈ s, a j with hSdef
  have h : ∀ i ∈ s, (a i / S - q i) ^ 2 / q i = a i ^ 2 / q i / S ^ 2 - 2 * (a i / S) + q i := by
    intro i hi
    have := (hq i hi).ne'
    field_simp
    ring
  rw [sum_congr rfl h, sum_add_distrib, sum_sub_distrib, ← sum_div, ← mul_sum, ← sum_div, hsum,
    ← hSdef, div_self hS]
  field_simp
  ring

/-- Mixing with weight `λ` of the square-root profile costs at most `(∑ a) ^ 2 / λ`. -/
theorem search_mix (s : Finset ι) (a q : ι → ℝ) (lam : ℝ) (hlam : 0 < lam)
    (ha : ∀ i ∈ s, 0 < a i) (hq : ∀ i ∈ s, lam * (a i / ∑ j ∈ s, a j) ≤ q i) :
    ∑ i ∈ s, a i ^ 2 / q i ≤ (∑ i ∈ s, a i) ^ 2 / lam := by
  rcases s.eq_empty_or_nonempty with rfl | hne
  · simp
  have hS : 0 < ∑ j ∈ s, a j := sum_pos ha hne
  have h : ∀ i ∈ s, a i ^ 2 / q i ≤ (∑ j ∈ s, a j) * a i / lam := by
    intro i hi
    have hai := ha i hi
    have hlow : 0 < lam * (a i / ∑ j ∈ s, a j) := mul_pos hlam (div_pos hai hS)
    calc a i ^ 2 / q i ≤ a i ^ 2 / (lam * (a i / ∑ j ∈ s, a j)) :=
          div_le_div_of_nonneg_left (sq_nonneg _) hlow (hq i hi)
      _ = (∑ j ∈ s, a j) * a i / lam := by
          field_simp
  calc ∑ i ∈ s, a i ^ 2 / q i ≤ ∑ i ∈ s, (∑ j ∈ s, a j) * a i / lam := sum_le_sum h
    _ = (∑ i ∈ s, a i) ^ 2 / lam := by rw [← sum_div, ← mul_sum, sq]

end BLLM
