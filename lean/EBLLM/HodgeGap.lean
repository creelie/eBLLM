/-!
# The finite checks of the Hodge-only engine

Each theorem is one of the numbers the engine's checks rest on, taken from Bhattacharjee and
Bhattacharya, "Dense Algebraic Loci of Hodge Classes" (doi:10.5281/zenodo.23439578), and from
H8 ("Algebraic Loci of Weil Classes on Abelian Varieties").  They are arithmetic statements and
decide; none of them is a statement about Hodge classes, and none proves (F2) or (F3').
-/

namespace EBLLM.HodgeGap

/-- `r(ch E) = 7 n^2 - 2 n` for the product object (Hankel rank 3). -/
def polarisedRank (n : Nat) : Nat := 7 * n * n - 2 * n

theorem rank_three : polarisedRank 3 = 57 := by decide
theorem rank_four : polarisedRank 4 = 104 := by decide

/-- H8 thm:noconvolution: every convolution at n = 3 with |t_i - p| >= 2 has dim Ext^2 >= 69. -/
theorem e06_excluded : 69 > polarisedRank 3 := by decide
/-- H8 cor:efoursix: on E_0^8 every convolution within six consecutive shifts has dim Ext^2 >= 640. -/
theorem e08_excluded : 640 > polarisedRank 4 := by decide

/-- Products B x B' of Weil varieties of dimensions 2a, 2b, a + b = n, have moduli a^2 + b^2. -/
def productDim (n : Nat) : Nat := (List.range n).foldl (fun m a => if a = 0 then m else max m (a * a + (n - a) * (n - a))) 0

/-- Schoen products fill dimension 5 of the 9-dimensional family of Weil sixfolds. -/
theorem schoen_meagre : productDim 3 = 5 ∧ 5 < 3 * 3 := by decide

/-- The residue `t a` reduced mod `m`. -/
def frac (m t a : Nat) : Nat := (t * a) % m

/-- A shadow of the character `a` at level `m`: a non-unit `t` with every `t a_k` nonzero mod `m`
and `sum <t a_k> = m` (H8 Rem 4.26(b)); it is a lattice point of the Fine interior. -/
def isShadow (m : Nat) (a : List Nat) (t : Nat) : Bool :=
  Nat.gcd t m > 1 && a.all (fun x => frac m t x != 0) && a.foldl (fun s x => s + frac m t x) 0 == m

/-- The character (1,16,26,31,36) at level 55 has the shadow t = 11, so it has no block pattern. -/
theorem fermat110_shadow : isShadow 55 [1, 16, 26, 31, 36] 11 = true := by decide

/-- Euler's function on `m`, as a count. -/
def phi (m : Nat) : Nat := ((List.range m).filter (fun k => Nat.gcd (k + 1) m = 1)).length

/-- prop:cubicstop(iii): among the real cyclotomic fields `Q(zeta_m)^+` with `m <= 50`, the cubic
ones are exactly `m = 7, 9` (conductors; `Q(zeta_{2m}) = Q(zeta_m)` for odd `m`). -/
theorem cubic_cyclotomic :
    ((List.range 51).filter (fun m => 3 ≤ m ∧ m % 4 ≠ 2 ∧ phi m / 2 = 3)) = [7, 9] := by decide

/-- H8 prop:coversreach: an isotypic part of (F, 2)-Weil type on an abelian cover reaches a locus of
dimension `3 n - k/2 = 5` inside a Weil family of dimension `m n^2 = 8` for `m = 2, n = 2, k = 2`. -/
theorem covers_meagre : 3 * 2 - 2 / 2 < 2 * 2 * 2 := by decide

end EBLLM.HodgeGap
