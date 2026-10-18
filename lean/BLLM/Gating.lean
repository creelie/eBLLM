import BLLM.Basic

/-!
# Step gating against outcome gating

Precision of a step-gated chain is `∏ 1 / (1 + x i)`, bounded by
`exp (-∑ x) ≤ ∏ 1/(1+x) ≤ exp (-∑ x/(1+x))`; with perfect verifiers and constant error `ρ`
outcome gating costs `(1-ρ)^{-(n-1)}` times as much as step gating.
-/

open Real Finset

namespace BLLM

variable {ι : Type*}

/-- The posterior that a step accepted by a verifier with false-reject `η` and false-accept `δ`
is correct, when the generator errs with probability `ρ`, equals `1 / (1 + x)`. -/
theorem step_precision {ρ η δ : ℝ} (hρ1 : ρ < 1) (hη1 : η < 1) (hρ : 0 ≤ ρ) (hδ : 0 ≤ δ) :
    (1 - ρ) * (1 - η) / ((1 - ρ) * (1 - η) + ρ * δ)
      = 1 / (1 + ρ * δ / ((1 - ρ) * (1 - η))) := by
  have h1 : 0 < 1 - ρ := by linarith
  have h2 : 0 < 1 - η := by linarith
  have h3 : 0 < (1 - ρ) * (1 - η) + ρ * δ := by positivity
  field_simp

/-- **Precision bounds.** -/
theorem precision_bounds (s : Finset ι) (x : ι → ℝ) (hx : ∀ i ∈ s, 0 ≤ x i) :
    Real.exp (-∑ i ∈ s, x i) ≤ ∏ i ∈ s, 1 / (1 + x i) ∧
      ∏ i ∈ s, 1 / (1 + x i) ≤ Real.exp (-∑ i ∈ s, x i / (1 + x i)) := by
  constructor
  · rw [← Finset.sum_neg_distrib, Real.exp_sum]
    refine Finset.prod_le_prod (fun i _ => (Real.exp_pos _).le) (fun i hi => ?_)
    have h0 := hx i hi
    rw [Real.exp_neg, one_div]
    exact inv_anti₀ (by linarith) (by linarith [Real.add_one_le_exp (x i)])
  · rw [← Finset.sum_neg_distrib, Real.exp_sum]
    refine Finset.prod_le_prod (fun i hi => by have := hx i hi; positivity) (fun i hi => ?_)
    have h0 := hx i hi
    have e : 1 / (1 + x i) = -(x i / (1 + x i)) + 1 := by field_simp; ring
    rw [e]; exact Real.add_one_le_exp _

/-- **Cost separation.** With perfect verifiers and constant error `ρ`, outcome gating of an
`n`-step chain costs `n / (1-ρ)^n` and step gating costs `n / (1-ρ)`; the ratio is
`(1-ρ)^{-(n-1)}`, which is at least `1 + (n-1) ρ`. -/
theorem separation {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) (n : ℕ) :
    ((n + 1 : ℕ) : ℝ) / (1 - ρ) ^ (n + 1)
        = (((n + 1 : ℕ) : ℝ) / (1 - ρ)) * ((1 - ρ) ^ n)⁻¹ ∧
      1 + n * ρ ≤ ((1 - ρ) ^ n)⁻¹ := by
  have h1 : 0 < 1 - ρ := by linarith
  refine ⟨by rw [pow_succ]; field_simp, ?_⟩
  have hb : 1 + n * ρ ≤ (1 + ρ) ^ n := one_add_mul_le_pow (by linarith) n
  have hc : (1 + ρ) * (1 - ρ) ≤ 1 := by nlinarith
  have hd : (1 + ρ) ^ n * (1 - ρ) ^ n ≤ 1 := by
    rw [← mul_pow]; exact pow_le_one₀ (by nlinarith) hc
  have hpos : 0 < (1 - ρ) ^ n := pow_pos h1 n
  calc 1 + n * ρ ≤ (1 + ρ) ^ n := hb
    _ ≤ ((1 - ρ) ^ n)⁻¹ := by rw [le_inv_comm₀ (pow_pos (by linarith) n) hpos, ← one_div, le_div_iff₀ (pow_pos (by linarith) n)]; linarith [mul_comm ((1 + ρ) ^ n) ((1 - ρ) ^ n)]

/-- Outcome gating: the posterior that an accepted chain is correct, with prior `c`,
false-reject `η` and false-accept `δ`, equals `1 / (1 + (1-c) δ / (c (1-η)))`. -/
theorem outcome_precision {c η δ : ℝ} (hc : 0 < c) (hη1 : η < 1) (hc1 : c ≤ 1) (hδ : 0 ≤ δ) :
    c * (1 - η) / (c * (1 - η) + (1 - c) * δ)
      = 1 / (1 + (1 - c) * δ / (c * (1 - η))) := by
  have h2 : 0 < 1 - η := by linarith
  have h3 : 0 ≤ (1 - c) * δ := mul_nonneg (by linarith) hδ
  have h4 : 0 < c * (1 - η) + (1 - c) * δ := by positivity
  field_simp

end BLLM
