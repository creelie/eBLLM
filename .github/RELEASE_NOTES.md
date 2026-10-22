Version 3.4.0 of eBLLM and of Anaxia, the BLLM engine, uploaded by a second agent on Tubai's command.
It carries a closure by refutation, recorded as a CANDIDATE until refereed.

- **The claim.** Rios, Marrani and Chester (Phys. Rev. D 99 (2019) 046004, Sec. III A) state that
  Nishino's existence proofs for super Yang–Mills theories in the signatures (9+m)+(1+m) can be
  repeated in (9+8n)+1, (10+8n)+2, (11+8n)+3 and (12+8n)+4, including 27+3 and 19+3.
- **What is proved.** A theory built in Nishino's manner (five axioms that his construction
  satisfies) has k ≤ min(s,t) real null vectors and residual dimension s+t−2k equal to 10 or 2: the
  cubic gaugino terms reduce to a Fierz identity that forces spinors of dimension 2(d−2), so
  d = 3, 4, 6, 10. Hence s−t lies in {8, 0, −8} and none of the four families with n ≥ 1 carries
  such a theory. For one time, in (9+8n)+1 with n ≥ 1, every massless multiplet without tensor
  charges has at least 2^(2^(2+4n)) states, so there is no massless vector multiplet.
- **The construction.** `construct/multitime_sym.py` rebuilds the Witt bound, the dimension count
  and the single-time bound, checks the cubic identity with explicit gamma matrices, and carries two
  refuters (the mod-8 rule of the claim, complex null frames), each of which admits all eight
  claimed signatures with n = 1, 2 and is caught. Modlog run `multitime-sym`; control
  `multitime-sym-ten`, CANDIDATE (no Lean statement, not refereed).
- Paper, LaTeX source and code: https://github.com/creelie/cs-grav, release v1.0.0,
  doi:10.5281/zenodo.23558751.

The DOIs of releases 3.3.0 (10.5281/zenodo.23548148) and 3.3.1 (10.5281/zenodo.23557319) are
recorded, and the results, loop, numbers and growth figures were redrawn from the current data.
