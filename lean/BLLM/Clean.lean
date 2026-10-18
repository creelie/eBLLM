import Mathlib

/-!
# Probability of a clean run

If the wrong items of a run are accepted independently with probabilities `q i ∈ [0,1]`, the run
is clean with probability `∏ (1 - q i)`, and `1 - ∑ q ≤ ∏ (1 - q) ≤ exp (-∑ q)`.
-/

open Real Finset

namespace BLLM

variable {ι : Type*}

theorem clean_le_exp (s : Finset ι) (q : ι → ℝ) (h1 : ∀ i ∈ s, q i ≤ 1) :
    ∏ i ∈ s, (1 - q i) ≤ Real.exp (-∑ i ∈ s, q i) := by
  rw [← Finset.sum_neg_distrib, Real.exp_sum]
  refine Finset.prod_le_prod (fun i hi => by linarith [h1 i hi]) (fun i _ => ?_)
  have := Real.add_one_le_exp (-q i); linarith

theorem clean_ge (s : Finset ι) (q : ι → ℝ) (h0 : ∀ i ∈ s, 0 ≤ q i)
    (h1 : ∀ i ∈ s, q i ≤ 1) :
    1 - ∑ i ∈ s, q i ≤ ∏ i ∈ s, (1 - q i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | insert j t hj ih =>
    rw [Finset.sum_insert hj, Finset.prod_insert hj]
    have ih' := ih (fun i hi => h0 i (Finset.mem_insert_of_mem hi))
      (fun i hi => h1 i (Finset.mem_insert_of_mem hi))
    have hP : 0 ≤ ∏ i ∈ t, (1 - q i) :=
      Finset.prod_nonneg fun i hi => by linarith [h1 i (Finset.mem_insert_of_mem hi)]
    have hP1 : ∏ i ∈ t, (1 - q i) ≤ 1 :=
      Finset.prod_le_one (fun i hi => by linarith [h1 i (Finset.mem_insert_of_mem hi)])
        (fun i hi => by linarith [h0 i (Finset.mem_insert_of_mem hi)])
    have hj0 := h0 j (Finset.mem_insert_self j t)
    have hj1 := h1 j (Finset.mem_insert_self j t)
    nlinarith

/-- A run that must be clean with probability at least `1 - θ` has `∑ q ≤ log (1/(1-θ))`. -/
theorem clean_budget (s : Finset ι) (q : ι → ℝ) {θ : ℝ} (hθ1 : θ < 1)
    (h1 : ∀ i ∈ s, q i ≤ 1)
    (hclean : 1 - θ ≤ ∏ i ∈ s, (1 - q i)) :
    ∑ i ∈ s, q i ≤ Real.log (1 / (1 - θ)) := by
  have hpos : 0 < 1 - θ := by linarith
  have h := hclean.trans (clean_le_exp s q h1)
  rw [one_div, Real.log_inv, le_neg]
  rw [← Real.log_exp (-∑ i ∈ s, q i)]
  exact Real.log_le_log hpos h

end BLLM
