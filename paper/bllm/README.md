# BLLM: the entropy cost of sound self-improvement

Source, formal proofs and checks of the paper *BLLM: The Entropy Cost of Sound Self-Improvement
and a Typed Crossing Network Tested on Five Open Problems* by Deep Bhattacharjee and Ushashi
Bhattacharya. The engine the paper describes is Anaxia, the rest of this repository; its
container image is `ghcr.io/creelie/bllm-engine`.

- `paper/`: REVTeX 4.2 source (`main.tex`, `sections/`, `figures/` as PNG; `figures/src/` holds
  the plotting scripts, their data and the TikZ sources). Build with `latexmk -pdf main.tex`;
  there is no BibTeX pass.
- `lean/`: Lean 4 (v4.33.0) with Mathlib, fifty-nine theorems, each depending only on `propext`,
  `Classical.choice` and `Quot.sound` (`lean/axioms.txt`). Build with
  `lake build && lake env lean Axioms.lean`.
- `checks/`: Python, C and C++ programs, 55,271 checks. `bash checks/run_all.sh` runs them all and
  builds the Lean development.

This folder came from creelie/D7 (folder `BLLM`) with its history. The releases made there are
archived at Zenodo: v1.0.0 https://doi.org/10.5281/zenodo.23449605, all versions
https://doi.org/10.5281/zenodo.23449604. Later versions are released with the engine, from this
repository.
