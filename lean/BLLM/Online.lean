import BLLM.Basic
import BLLM.Singularity

/-!
# The online entropy law

Candidates arrive one at a time and the number of runs of each check is fixed on arrival.
With `S n = a 0 + ⋯ + a n` and `u n = log (S n / a 0)`, the weights
`w n = (a n / S n) / (2 (1 + u n) ^ 2)` have cumCost sums at most one for every sequence of
positive costs, so the schedule `⌈log (1 / (θ w n)) / log (1 / ε)⌉` is sound without any
knowledge of the future. Conversely every sound online schedule gives the doubling sequence
weights at most `1 / (N + 1)` infinitely often.
-/

open Real Finset

namespace BLLM

/-- `1 - s / t ≤ log (t / s)` for `s, t > 0`. -/
theorem ratio_le_log {s t : ℝ} (hs : 0 < s) (ht : 0 < t) :
    1 - s / t ≤ Real.log (t / s) := by
  have h := Real.one_sub_inv_le_log_of_pos (div_pos ht hs)
  rwa [inv_div] at h

/-- One step of the telescoping bound. -/
theorem telescope_step {x y : ℝ} (hx : 0 ≤ x) (hxy : x ≤ y) :
    (y - x) / (1 + y) ^ 2 ≤ 1 / (1 + x) - 1 / (1 + y) := by
  have h1 : 0 < 1 + x := by linarith
  have h2 : 0 < 1 + y := by linarith
  rw [div_sub_div _ _ h1.ne' h2.ne', div_le_div_iff₀ (by positivity) (by positivity)]
  have hd : 0 ≤ y - x := sub_nonneg.2 hxy
  nlinarith [mul_nonneg (mul_nonneg hd hd) h2.le]

/-- The telescoping sum `∑ (u (n+1) - u n) / (1 + u (n+1))² ≤ 1 / (1 + u 0) - 1 / (1 + u N)`. -/
theorem telescope_sum (u : ℕ → ℝ) (h0 : 0 ≤ u 0) (hmono : Monotone u) (N : ℕ) :
    ∑ n ∈ range N, (u (n + 1) - u n) / (1 + u (n + 1)) ^ 2
      ≤ 1 / (1 + u 0) - 1 / (1 + u N) := by
  induction N with
  | zero => simp
  | succ N ih =>
    rw [sum_range_succ]
    have := telescope_step (le_trans h0 (hmono (Nat.zero_le N))) (hmono (Nat.le_succ N))
    linarith

/-- Partial sums of the costs. -/
noncomputable def cumCost (a : ℕ → ℝ) (n : ℕ) : ℝ := ∑ k ∈ range (n + 1), a k

/-- The online weight of the `n`-th candidate. -/
noncomputable def onlineWeight (a : ℕ → ℝ) (n : ℕ) : ℝ :=
  (a n / cumCost a n) / (2 * (1 + Real.log (cumCost a n / a 0)) ^ 2)

theorem cumCost_pos (a : ℕ → ℝ) (ha : ∀ n, 0 < a n) (n : ℕ) : 0 < cumCost a n :=
  sum_pos (fun k _ => ha k) nonempty_range_add_one

theorem cumCost_succ (a : ℕ → ℝ) (n : ℕ) : cumCost a (n + 1) = cumCost a n + a (n + 1) := by
  unfold cumCost; rw [sum_range_succ]

theorem cumCost_mono (a : ℕ → ℝ) (ha : ∀ n, 0 < a n) : Monotone (cumCost a) :=
  monotone_nat_of_le_succ fun n => by rw [cumCost_succ]; linarith [ha (n + 1)]

theorem a0_le_cumCost (a : ℕ → ℝ) (ha : ∀ n, 0 < a n) (n : ℕ) : a 0 ≤ cumCost a n := by
  have := cumCost_mono a ha (Nat.zero_le n)
  simpa [cumCost] using this

