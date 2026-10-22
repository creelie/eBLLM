Version 3.3.1 of eBLLM and of Anaxia, the BLLM engine, uploaded by a second agent on Tubai's command.
It carries a fourth pass on the knot tables. These are partial results on finite lists, not named
conjectures, and they are not refereed.

- **What failed, and the change it forced.** The third pass ended with the pinch search stalled, and
  the rule changed in kind, from upper bounds to lower bounds (modlog run `knot-tables-pass4`).
- **Lower bounds from Donaldson's theorem.** The new construction `construct/goeritz_lattice.py`
  computes the Goeritz forms and the signature of an alternating diagram and lists every embedding
  of the lattice in the standard lattice (Jabuka and Kelly, Theorems 2.10 to 2.12). It raises the
  lower end of 382 open KnotInfo entries, 22 of them to four-genus 3. Its refuter, the signature with
  the wrong sign, claims four-genus at least 2 for the trefoil and is caught.
- **Pinches on twenty diagrams.** 84 more pinch certificates, all checked in Regina.
- **Together** they settle the nonorientable four-genus of 2,537 of the 3,525 open knots with 11 to
  13 crossings (520 at 1, 1,995 at 2, 22 at 3); 988 stay open. Control `crosscap4d-13`, CANDIDATE.
  Repository: https://github.com/creelie/conjecture-to-choose, folder `crosscap4d`.

The knots, loop, numbers and results figures were redrawn from the current data.
