Version 2.0.0 of eBLLM. It keeps everything of version 1.0.0 (the VSI circuit, the release
algebra and the Lean-checked review) and adds the BLLM system of D. Bhattacharjee and
U. Bhattacharya, *BLLM: The Entropy Cost of Sound Self-Improvement and a Typed Crossing Network
Tested on Five Open Problems* (2026).

- `src/ebllm/bllm/`: entropy-law check schedules, the typed crossing network of known
  constructions (each candidate is checked by a program and attacked by a refuter), booster
  weights, the shared SQLite memory with retrieval, target points, the attack channel, five
  target agents, language-model, local-model and non-model proposers, the connectome selector,
  and the task records. `ebllm demo`, `schedule`, `tasks`, `attack`, `gap`, `bridge`, `brain`
  and `providers` are new commands.
- `experiments/`: the benchmark on five open problems (lattice Yang–Mills mass gap, Hodge,
  the standard conjecture of Lefschetz type, Chowla, Erdős problem 1183) with the logs of every
  run, the memory, channel and agent studies, and the continuous loop. None of the five problems
  is solved and no pass line is crossed.
- Erdős problem 1183: exact and weighted-poset searches, f(n) exactly for n ≤ 19, the proof that
  m-sequence level colourings have monochromatic sublattices of order n^(log2 3), and the grid
  searches at n = 20 (f(20) is 11 or 12).
- Yang–Mills: forest gauge fixing for SU(2) lattice gauge theory with four Lean theorems
  (`lean/EBLLM/GaugeFix.lean`), and a Monte Carlo scout of the Dobrushin–Shlosman condition on
  boxes, whose outputs are estimates, not proofs.
- `experiments/finetune/`: LoRA fine-tuning of the local proposer on its checked choices.
- `scripts/check_hardware.py` and `HARDWARE.md`: what each component needs.
- 58 unit tests; the Lean library has 30 theorems, each depending only on the standard axioms.

The memory of the continuous loop is shipped compressed as `experiments/memory/loop.sqlite.gz`
(`gunzip -k` it to resume the loop).
