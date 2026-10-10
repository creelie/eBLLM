The first release of eBLLM, a Python package and a Lean library implementing version 1.1 of the
VSI circuit (D. Bhattacharjee, *Synthetic Neuromorphic Superintelligence for Verifier-Gated
Conjecture Closure*, 15 May 2026).

- `pip install ebllm-1.0.0-py3-none-any.whl`, then `ebllm --help`.
- The release algebra, obligation graphs, the Module 26 playbook with a corrected collapse guard,
  sand-tile toppling with a toppling budget, scope loss, Accuracy26, Kappa words, run ledgers and
  the Section 32 contract report.
- Verifiers as programs: a Lean source scan and `#print axioms` audit, and command verifiers.
- 25 controls: the closures and partial results recorded by this project (all CANDIDATE until
  refereed), six calibration theorems, and eight open problems (OPEN).
- `docs/REVIEW.md` reviews the paper's numbered results. Theorem 10.4, Proposition 10.2, the
  second part of Lemma 6.2, Proposition 8.2, the "only if" of Proposition 21.1 and the collapse
  guard of Theorem 30.1 are false as stated; each counterexample is proved in Lean (26 theorems,
  standard axioms only, replayed by `leanchecker --fresh`) and checked in C, C++ and Julia.
