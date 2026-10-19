import BLLM.Basic
import BLLM.EntropyLaw

/-!
# Subagents and cascades

A coordinator splits the candidates into groups, one for each subagent. The chain rule of
the entropy splits the cost of soundness into the cost of the split and the costs inside the
groups, the split of the budget in proportion to the group totals is optimal, and with that
split every subagent computes the flat optimal schedule from its own costs and one number.

A cascade runs `r` cheap weak checks of cost `b` and soundness `ε` before one exact strong
check of cost `c`. With a fraction `ρ` of incorrect candidates, the weak runs cost `b r` and the
strong check is reached by an incorrect candidate with probability at most `ε ^ r`.
-/

open Real Finset

namespace BLLM

variable {ι κ : Type*} [DecidableEq κ]

/-- The total cost of the group `k`. -/
noncomputable def groupCost (s : Finset ι) (g : ι → κ) (a : ι → ℝ) (k : κ) : ℝ :=
  ∑ i ∈ s.filter (fun i => g i = k), a i

theorem groupCost_pos (s : Finset ι) (g : ι → κ) (a : ι → ℝ) (ha : ∀ i ∈ s, 0 < a i)
    {k : κ} (hk : k ∈ s.image g) : 0 < groupCost s g a k := by
  obtain ⟨i, hi, rfl⟩ := Finset.mem_image.1 hk
  exact Finset.sum_pos (fun j hj => ha j (Finset.mem_filter.1 hj).1)
    ⟨i, Finset.mem_filter.2 ⟨hi, rfl⟩⟩

theorem groupCost_sum (s : Finset ι) (g : ι → κ) (a : ι → ℝ) :
    ∑ k ∈ s.image g, groupCost s g a k = ∑ i ∈ s, a i := by
  unfold groupCost
  exact Finset.sum_fiberwise_of_maps_to (fun i hi => Finset.mem_image_of_mem g hi) a

/-- **Chain rule.** `∑ a log (A / a) = ∑_k A_k log (A / A_k) + ∑_k ∑_{i ∈ k} a i log (A_k / a i)`. -/
theorem chain_rule (s : Finset ι) (g : ι → κ) (a : ι → ℝ) (ha : ∀ i ∈ s, 0 < a i) :
    ∑ i ∈ s, a i * Real.log ((∑ j ∈ s, a j) / a i)
      = ∑ k ∈ s.image g, groupCost s g a k * Real.log ((∑ j ∈ s, a j) / groupCost s g a k)
        + ∑ k ∈ s.image g, ∑ i ∈ s.filter (fun i => g i = k),
            a i * Real.log (groupCost s g a k / a i) := by
  rw [← Finset.sum_add_distrib,
    ← Finset.sum_fiberwise_of_maps_to (fun i hi => Finset.mem_image_of_mem g hi)]
  refine Finset.sum_congr rfl fun k hk => ?_
  have hAk := groupCost_pos s g a ha hk
  have hA : 0 < ∑ j ∈ s, a j := by
    rw [← groupCost_sum s g a]
    exact Finset.sum_pos (fun k hk => groupCost_pos s g a ha hk) ⟨k, hk⟩
  have hfun : ∀ i ∈ s.filter (fun i => g i = k),
      a i * Real.log ((∑ j ∈ s, a j) / a i)
        = a i * Real.log ((∑ j ∈ s, a j) / groupCost s g a k)
          + a i * Real.log (groupCost s g a k / a i) := by
    intro i hi
    have hai := ha i (Finset.mem_filter.1 hi).1
    rw [← mul_add, ← Real.log_mul (by positivity) (by positivity)]
    congr 2; field_simp
  rw [Finset.sum_congr rfl hfun, Finset.sum_add_distrib, ← Finset.sum_mul]
  rfl

