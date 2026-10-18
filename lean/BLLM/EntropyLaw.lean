import BLLM.Basic

/-!
# The entropy law for finite chains

For costs `a i > 0` with total `A`, soundness error `0 < ε < 1` and budget `0 < θ ≤ 1`,
every repetition schedule `r` with `∑ ε ^ r i ≤ θ` costs at least
`(∑ a log (A / a) + A log (1/θ)) / log (1/ε)`, and the ceiling schedule meets the budget at a
cost at most one `A` above that bound.
-/

open Real Finset

namespace BLLM

variable {ι : Type*}

/-- Entropy lower bound in un-normalised form. -/
theorem entropy_lower (s : Finset ι) (a β : ι → ℝ) {θ : ℝ}
    (ha : ∀ i ∈ s, 0 < a i) (hβ : ∀ i ∈ s, 0 < β i) (hθ : 0 < θ)
    (hsum : ∑ i ∈ s, β i ≤ θ) :
    ∑ i ∈ s, a i * Real.log ((∑ j ∈ s, a j) / a i) + (∑ j ∈ s, a j) * Real.log (1 / θ)
      ≤ ∑ i ∈ s, a i * Real.log (1 / β i) := by
  rcases s.eq_empty_or_nonempty with rfl | hne
  · simp
  set A := ∑ j ∈ s, a j with hAdef
  have hA : 0 < A := Finset.sum_pos ha hne
  have hterm : ∀ i ∈ s, a i * Real.log (A / a i) + a i * Real.log (1 / θ)
      ≤ a i * Real.log (1 / β i) + (A / θ) * β i - a i := by
    intro i hi
    have := entropy_term (ha i hi) (hβ i hi) hA hθ
    have e : A * β i / θ = (A / θ) * β i := by ring
    linarith
  have hs := Finset.sum_le_sum hterm
  rw [Finset.sum_add_distrib, ← Finset.sum_mul, Finset.sum_sub_distrib,
    Finset.sum_add_distrib, ← Finset.mul_sum] at hs
  have hb : (A / θ) * ∑ i ∈ s, β i ≤ A := by
    calc (A / θ) * ∑ i ∈ s, β i ≤ (A / θ) * θ :=
          mul_le_mul_of_nonneg_left hsum (by positivity)
      _ = A := by field_simp
  linarith

/-- **Entropy law, lower bound.** Every schedule `r` with `∑ ε ^ r i ≤ θ` satisfies
`(∑ a log (A / a) + A log (1/θ)) / log (1/ε) ≤ ∑ a i * r i`. -/
theorem verification_lower (s : Finset ι) (a : ι → ℝ) (r : ι → ℕ) {ε θ : ℝ}
    (ha : ∀ i ∈ s, 0 < a i) (hε0 : 0 < ε) (hε1 : ε < 1) (hθ : 0 < θ)
    (hsum : ∑ i ∈ s, ε ^ r i ≤ θ) :
    (∑ i ∈ s, a i * Real.log ((∑ j ∈ s, a j) / a i) + (∑ j ∈ s, a j) * Real.log (1 / θ))
      / Real.log (1 / ε) ≤ ∑ i ∈ s, a i * r i := by
  have hL := log_inv_pos hε0 hε1
  have h := entropy_lower s a (fun i => ε ^ r i) ha (fun i _ => pow_pos hε0 _) hθ hsum
  have e : ∑ i ∈ s, a i * Real.log (1 / ε ^ r i)
      = (∑ i ∈ s, a i * r i) * Real.log (1 / ε) := by
    rw [Finset.sum_mul]; refine Finset.sum_congr rfl fun i _ => ?_
    rw [log_inv_pow]; ring
  rw [e] at h
  rw [div_le_iff₀ hL]; exact h

/-- The ceiling schedule `r i = ⌈log (A / (θ a i)) / log (1/ε)⌉₊`. -/
noncomputable def ceilSchedule (s : Finset ι) (a : ι → ℝ) (ε θ : ℝ) (i : ι) : ℕ :=
  ⌈Real.log ((∑ j ∈ s, a j) / (θ * a i)) / Real.log (1 / ε)⌉₊

