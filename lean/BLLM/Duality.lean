import Mathlib

/-!
# The duality criterion for sound infinite schedules

A check run at error level `δ ∈ (0,1]` costs `a κ(δ)` with `κ ≥ 0`. Put
`ψ(u) = inf_{0<δ≤1} (κ δ + u δ)`. A schedule with `∑ δ < ∞` and `∑ a κ(δ) < ∞` exists exactly
when `∑ a ψ(λ / a) < ∞` for some `λ > 0`, and then this holds for every `λ > 0`.
-/

open Real Set

namespace BLLM

/-- The dual cost `ψ(u) = inf_{0<δ≤1} (κ δ + u δ)`. -/
noncomputable def dualCost (κ : ℝ → ℝ) (u : ℝ) : ℝ :=
  ⨅ δ : Ioc (0 : ℝ) 1, κ δ + u * δ

theorem dualCost_nonneg (κ : ℝ → ℝ) (hκ : ∀ δ, 0 ≤ κ δ) {u : ℝ} (hu : 0 ≤ u) :
    0 ≤ dualCost κ u := by
  have : Nonempty (Ioc (0 : ℝ) 1) := ⟨⟨1, by norm_num, le_rfl⟩⟩
  exact le_ciInf fun δ => add_nonneg (hκ δ) (mul_nonneg hu δ.2.1.le)

theorem dualCost_le (κ : ℝ → ℝ) (hκ : ∀ δ, 0 ≤ κ δ) {u : ℝ} (hu : 0 ≤ u)
    (δ : Ioc (0 : ℝ) 1) : dualCost κ u ≤ κ δ + u * δ :=
  ciInf_le ⟨0, by rintro _ ⟨d, rfl⟩; exact add_nonneg (hκ d) (mul_nonneg hu d.2.1.le)⟩ δ

/-- Necessity, for every `λ > 0`. -/
theorem dual_summable_of_schedule (κ : ℝ → ℝ) (hκ : ∀ δ, 0 ≤ κ δ) (a : ℕ → ℝ)
    (ha : ∀ n, 0 < a n) (δ : ℕ → ℝ) (hδ : ∀ n, δ n ∈ Ioc (0 : ℝ) 1) (hD : Summable δ)
    (hV : Summable fun n => a n * κ (δ n)) {lam : ℝ} (hlam : 0 < lam) :
    Summable fun n => a n * dualCost κ (lam / a n) := by
  refine Summable.of_nonneg_of_le
    (fun n => mul_nonneg (ha n).le (dualCost_nonneg κ hκ (div_pos hlam (ha n)).le))
    (fun n => ?_) (hV.add (hD.mul_left lam))
  have h := dualCost_le κ hκ (div_pos hlam (ha n)).le ⟨δ n, hδ n⟩
  have h2 := mul_le_mul_of_nonneg_left h (ha n).le
  calc a n * dualCost κ (lam / a n) ≤ a n * (κ (δ n) + lam / a n * δ n) := h2
    _ = a n * κ (δ n) + lam * δ n := by have := (ha n).ne'; field_simp

/-- Sufficiency, from a single `λ > 0`. -/
theorem schedule_of_dual_summable (κ : ℝ → ℝ) (hκ : ∀ δ, 0 ≤ κ δ) (a : ℕ → ℝ)
    (ha : ∀ n, 0 < a n) {lam : ℝ} (hlam : 0 < lam)
    (hψ : Summable fun n => a n * dualCost κ (lam / a n)) :
    ∃ δ : ℕ → ℝ, (∀ n, δ n ∈ Ioc (0 : ℝ) 1) ∧ Summable δ ∧
      Summable fun n => a n * κ (δ n) := by
  have : Nonempty (Ioc (0 : ℝ) 1) := ⟨⟨1, by norm_num, le_rfl⟩⟩
  have hex : ∀ n, ∃ d : Ioc (0 : ℝ) 1,
      κ d + lam / a n * d < dualCost κ (lam / a n) + (1 / 2) ^ n / a n := by
    intro n
    have hlt : dualCost κ (lam / a n) < dualCost κ (lam / a n) + (1 / 2) ^ n / a n := by
      have : 0 < (1 / 2 : ℝ) ^ n / a n := by have := ha n; positivity
      linarith
    exact exists_lt_of_ciInf_lt hlt
  choose d hd using hex
  have hbound : ∀ n, a n * κ (d n) + lam * d n
      ≤ a n * dualCost κ (lam / a n) + (1 / 2) ^ n := by
    intro n
    have h := mul_le_mul_of_nonneg_left (hd n).le (ha n).le
    have e1 : a n * (κ (d n) + lam / a n * d n) = a n * κ (d n) + lam * d n := by
      have := (ha n).ne'; field_simp
    have e2 : a n * (dualCost κ (lam / a n) + (1 / 2) ^ n / a n)
        = a n * dualCost κ (lam / a n) + (1 / 2) ^ n := by
      have := (ha n).ne'; field_simp
    rw [e1, e2] at h; exact h
  have hsum : Summable fun n => a n * dualCost κ (lam / a n) + (1 / 2 : ℝ) ^ n :=
    hψ.add (summable_geometric_of_lt_one (by norm_num) (by norm_num))
  refine ⟨fun n => d n, fun n => (d n).2, ?_, ?_⟩
  · have : Summable fun n => lam * (d n : ℝ) :=
      Summable.of_nonneg_of_le (fun n => mul_nonneg hlam.le (d n).2.1.le)
        (fun n => by have := mul_nonneg (ha n).le (hκ (d n)); linarith [hbound n]) hsum
    simpa [hlam.ne'] using this.mul_left lam⁻¹
  · exact Summable.of_nonneg_of_le (fun n => mul_nonneg (ha n).le (hκ (d n)))
      (fun n => by have := mul_nonneg hlam.le (d n).2.1.le; linarith [hbound n]) hsum

end BLLM
