"""Construction mode: build the object a conjecture forbids, then check it.

The forward rules of Anaxia cross results that are already proved; they never
write down a new graph. Construction mode does. It searches for planar
3-colouring gadgets (graphs with two or three contact vertices whose proper
3-colourings never give the contacts one colour), assembles them into whole
graphs, and checks every output from scratch with code that shares nothing
with the search: planarity by networkx, short cycles by depth-first search,
distances by breadth-first search, colourability by backtracking and by three
independent SAT solvers.

  graphcheck         the independent checks
  steinberg_rebuild  Steinberg's counterexample (Cohen-Addad, Hebdige, Kral',
                     Li, Salgado 2016) rebuilt edge by edge, the calibration
  proof_builder      goal-directed builder: grows a gadget together with its
                     forcing argument, and may use library gadgets as lemmas
  assemble           gadget -> full planar non-3-colourable graph
  cegar_forcer       exists-forall SAT search for a forcer of given size
  cegar_book, cegar_hub  the same search on book and hub frames
  gadget_algebra     typed gadget library closed under planar composition
  g1prime            a triangle-free variant of Steinberg's gadget
  reflexive          reflexive lattice polytopes: duality, covers, descents to
                     minimal seeds, free sums, the pair-chain bound on every descent
  reformulate        definition repair (a definition is replaced only when it
                     gains consequences) and the witness gate for conditional
                     results
  transvections      bridge index = meridional rank for knots, by colourings of a
                     diagram with pseudo-reflections (243 thirteen-crossing knots)
  brane_formfactor   the entire zero-free form factor of a scale-invariant brane
                     gas, its power counting, one-loop tuning, vacuum energy and
                     the refuters (resonances, reflection positivity)
  theophys           the beta-function series for pi and the hidden-zero partial-wave
                     relation of TheoPhysEval (arXiv:2610.16733), with refuters

Stored results (data/, each with the log of the run that found it): the 15-vertex
gadget the builder found from the rules alone, isomorphic to Steinberg's G1; the
42-vertex gadget it found with that gadget and the triangle T as lemmas,
isomorphic to Steinberg's G2; and a 48-vertex level-two gadget with contact
distances 5, 4, 5 from the same lemmas. These are rediscoveries of known
gadgets and a variant of them, not new theorems. SNAPSHOT.sha256 records the
source files this package was taken from.
"""
import json
import os

DATA = os.path.join(os.path.dirname(__file__), "data")


def gadget(name):
    """A stored gadget as (graph, contacts); contacts are 0, 1, 2 (or 0, 1)."""
    import networkx as nx  # only the gadget half of construction mode needs it
    with open(os.path.join(DATA, name + ".json")) as f:
        d = json.load(f)
    G = nx.Graph()
    contacts = d.get("contacts", [0, 1, 2])
    G.add_nodes_from(contacts)
    G.add_edges_from(tuple(e) for e in d["edges"])
    return G, contacts


GADGETS = ("rediscovered_n15", "G2_rediscovered_n42", "level2_n48", "T", "G1prime")
