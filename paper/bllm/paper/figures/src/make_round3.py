"""Figures of the gap law and of the three wiring diagrams (worm, fly, human cortex).

Reads the summaries written by prep_brains.py and data/idea_gap.json; the bridge simulation uses
the eBLLM package (pip install ebllm, or EBLLM_SRC=<path to eBLLM/src>).  PNG at 400 dpi.
"""
import json
import math
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "..")
if os.environ.get("EBLLM_SRC"):
    sys.path.insert(0, os.environ["EBLLM_SRC"])

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY, PURPLE = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555", "#5b2a86"
DPI = 400


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=DPI, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def title(ax, s):
    ax.set_title(s, loc="left", fontweight="bold")


# -- the gap law ----------------------------------------------------------------------------------
def fig_gap():
    d = json.load(open(os.path.join(DATA, "idea_gap.json")))
    ax_name = "opportunity"
    names = list(d["shares"])
    classes = d["axes"][ax_name]
    S = np.array([d["shares"][n][ax_name] for n in names], float)
    S /= S.sum(1, keepdims=True)
    pi = S[0]
    r = np.sqrt(pi) / np.sqrt(pi).sum()
    opt = np.sqrt(pi).sum() ** 2
    rows = np.vstack([S, r])
    labels = names + ["square-root"]

    fig = plt.figure(figsize=(7.3, 2.75))
    ax = fig.add_axes([-0.03, 0.0, 0.42, 0.95], projection="3d")
    short = ["Human", "Claude", "Gemini", "OSS-20B", "OSS-120B", "5.4-mini", "Qwen-8B", "Qwen-32B",
             "DS-Flash", "DS-Pro", "sqrt"]
    nx, ny = rows.shape
    xs, ys = np.meshgrid(np.arange(nx), np.arange(ny), indexing="ij")
    cols = []
    for i in range(nx):
        c = GREEN if i == 0 else (PURPLE if i == nx - 1 else BLUE)
        cols += [c] * ny
    ax.bar3d(xs.ravel() - 0.32, ys.ravel() - 0.32, 0 * xs.ravel(), 0.64, 0.64, rows.ravel(),
             color=cols, alpha=0.9, edgecolor="k", linewidth=0.15, shade=True)
    ax.set_xticks(range(nx))
    ax.set_xticklabels(short, fontsize=5, rotation=0, ha="right", va="top")
    ax.set_yticks(range(ny))
    ax.set_yticklabels(["puzzle", "explanation", "scope", "evidence", "bridge", "failure", "resource"],
                       fontsize=5.2, ha="left", va="center")
    ax.set_zticks([0, 0.2, 0.4, 0.6])
    ax.tick_params(axis="z", labelsize=5.5, pad=0)
    ax.tick_params(axis="x", pad=-5)
    ax.tick_params(axis="y", pad=-4)
    ax.view_init(elev=24, azim=-35)
    ax.set_box_aspect((2.2, 1.1, 0.8))
    ax.set_title("(a) shares of seven kinds of research opportunity", loc="left", fontweight="bold",
                 fontsize=8, y=0.98)

    ax = fig.add_axes([0.44, 0.17, 0.25, 0.68])
    lam = np.linspace(0.0, 1.0, 401)
    for i, n in enumerate(names[1:], 1):
        q = S[i]
        cost = [(pi / ((1 - t) * q + t * r)).sum() for t in lam]
        ax.plot(lam, np.array(cost) / opt, color=plt.cm.viridis(i / 10), lw=0.9, label=n)
    ax.plot(lam[8:], 1 / lam[8:], ":", color=RED, lw=1.0, label=r"bound $1/\lambda$")
    ax.axhline(7 / opt, color=GREEN, lw=0.9, ls="--", label="copy the humans ($K$)")
    ax.axhline(1, color="k", lw=0.8)
    ax.set_ylim(0.9, 4.5)
    ax.set_xlabel(r"weight $\lambda$ on square-root sampling")
    ax.set_ylabel(r"$C(\pi,q_\lambda)\,/\,e^{H_{1/2}(\pi)}$")
    ax.legend(fontsize=4.6, ncol=1, frameon=False, loc="upper right", handlelength=1.4, labelspacing=0.15)
    title(ax, "(b) the gap and its closure")

    ax = fig.add_axes([0.75, 0.17, 0.25, 0.68])
    try:
        from ebllm.bllm.gap import bridge_simulation
        q = S[names.index("GPT-OSS-120B")]
        w = 100
        for lamb, col, lab in ((0.5, BLUE, r"BLLM, $\lambda=0.5$"), (1.0, PURPLE, r"BLLM, $\lambda=1$")):
            res = [bridge_simulation(list(pi), list(q), problems=3000, lam=lamb, window=w, seed=s) for s in range(6)]
            b = np.mean([x["bllm"] for x in res], 0)
            ax.plot(np.arange(1, len(b) + 1) * w, b, color=col, lw=1.0, label=lab)
        llm = np.mean([x["llm"] for x in res], 0)
        o = np.mean([x["optimum"] for x in res], 0)
        ax.plot(np.arange(1, len(llm) + 1) * w, llm, color=GOLD, lw=1.0, label="GPT-OSS-120B alone")
        ax.plot(np.arange(1, len(o) + 1) * w, o, color="k", lw=0.8, label="square-root, true needs")
    except ImportError:
        ax.text(0.5, 0.5, "install ebllm", transform=ax.transAxes, ha="center")
    ax.set_xlabel("problems solved")
    ax.set_ylabel("proposals per problem")
    ax.set_ylim(4, 32)
    ax.legend(fontsize=5, frameon=False, loc="center right")
    title(ax, "(c) a spiking selector learns it")
    save(fig, "fig_gap")