/-- Soundness of the online weights: their partial sums never exceed one. -/
theorem onlineWeight_sum_le (a : ℕ → ℝ) (ha : ∀ n, 0 < a n) (N : ℕ) :
    ∑ n ∈ range N, onlineWeight a n ≤ 1 := by
  set u : ℕ → ℝ := fun n => Real.log (cumCost a n / a 0) with hu
  have hS := cumCost_pos a ha
  have hu0 : u 0 = 0 := by simp [hu, cumCost, (ha 0).ne']
  have humono : Monotone u := fun m n hmn => by
    apply Real.log_le_log (div_pos (hS m) (ha 0))
    exact div_le_div_of_nonneg_right (cumCost_mono a ha hmn) (ha 0).le
  have hunn : ∀ n, 0 ≤ u n := fun n => hu0 ▸ humono (Nat.zero_le n)
  have hstep : ∀ n, onlineWeight a (n + 1) ≤
      (1 / 2) * ((u (n + 1) - u n) / (1 + u (n + 1)) ^ 2) := by
    intro n
    have hdiff : u (n + 1) - u n = Real.log (cumCost a (n + 1) / cumCost a n) := by
      simp only [hu]
      rw [← Real.log_div (div_pos (hS _) (ha 0)).ne' (div_pos (hS _) (ha 0)).ne']
      congr 1; field_simp [(hS n).ne', (ha 0).ne']
    have hfrac : a (n + 1) / cumCost a (n + 1) = 1 - cumCost a n / cumCost a (n + 1) := by
      rw [cumCost_succ]; field_simp [(by rw [← cumCost_succ]; exact (hS (n + 1)).ne' :
        cumCost a n + a (n + 1) ≠ 0)]; ring
    have hle : a (n + 1) / cumCost a (n + 1) ≤ u (n + 1) - u n := by
      rw [hfrac, hdiff]; exact ratio_le_log (hS n) (hS (n + 1))
    have hpos : 0 < 2 * (1 + u (n + 1)) ^ 2 := by have := hunn (n + 1); positivity
    unfold onlineWeight
    rw [show (1 / 2) * ((u (n + 1) - u n) / (1 + u (n + 1)) ^ 2) =
      (u (n + 1) - u n) / (2 * (1 + u (n + 1)) ^ 2) by field_simp]
    exact div_le_div_of_nonneg_right hle hpos.le
  cases N with
  | zero => simp
  | succ N =>
    rw [sum_range_succ']
    have hw0 : onlineWeight a 0 = 1 / 2 := by
      unfold onlineWeight; simp [cumCost, (ha 0).ne']
    have hsum : ∑ n ∈ range N, onlineWeight a (n + 1) ≤
        (1 / 2) * ∑ n ∈ range N, (u (n + 1) - u n) / (1 + u (n + 1)) ^ 2 := by
      rw [mul_sum]; exact sum_le_sum fun n _ => hstep n
    have ht := telescope_sum u (hunn 0) humono N
    have hN : 0 ≤ (1 + u N)⁻¹ := by have := hunn N; positivity
    rw [hu0] at ht
    norm_num at ht
    linarith

/-- The online schedule. -/
noncomputable def onlineSchedule (a : ℕ → ℝ) (ε θ : ℝ) : ℕ → ℕ :=
  costSchedule (fun n => θ * onlineWeight a n) ε

theorem onlineWeight_pos (a : ℕ → ℝ) (ha : ∀ n, 0 < a n) (n : ℕ) : 0 < onlineWeight a n := by
  unfold onlineWeight
  have hS := cumCost_pos a ha n
  have hl : 0 ≤ Real.log (cumCost a n / a 0) :=
    Real.log_nonneg (by rw [le_div_iff₀ (ha 0), one_mul]; exact a0_le_cumCost a ha n)
  apply div_pos (div_pos (ha n) hS)
  apply mul_pos two_pos
  apply pow_pos
  linarith

/-- The online schedule is sound for every sequence of positive costs and every horizon. -/
theorem onlineSchedule_sound (a : ℕ → ℝ) {ε θ : ℝ} (ha : ∀ n, 0 < a n)
    (hε0 : 0 < ε) (hε1 : ε < 1) (hθ : 0 < θ) (N : ℕ) :
    ∑ n ∈ range N, ε ^ onlineSchedule a ε θ n ≤ θ := by
  have hpos : ∀ n, 0 < θ * onlineWeight a n := fun n => mul_pos hθ (onlineWeight_pos a ha n)
  calc ∑ n ∈ range N, ε ^ onlineSchedule a ε θ n
      ≤ ∑ n ∈ range N, θ * onlineWeight a n :=
        sum_le_sum fun n _ => costSchedule_pow_le _ hpos hε0 hε1 n
    _ = θ * ∑ n ∈ range N, onlineWeight a n := by rw [mul_sum]
    _ ≤ θ * 1 := mul_le_mul_of_nonneg_left (onlineWeight_sum_le a ha N) hθ.le
    _ = θ := mul_one θ

/-- Weights with bounded partial sums are at most `1 / (N + 1)` infinitely often. -/
theorem small_weight_often (w : ℕ → ℝ) (hw : ∀ n, 0 ≤ w n)
    (hsum : ∀ N, ∑ n ∈ range N, w n ≤ 1) (M : ℕ) :
    ∃ N, M ≤ N ∧ w N ≤ 1 / ((N : ℝ) + 1) := by
  by_contra h
  simp only [not_exists, not_and, not_le] at h
  have hs : Summable w := summable_of_sum_range_le hw hsum
  have hsM : Summable fun n => w (n + M) := (summable_nat_add_iff M).mpr hs
  set g : ℕ → ℝ := fun k => 1 / ((k : ℝ) + 1) with hgdef
  have hg : Summable (fun n => g (n + M)) := by
    refine Summable.of_nonneg_of_le (fun n => ?_) (fun n => ?_) hsM
    · simp only [hgdef]; positivity
    · exact (h (n + M) (Nat.le_add_left M n)).le
  have hg' : Summable g := (summable_nat_add_iff M).mp hg
  have hh : Summable (fun n : ℕ => (fun k : ℕ => 1 / (k : ℝ)) (n + 1)) := by
    refine hg'.congr (fun n => ?_)
    simp only [hgdef]; push_cast; ring
  exact Real.not_summable_one_div_natCast ((summable_nat_add_iff 1).mp hh)

/-- The price of not knowing the future: every sound online schedule spends at least
`log ((N + 1) / θ)` on a candidate, measured in units of `log (1/ε)`, infinitely often. -/
theorem online_lower {ε θ : ℝ} (hε0 : 0 < ε) (_hε1 : ε < 1) (hθ : 0 < θ) (r : ℕ → ℕ)
    (hsound : ∀ N, ∑ n ∈ range N, ε ^ r n ≤ θ) (M : ℕ) :
    ∃ N, M ≤ N ∧ Real.log (((N : ℝ) + 1) / θ) ≤ r N * Real.log (1 / ε) := by
  obtain ⟨N, hMN, hN⟩ := small_weight_often (fun n => ε ^ r n / θ)
    (fun n => by positivity)
    (fun N => by rw [← sum_div, div_le_one hθ]; exact hsound N) M
  refine ⟨N, hMN, ?_⟩
  have hpow : ε ^ r N ≤ θ / ((N : ℝ) + 1) := by
    rw [div_le_iff₀ hθ] at hN
    rw [le_div_iff₀ (by positivity)]
    calc ε ^ r N * ((N : ℝ) + 1) ≤ 1 / ((N : ℝ) + 1) * θ * ((N : ℝ) + 1) := by
          gcongr
      _ = θ := by field_simp
  have hlog := Real.log_le_log (pow_pos hε0 _) hpow
  have e1 : Real.log (ε ^ r N) = - (r N * Real.log (1 / ε)) := by
    rw [Real.log_pow, one_div, Real.log_inv]; ring
  have e2 : Real.log (θ / ((N : ℝ) + 1)) = - Real.log (((N : ℝ) + 1) / θ) := by
    rw [← Real.log_inv, inv_div]
  linarith

/-- The entropy of the doubling profile: `∑_{k<N} (k+1) / 2^(k+1) = 2 - (N+2) / 2^N`. -/
theorem doubling_sum (N : ℕ) :
    ∑ k ∈ range N, ((k : ℝ) + 1) / 2 ^ (k + 1) = 2 - ((N : ℝ) + 2) / 2 ^ N := by
  induction N with
  | zero => norm_num
  | succ N ih =>
    rw [sum_range_succ, ih]; push_cast; field_simp; ring

end BLLM
