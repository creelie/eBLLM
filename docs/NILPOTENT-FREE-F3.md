# Nilpotent-free matrix spaces over F3

For 3 by 3 matrices over the field with three elements, the maximum dimension of a linear subspace containing no nonzero nilpotent is **5**. This refutes the finite-field universal assertion of Wigderson's Conjecture 8 at this one pair of parameters.

Preprint: [hexagon:2610.00480v1](https://hexagonmath.org/2610.00480v1). Original code: [congenial-waddle](https://github.com/creelie/congenial-waddle), commit `02576f2e4030f8a6233a4892b7e5d59f981e52b3`, [archival DOI](https://doi.org/10.5281/zenodo.23343183). The result is attributed to Deep Bhattacharjee. This integration and independent checker were prepared with OpenAI Codex on 24 October 2026.

```console
anaxia construct nilpotent-free
anaxia construct nilpotent-free --full
```

The first command checks the 243 elements of the five-parameter construction and verifies injectivity. Its report explicitly leaves `upper_bound_verified` false. The second command compiles the bundled C source, runs the entire search, and validates the complete table and coverage recurrence. A C compiler is required; on Windows it can use Lean's bundled clang and import libraries. A source SHA-256 with LF-normalised newlines is checked before compilation. No stored success flag substitutes for executing the verifier.

| Depth | Nodes | Closed |
|---|---:|---:|
| 0 | 1 | 0 |
| 1 | 27 | 9 |
| 2 | 486 | 228 |
| 3 | 6,966 | 5,165 |
| 4 | 48,627 | 0 |
| 5 | 1,312,929 | 1,248,453 |
| 6 | 1,740,852 | 1,740,852 |

The total is 3,109,888 nodes, with no open leaf. The independent verifier tests the trace, second characteristic coefficient and determinant. The original Lean search tests the matrix cube. A separate rerun of the original trace-zero enumeration checked all 25,095,280 five-dimensional subspaces of the trace-zero matrices and also found a nonzero nilpotent in every one.

The written reduction covers every six-dimensional subspace: either it intersects the strictly upper triangular matrices, or it is the graph of a 3 by 6 coefficient matrix. A closed node supplies a nonzero vector supported only on fixed columns, so it covers every completion. Every unclosed node has all 27 possible next columns. This gives coverage of all 3^18 coefficient matrices.

The lower-bound space consists of `[[a,0,b],[0,c-d-e,c],[b,d,e]]`. A direct algebraic proof is included in the revised submission manuscript. The checker also exhaustively verifies this finite construction.

The mathematical result is an unconditional computer-assisted finite theorem. The compiler and execution environment are part of its computational trust. The archived Lean main theorem additionally trusts two `native_decide` evaluations; the engine's standard-axioms-only formal gate therefore remains zero, and its human/referee gate is also zero. The control label remains `CANDIDATE` under the existing release algebra. This integration does not change those gates or assert journal acceptance, and it does not settle other fields or matrix sizes.

`xerj` was inspected as a possible reference tool. It provides local document and source retrieval, not a proof certificate for this theorem. No installation, index upload or feedback submission was performed.
