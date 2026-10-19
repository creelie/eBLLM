import BLLM.EntropyLaw

/-!
# Towers of verified layers

A tower of depth `n` stacks `n` layers, each acting on the output of the layer below and
each certifying what it passes up with a false-accept budget `β k`. One false accept
anywhere contaminates everything above it, so the budgets share one total `θ`.
The entropy law with unit weights bounds the certification cost of the whole tower below
by `n log (n / θ)`, and the bound grows by at least `log ((n + 1) / θ)` with each layer.
The search cost of every stage stays above the proposer bound, so past a finite depth a
deeper tower costs more than a shallow one, and along an infinite tower whose budgets are
summable the cost of a single stage tends to infinity.
-/

open Real Finset Filter Topology

namespace BLLM

/-- The certification cost of a depth-`n` tower: budgets `β k > 0` with `∑ β k ≤ θ`
force `∑ log (1 / β k) ≥ n log (n / θ)`. -/
theorem tower_cost_lower (n : ℕ) (β : ℕ → ℝ) {θ : ℝ} (hβ : ∀ k ∈ range n, 0 < β k)
    (hθ : 0 < θ) (hsum : ∑ k ∈ range n, β k ≤ θ) :
    n * Real.log (n / θ) ≤ ∑ k ∈ range n, Real.log (1 / β k) := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp
  have h := entropy_lower (range n) (fun _ => (1 : ℝ)) β (fun _ _ => one_pos) hβ hθ hsum
  simp only [sum_const, card_range, nsmul_eq_mul, mul_one, div_one, one_mul] at h
  have hn' : (n : ℝ) ≠ 0 := by exact_mod_cast hn.ne'
  have e : Real.log (n / θ) = Real.log n + Real.log (1 / θ) := by
    rw [Real.log_div hn' hθ.ne', one_div, Real.log_inv]; ring
  rw [e, mul_add]
  simpa [sum_const, card_range] using h

/-- The same bound in checks: a layer certified by `r k` independent checks of soundness
error `ε` has `β k = ε ^ r k`, and the tower needs at least `n log (n / θ) / log (1 / ε)`
checks in all. -/
theorem tower_checks_lower (n : ℕ) (r : ℕ → ℕ) {ε θ : ℝ} (hε0 : 0 < ε) (hε1 : ε < 1)
    (hθ : 0 < θ) (hsum : ∑ k ∈ range n, ε ^ r k ≤ θ) :
    n * Real.log (n / θ) / Real.log (1 / ε) ≤ ∑ k ∈ range n, (r k : ℝ) := by
  have hL := log_inv_pos hε0 hε1
  have h := tower_cost_lower n (fun k => ε ^ r k) (fun k _ => pow_pos hε0 _) hθ hsum
  have e : ∑ k ∈ range n, Real.log (1 / ε ^ r k) = (∑ k ∈ range n, (r k : ℝ)) * Real.log (1 / ε) := by
    rw [sum_mul]; exact sum_congr rfl fun k _ => log_inv_pow ε (r k)
  rw [e] at h
  rw [div_le_iff₀ hL]; exact h

/-- Each layer raises the lower bound by at least `log ((n + 1) / θ)`. -/
theorem tower_increment (n : ℕ) {θ : ℝ} (hθ : 0 < θ) :
    Real.log ((n + 1) / θ) ≤ (n + 1) * Real.log ((n + 1) / θ) - n * Real.log (n / θ) := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · simp
  have hn' : (0 : ℝ) < n := by exact_mod_cast hn
  have hle : Real.log (n / θ) ≤ Real.log ((n + 1) / θ) :=
    Real.log_le_log (div_pos hn' hθ) (div_le_div_of_nonneg_right (by linarith) hθ.le)
  nlinarith [mul_le_mul_of_nonneg_left hle hn'.le]

/-- The increments are unbounded. -/
theorem tower_increment_unbounded {θ : ℝ} (hθ : 0 < θ) :
    Tendsto (fun n : ℕ => Real.log ((n + 1) / θ)) atTop atTop := by
  have h : Tendsto (fun n : ℕ => ((n : ℝ) + 1) / θ) atTop atTop := by
    apply Tendsto.atTop_div_const hθ
    exact tendsto_atTop_add_const_right _ 1 tendsto_natCast_atTop_atTop
  exact Real.tendsto_log_atTop.comp h

/-- **Saturation.** If every stage costs at least `B` to search and a depth-`n` tower at
least `c n log (n / θ)` to certify (`c > 0`, `θ ≤ 1`), then for every cost `T₁` there is a
depth beyond which every tower costs more than `T₁`; in particular more than the
depth-one tower. -/
theorem tower_saturates {B c θ : ℝ} (T₁ : ℝ) (hc : 0 < c) (hθ0 : 0 < θ) (hθ1 : θ ≤ 1)
    (S V : ℕ → ℝ) (hS : ∀ n, B ≤ S n) (hV : ∀ n : ℕ, c * n * Real.log (n / θ) ≤ V n) :
    ∃ N : ℕ, ∀ n ≥ N, T₁ < S n + V n := by
  refine ⟨max 3 (⌈(T₁ - B) / c⌉₊ + 1), fun n hn => ?_⟩
  have h3 : (3 : ℝ) ≤ n := by exact_mod_cast le_trans (le_max_left _ _) hn
  have hN : ((⌈(T₁ - B) / c⌉₊ : ℕ) : ℝ) + 1 ≤ n := by exact_mod_cast le_trans (le_max_right _ _) hn
  have hpos : (0 : ℝ) < n := by linarith
  have hlog1 : 1 ≤ Real.log (n / θ) := by
    have he : Real.exp 1 < 3 := lt_trans Real.exp_one_lt_d9 (by norm_num)
    have hn1 : Real.exp 1 ≤ n / θ := by
      have : (n : ℝ) ≤ n / θ := by rw [le_div_iff₀ hθ0]; nlinarith
      linarith
    rw [← Real.log_exp 1]
    exact Real.log_le_log (Real.exp_pos 1) hn1
  have hcn : c * n ≤ c * n * Real.log (n / θ) := by
    have : 0 ≤ c * n := by positivity
    nlinarith
  have hceil : (T₁ - B) / c < n := by
    have := Nat.le_ceil ((T₁ - B) / c); linarith
  have hT : T₁ - B < c * n := by rwa [div_lt_iff₀ hc, mul_comm] at hceil
  linarith [hS n, hV n]

/-- Along an infinite tower whose budgets are summable, the certification cost of a single
stage tends to infinity. -/
theorem stage_cost_diverges (β : ℕ → ℝ) (hβ : ∀ k, 0 < β k) (hsum : Summable β) :
    Tendsto (fun k => Real.log (1 / β k)) atTop atTop := by
  have h0 : Tendsto β atTop (𝓝[>] 0) :=
    tendsto_nhdsWithin_iff.2 ⟨hsum.tendsto_atTop_zero, Eventually.of_forall hβ⟩
  have hinv : Tendsto (fun k => 1 / β k) atTop atTop := by
    have h := tendsto_inv_nhdsGT_zero.comp h0
    simpa [one_div, Function.comp_def] using h
  exact Real.tendsto_log_atTop.comp hinv

end BLLM
