"""Data panels of the online law and the cascade (PDF, included by the TikZ figures)."""
import math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 9, "axes.titlesize": 9.5,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 7.5, "axes.linewidth": 0.6, "pdf.fonttype": 42,
})
BLUE, RED, GREEN, GOLD, GREY = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555"


def online_excess(loga, eps=0.5, theta=1e-6):
    """Excess (V_N - (A_N/L)(H + log 1/theta)) / A_N of the online rule, and log10(A_N/a_1).

    Works with logarithms of the costs so that dynamic ranges of 10^300 are fine."""
    L = math.log(1 / eps)
    loga = np.asarray(loga, dtype=float)
    logS = np.logaddexp.accumulate(loga)
    u = logS - loga[0]
    logw = (loga - logS) - math.log(2) - 2 * np.log1p(u)
    r = np.ceil((-math.log(theta) - logw) / L)
    out_x, out_y = [], []
    # running sums, scaled by the current total to avoid overflow
    for N in range(1, len(loga) + 1):
        if N > 200 and N % max(1, len(loga) // 400) and N != len(loga):
            continue
        lA = logS[N - 1]
        q = np.exp(loga[:N] - lA)  # p^(N)
        V = float((q * r[:N]).sum())  # V_N / A_N
        Hn = float(-(q * (loga[:N] - lA)).sum())
        out_x.append(u[N - 1] / math.log(10))
        out_y.append(V - (Hn + math.log(1 / theta)) / L)
    out_x, out_y = np.array(out_x), np.array(out_y)
    keep = out_x > 0
    return out_x[keep], out_y[keep]


def fig_online_panel():
    eps, theta = 0.5, 1e-6
    L = math.log(1 / eps)
    fig, ax = plt.subplots(figsize=(3.55, 2.55))
    rng = np.random.default_rng(20261018)
    for k in range(40):
        n = 3000
        drift = rng.uniform(0.01, 0.12)
        loga = drift * np.arange(n) + rng.uniform(0.5, 2.5) * rng.standard_normal(n)
        x, y = online_excess(loga, eps, theta)
        ax.plot(x, y, color=GREY, lw=0.45, alpha=0.55)
    N = 1000
    x, y = online_excess(np.arange(N) * math.log(2), eps, theta)
    ax.plot(x, y, color=RED, lw=1.2, label=r"doubling $a_n=2^{n-1}$")
    R = 10.0 ** np.logspace(-0.6, math.log10(300), 600)
    lr = np.log(R)
    ax.plot(np.log10(R), (math.log(2) + 2 * np.log1p(lr)) / L + 1, "--", color=BLUE, lw=1.0,
            label="guarantee (upper bound)")
    nec = np.log(np.log2(1 + R)) / (2 * L) - 1 - 2 * math.log(2) / L
    ax.plot(np.log10(R), nec, ":", color="k", lw=1.0, label="necessary (lower bound)")
    ax.plot([], [], color=GREY, lw=0.8, label="40 random profiles")
    ax.set_xlabel(r"$\log_{10}(A_N/a_1)$")
    ax.set_ylabel(r"excess per unit cost")
    ax.set_xscale("log")
    ax.set_xlim(0.3, 300)
    ax.set_ylim(-3, 25)
    ax.legend(loc="upper left", frameon=True, framealpha=1, edgecolor="0.8", fontsize=6.6)
    ax.grid(alpha=0.25, lw=0.4)
    fig.savefig(os.path.join(HERE, "tikz", "panel_online.pdf"), bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def cascade_cost(r, b, c, rho, eps):
    return b * r + c * (1 - rho) + c * rho * eps ** r


def fig_cascade_panel():
    b, c, eps = 1e-3, 1.0, 0.5
    L = math.log(1 / eps)
    fig, ax = plt.subplots(figsize=(3.55, 2.55))
    rs = np.arange(0, 31)
    for rho, col in [(0.5, BLUE), (0.9, GREEN), (0.99, RED)]:
        E = cascade_cost(rs, b, c, rho, eps)
        ax.plot(rs, E, "o-", color=col, ms=2.4, lw=0.9, label=rf"$\rho={rho}$")
        lo = c * (1 - rho) + b / L * (1 + math.log(c * rho * L / b))
        ax.axhline(lo, color=col, ls="--", lw=0.7)
        rstar = math.ceil(math.log(c * rho * L / b) / L)
        ax.plot([rstar], [cascade_cost(rstar, b, c, rho, eps)], marker="*", color=col, ms=7, mec="k", mew=0.4)
    ax.axhline(1.0, color="k", ls=":", lw=0.9, label="strong check alone")
    ax.set_yscale("log")
    ax.set_xlabel(r"weak runs $r$ per candidate")
    ax.set_ylabel(r"expected cost $E(r)/c$")
    ax.set_xlim(0, 30)
    ax.set_ylim(8e-3, 1.4)
    ax.legend(loc="lower left", frameon=True, framealpha=1, edgecolor="0.8", fontsize=6.6, ncol=2)
    ax.grid(alpha=0.25, lw=0.4, which="both")
    fig.savefig(os.path.join(HERE, "tikz", "panel_cascade.pdf"), bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


if __name__ == "__main__":
    fig_online_panel()
    fig_cascade_panel()
