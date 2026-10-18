Version 2.0.1 of eBLLM, a correction to version 2.0.0.

- Erdős problem 1183: f(20) = 12. The level colouring 000101100111001011100 has no monochromatic
  sublattice with 13 members (levelmono.py, and the independent dual search of the Erdős 1183
  verification code), and every colouring of 2^[20] has one with 12 members by Theorem 7.6 of the
  fifth version of D. Bhattacharjee, P. Mandal and U. Bhattacharya, *Resolving Erdős–Ulam
  monochromatic union-closed family conjectures* (doi:10.5281/zenodo.23374973), whose proof ends in
  a finite check. Version 2.0.0 gave f(20) as 11 or 12. The table of values, the benchmark state
  and `level_witnesses.txt` now run to n = 20, and a grid colouring of 2^[20] reported without a
  monochromatic sublattice of 12 members is rejected for rechecking instead of accepted.

Everything else is as in version 2.0.0: the BLLM system of D. Bhattacharjee and U. Bhattacharya,
*BLLM: The Entropy Cost of Sound Self-Improvement and a Typed Crossing Network Tested on Five Open
Problems* (2026), the benchmark on five open problems with the logs of every run (none of the five
problems is solved and no pass line is crossed), 58 unit tests and a Lean library of 30 theorems,
each depending only on the standard axioms.
