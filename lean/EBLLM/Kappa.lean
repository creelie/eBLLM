/-!
# Finite coverage of the Kappa generator (Lemma 4.1 of the VSI paper)

The raw words of length `m` over an operator alphabet `O` number `|O| ^ m`, so the words of
length at most `K` number `∑_{m ≤ K} |O| ^ m`; type filtering only removes words.  This is the
finite-coverage half of Lemma 4.1.
-/

namespace EBLLM.Kappa

/-- All words of length `m` over the alphabet `O`. -/
def words {α : Type} (O : List α) : Nat → List (List α)
  | 0 => [[]]
  | m + 1 => (words O m).flatMap (fun w => O.map (fun o => o :: w))

theorem length_flatMap_const {α β : Type} (l : List α) (f : α → List β) (c : Nat)
    (h : ∀ a, (f a).length = c) : (l.flatMap f).length = l.length * c := by
  induction l with
  | nil => simp
  | cons a l ih => simp [List.flatMap_cons, h, ih, Nat.succ_mul, Nat.add_comm]

theorem length_words {α : Type} (O : List α) : ∀ m, (words O m).length = O.length ^ m
  | 0 => rfl
  | m + 1 => by
    simp only [words]
    rw [length_flatMap_const _ _ O.length (fun _ => by simp), length_words O m, Nat.pow_succ]

/-- Every well-typed word is a raw word, so typed words of length `m` are at most `|O| ^ m`. -/
theorem typed_le {α : Type} (O : List α) (typed : List α → Bool) (m : Nat) :
    ((words O m).filter typed).length ≤ O.length ^ m := by
  rw [← length_words O m]
  exact List.length_filter_le _ _

end EBLLM.Kappa
