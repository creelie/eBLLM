import BLLM.Basic

/-!
# The Rényi law for polynomially sound checks

A check run at error level `δ` costs `a δ ^ (-s)` with `s > 0`. If `∑ δ i ≤ θ` then
`(∑ a ^ (1/(1+s))) ^ (1+s) ≤ (∑ a δ ^ (-s)) θ ^ s`, and the allocation
`δ i = θ a i ^ (1/(1+s)) / ∑ a ^ (1/(1+s))` attains equality.
-/

open Real Finset

namespace BLLM

variable {ι : Type*}

/-- **Rényi law, lower bound** (Hölder). -/
theorem renyi_lower (s : Finset ι) (a δ : ι → ℝ) {σ θ : ℝ} (hσ : 0 < σ)
    (ha : ∀ i ∈ s, 0 < a i) (hδ : ∀ i ∈ s, 0 < δ i) (hθ : 0 < θ)
    (hsum : ∑ i ∈ s, δ i ≤ θ) :
    (∑ i ∈ s, a i ^ (1 + σ)⁻¹) ^ (1 + σ) ≤ (∑ i ∈ s, a i * δ i ^ (-σ)) * θ ^ σ := by
  set p : ℝ := 1 + σ with hp
  set q : ℝ := (1 + σ) / σ with hq
  have hp1 : 1 < p := by linarith
  have hp0 : 0 < p := by linarith
  have hpq : p.HolderConjugate q := by
    rw [Real.holderConjugate_iff_eq_conjExponent hp1, hp, hq]
    congr 1; ring
  have hqinv : q⁻¹ = σ / p := by rw [hq, hp, inv_div]
  set f : ι → ℝ := fun i => (a i * δ i ^ (-σ)) ^ p⁻¹
  set g : ι → ℝ := fun i => δ i ^ q⁻¹
  have hfg : ∀ i ∈ s, f i * g i = a i ^ p⁻¹ := by
    intro i hi
    have hai := ha i hi; have hdi := hδ i hi
    simp only [f, g]
    rw [Real.mul_rpow hai.le (Real.rpow_nonneg hdi.le _), ← Real.rpow_mul hdi.le, mul_assoc,
      ← Real.rpow_add hdi, hqinv]
    have : -σ * p⁻¹ + σ / p = 0 := by field_simp; ring
    rw [this, Real.rpow_zero, mul_one]
  have hf : ∀ i ∈ s, 0 ≤ f i := fun i hi =>
    Real.rpow_nonneg (mul_nonneg (ha i hi).le (Real.rpow_nonneg (hδ i hi).le _)) _
  have hg : ∀ i ∈ s, 0 ≤ g i := fun i hi => Real.rpow_nonneg (hδ i hi).le _
  have hH := Real.inner_le_Lp_mul_Lq_of_nonneg s hpq hf hg
  have hfp : ∀ i ∈ s, f i ^ p = a i * δ i ^ (-σ) := fun i hi =>
    Real.rpow_inv_rpow (mul_nonneg (ha i hi).le (Real.rpow_nonneg (hδ i hi).le _)) hp0.ne'
  have hgq : ∀ i ∈ s, g i ^ q = δ i := fun i hi =>
    Real.rpow_inv_rpow (hδ i hi).le (by rw [hq]; positivity)
  rw [Finset.sum_congr rfl hfg, Finset.sum_congr rfl hfp, Finset.sum_congr rfl hgq] at hH
  set V := ∑ i ∈ s, a i * δ i ^ (-σ)
  set S := ∑ i ∈ s, a i ^ p⁻¹
  set D := ∑ i ∈ s, δ i
  have hV : 0 ≤ V := Finset.sum_nonneg fun i hi =>
    mul_nonneg (ha i hi).le (Real.rpow_nonneg (hδ i hi).le _)
  have hS : 0 ≤ S := Finset.sum_nonneg fun i hi => Real.rpow_nonneg (ha i hi).le _
  have hD : 0 ≤ D := Finset.sum_nonneg fun i hi => (hδ i hi).le
  have h1 : S ≤ V ^ p⁻¹ * θ ^ (σ / p) := by
    refine hH.trans ?_
    rw [one_div, one_div, hqinv]
    exact mul_le_mul_of_nonneg_left
      (Real.rpow_le_rpow hD hsum (by positivity)) (Real.rpow_nonneg hV _)
  calc S ^ p ≤ (V ^ p⁻¹ * θ ^ (σ / p)) ^ p := Real.rpow_le_rpow hS h1 hp0.le
    _ = V * θ ^ σ := by
        rw [Real.mul_rpow (Real.rpow_nonneg hV _) (Real.rpow_nonneg hθ.le _),
          Real.rpow_inv_rpow hV hp0.ne', ← Real.rpow_mul hθ.le]
        congr 2; field_simp

/-- **Rényi law, attainment.** -/
theorem renyi_attain (s : Finset ι) (a : ι → ℝ) {σ θ : ℝ} (hσ : 0 < σ)
    (ha : ∀ i ∈ s, 0 < a i) (hθ : 0 < θ) (hne : s.Nonempty) :
    let S := ∑ i ∈ s, a i ^ (1 + σ)⁻¹
    (∑ i ∈ s, θ * a i ^ (1 + σ)⁻¹ / S) = θ ∧
      (∑ i ∈ s, a i * (θ * a i ^ (1 + σ)⁻¹ / S) ^ (-σ)) * θ ^ σ = S ^ (1 + σ) := by
  intro S
  have hS : 0 < S := Finset.sum_pos (fun i hi => Real.rpow_pos_of_pos (ha i hi) _) hne
  refine ⟨?_, ?_⟩
  · rw [← Finset.sum_div, ← Finset.mul_sum, mul_div_assoc, div_self hS.ne', mul_one]
  · have hterm : ∀ i ∈ s, a i * (θ * a i ^ (1 + σ)⁻¹ / S) ^ (-σ)
        = θ ^ (-σ) * S ^ σ * a i ^ (1 + σ)⁻¹ := by
      intro i hi
      have hai := ha i hi
      have hai' : 0 < a i ^ (1 + σ)⁻¹ := Real.rpow_pos_of_pos hai _
      rw [Real.div_rpow (by positivity) hS.le, Real.mul_rpow hθ.le hai'.le,
        ← Real.rpow_mul hai.le, Real.rpow_neg hS.le, div_inv_eq_mul]
      have e2 : a i * a i ^ ((1 + σ)⁻¹ * -σ) = a i ^ (1 + σ)⁻¹ := by
        have h := Real.rpow_add hai 1 ((1 + σ)⁻¹ * -σ)
        rw [Real.rpow_one] at h
        rw [← h]; congr 1; field_simp; ring
      calc a i * (θ ^ (-σ) * a i ^ ((1 + σ)⁻¹ * -σ) * S ^ σ)
          = θ ^ (-σ) * S ^ σ * (a i * a i ^ ((1 + σ)⁻¹ * -σ)) := by ring
        _ = θ ^ (-σ) * S ^ σ * a i ^ (1 + σ)⁻¹ := by rw [e2]
    rw [Finset.sum_congr rfl hterm, ← Finset.mul_sum]
    rw [show θ ^ (-σ) * S ^ σ * S * θ ^ σ = (θ ^ (-σ) * θ ^ σ) * (S ^ σ * S) by ring,
      ← Real.rpow_add hθ, neg_add_cancel, Real.rpow_zero, one_mul]
    conv_lhs => rw [show S ^ σ * S = S ^ σ * S ^ (1 : ℝ) by rw [Real.rpow_one]]
    rw [← Real.rpow_add hS, add_comm]

end BLLM

namespace BLLM

/-- **Polynomial checks along an infinite run.** A schedule `δ` with `∑ δ < ∞` and
`∑ a δ ^ (-σ) < ∞` exists exactly when `∑ a ^ (1/(1+σ)) < ∞`. -/
theorem poly_schedule_iff (a : ℕ → ℝ) {σ : ℝ} (hσ : 0 < σ) (ha : ∀ n, 0 < a n) :
    (∃ δ : ℕ → ℝ, (∀ n, 0 < δ n) ∧ Summable δ ∧ Summable fun n => a n * δ n ^ (-σ)) ↔
      Summable fun n => a n ^ (1 + σ)⁻¹ := by
  constructor
  · rintro ⟨δ, hδ, hD, hV⟩
    set θ := (∑' n, δ n) + 1
    have hθ : 0 < θ := by
      have : (0:ℝ) ≤ ∑' n, δ n := tsum_nonneg fun n => (hδ n).le
      linarith
    have hpos : 0 < 1 + σ := by linarith
    refine summable_of_sum_range_le (c := ((∑' n, a n * δ n ^ (-σ)) * θ ^ σ) ^ (1 + σ)⁻¹)
      (fun n => Real.rpow_nonneg (ha n).le _) (fun N => ?_)
    have hN := renyi_lower (Finset.range N) a δ hσ (fun i _ => ha i) (fun i _ => hδ i) hθ
      (by
        have := hD.sum_le_tsum (Finset.range N) (fun i _ => (hδ i).le)
        linarith)
    have hS : 0 ≤ ∑ i ∈ Finset.range N, a i ^ (1 + σ)⁻¹ :=
      Finset.sum_nonneg fun i _ => Real.rpow_nonneg (ha i).le _
    have hVN : ∑ i ∈ Finset.range N, a i * δ i ^ (-σ) ≤ ∑' n, a n * δ n ^ (-σ) :=
      hV.sum_le_tsum _ (fun i _ => mul_nonneg (ha i).le (Real.rpow_nonneg (hδ i).le _))
    have h2 : (∑ i ∈ Finset.range N, a i ^ (1 + σ)⁻¹) ^ (1 + σ)
        ≤ (∑' n, a n * δ n ^ (-σ)) * θ ^ σ :=
      hN.trans (mul_le_mul_of_nonneg_right hVN (Real.rpow_nonneg hθ.le _))
    have h3 := Real.rpow_le_rpow (Real.rpow_nonneg hS _) h2 (inv_nonneg.2 hpos.le)
    rwa [← Real.rpow_mul hS, mul_inv_cancel₀ hpos.ne', Real.rpow_one] at h3
  · intro hS
    refine ⟨fun n => a n ^ (1 + σ)⁻¹, fun n => Real.rpow_pos_of_pos (ha n) _, hS, ?_⟩
    refine hS.congr fun n => ?_
    have h := Real.rpow_add (ha n) 1 ((1 + σ)⁻¹ * -σ)
    rw [Real.rpow_one] at h
    rw [← Real.rpow_mul (ha n).le, ← h]
    congr 1
    have : (1 + σ) ≠ 0 := by linarith
    field_simp; ring

end BLLM
