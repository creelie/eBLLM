/-!
# A gauge fixing of the four-dimensional lattice with one fixed link in every plaquette

Sites of `ℤ⁴` are read modulo 2 as `x : Fin 16`, bit `μ` of `x` being the parity of the
coordinate `x_μ`; the forward link from `x` in direction `μ` is the pair `(x, μ)`.  The pattern
fixes, at each site, the single forward link in direction `sig x`.  The four links of the
plaquette at `x` in the plane `(μ, ν)` are `(x, μ)`, `(x + e_μ, ν)`, `(x + e_ν, μ)` and `(x, ν)`;
moving by `e_μ` flips bit `μ`.  The theorems check, over all residues, that every plaquette has
exactly one fixed link and that every remaining link has exactly `12` remaining partners in its six
plaquettes (instead of `18` without gauge fixing).
-/

namespace EBLLM.GaugeFix

/-- The fixed direction at a site, indexed by the parities `x_0 + 2 x_1 + 4 x_2 + 8 x_3`. -/
def table : List Nat := [0, 0, 2, 3, 3, 1, 2, 1, 1, 2, 1, 3, 3, 2, 0, 0]

def sig (x : Fin 16) : Nat := table.getD x.val 0

/-- Move by the unit vector `e_μ` (modulo 2). -/
def step (x : Fin 16) (μ : Fin 4) : Fin 16 := ⟨(x.val ^^^ (1 <<< μ.val)) % 16, Nat.mod_lt _ (by decide)⟩

def fixedLink (x : Fin 16) (μ : Fin 4) : Bool := sig x == μ.val

/-- The number of fixed links of the plaquette at `x` in the plane `(μ, ν)`. -/
def fixedCount (x : Fin 16) (μ ν : Fin 4) : Nat :=
  [fixedLink x μ, fixedLink (step x μ) ν, fixedLink (step x ν) μ, fixedLink x ν].countP id

theorem one_fixed_per_plaquette :
    ∀ x : Fin 16, ∀ μ ν : Fin 4, μ.val < ν.val → fixedCount x μ ν = 1 := by decide

/-- The other three links of the plaquette at base `y` in the plane `(μ, ν)` that contain the
forward link `(x, μ)`; the plaquette is either based at `x` or at `x - e_ν`. -/
def partners (x : Fin 16) (μ ν : Fin 4) : List Bool :=
  -- plaquette based at x: the other links are (x + e_μ, ν), (x + e_ν, μ), (x, ν)
  [fixedLink (step x μ) ν, fixedLink (step x ν) μ, fixedLink x ν] ++
  -- plaquette based at x - e_ν (= x + e_ν mod 2): links (y, ν), (y + e_ν, μ) = (x, μ) itself is
  -- excluded, (y + e_μ, ν), (y, μ)
  (let y := step x ν; [fixedLink y ν, fixedLink (step y μ) ν, fixedLink y μ])

/-- Remaining partners of a remaining link `(x, μ)`: summed over the three planes through `μ`,
two plaquettes each. -/
def activePartners (x : Fin 16) (μ : Fin 4) : Nat :=
  ((List.finRange 4).filter (fun ν => ν != μ)).foldl
    (fun acc ν => acc + (partners x μ ν).countP (fun b => !b)) 0

theorem twelve_neighbours :
    ∀ x : Fin 16, ∀ μ : Fin 4, fixedLink x μ = false → activePartners x μ = 12 := by decide

/-- Without gauge fixing each link has `6 · 3 = 18` partners; with the pattern, `6 · 2 = 12`.
In the normalisation `β_W = 4β` of the sharp-quarter argument the single-link Dobrushin
coefficient is at most `12 |β| = 3 β_W`. -/
theorem threshold : 6 * 3 = 18 ∧ 6 * 2 = 12 ∧ 12 = 3 * 4 := by decide

/-- Exactly one fixed forward link at every site. -/
theorem one_per_site : ∀ x : Fin 16, ((List.finRange 4).filter (fun μ => fixedLink x μ)).length = 1 := by
  decide

end EBLLM.GaugeFix
