# Using eBLLM

## The release algebra

```python
from ebllm import VERIFIERS, emit, release_product

factors = {chi: 1 for chi in VERIFIERS}      # proof, formal, code, trace, sim, risk, lit, human
factors["human"] = 0                         # not yet refereed
release_product(factors)                     # 0
emit(factors, kind="refutation", model_ok=True)   # Label.CANDIDATE
```

When every required factor is 1, `emit` returns CONDITIONAL if the result still carries named
conditions, and otherwise COUNTEREXAMPLE for a refutation, INDEPENDENCE for an independence result
and THEOREM for a proof. When some factor is 0 it returns CANDIDATE if a complete candidate
argument exists (`model_ok`), OPEN if not but the attempt is still producing new machinery, and
BUJ if neither. `required` restricts the factors a label depends on (the calibration theorems use
proof, risk, literature and referee only).

## Obligation graphs

```python
from ebllm.obligations import ObligationGraph

g = ObligationGraph()
g.add("lemma-1", status="PASS", verifier="Lean: Foo.lemma1")
g.add("lemma-2")                              # UNK
g.add("main", kind="theorem")
g.bridge(["lemma-1", "lemma-2"], "main")      # zero scope loss
g.releasable("main")                          # False
g.blockers("main")                            # ["lemma-2"]
g.debt_mass()                                 # 2.0
```

A node is certified if it is a PASS leaf or the conclusion of a zero-loss bridge whose premises
are all certified (Theorem 6.3). A bridge with positive scope loss never certifies.

## Verifiers

A verifier is the integer 0 or 1, or a callable returning one.

```python
from ebllm.verifiers import CommandVerifier, LeanAxiomVerifier

code = CommandVerifier(["./build/sandtile"], expect=r"^OK$")
formal = LeanAxiomVerifier("lean", imports=["EBLLM.SandTile"],
                           theorems=["EBLLM.SandTile.dissipative_count"])
code(), formal()                              # (1, 1) after `lake build` in lean/
```

`LeanAxiomVerifier` writes a temporary file with `#print axioms` for each theorem, runs
`lake env lean` on it, and returns 1 only if Lean succeeds, every theorem is reported, and none
uses an axiom other than `propext`, `Classical.choice` and `Quot.sound`. Pair it with
`ebllm scan` on the sources, which catches `native_decide`, `implemented_by`, `unsafe`, debug
options and environment commands that an axiom report alone can miss.

## The engine

```python
from ebllm.engine import Engine, Proposal

eng = Engine(package, graph, verifiers={...}, root="main", kind="proof")
rec = eng.step(0, Proposal(obligations=[...], bridges=[...], checks={"lemma-2": formal}))
rec["label"], rec["blocking"]
```

At each step the generator's proposal adds obligations and bridges, the checks set obligation
statuses, failed checks become playbook bullets, and the playbook update passes the collapse
guard. The proof factor is forced to 0 while the graph does not certify the root. `Engine.run`
calls a generator function until a released label or the step limit.

## JSON specs

`ebllm run SPEC [--ledger FILE]` runs one step from a file like
[`examples/theorem-10-4.json`](../examples/theorem-10-4.json):

| key | meaning |
|---|---|
| `package` | the conjecture package: `name`, `domain`, `hypothesis`, `conclusion`, `barriers`, `residues` |
| `kind` | `proof` or `refutation` |
| `root` | the obligation whose certification is the result |
| `obligations` | list of obligations (`name`, `kind`, `weight`, `status`, `verifier`) |
| `bridges` | list of `[premises, conclusion, scope_loss]` |
| `checks` | obligation name → verifier |
| `verifiers` | the eight release factors → verifier |
| `model_ok` | whether a complete candidate argument exists |
| `theta` | the collapse-guard threshold (0 by default) |

A verifier in a spec is `0`, `1`, `{"cmd": [...], "expect": "regex", "cwd": "..."}` or
`{"lean": {"project": "...", "imports": [...], "theorems": [...]}}`. Paths are relative to the
directory `ebllm run` is started from. The command exits with 0 for THEOREM, COUNTEREXAMPLE or
INDEPENDENCE and with 2 otherwise, and prints the contract report of Section 32.

## Adding a control

Add a JSON file to `src/ebllm/controls/` with the fields of `ebllm.controls.Control`. Store the
factors, never the label: the label is recomputed from the factors each time, so changing a
factor is the only way to change a label.
