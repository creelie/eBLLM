/-!
# Sand-tile toppling (Section 10 of the VSI paper)

Two sites joined by one edge.  A site whose height exceeds `θ` topples: it loses `Δ` and its
neighbour gains `share` (`share = Δ` is the conservative case, `share < Δ` absorbs the rest
into the residue ledger).  The lowest unstable site topples first.  Heights are integers in a
common unit, so the counterexamples below are exact.

* Proposition 10.2 says that a finite-energy conservative run on a locally finite graph either
  stabilizes or exposes an infinite dependency path.  `conservative_never_stable` gives a run on a
  finite graph (so with no infinite path) that never stabilizes.
* Theorem 10.4 bounds the number of topplings by `H0 · |Λ| · diam Λ / θ_min`, which is 4 for both
  runs below.  The conservative run never stops, and `dissipative_count` shows a run with
  `Δ ≥ θ_min`, as the paper's proof assumes, that needs 100 topplings.
* `count_bound` is a correct replacement: if every toppling absorbs at least `ε > 0` of burden
  and the total burden stays at least `-B`, then `k` topplings need `k · ε ≤ M₀ + B`.
-/

namespace EBLLM.SandTile

structure Two where
  a : Int
  b : Int
  deriving DecidableEq, Repr

/-- One toppling of the lowest unstable site, or `none` if the configuration is stable. -/
def step (θ Δ share : Int) (s : Two) : Option Two :=
  if s.a > θ then some ⟨s.a - Δ, s.b + share⟩
  else if s.b > θ then some ⟨s.a + share, s.b - Δ⟩
  else none

/-- Topple for at most `fuel` steps: `some (k, s)` if the run is stable after `k` topplings. -/
def run (θ Δ share : Int) : Nat → Two → Option (Nat × Two)
  | 0, s => if step θ Δ share s = none then some (0, s) else none
  | fuel + 1, s =>
    match step θ Δ share s with
    | none => some (0, s)
    | some t => (run θ Δ share fuel t).map (fun p => (p.1 + 1, p.2))

/-- The conservative run, in units of 1/2: heights (1, 1), θ = 1/2, Δ = 1. -/
theorem conservative_cycle :
    step 1 2 2 ⟨2, 2⟩ = some ⟨0, 4⟩ ∧ step 1 2 2 ⟨0, 4⟩ = some ⟨2, 2⟩ := by decide

theorem conservative_never_stable :
    ∀ n, run 1 2 2 n ⟨2, 2⟩ = none ∧ run 1 2 2 n ⟨0, 4⟩ = none := by
  intro n
  induction n with
  | zero => decide
  | succ n ih =>
    constructor
    · show (match step 1 2 2 ⟨2, 2⟩ with
        | none => some (0, ⟨2, 2⟩)
        | some t => (run 1 2 2 n t).map (fun p => (p.1 + 1, p.2))) = none
      rw [conservative_cycle.1]
      simp [ih.2]
    · show (match step 1 2 2 ⟨0, 4⟩ with
        | none => some (0, ⟨0, 4⟩)
        | some t => (run 1 2 2 n t).map (fun p => (p.1 + 1, p.2))) = none
      rw [conservative_cycle.2]
      simp [ih.1]

/-- Burden is conserved by every toppling of the conservative run. -/
theorem conservative_mass (s t : Two) (h : step 1 2 2 s = some t) : t.a + t.b = s.a + s.b := by
  unfold step at h
  split at h
  · cases h; simp; omega
  · split at h
    · cases h; simp; omega
    · cases h

/-- The bound of Theorem 10.4 for these runs: H0 · |Λ| · diam / θ_min = 2 · 2 · 1 / 1 = 4 in
units of 1/2, and 200 · 2 · 1 / 100 = 4 in units of 1/100. -/
theorem bound_is_four : 2 * 2 * 1 / 1 = 4 ∧ 200 * 2 * 1 / 100 = 4 := by decide

/-- The dissipative run, in units of 1/100: heights (2, 2), θ = 1, Δ = 2, share 99/100 of Δ.
It stabilizes at (1, 1) after exactly 100 topplings. -/
theorem dissipative_count : run 100 200 198 200 ⟨200, 200⟩ = some (100, ⟨100, 100⟩) := by decide

/-- A correct bound: a burden sequence that drops by at least `ε` at every toppling and stays
at least `-B` allows at most `(M₀ + B) / ε` topplings. -/
theorem count_bound (m : Nat → Int) (ε B : Int) (k : Nat)
    (hstep : ∀ i, i < k → m (i + 1) ≤ m i - ε) (hlow : -B ≤ m k) :
    k * ε ≤ m 0 + B := by
  have key : ∀ j, j ≤ k → m j ≤ m 0 - j * ε := by
    intro j
    induction j with
    | zero => intro _; simp
    | succ j ih =>
      intro hj
      have h1 := hstep j (by omega)
      have h2 := ih (by omega)
      have e : ((j + 1 : Nat) : Int) * ε = (j : Int) * ε + ε := by
        rw [Int.natCast_add, Int.add_mul, Int.natCast_one, Int.one_mul]
      rw [e]
      generalize (j : Int) * ε = x at h2 ⊢
      omega
  have := key k (Nat.le_refl k)
  generalize (k : Int) * ε = x at this ⊢
  omega

end EBLLM.SandTile