# -- the worm --------------------------------------------------------------------------------------
KIND_COL = {"sensory": "#d62728", "inter": "#1f4e99", "motor": "#1b7837", "muscle": "#8c6d31"}


def fig_worm():
    w = json.load(open(os.path.join(DATA, "worm.json")))
    nodes, kind, z = w["nodes"], w["kind"], np.array(w["depth"])
    idx = {n: i for i, n in enumerate(nodes)}
    fx = np.array([np.nan if v is None else v for v in w["fiedler"]])
    neu = ~np.isnan(fx)
    fxs = np.full(len(fx), np.nan)
    rk = np.argsort(np.argsort(fx[neu]))
    fxs[neu] = rk / (neu.sum() - 1)
    mus = [i for i, k in enumerate(kind) if k == "muscle"]
    mus_sorted = sorted(mus, key=lambda i: (nodes[i][0], nodes[i]))
    X = fxs.copy()
    for j, i in enumerate(mus_sorted):
        X[i] = j / max(1, len(mus_sorted) - 1)
    Y = z.copy()

    fig = plt.figure(figsize=(7.3, 3.1))
    ax = fig.add_axes([0.0, 0.0, 0.5, 0.92])
    segs, lw = [], []
    for s, t, wt in w["chemical"]:
        segs.append([(X[idx[s]], Y[idx[s]]), (X[idx[t]], Y[idx[t]])])
        lw.append(0.08 + 0.05 * math.log1p(wt))
    ax.add_collection(LineCollection(segs, colors="#777777", linewidths=lw, alpha=0.18, zorder=1))
    segs = [[(X[idx[s]], Y[idx[s]]), (X[idx[t]], Y[idx[t]])] for s, t, _ in w["electrical"]]
    ax.add_collection(LineCollection(segs, colors="#2b8cbe", linewidths=0.25, alpha=0.35, zorder=2))
    for k, c in KIND_COL.items():
        m = np.array([kk == k for kk in kind])
        ax.scatter(X[m], Y[m], s=7 if k != "muscle" else 4, c=c, edgecolors="white", linewidths=0.2,
                   zorder=3, label=f"{k} ({m.sum()})")
    for n in ("ASHL", "AWCL", "ASEL", "AFDL", "AIYL", "AIBL", "RIAL", "AVAL", "AVBL", "AVDL", "PVCL",
              "DA01", "VB01", "DD01", "RMDDL", "SMDVL", "dBWML10", "vBWMR12"):
        if n in idx:
            ax.annotate(n, (X[idx[n]], Y[idx[n]]), fontsize=4.6, xytext=(2, 1.5), textcoords="offset points",
                        zorder=4)
    ax.set_xlim(-0.03, 1.03)
    ax.set_xlabel("spectral rank of the neurons (Laplacian eigenvector); muscles spread by name")
    ax.set_ylabel("processing depth $z$, $Lz=w_{\\mathrm{in}}-w_{\\mathrm{out}}$")
    ax.legend(loc="lower left", fontsize=5.5, frameon=True, framealpha=0.85, markerscale=1.4)
    ax.text(0.01, 0.985, f"{w['synapses']['chemical']:,} chemical synapses in {len(w['chemical']):,} connections (grey);\n"
            f"{w['synapses']['electrical']:,} gap-junction contacts in {len(w['electrical']):,} (blue)",
            transform=ax.transAxes, fontsize=5.2, va="top")
    title(ax, "(a) the C. elegans hermaphrodite, Cook et al. 2019")

    # class-to-class synapses, 3D
    K = list(KIND_COL)
    Mc = np.zeros((4, 4))
    for s, t, wt in w["chemical"]:
        Mc[K.index(kind[idx[s]]), K.index(kind[idx[t]])] += wt
    ax = fig.add_axes([0.51, 0.06, 0.25, 0.82], projection="3d")
    xs, ys = np.meshgrid(np.arange(4), np.arange(4), indexing="ij")
    cols = [KIND_COL[K[i]] for i in xs.ravel()]
    ax.bar3d(xs.ravel() - 0.3, ys.ravel() - 0.3, 0, 0.6, 0.6, Mc.ravel(), color=cols, alpha=0.88,
             edgecolor="k", linewidth=0.2)
    ax.set_xticks(range(4)); ax.set_xticklabels(["sens.", "inter", "motor", "musc."], fontsize=6)
    ax.set_yticks(range(4)); ax.set_yticklabels(["sens.", "inter", "motor", "musc."], fontsize=6)
    ax.set_xlabel("from", labelpad=-6, fontsize=7); ax.set_ylabel("to", labelpad=-6, fontsize=7)
    ax.set_zlabel("synapses", labelpad=-7, fontsize=6)
    ax.tick_params(axis="z", labelsize=5.5, pad=0)
    ax.tick_params(axis="x", pad=-4); ax.tick_params(axis="y", pad=-4)
    ax.view_init(elev=30, azim=-52)
    ax.set_title("(b) chemical synapses, class to class", loc="left", fontweight="bold", fontsize=8.5, y=1.04)

    ax = fig.add_axes([0.875, 0.16, 0.125, 0.72])
    for k, c in KIND_COL.items():
        m = np.array([kk == k for kk in kind])
        ax.hist(z[m], bins=np.linspace(z.min(), z.max(), 26), orientation="horizontal", histtype="stepfilled",
                alpha=0.45, color=c, edgecolor=c, linewidth=0.6)
    ax.set_ylabel("processing depth $z$")
    ax.set_xlabel("cells")
    title(ax, "(c) depth by class")
    save(fig, "fig_worm")