/-- The ceiling schedule meets the budget. -/
theorem ceilSchedule_sound (s : Finset ι) (a : ι → ℝ) {ε θ : ℝ}
    (ha : ∀ i ∈ s, 0 < a i) (hε0 : 0 < ε) (hε1 : ε < 1) (hθ : 0 < θ) :
    ∑ i ∈ s, ε ^ ceilSchedule s a ε θ i ≤ θ := by
  rcases s.eq_empty_or_nonempty with rfl | hne
  · simp [hθ.le]
  have hL := log_inv_pos hε0 hε1
  set A := ∑ j ∈ s, a j with hAdef
  have hA : 0 < A := Finset.sum_pos ha hne
  have hterm : ∀ i ∈ s, ε ^ ceilSchedule s a ε θ i ≤ θ / A * a i := by
    intro i hi
    have hai := ha i hi
    have hc : Real.log (A / (θ * a i)) / Real.log (1 / ε) ≤ ceilSchedule s a ε θ i :=
      Nat.le_ceil _
    rw [div_le_iff₀ hL] at hc
    have hy : 0 < θ / A * a i := by positivity
    rw [← Real.log_le_log_iff (pow_pos hε0 _) hy]
    have e1 : Real.log (ε ^ ceilSchedule s a ε θ i)
        = - ((ceilSchedule s a ε θ i : ℝ) * Real.log (1 / ε)) := by
      rw [Real.log_pow, one_div, Real.log_inv]; ring
    have e2 : Real.log (θ / A * a i) = - Real.log (A / (θ * a i)) := by
      rw [← Real.log_inv]; congr 1; field_simp
    rw [e1, e2]; linarith
  calc ∑ i ∈ s, ε ^ ceilSchedule s a ε θ i ≤ ∑ i ∈ s, θ / A * a i := Finset.sum_le_sum hterm
    _ = θ := by rw [← Finset.mul_sum, ← hAdef]; field_simp

/-- **Entropy law, upper bound.** For `θ ≤ 1` the ceiling schedule costs at most
`(∑ a log (A / a) + A log (1/θ)) / log (1/ε) + A`. -/
theorem ceilSchedule_cost (s : Finset ι) (a : ι → ℝ) {ε θ : ℝ}
    (ha : ∀ i ∈ s, 0 < a i) (hε0 : 0 < ε) (hε1 : ε < 1) (hθ : 0 < θ) (hθ1 : θ ≤ 1) :
    ∑ i ∈ s, a i * ceilSchedule s a ε θ i
      ≤ (∑ i ∈ s, a i * Real.log ((∑ j ∈ s, a j) / a i) + (∑ j ∈ s, a j) * Real.log (1 / θ))
          / Real.log (1 / ε) + ∑ j ∈ s, a j := by
  have hL := log_inv_pos hε0 hε1
  set A := ∑ j ∈ s, a j with hAdef
  have hterm : ∀ i ∈ s, a i * ceilSchedule s a ε θ i
      ≤ (a i * Real.log (A / a i) + a i * Real.log (1 / θ)) / Real.log (1 / ε) + a i := by
    intro i hi
    have hai := ha i hi
    have haA : a i ≤ A := Finset.single_le_sum (fun j hj => (ha j hj).le) hi
    have hA : 0 < A := lt_of_lt_of_le hai haA
    have hx0 : 0 ≤ Real.log (A / (θ * a i)) / Real.log (1 / ε) := by
      apply div_nonneg _ hL.le
      apply Real.log_nonneg
      rw [le_div_iff₀ (by positivity), one_mul]
      calc θ * a i ≤ 1 * a i := mul_le_mul_of_nonneg_right hθ1 hai.le
        _ = a i := one_mul _
        _ ≤ A := haA
    have hc := Nat.ceil_lt_add_one hx0
    have e : Real.log (A / (θ * a i)) = Real.log (A / a i) + Real.log (1 / θ) := by
      rw [← Real.log_mul (by positivity) (by positivity)]; congr 1; field_simp
    have h1 : a i * ceilSchedule s a ε θ i
        ≤ a i * (Real.log (A / (θ * a i)) / Real.log (1 / ε) + 1) :=
      mul_le_mul_of_nonneg_left hc.le hai.le
    calc a i * ceilSchedule s a ε θ i
        ≤ a i * (Real.log (A / (θ * a i)) / Real.log (1 / ε) + 1) := h1
      _ = (a i * Real.log (A / a i) + a i * Real.log (1 / θ)) / Real.log (1 / ε) + a i := by
          rw [e]; field_simp
  calc ∑ i ∈ s, a i * ceilSchedule s a ε θ i
      ≤ ∑ i ∈ s, ((a i * Real.log (A / a i) + a i * Real.log (1 / θ)) / Real.log (1 / ε)
          + a i) := Finset.sum_le_sum hterm
    _ = _ := by
        rw [Finset.sum_add_distrib, ← Finset.sum_div, Finset.sum_add_distrib, ← Finset.sum_mul]

end BLLM