/-- **Splitting the budget.** Whatever budgets `θ_k > 0` with `∑ θ_k ≤ θ` the coordinator hands
to the groups, the sum of the entropy lower bounds of the groups is at least the entropy lower
bound of the whole profile at budget `θ`. -/
theorem split_lower (s : Finset ι) (g : ι → κ) (a : ι → ℝ) (θk : κ → ℝ) {θ : ℝ}
    (ha : ∀ i ∈ s, 0 < a i) (hθk : ∀ k ∈ s.image g, 0 < θk k) (hθ : 0 < θ)
    (hsum : ∑ k ∈ s.image g, θk k ≤ θ) :
    ∑ i ∈ s, a i * Real.log ((∑ j ∈ s, a j) / a i) + (∑ j ∈ s, a j) * Real.log (1 / θ)
      ≤ ∑ k ∈ s.image g, (∑ i ∈ s.filter (fun i => g i = k),
            a i * Real.log (groupCost s g a k / a i)
          + groupCost s g a k * Real.log (1 / θk k)) := by
  have h := entropy_lower (s.image g) (groupCost s g a) θk
    (fun k hk => groupCost_pos s g a ha hk) hθk hθ hsum
  rw [groupCost_sum] at h
  rw [chain_rule s g a ha, Finset.sum_add_distrib]
  linarith

/-- **Proportional split.** With budget `θ A_k / A`, the optimal schedule of a group computed from
the group alone is the optimal schedule of the whole profile. -/
theorem proportional_split (s : Finset ι) (g : ι → κ) (a : ι → ℝ) (ε θ : ℝ) (k : κ) (i : ι)
    (hA : 0 < ∑ j ∈ s, a j) (hAk : 0 < groupCost s g a k) (hθ : 0 < θ) (hai : 0 < a i) :
    ceilSchedule (s.filter (fun i => g i = k)) a ε
        (θ * groupCost s g a k / ∑ j ∈ s, a j) i
      = ceilSchedule s a ε θ i := by
  unfold ceilSchedule
  have e : (∑ j ∈ s.filter (fun i => g i = k), a j)
      / ((θ * groupCost s g a k / ∑ j ∈ s, a j) * a i)
      = (∑ j ∈ s, a j) / (θ * a i) := by
    change groupCost s g a k / ((θ * groupCost s g a k / ∑ j ∈ s, a j) * a i) = _
    field_simp
  rw [e]

