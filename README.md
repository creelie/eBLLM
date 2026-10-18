# BLLM: the entropy law of sound recursive self-improvement

Source, formal proofs and checks of the paper "Beyond the LLM: BLLM and the
Entropy Law of Sound Recursive Self-Improvement" by Deep Bhattacharjee and
Ushashi Bhattacharya. The compiled paper is
[`preprintBeyondTheLLM/BeyondTheLLM.pdf`](../preprintBeyondTheLLM/BeyondTheLLM.pdf).

- `paper/`: REVTeX 4.2 source (`main.tex`, `sections/`, `figures/` as PNG;
  `figures/src/` holds the plotting script and the TikZ sources). Build with
  `latexmk -pdf main.tex`; there is no BibTeX pass.
- `lean/`: Lean 4 (v4.33.0) with Mathlib, thirty-nine theorems, each depending
  only on `propext`, `Classical.choice` and `Quot.sound` (`lean/axioms.txt`).
  Build with `lake build && lake env lean Axioms.lean`.
- `checks/`: Python, C and C++ programs, 33,505 checks.
  `bash checks/run_all.sh` runs them all and builds the Lean development.
