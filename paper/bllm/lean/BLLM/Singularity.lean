import BLLM.Basic

/-!
# Sound infinite schedules

For costs `0 < a n ≤ 1` with `∑ a n < ∞` and soundness error `0 < ε < 1`, there is a schedule
`r` with `∑ ε ^ r n < ∞` and `∑ a n r n < ∞` exactly when `∑ a n log (1 / a n) < ∞`.
-/

open Real

namespace BLLM

/-- Necessity: a sound schedule of finite total cost forces finite cost entropy. -/
theorem entropy_summable_of_schedule (a : ℕ → ℝ) (r : ℕ → ℕ) {ε : ℝ}
    (ha : ∀ n, 0 < a n) (ha1 : ∀ n, a n ≤ 1) (hε0 : 0 < ε) (hε1 : ε < 1)
    (hF : Summable fun n => ε ^ r n) (hV : Summable fun n => a n * r n) :
    Summable fun n => a n * Real.log (1 / a n) := by
  have hL := log_inv_pos hε0 hε1
  refine Summable.of_nonneg_of_le (fun n => ?_) (fun n => ?_)
    ((hV.mul_left (Real.log (1 / ε))).add hF)
  · apply mul_nonneg (ha n).le
    apply Real.log_nonneg
    rw [le_div_iff₀ (ha n), one_mul]; exact ha1 n
  · have h := gibbs_term (ha n) (pow_pos hε0 (r n))
    rw [log_inv_pow] at h
    have : 0 ≤ a n := (ha n).le
    nlinarith

/-- The schedule `r n = ⌈log (1 / a n) / log (1/ε)⌉₊`, for which `ε ^ r n ≤ a n`. -/
noncomputable def costSchedule (a : ℕ → ℝ) (ε : ℝ) (n : ℕ) : ℕ :=
  ⌈Real.log (1 / a n) / Real.log (1 / ε)⌉₊

theorem costSchedule_pow_le (a : ℕ → ℝ) {ε : ℝ} (ha : ∀ n, 0 < a n)
    (hε0 : 0 < ε) (hε1 : ε < 1) (n : ℕ) : ε ^ costSchedule a ε n ≤ a n := by
  have hL := log_inv_pos hε0 hε1
  have hc : Real.log (1 / a n) / Real.log (1 / ε) ≤ costSchedule a ε n := Nat.le_ceil _
  rw [div_le_iff₀ hL] at hc
  rw [← Real.log_le_log_iff (pow_pos hε0 _) (ha n)]
  have e1 : Real.log (ε ^ costSchedule a ε n) = - ((costSchedule a ε n : ℝ) * Real.log (1 / ε)) := by
    rw [Real.log_pow, one_div, Real.log_inv]; ring
  have e2 : Real.log (a n) = - Real.log (1 / a n) := by
    rw [one_div, Real.log_inv]; ring
  rw [e1, e2]; linarith

/-- Sufficiency: finite cost entropy gives a sound schedule of finite total cost. -/
theorem schedule_of_entropy_summable (a : ℕ → ℝ) {ε : ℝ}
    (ha : ∀ n, 0 < a n) (ha1 : ∀ n, a n ≤ 1) (hε0 : 0 < ε) (hε1 : ε < 1)
    (hA : Summable a) (hH : Summable fun n => a n * Real.log (1 / a n)) :
    Summable (fun n => ε ^ costSchedule a ε n) ∧
      Summable (fun n => a n * costSchedule a ε n) := by
  have hL := log_inv_pos hε0 hε1
  refine ⟨Summable.of_nonneg_of_le (fun n => (pow_pos hε0 _).le)
    (costSchedule_pow_le a ha hε0 hε1) hA, ?_⟩
  refine Summable.of_nonneg_of_le (fun n => mul_nonneg (ha n).le (Nat.cast_nonneg _))
    (fun n => ?_) ((hH.div_const (Real.log (1 / ε))).add hA)
  have hx0 : 0 ≤ Real.log (1 / a n) / Real.log (1 / ε) := by
    apply div_nonneg _ hL.le
    apply Real.log_nonneg
    rw [le_div_iff₀ (ha n), one_mul]; exact ha1 n
  have hc := (Nat.ceil_lt_add_one hx0).le
  calc a n * costSchedule a ε n
      ≤ a n * (Real.log (1 / a n) / Real.log (1 / ε) + 1) :=
        mul_le_mul_of_nonneg_left hc (ha n).le
    _ = a n * Real.log (1 / a n) / Real.log (1 / ε) + a n := by ring

/-- **Sound-schedule criterion.** -/
theorem sound_schedule_iff (a : ℕ → ℝ) {ε : ℝ}
    (ha : ∀ n, 0 < a n) (ha1 : ∀ n, a n ≤ 1) (hε0 : 0 < ε) (hε1 : ε < 1)
    (hA : Summable a) :
    (∃ r : ℕ → ℕ, Summable (fun n => ε ^ r n) ∧ Summable (fun n => a n * r n)) ↔
      Summable fun n => a n * Real.log (1 / a n) := by
  constructor
  · rintro ⟨r, hF, hV⟩; exact entropy_summable_of_schedule a r ha ha1 hε0 hε1 hF hV
  · intro hH; exact ⟨_, schedule_of_entropy_summable a ha ha1 hε0 hε1 hA hH⟩

/-- Shifting a schedule by `k` multiplies the expected false-accept count by `ε ^ k`
and adds `k ∑ a` to the cost; any budget `θ > 0` is reached by a finite shift. -/
theorem shift_schedule (r : ℕ → ℕ) (k : ℕ) {ε : ℝ} :
    (fun n => ε ^ (r n + k)) = fun n => ε ^ k * ε ^ r n := by
  funext n; rw [pow_add, mul_comm]

end BLLM
