/-!
# Why the learn-from-failure loop stops, and why a descent of point counts is short

The loop of `src/ebllm/bllm/selfmod.py` changes one rule after each failed attempt and refuses a
change it has made before. Its changes are therefore a list without repetitions drawn from the
finite set of changes the playbook can propose, and a list without repetitions inside a list `C` is
no longer than `C`: the loop makes at most `C.length` changes and `C.length + 1` attempts.

The same counting bounds a descent in which every step moves an integer strictly up or strictly
down inside a range: the values form a strictly monotone list inside the range, so there are at
most as many steps as the range is long. For the seeds of reflexive polytopes the integer is the
number of lattice points of the polytope, or of its dual.
-/

namespace EBLLM.SelfMod

/-- A list without repetitions inside a finite list `C` is no longer than `C`. -/
theorem nodup_length_le {α : Type} [DecidableEq α] :
    ∀ (l C : List α), l.Nodup → (∀ x, x ∈ l → x ∈ C) → l.length ≤ C.length
  | [], _, _, _ => Nat.zero_le _
  | a :: t, C, hnd, hsub => by
    have ha : a ∈ C := hsub a (List.mem_cons_self ..)
    have hnot : a ∉ t := (List.nodup_cons.mp hnd).1
    have ht : t.Nodup := (List.nodup_cons.mp hnd).2
    have hsub' : ∀ x, x ∈ t → x ∈ C.erase a := by
      intro x hx
      have hxa : x ≠ a := fun h => hnot (h ▸ hx)
      exact (List.mem_erase_of_ne hxa).mpr (hsub x (List.mem_cons_of_mem a hx))
    have ih := nodup_length_le t (C.erase a) ht hsub'
    have hlen := List.length_erase_of_mem ha
    have hpos := List.length_pos_of_mem ha
    simp only [List.length_cons]
    omega

/-- The loop never repeats a change, so it makes at most as many changes as there are. -/
theorem loop_changes_le {α : Type} [DecidableEq α] (changes C : List α) (hnew : changes.Nodup)
    (hfrom : ∀ c, c ∈ changes → c ∈ C) : changes.length ≤ C.length :=
  nodup_length_le changes C hnew hfrom

/-- Every attempt after the first follows one change, so the loop stops after at most
`C.length + 1` attempts. -/
theorem loop_attempts_le {α : Type} [DecidableEq α] (changes C : List α) (attempts : Nat)
    (hrun : attempts = changes.length + 1) (hnew : changes.Nodup)
    (hfrom : ∀ c, c ∈ changes → c ∈ C) : attempts ≤ C.length + 1 := by
  have := loop_changes_le changes C hnew hfrom
  omega

/-- A strictly increasing list of integers in `[lo, hi]` has at most `hi + 1 - lo` entries. -/
theorem strict_chain_length_le (l : List Nat) (lo hi : Nat) (hinc : l.Pairwise (· < ·))
    (hin : ∀ x, x ∈ l → lo ≤ x ∧ x ≤ hi) : l.length ≤ hi + 1 - lo := by
  have hnd : l.Nodup := hinc.imp (fun h => Nat.ne_of_lt h)
  have hsub : ∀ x, x ∈ l → x ∈ List.range' lo (hi + 1 - lo) := by
    intro x hx
    have := hin x hx
    rw [List.mem_range'_1]
    omega
  have := nodup_length_le l (List.range' lo (hi + 1 - lo)) hnd hsub
  rwa [List.length_range'] at this

/-- A descent whose every step raises an integer strictly inside `[lo, hi]` has at most `hi - lo`
steps: the values before and after each step form a strictly increasing list of length
`steps + 1`. -/
theorem descent_steps_le (values : List Nat) (lo hi steps : Nat) (hlen : values.length = steps + 1)
    (hinc : values.Pairwise (· < ·)) (hin : ∀ x, x ∈ values → lo ≤ x ∧ x ≤ hi) (hlohi : lo ≤ hi) :
    steps ≤ hi - lo := by
  have := strict_chain_length_le values lo hi hinc hin
  omega

/-- The same bound for a descent whose every step lowers the integer, such as the number of lattice
points of the polytope. -/
theorem descent_steps_le_of_decreasing (values : List Nat) (lo hi steps : Nat)
    (hlen : values.length = steps + 1) (hdec : values.Pairwise (· > ·))
    (hin : ∀ x, x ∈ values → lo ≤ x ∧ x ≤ hi) (hlohi : lo ≤ hi) : steps ≤ hi - lo := by
  apply descent_steps_le values.reverse lo hi steps
  · rw [List.length_reverse]; exact hlen
  · exact List.pairwise_reverse.mpr hdec
  · intro x hx; exact hin x (List.mem_reverse.mp hx)
  · exact hlohi

end EBLLM.SelfMod