# -- the fly ---------------------------------------------------------------------------------------
GROUPS = [   # the FlyWire super-groups of neuropils, with their abbreviations
    ("OL", ["LA", "ME", "AME", "LO", "LOP", "OCG"]),
    ("AL", ["AL"]),
    ("LH", ["LH"]),
    ("MB", ["MB_CA", "MB_PED", "MB_VL", "MB_ML"]),
    ("SNP", ["SLP", "SIP", "SMP"]),
    ("INP", ["CRE", "SCL", "ICL", "IB", "ATL"]),
    ("LX", ["BU", "LAL", "GA"]),
    ("CX", ["FB", "EB", "PB", "NO"]),
    ("VLNP", ["AOTU", "AVLP", "PVLP", "PLP", "WED"]),
    ("VMNP", ["VES", "EPA", "GOR", "SPS", "IPS"]),
    ("PENP", ["SAD", "AMMC", "FLA", "CAN", "PRW"]),
    ("GNG", ["GNG"]),
    ("UN", ["UNASGD"]),
]


def fig_fly():
    d = np.load(os.path.join(DATA, "fly.npz"))
    M, ntm, nps = d["M"], d["ntm"], [str(x) for x in d["neuropils"]]
    neurons, conns, syn = d["meta"]
    order, bounds, gnames = [], [], []
    for g, members in GROUPS:
        start = len(order)
        for m in members:
            for side in ("_L", "_R", ""):
                if m + side in nps and nps.index(m + side) not in order:
                    order.append(nps.index(m + side))
        bounds.append((start, len(order)))
        gnames.append(g)
    assert sorted(order) == list(range(len(nps))), set(range(len(nps))) - set(order)
    Mo = M[np.ix_(order, order)]
    fig = plt.figure(figsize=(7.3, 3.25))
    ax = fig.add_axes([0.0, 0.06, 0.40, 0.84])
    im = ax.imshow(Mo + 1, norm=LogNorm(vmin=10, vmax=Mo.max()), cmap="magma_r", interpolation="nearest")
    for a, b in bounds:
        ax.axhline(a - 0.5, color="#3a6ea5", lw=0.35)
        ax.axvline(a - 0.5, color="#3a6ea5", lw=0.35)
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([nps[i] for i in order], rotation=90, fontsize=2.9)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([nps[i] for i in order], fontsize=2.9)
    ax.tick_params(length=1, pad=0.5)
    cax = fig.add_axes([0.405, 0.2, 0.008, 0.6])
    cb = fig.colorbar(im, cax=cax)
    cb.ax.set_title("synapses", fontsize=6, pad=3)
    cb.ax.tick_params(labelsize=5.5)
    ax.set_xlabel("neuropil of the synapse", fontsize=7)
    ax.set_ylabel("neuropil of the input of the presynaptic neuron", fontsize=7)
    title(ax, f"(a) information flow through {len(nps)} neuropils")

    nt_names = ["GABA", "ACh", "Glu", "Oct", "Ser", "DA"]
    G = np.array([ntm[[order[i] for i in range(a, b)]].sum(0) for a, b in bounds])
    G = G / G.sum(1, keepdims=True)
    ax = fig.add_axes([0.45, 0.06, 0.29, 0.84], projection="3d")
    ng = len(gnames)
    xs, ys = np.meshgrid(np.arange(ng), np.arange(6), indexing="ij")
    ntc = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e", "#8c564b"]
    ax.bar3d(xs.ravel() - 0.3, ys.ravel() - 0.3, 0, 0.6, 0.6, G.ravel(), color=[ntc[j] for j in ys.ravel()],
             alpha=0.9, edgecolor="k", linewidth=0.15)
    ax.set_xticks(range(ng)); ax.set_xticklabels(gnames, fontsize=4.4, rotation=35, ha="right", va="top")
    ax.set_zticks([0, 0.2, 0.4, 0.6, 0.8])
    ax.set_yticks(range(6)); ax.set_yticklabels(nt_names, fontsize=5.5, ha="left")
    ax.tick_params(axis="z", labelsize=5.5, pad=0); ax.tick_params(axis="x", pad=-4); ax.tick_params(axis="y", pad=-3)
    ax.view_init(elev=26, azim=-62)
    ax.set_box_aspect((1.8, 1.0, 0.8))
    ax.set_title("(b) transmitters: fraction of synapses", loc="left", fontweight="bold", fontsize=8.5, y=1.02)
    ax.text2D(0.02, 0.9, "OL optic, AL antennal lobe, LH lateral horn, MB mushroom body,\n"
              "SNP superior, INP inferior, LX lateral complex, CX central complex,\n"
              "VLNP/VMNP ventrolateral/medial, PENP periesophageal,\nGNG gnathal ganglion, UN unassigned",
              transform=ax.transAxes, fontsize=4.6, va="top")

    ax = fig.add_axes([0.85, 0.17, 0.15, 0.68])
    for key, col, lab in (("outdeg", RED, "output partners"), ("indeg", BLUE, "input partners")):
        h = d[key].astype(float)
        k = np.nonzero(h)[0]
        ax.loglog(k[k > 0], h[k[k > 0]], ".", ms=1.4, color=col, label=lab, alpha=0.7)
    ax.set_xlabel("partners per neuron")
    ax.set_ylabel("neurons")
    ax.legend(fontsize=5.5, frameon=False, markerscale=4)
    ax.text(0.03, 0.12, f"{neurons:,} neurons\n{conns/1e6:.2f} M links\n{syn/1e6:.1f} M synapses\n($\\geq 5$ per link)",
            transform=ax.transAxes, fontsize=5, ha="left", va="bottom")
    title(ax, "(c) degrees")
    save(fig, "fig_fly")


