# Auxiliary power-counting arithmetic

Source: the manuscript archive https://doi.org/10.5281/zenodo.23601921, commit c0a9d31. This copy repairs two `List.mem_cons_self` API uses and explicitly normalizes an integer cast for Lean 4.34.1. No theorem statement has changed. All 17 theorems re-elaborated successfully; their printed axioms contain only propext and Quot.sound, or no axioms. No sorryAx or native evaluation is used.

Run `lean PowerCounting.lean`. The file proves integer degree inequalities and algebraic tuning identities, not the analytic, probabilistic, renormalization or unitarity parts of the gravity manuscript. `AXIOMS.txt` records the fresh audit.
