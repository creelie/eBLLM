/-!
# The collapse guard of Module 26 (Sections 18 and 30 of the VSI paper)

A bullet has an identifier and a flag saying whether it records an unresolved core failure
(status FAIL or UNK and no passing verifier).  The paper's guard is
`Collapse(P, P') = 1 - |Core P ∩ Core P'| / |Core P|`, and an update is accepted when
`Collapse ≤ θ`.  For `θ = a / b` we compare `lost * b ≤ a * |Core P|` in `Nat`.

Findings proved here:
* `paper_rejects_resolution`: the paper's guard counts a *resolved* failure (its verifier now
  passes, so it leaves the core) as collapse.  Under the hypothesis of Theorem 30.1,
  `θ < 1/|Core P|`, it rejects the update that records a successful repair.
* `paper_guard_lapses`: the hypothesis `θ < 1/|Core P_t|` is not stable in time.  With a fixed
  `θ = 1/3`, once the core holds three failures an update that silently deletes one of them is
  accepted, so Corollary 30.2 (the core never loses an unresolved failure) fails.
* `density_padding`: the proof-critical density of Proposition 30.4 drops when an unrelated
  passing bullet is added, with no failure resolved, so a drop is not evidence of progress.

The guard of circuit v1.1 counts only core bullets that disappear from the playbook:
* `v11_keeps_core`: with `θ = 0`, every accepted update keeps every unresolved failure;
* `v11_accepts_resolution`: resolving failures never trips the guard.
-/

namespace EBLLM.Playbook

structure Bullet where
  id : Nat
  core : Bool
  deriving DecidableEq, Repr

def coreIds (P : List Bullet) : List Nat := (P.filter (·.core)).map (·.id)

def ids (P : List Bullet) : List Nat := P.map (·.id)

/-- Old core failures that are no longer core failures (deleted or resolved). -/
def lostPaper (P P' : List Bullet) : Nat := (coreIds P).countP (fun i => !(coreIds P').contains i)

/-- Old core failures that are no longer in the playbook at all. -/
def lostV11 (P P' : List Bullet) : Nat := (coreIds P).countP (fun i => !(ids P').contains i)

/-- Accept iff Collapse ≤ a / b. -/
def acceptPaper (a b : Nat) (P P' : List Bullet) : Bool :=
  decide (lostPaper P P' * b ≤ a * (coreIds P).length)

def acceptV11 (a b : Nat) (P P' : List Bullet) : Bool :=
  decide (lostV11 P P' * b ≤ a * (coreIds P).length)

/-- Two core failures; the update resolves the first. -/
def P2 : List Bullet := [⟨0, true⟩, ⟨1, true⟩]
def P2resolved : List Bullet := [⟨0, false⟩, ⟨1, true⟩]

/-- With θ = 1/3 < 1/|Core| = 1/2 the paper's guard rejects the resolution. -/
theorem paper_rejects_resolution : acceptPaper 1 3 P2 P2resolved = false := by decide

theorem v11_accepts_this_resolution : acceptV11 0 1 P2 P2resolved = true := by decide

/-- Three core failures; the update deletes the third without resolving it. -/
def P3 : List Bullet := [⟨0, true⟩, ⟨1, true⟩, ⟨2, true⟩]
def P3deleted : List Bullet := [⟨0, true⟩, ⟨1, true⟩]

/-- With a fixed θ = 1/3 the paper's guard accepts the deletion once |Core| = 3. -/
theorem paper_guard_lapses :
    acceptPaper 1 3 P3 P3deleted = true ∧ (coreIds P3deleted).length < (coreIds P3).length := by
  decide

theorem v11_rejects_this_deletion : acceptV11 0 1 P3 P3deleted = false := by decide

/-- With θ = 0, every update accepted by the v1.1 guard keeps every old core failure. -/
theorem v11_keeps_core (b : Nat) (hb : 0 < b) (P P' : List Bullet)
    (h : acceptV11 0 b P P' = true) : ∀ i ∈ coreIds P, i ∈ ids P' := by
  simp only [acceptV11, Nat.zero_mul, Nat.le_zero, decide_eq_true_eq, Nat.mul_eq_zero] at h
  have h0 : lostV11 P P' = 0 := by
    rcases h with h | h
    · exact h
    · omega
  intro i hi
  have := (List.countP_eq_zero.1 h0) i hi
  simpa using this

/-- Resolving bullets keeps their identifiers. -/
def resolve (S : List Nat) (P : List Bullet) : List Bullet :=
  P.map (fun x => if S.contains x.id then { x with core := false } else x)

theorem ids_resolve (S : List Nat) (P : List Bullet) : ids (resolve S P) = ids P := by
  simp only [ids, resolve, List.map_map]
  apply List.map_congr_left
  intro x _
  show (if S.contains x.id = true then { x with core := false } else x).id = x.id
  split <;> rfl

theorem coreIds_sub_ids (P : List Bullet) : ∀ i ∈ coreIds P, i ∈ ids P := by
  intro i hi
  simp only [coreIds, List.mem_map, List.mem_filter] at hi
  obtain ⟨x, ⟨hx, _⟩, rfl⟩ := hi
  exact List.mem_map_of_mem hx

/-- Resolutions never trip the v1.1 guard, whatever θ. -/
theorem v11_accepts_resolution (a b : Nat) (S : List Nat) (P : List Bullet) :
    acceptV11 a b P (resolve S P) = true := by
  have h0 : lostV11 P (resolve S P) = 0 := by
    apply List.countP_eq_zero.2
    intro i hi
    rw [ids_resolve]
    simpa using coreIds_sub_ids P i hi
  simp [acceptV11, h0]

/-- Density |Core| / |P| as a pair (numerator, denominator). -/
def densityLt (P Q : List Bullet) : Bool :=
  decide ((coreIds P).length * Q.length < (coreIds Q).length * P.length)

/-- Adding an unrelated passing bullet lowers the density with the core unchanged. -/
theorem density_padding :
    densityLt (P2 ++ [⟨7, false⟩]) P2 = true ∧ coreIds (P2 ++ [⟨7, false⟩]) = coreIds P2 := by
  decide

end EBLLM.Playbook