# -- the human cortex ------------------------------------------------------------------------------
TYPE_COL = {"PYRAMIDAL": "#b2182b", "INTERNEURON": "#1f4e99", "SPINY_STELLATE": "#ff7f0e",
            "ASTROCYTE": "#1b7837", "OLIGO": "#9e9ac8", "MG_OPC": "#8c6d31", "BLOOD_VESSEL_CELL": "#e377c2"}


def fig_cortex():
    h = np.load(os.path.join(DATA, "h01.npz"))
    xyz, typ, lay = h["xyz"], h["type"], h["layer"]
    ok = (xyz > 1).all(1)
    xyz, typ, lay = xyz[ok], typ[ok], lay[ok]
    allxy, alltype, alllayer = h["allxy"], h["alltype"], h["alllayer"]
    okall = (allxy > 1).all(1)
    allxy, alltype, alllayer = allxy[okall], alltype[okall], alllayer[okall]
    L1 = np.median(allxy[alllayer == "Layer 1"], 0)
    WM = np.median(allxy[alllayer == "White matter"], 0)
    u = (WM - L1) / np.linalg.norm(WM - L1)
    depth = (allxy - L1) @ u
    depth -= np.percentile(depth[alllayer == "Layer 1"], 2)     # 0 at the outer edge of layer 1

    fig = plt.figure(figsize=(7.3, 3.0))
    ax = fig.add_axes([-0.02, 0.0, 0.44, 0.95], projection="3d")
    for t, c in TYPE_COL.items():
        m = typ == t
        s = 2.2 if t in ("PYRAMIDAL", "INTERNEURON", "SPINY_STELLATE") else 0.9
        ax.scatter(xyz[m, 0], xyz[m, 1], xyz[m, 2], s=s, c=c, alpha=0.75, linewidths=0,
                   label=t.replace("_", " ").lower().replace("mg opc", "microglia, OPC"), depthshade=False)
    ax.set_xlabel("x (µm)", labelpad=-6, fontsize=7); ax.set_ylabel("y (µm)", labelpad=-6, fontsize=7)
    ax.set_zlabel("z (µm)", labelpad=-8, fontsize=7)
    ax.tick_params(labelsize=5, pad=-2)
    ax.set_zticks([0, 80, 160])
    ax.set_box_aspect((3.9, 2.4, 0.55))
    ax.view_init(elev=38, azim=-115)
    ax.legend(loc="upper left", fontsize=4.8, markerscale=3, frameon=False, bbox_to_anchor=(0.0, 0.92))
    ax.set_title(f"(a) H01: {len(xyz):,} of {int(h['total'][0]):,} somas, human temporal cortex", loc="left",
                 fontweight="bold", fontsize=8)

    ax = fig.add_axes([0.47, 0.16, 0.27, 0.72])
    bins = np.linspace(np.percentile(depth, 0.5), np.percentile(depth, 99.5), 70)
    for t in ("PYRAMIDAL", "INTERNEURON", "ASTROCYTE", "OLIGO", "MG_OPC", "SPINY_STELLATE"):
        m = alltype == t
        hh, e = np.histogram(depth[m], bins=bins)
        ax.plot(0.5 * (e[1:] + e[:-1]), hh, color=TYPE_COL[t], lw=0.9,
                label=t.replace("_", " ").lower().replace("mg opc", "microglia, OPC"))
    for l in ("Layer 2", "Layer 3", "Layer 4", "Layer 5", "Layer 6", "White matter"):
        prev = {"Layer 2": "Layer 1", "Layer 3": "Layer 2", "Layer 4": "Layer 3", "Layer 5": "Layer 4",
                "Layer 6": "Layer 5", "White matter": "Layer 6"}[l]
        b = 0.5 * (np.median(depth[alllayer == prev]) + np.median(depth[alllayer == l]))
        ax.axvline(b, color=GREY, lw=0.4, ls="--")
    centres = {l: np.median(depth[alllayer == l]) for l in ("Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5",
                                                              "Layer 6", "White matter")}
    for l, c in centres.items():
        ax.text(c, 1.01, l.replace("Layer ", "L").replace("White matter", "WM"), transform=ax.get_xaxis_transform(),
                ha="center", fontsize=6)
    ax.set_xlabel("depth across the layers, from the outer edge of layer 1 (µm)", fontsize=7.5)
    ax.set_ylabel("somas per bin")
    ax.legend(fontsize=5, frameon=False, loc="upper right")
    ax.set_title("(b) cell types across the layers", loc="left", fontweight="bold", y=1.07)

    layers = [str(x) for x in h["layers"]][:7]
    types = [str(x) for x in h["types"]]
    ct = h["crosstab"][:7]
    show = ["PYRAMIDAL", "INTERNEURON", "SPINY_STELLATE", "ASTROCYTE", "OLIGO", "MG_OPC"]
    ax = fig.add_axes([0.81, 0.16, 0.19, 0.72])
    left = np.zeros(len(layers))
    for t in show:
        v = ct[:, types.index(t)] / ct.sum(1)
        ax.barh(range(len(layers)), v, left=left, color=TYPE_COL[t], height=0.78, edgecolor="white", linewidth=0.3)
        left += v
    ax.barh(range(len(layers)), 1 - left, left=left, color="#dddddd", height=0.78)
    ax.set_yticks(range(len(layers)))
    ax.set_yticklabels([l.replace("White matter", "white m.") for l in layers], fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel("fraction of somas")
    ax.set_xlim(0, 1)
    title(ax, "(c) composition")
    save(fig, "fig_cortex")


if __name__ == "__main__":
    which = sys.argv[1:] or ["gap", "worm", "fly", "cortex"]
    for w in which:
        globals()["fig_" + w]()
        print("wrote fig_" + w)