/-- **Weak before strong, lower bound.** For every number `r` of weak runs,
`b r + c ρ ε ^ r ≥ (b / L) (1 + log (c ρ L / b))` with `L = log (1/ε)`. -/
theorem cascade_lower {b c ρ ε : ℝ} (hb : 0 < b) (hc : 0 < c) (hρ : 0 < ρ)
    (hε0 : 0 < ε) (hε1 : ε < 1) (r : ℕ) :
    b / Real.log (1 / ε) * (1 + Real.log (c * ρ * Real.log (1 / ε) / b))
      ≤ b * r + c * ρ * ε ^ r := by
  have hL := log_inv_pos hε0 hε1
  have hy : 0 < c * ρ * ε ^ r := by positivity
  have hlogε : Real.log ε = - Real.log (1 / ε) := by
    rw [one_div, Real.log_inv]; ring
  have hly : Real.log (c * ρ * ε ^ r) = Real.log (c * ρ) - r * Real.log (1 / ε) := by
    rw [Real.log_mul (by positivity) (by positivity), Real.log_pow, hlogε]; ring
  have key := Real.log_le_sub_one_of_pos
    (show 0 < c * ρ * ε ^ r * Real.log (1 / ε) / b by positivity)
  have e1 : Real.log (c * ρ * ε ^ r * Real.log (1 / ε) / b)
      = Real.log (c * ρ * ε ^ r) + Real.log (Real.log (1 / ε)) - Real.log b := by
    rw [Real.log_div (by positivity) hb.ne', Real.log_mul hy.ne' hL.ne']
  have e2 : Real.log (c * ρ * Real.log (1 / ε) / b)
      = Real.log (c * ρ) + Real.log (Real.log (1 / ε)) - Real.log b := by
    rw [Real.log_div (by positivity) hb.ne', Real.log_mul (by positivity) hL.ne']
  rw [e1, hly] at key
  rw [e2]
  have h3 : b / Real.log (1 / ε) * (c * ρ * ε ^ r * Real.log (1 / ε) / b) = c * ρ * ε ^ r := by
    field_simp
  have h4 : b / Real.log (1 / ε) * (Real.log (c * ρ) - r * Real.log (1 / ε)
        + Real.log (Real.log (1 / ε)) - Real.log b + 1)
      ≤ b / Real.log (1 / ε) * (c * ρ * ε ^ r * Real.log (1 / ε) / b) :=
    mul_le_mul_of_nonneg_left (by linarith) (by positivity)
  have h5 : b / Real.log (1 / ε) * (Real.log (c * ρ) - r * Real.log (1 / ε)
        + Real.log (Real.log (1 / ε)) - Real.log b + 1)
      = b / Real.log (1 / ε) * (1 + (Real.log (c * ρ) + Real.log (Real.log (1 / ε))
          - Real.log b)) - b * r := by
    field_simp; ring
  linarith

/-- **Weak before strong, upper bound.** If `b ≤ c ρ L`, the cascade with
`r = ⌈log (c ρ L / b) / L⌉` weak runs costs at most `(b / L) (1 + log (c ρ L / b)) + b`. -/
theorem cascade_upper {b c ρ ε : ℝ} (hb : 0 < b) (hc : 0 < c) (hρ : 0 < ρ)
    (hε0 : 0 < ε) (hε1 : ε < 1) (hbig : b ≤ c * ρ * Real.log (1 / ε)) :
    b * ⌈Real.log (c * ρ * Real.log (1 / ε) / b) / Real.log (1 / ε)⌉₊
        + c * ρ * ε ^ ⌈Real.log (c * ρ * Real.log (1 / ε) / b) / Real.log (1 / ε)⌉₊
      ≤ b / Real.log (1 / ε) * (1 + Real.log (c * ρ * Real.log (1 / ε) / b)) + b := by
  have hL := log_inv_pos hε0 hε1
  set x := Real.log (c * ρ * Real.log (1 / ε) / b) / Real.log (1 / ε) with hx
  set n := ⌈x⌉₊ with hn
  have hq : 1 ≤ c * ρ * Real.log (1 / ε) / b := by rw [le_div_iff₀ hb, one_mul]; exact hbig
  have hx0 : 0 ≤ x := div_nonneg (Real.log_nonneg hq) hL.le
  have hn1 : (n : ℝ) < x + 1 := Nat.ceil_lt_add_one hx0
  have hn0 : x ≤ n := Nat.le_ceil x
  have hlogε : Real.log ε = - Real.log (1 / ε) := by
    rw [one_div, Real.log_inv]; ring
  have hpow : ε ^ n ≤ b / (c * ρ * Real.log (1 / ε)) := by
    rw [← Real.log_le_log_iff (pow_pos hε0 _) (by positivity), Real.log_pow, hlogε,
      Real.log_div hb.ne' (by positivity)]
    have hxl : x * Real.log (1 / ε) = Real.log (c * ρ * Real.log (1 / ε) / b) := by
      rw [hx]; field_simp
    rw [Real.log_div (by positivity) hb.ne'] at hxl
    nlinarith [mul_le_mul_of_nonneg_right hn0 hL.le]
  have h1 : c * ρ * ε ^ n ≤ b / Real.log (1 / ε) := by
    calc c * ρ * ε ^ n ≤ c * ρ * (b / (c * ρ * Real.log (1 / ε))) :=
          mul_le_mul_of_nonneg_left hpow (by positivity)
      _ = b / Real.log (1 / ε) := by field_simp
  have h2 : b * n ≤ b * (x + 1) := mul_le_mul_of_nonneg_left hn1.le hb.le
  have h3 : b * (x + 1) = b / Real.log (1 / ε) * Real.log (c * ρ * Real.log (1 / ε) / b) + b := by
    rw [hx]; field_simp
  have h4 : b / Real.log (1 / ε) * (1 + Real.log (c * ρ * Real.log (1 / ε) / b))
      = b / Real.log (1 / ε) + b / Real.log (1 / ε) * Real.log (c * ρ * Real.log (1 / ε) / b) := by
    ring
  linarith

end BLLM
