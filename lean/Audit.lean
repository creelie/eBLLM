import EBLLM

/-! Every theorem of the library, with its axioms.  The audit requires that none uses an axiom
other than `propext`, `Classical.choice` and `Quot.sound`; `sorryAx` would reveal a `sorry` and
`Lean.ofReduceBool` a `native_decide`. -/

#print axioms EBLLM.rel_eq_true_iff
#print axioms EBLLM.rel_false_of_mem
#print axioms EBLLM.no_shortcut
#print axioms EBLLM.released_only_if_all
#print axioms EBLLM.debt_eq_zero_of_released
#print axioms EBLLM.cor_6_4
#print axioms EBLLM.Scope.loss_comp
#print axioms EBLLM.Scope.lemma_6_2_false
#print axioms EBLLM.Playbook.paper_rejects_resolution
#print axioms EBLLM.Playbook.v11_accepts_this_resolution
#print axioms EBLLM.Playbook.paper_guard_lapses
#print axioms EBLLM.Playbook.v11_rejects_this_deletion
#print axioms EBLLM.Playbook.v11_keeps_core
#print axioms EBLLM.Playbook.ids_resolve
#print axioms EBLLM.Playbook.coreIds_sub_ids
#print axioms EBLLM.Playbook.v11_accepts_resolution
#print axioms EBLLM.Playbook.density_padding
#print axioms EBLLM.SandTile.conservative_cycle
#print axioms EBLLM.SandTile.conservative_never_stable
#print axioms EBLLM.SandTile.conservative_mass
#print axioms EBLLM.SandTile.bound_is_four
#print axioms EBLLM.SandTile.dissipative_count
#print axioms EBLLM.SandTile.count_bound
#print axioms EBLLM.Kappa.length_flatMap_const
#print axioms EBLLM.Kappa.length_words
#print axioms EBLLM.Kappa.typed_le
