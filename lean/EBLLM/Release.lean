/-!
# The release algebra (Sections 2, 3, 6 and 21 of the VSI paper)

`Rel` is the product of the verifier factors.  With factors in `Bool` the product is `List.all`.
The paper's Theorem 2.2 (no visual or machine-learning shortcut), Theorem 3.1 (CMV release
blocking) and Theorem 21.3 (no collapse-free false release) all reduce to `rel_false_of_mem`:
one zero factor blocks release whatever the other factors are.

Corollary 6.4 (debt-monotone release blocking) is true, but not for the reason the paper gives
("every increase in DebtMass corresponds to at least one additional non-PASS terminal vertex",
which fails when only weights change).  The reason is `debt_eq_zero_of_released`: a released
state has no debt at all.
-/

namespace EBLLM

/-- The release product of a list of verifier factors. -/
def rel (fs : List Bool) : Bool := fs.all id

theorem rel_eq_true_iff (fs : List Bool) : rel fs = true ↔ ∀ b ∈ fs, b = true := by
  simp [rel, List.all_eq_true]

/-- One zero factor blocks release (Theorems 2.2, 3.1 and 21.3). -/
theorem rel_false_of_mem {fs : List Bool} (h : false ∈ fs) : rel fs = false := by
  cases hr : rel fs with
  | false => rfl
  | true => exact absurd ((rel_eq_true_iff fs).1 hr false h) (by decide)

/-- Adding or improving other factors cannot release while one factor stays zero. -/
theorem no_shortcut (fs gs hs : List Bool) : rel (fs ++ false :: gs ++ hs) = false :=
  rel_false_of_mem (by simp)

/-- The labels a run may emit. -/
inductive Label
  | theorem_ | counterexample | conditional | independence | candidate | buj | open_
  deriving DecidableEq, Repr

/-- The transition rule of Section 6.1, as implemented in `ebllm.release.emit`. -/
def emit (fs : List Bool) (refutation independence conditional modelOk machinery : Bool) : Label :=
  if rel fs then
    if conditional then .conditional
    else if refutation then .counterexample
    else if independence then .independence
    else .theorem_
  else if modelOk then .candidate
  else if machinery then .open_ else .buj

/-- A theorem or counterexample label is emitted only when every factor is one. -/
theorem released_only_if_all {fs : List Bool} {r i c m k : Bool}
    (h : emit fs r i c m k = .theorem_ ∨ emit fs r i c m k = .counterexample) :
    ∀ b ∈ fs, b = true := by
  apply (rel_eq_true_iff fs).1
  cases hr : rel fs
  · simp only [emit, hr] at h
    cases m <;> cases k <;> simp at h
  · rfl

/-- A terminal leaf of the obligation graph: its weight and whether it passed. -/
structure Leaf where
  weight : Nat
  pass : Bool
  deriving DecidableEq, Repr

/-- Release of a state, read from its terminal leaves (Theorem 6.3). -/
def relLeaves (ls : List Leaf) : Bool := ls.all (·.pass)

/-- DebtMass: the total weight of the leaves that did not pass. -/
def debt : List Leaf → Nat
  | [] => 0
  | l :: ls => (if l.pass then 0 else l.weight) + debt ls

theorem debt_eq_zero_of_released : ∀ {ls : List Leaf}, relLeaves ls = true → debt ls = 0
  | [], _ => rfl
  | l :: ls, h => by
    simp only [relLeaves, List.all_cons, Bool.and_eq_true] at h
    simp [debt, h.1, debt_eq_zero_of_released (ls := ls) h.2]

/-- Corollary 6.4: if `S` carries more debt than `S'`, then `S` is not released, so
`Rel S ≤ Rel S'`. -/
theorem cor_6_4 (S S' : List Leaf) (h : debt S' < debt S) : relLeaves S = false := by
  cases hr : relLeaves S
  · rfl
  · rw [debt_eq_zero_of_released hr] at h
    exact absurd h (Nat.not_lt_zero _)

/-- The paper's reason for Corollary 6.4 is not valid: debt can increase with the same set of
non-passing leaves, when only a weight changes. -/
example : debt [⟨1, false⟩] < debt [⟨2, false⟩] := by decide

end EBLLM
