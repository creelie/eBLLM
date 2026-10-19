Version 2.1.0 of eBLLM. The engine is now called **Anaxia**, the BLLM engine.

- The command is `anaxia` (`ebllm` remains, and `python -m anaxia` works), and the container image
  ghcr.io/creelie/bllm-engine runs it as its entry point.
- The image is rebuilt and published as `latest` and as the package version on every merge to main
  and on every release, after the version, the command line and the Lean axiom audit pass inside
  the new image. A running image compares its version, commit and build time with those of
  `latest` and prints one line with the pull command when a newer image is published;
  `anaxia update` shows both sides and `ANAXIA_NO_UPDATE_CHECK=1` turns the check off.
- This repository is now the home of the BLLM paper of D. Bhattacharjee and U. Bhattacharya,
  *BLLM: The Entropy Cost of Sound Self-Improvement and a Typed Crossing Network Tested on Five
  Open Problems*: its source, its Lean development (59 theorems with Mathlib, standard axioms
  only) and its checks are in `paper/bllm`, with their history from creelie/D7.
- A new README with the engine diagram, and `RELEASING.md`: a closure is finished only when the
  engine and the paper both carry it.

None of the five benchmark problems is solved. 65 unit tests, C, C++ and Julia checks, and a Lean
library of 30 theorems, each depending only on the standard axioms.
