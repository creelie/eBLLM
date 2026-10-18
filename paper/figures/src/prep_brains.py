"""Summaries of three published wiring datasets for the brain figures.

Usage: python3 prep_brains.py WORM_EDGES WORM_TABLES FLYWIRE_FEATHER H01_SOMAS

  WORM_EDGES      herm_full_edgelist.csv: the C. elegans hermaphrodite of S. J. Cook et al., Nature 571
                  (2019) 63-71, as distributed by OpenWorm (c302)
  WORM_TABLES     CElegansNeuronTables.xls of L. R. Varshney et al., PLoS Comput. Biol. 7 (2011) e1001066
                  (WormAtlas): sensory neurons and neuron-to-muscle synapses
  FLYWIRE_FEATHER proofread_connections_783.feather of FlyWire (S. Dorkenwald et al., Nature 634 (2024)
                  124-138), Zenodo 10.5281/zenodo.10676866, CC BY 4.0
  H01_SOMAS       the soma table of H01 (A. Shapson-Coe et al., Science 384 (2024) eadk4858)

Writes data/worm.json, data/fly.npz and data/h01.npz next to this file: only derived summaries.
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")


def worm(edges_path, tables_path):
    e = pd.read_csv(edges_path, skipinitialspace=True)
    e.columns = [c.strip() for c in e.columns]
    for c in ("Source", "Target", "Type"):
        e[c] = e[c].str.strip()
    t = pd.read_excel(tables_path, sheet_name=None)
    norm = lambda s: re.sub(r"([A-Z]+)0(\d)$", r"\1\2", s)
    neurons = set(t["Connectome"].Origin) | set(t["Connectome"].Target)
    sensory = set(t["Sensory"].Neuron)
    motor = set(t["NeuronsToMuscle"].Neuron) | {"VC6"}
    nodes = sorted(set(e.Source) | set(e.Target))

    def kind(n):
        m = norm(n)
        if m in sensory:
            return "sensory"
        if m in motor:
            return "motor"
        if m in neurons:
            return "inter"
        return "muscle"
    kinds = {n: kind(n) for n in nodes}
    idx = {n: i for i, n in enumerate(nodes)}
    N = len(nodes)
    W = np.zeros((N, N))
    for s, d, w in zip(e.Source, e.Target, e.Weight):
        W[idx[s], idx[d]] += w
    A = (W + W.T) / 2
    np.fill_diagonal(A, 0)
    deg = A.sum(1)
    L = np.diag(deg) - A
    b = W.sum(0) - W.sum(1)                       # in-weight minus out-weight
    z = np.linalg.lstsq(L, b - b.mean(), rcond=None)[0]
    z -= z.mean()
    # Fiedler vector of the normalised Laplacian of the neurons
    neu = [i for i, n in enumerate(nodes) if kinds[n] != "muscle"]
    An = A[np.ix_(neu, neu)]
    dn = An.sum(1)
    keep = dn > 0
    neu = [i for i, k in zip(neu, keep) if k]
    An = A[np.ix_(neu, neu)]
    dn = An.sum(1)
    Dm = np.diag(1 / np.sqrt(dn))
    Ln = np.eye(len(neu)) - Dm @ An @ Dm
    vals, vecs = np.linalg.eigh(Ln)
    # the lowest nontrivial eigenvector that is spread over the network (participation ratio at
    # least a quarter of the neurons); the lowest ones localise on small, weakly attached groups
    j = next(k for k in range(1, len(vals)) if 1 / (vecs[:, k] ** 4).sum() >= len(neu) / 4)
    f = Dm @ vecs[:, j]
    fx = {nodes[i]: float(v) for i, v in zip(neu, f)}
    chem = [(s, d, float(w)) for s, d, w, ty in zip(e.Source, e.Target, e.Weight, e.Type) if ty == "chemical"]
    elec = [(s, d, float(w)) for s, d, w, ty in zip(e.Source, e.Target, e.Weight, e.Type) if ty == "electrical"]
    out = dict(nodes=nodes, kind=[kinds[n] for n in nodes], depth=[float(x) for x in z],
               fiedler=[fx.get(n) for n in nodes], chemical=chem, electrical=elec,
               lambda2=float(vals[j]), eigen_index=int(j),
               counts={k: sum(1 for v in kinds.values() if v == k) for k in ("sensory", "inter", "motor", "muscle")},
               synapses=dict(chemical=int(sum(w for _, _, w in chem)), electrical=int(sum(w for _, _, w in elec))))
    json.dump(out, open(os.path.join(OUT, "worm.json"), "w"))
    print("worm", N, out["counts"], out["synapses"], len(chem), len(elec))


def fly(path):
    import pyarrow.feather as feather
    cols = ["pre_pt_root_id", "post_pt_root_id", "neuropil", "syn_count",
            "gaba_avg", "ach_avg", "glut_avg", "oct_avg", "ser_avg", "da_avg"]
    df = feather.read_table(path, columns=cols).to_pandas()
    df = df[df.syn_count >= 5]
    df["neuropil"] = df["neuropil"].astype(str)
    nts = ["gaba_avg", "ach_avg", "glut_avg", "oct_avg", "ser_avg", "da_avg"]
    df["nt"] = np.argmax(df[nts].to_numpy(), axis=1)
    # the neuropil where each neuron receives most of its input
    inp = df.groupby(["post_pt_root_id", "neuropil"]).syn_count.sum().reset_index()
    home = inp.sort_values("syn_count").drop_duplicates("post_pt_root_id", keep="last")
    home = home.set_index("post_pt_root_id").neuropil
    df["src"] = df.pre_pt_root_id.map(home)
    flow = df.dropna(subset=["src"]).groupby(["src", "neuropil"]).syn_count.sum()
    nps = sorted(set(df.neuropil))
    ix = {p: i for i, p in enumerate(nps)}
    M = np.zeros((len(nps), len(nps)))
    for (a, b), v in flow.items():
        M[ix[a], ix[b]] += v
    ntm = np.zeros((len(nps), 6))
    g = df.groupby(["neuropil", "nt"]).syn_count.sum()
    for (p, k), v in g.items():
        ntm[ix[p], k] += v
    outdeg = df.groupby("pre_pt_root_id").post_pt_root_id.nunique().to_numpy()
    indeg = df.groupby("post_pt_root_id").pre_pt_root_id.nunique().to_numpy()
    neurons = len(set(df.pre_pt_root_id) | set(df.post_pt_root_id))
    np.savez_compressed(os.path.join(OUT, "fly.npz"), M=M, ntm=ntm, neuropils=np.array(nps),
                        outdeg=np.bincount(outdeg), indeg=np.bincount(indeg),
                        meta=np.array([neurons, len(df), int(df.syn_count.sum())]))
    print("fly", len(nps), "neuropils", neurons, "neurons", len(df), "connections", int(df.syn_count.sum()), "synapses")


def h01(path, n=9000, seed=7):
    s = pd.read_csv(path)
    for c in ("celltype", "layer"):
        s[c] = [str(v) if isinstance(v, str) else "unknown" for v in s[c]]
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(s), size=min(n, len(s)), replace=False)
    sub = s.iloc[np.sort(pick)]
    um = np.array([0.008, 0.008, 0.033])
    xyz = sub[["x", "y", "z"]].to_numpy() * um
    types = sorted(s.celltype.astype(str).unique())
    layers = sorted(s.layer.astype(str).unique())
    ct = pd.crosstab(s.layer.astype(str), s.celltype.astype(str)).reindex(index=layers, columns=types, fill_value=0)
    # depth profile: soma density of each type along the axis of the layers
    allxyz = s[["x", "y", "z"]].to_numpy() * um
    np.savez_compressed(os.path.join(OUT, "h01.npz"), xyz=xyz, type=np.array(list(sub.celltype), dtype="U24"),
                        layer=np.array(list(sub.layer), dtype="U24"), types=np.array(types), layers=np.array(layers),
                        crosstab=ct.to_numpy(), total=np.array([len(s)]),
                        extent=np.array([allxyz.min(0), allxyz.max(0)]),
                        allxy=allxyz[:, :2].astype(np.float32), alltype=np.array(list(s.celltype), dtype="U24"),
                        alllayer=np.array(list(s.layer), dtype="U24"))
    print("h01", len(s), dict(s.celltype.value_counts()), dict(s.layer.value_counts()))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(os.path.join(OUT, "worm.json")):
        worm(sys.argv[1], sys.argv[2])
    h01(sys.argv[4])
    fly(sys.argv[3])
