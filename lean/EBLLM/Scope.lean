/-!
# Scope loss of bridges (Lemma 6.2 of the VSI paper)

A bridge `f : D_a → D_b` is a partial map: `f x = none` means that `x` is lost (it is not
transported to a verifier-coherent point).  On a finite domain, listed as `xs`, the scope loss
is the number of lost points.

Lemma 6.2 claims `ScopeLoss (g ∘ f) ≥ ScopeLoss f + ScopeLoss g`.  `lemma_6_2_false` refutes
it.  The correct statement is the exact decomposition `loss_comp`: the composite loses what `f`
loses plus the points that `f` sends into the part of `D_b` that `g` loses.
-/

namespace EBLLM.Scope

/-- The number of lost points in a list of transported values. -/
def loss : List (Option Nat) → Nat
  | [] => 0
  | none :: l => loss l + 1
  | some _ :: l => loss l

/-- Transport the values of `f` through `g`. -/
def comp (g : Nat → Option Nat) (f : List (Option Nat)) : List (Option Nat) :=
  f.map (fun o => o.bind g)

/-- The points that `f` transports into the part of `D_b` that `g` loses. -/
def pulled (g : Nat → Option Nat) : List (Option Nat) → Nat
  | [] => 0
  | none :: l => pulled g l
  | some y :: l => (if g y = none then 1 else 0) + pulled g l

/-- The scope loss of `g` on the domain `{0, …, nb - 1}`. -/
def lossOn (g : Nat → Option Nat) (nb : Nat) : Nat := loss ((List.range nb).map g)

theorem loss_comp (g : Nat → Option Nat) :
    ∀ f : List (Option Nat), loss (comp g f) = loss f + pulled g f
  | [] => rfl
  | none :: l => by
    simp only [comp, List.map_cons, Option.bind_none, loss, pulled]
    have := loss_comp g l
    simp only [comp] at this
    omega
  | some y :: l => by
    simp only [comp, List.map_cons, Option.bind_some, pulled]
    have ih := loss_comp g l
    simp only [comp] at ih
    cases h : g y with
    | none => simp [loss, ih]; omega
    | some z => simp [loss, ih]

/-- Lemma 6.2 is false: `D_a = {0}`, `D_b = {0, 1}`, `f 0 = 0`, `g` loses `1`. -/
theorem lemma_6_2_false :
    ¬ ∀ (f : List (Option Nat)) (g : Nat → Option Nat) (nb : Nat),
        loss (comp g f) ≥ loss f + lossOn g nb := by
  intro h
  have := h [some 0] (fun y => if y = 0 then some 0 else none) 2
  revert this
  decide

end EBLLM.Scope
