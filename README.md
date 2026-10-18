# eBLLM 2: verifier-gated conjecture closure and the BLLM crossing network

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23286641.svg)](https://doi.org/10.5281/zenodo.23286641)

eBLLM is a Python package and a Lean library that implement the VSI circuit of

> Deep Bhattacharjee, *Synthetic Neuromorphic Superintelligence for Verifier-Gated Conjecture
> Closure: Sand-Tile Automata, K-Dot Circuits, and Phenomenological Proof Learning* (15 May 2026),
> [`paper/VSI-verifier-gated-conjecture-closure-2026-05-15.pdf`](paper/VSI-verifier-gated-conjecture-closure-2026-05-15.pdf).

The package turns a conjecture into a typed package, an attempt into an obligation graph, and every
failed step into a recorded residue. A result is released only when every verifier factor is 1:
the proof, a Lean kernel check, programs with checked output, the trace, simulations, the risk
audit, the literature check and a human referee. The engine does not prove anything by itself.
Whatever generates the steps (a person, a script, a language model), obligations change status
only through verifiers, and the label comes only from the release algebra.

This is version 1.1 of the circuit. A line-by-line review of the paper's numbered results is in
[`docs/REVIEW.md`](docs/REVIEW.md): the release discipline is sound, but Theorem 10.4,
Proposition 10.2, the second part of Lemma 6.2, Proposition 8.2, the "only if" of
Proposition 21.1 and the collapse guard of Theorem 30.1 are false as stated, and each
counterexample is proved in Lean. [`docs/CIRCUIT-v1.1.md`](docs/CIRCUIT-v1.1.md) lists the
corrections the package implements.

## Version 2: the BLLM system

Version 2 adds the system of D. Bhattacharjee and U. Bhattacharya, *BLLM: The Entropy Cost of
Sound Self-Improvement and a Typed Crossing Network Tested on Five Open Problems* (2026; paper,
Lean development and checks in [creelie/D7](https://github.com/creelie/D7), folder `BLLM`).

- `src/ebllm/bllm/`: entropy-law check schedules (`schedules.py`), the typed crossing network of
  known constructions (`crossing.py`, `hyperlib.py`), booster weights (`boosters.py`), the shared
  SQLite memory with retrieval (`memory.py`), target points (`targets.py`), the attack channel
  (`attackflow.py`), the five target agents (`agents.py`), the proposers (language models, a
  local model, non-model proposers; `proposers.py`), the connectome selector (`brain.py`,
  `neuro.py`), the benchmark (`benchmark.py`, `superbrain.py`) and the stepwise task records
  (`tasks/`). Every candidate is checked by a program and attacked by a refuter before it counts.
- `experiments/`: the benchmark on five open problems (the lattice mass gap of Yang–Mills theory,
  the Hodge conjecture, Grothendieck's standard conjecture of Lefschetz type, Chowla's conjecture
  and Erdős problem 1183) with the logs of every run; the memory, channel and agent studies; the
  continuous loop (`loop.py`; its memory is `memory/loop.sqlite.gz`, unpack it with `gunzip -k`
  to resume). **None of the five problems is solved and no pass line is crossed.**
- `experiments/erdos1183/`: exact SAT and weighted-poset searches (f(n) exactly for n ≤ 19), the
  proof that m-sequence level colourings have monochromatic sublattices of order n^(log₂ 3)
  (`mseq/NOTES.md`), and the grid-colouring searches at n = 20 (`gridsearch.c`, `gridwit.c`,
  `gridcegar.py`; f(20) is 11 or 12).
- `experiments/yangmills/`: a Monte Carlo scout of the Dobrushin–Shlosman condition on gauge-fixed
  boxes (`ds_block.py`). Its outputs are estimates, not proofs. The forest gauge fixing it uses is
  stated in Lean in `lean/EBLLM/GaugeFix.lean`.
- `experiments/finetune/`: LoRA fine-tuning of the local proposer on its checked choices.
- [`HARDWARE.md`](HARDWARE.md) and `scripts/check_hardware.py`: what each component needs;
  [`DEVICE_RUN.md`](DEVICE_RUN.md): the runs meant for a larger machine.

## Install

```sh
pip install .            # or the wheel from the latest release
ebllm --version
```

Python 3.9 or later, with no dependencies. The Lean library needs
[elan](https://github.com/leanprover/elan); `lean/lean-toolchain` pins Lean 4.34.1, and the
library uses Lean core only, without Mathlib.

## Use

```sh
ebllm controls                 # closures, calibration theorems and open problems, with their labels
ebllm counterexamples          # the counterexamples to Theorem 10.4, Lemma 6.2 and the collapse guard
ebllm scan lean/               # Lean sources: sorry, axiom, native_decide, unsafe, ... (comments ignored)
ebllm axioms audit.log 30      # audit the output of #print axioms: only propext, Classical.choice, Quot.sound
ebllm run examples/theorem-10-4.json   # one engine step from a JSON spec, with its contract report
```

[`docs/USAGE.md`](docs/USAGE.md) explains the spec format and the Python interface.

## Labels of the recorded results

`ebllm controls` computes these from the verifier factors stored in `src/ebllm/controls/`. Every
result of this project that has not been refereed is a CANDIDATE, however strong its formal
evidence; open problems are OPEN.

| control | group | label | blocking verifiers |
|---|---|---|---|
| Graffiti.pc Conjectures 319, 352, 358, 359, 427 on domination (refuted) | closure | CANDIDATE | human |
| Tran's Conjecture 8.6 on regular Morley tetrahedra (refuted) | closure | CANDIDATE | human |
| Shankar's Conjecture 4.1 on even-intersecting lattice paths (proved) | closure | CANDIDATE | formal, human |
| Wang–Tian conjecture on tau_k-maximal graphs (proved) | closure | CANDIDATE | formal, human |
| Hou–Zhao Conjecture 4.10, Welch functions not third-order sum-free (proved) | closure | CANDIDATE | formal, human |
| Graffiti.pc / WOWII Conjecture 66, forest number (refuted) | closure | CANDIDATE | human |
| Densest packings of two translates of a lattice in R^4 (theorem; the 24-cell conjecture stays open) | partial | CANDIDATE | formal, human |
| Erdős Problem 1183: the lower bound of Theorem 1.4 | partial | CANDIDATE | human |
| Hodge conjecture for Fermat fourfolds of odd degree (Theorem F) | partial | CANDIDATE | formal, human |
| Blowup above alpha = 1/3 in viscous Katz–Pavlović dyadic models with small shell ratios | partial | CANDIDATE | formal, human |
| Lehmer's totient problem: a Lehmer number has at least 16 prime factors (partial result) | partial | CANDIDATE | formal, human |
| Fermat's Last Theorem | calibration | THEOREM | — |
| Kepler conjecture (sphere packing in dimension 3) | calibration | THEOREM | — |
| Navier–Stokes breakdown, alternatives (C) and (D) (OpenAI) | calibration | CANDIDATE | risk, human |
| Poincaré conjecture | calibration | THEOREM | — |
| Sphere packing in dimension 24 | calibration | THEOREM | — |
| Sphere packing in dimension 8 | calibration | THEOREM | — |
| Birch and Swinnerton-Dyer conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Collatz conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Densest packing in R^4 (D4 / 24-cell conjecture) | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Hodge conjecture | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Lehmer's totient problem | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| P versus NP | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Riemann hypothesis | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |
| Yang–Mills existence and mass gap | open | OPEN | proof, formal, code, trace, sim, risk, lit, human |

## Checks

`checks/run_all.sh` runs everything that CI runs:

- 58 Python tests (`tests/`);
- `checks/c/sandtile.c`: the conservative two-site run does not stabilize in 10⁶ topplings, the
  dissipative run with absorbed share 1/N needs exactly N topplings for N up to 10⁴ (the bound of
  Theorem 10.4 is 4), and chip-firing is abelian on 200 random graphs;
- `checks/cpp/scope_playbook.cpp`: all 9,710 pairs of partial maps on at most three points (the
  composition law holds, superadditivity fails for 2,976), and 4,340 playbook updates (the v1.1
  guard never loses a core failure; the paper's guard rejects all 1,880 updates that record a
  repair);
- `checks/julia/release_accuracy.jl`: all 2⁸ factor assignments of the release algebra, and
  Proposition 21.1 on 20,000 random steps;
- the Lean library: `lake build`, the source scan, the axiom audit of all 30 theorems
  (`lean/Audit.lean`), and an independent replay with `leanchecker --fresh`;
- the example run, whose label must be CANDIDATE with only the human factor blocking.

## Citing

See [`CITATION.cff`](CITATION.cff). Each release is archived on Zenodo.

- v1.0.0: [10.5281/zenodo.23286642](https://doi.org/10.5281/zenodo.23286642)
- v2.0.0: the DOI is recorded here once Zenodo has minted it
- all versions (concept DOI): [10.5281/zenodo.23286641](https://doi.org/10.5281/zenodo.23286641)

## Licence

MIT, see [`LICENSE`](LICENSE). The paper in `paper/` is the author's and is included for
reference.

Built with the help of an AI coding assistant; the author checked and is responsible for the
content.
