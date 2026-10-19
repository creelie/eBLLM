"""Data figures of the BLLM paper (PNG at 300 dpi)."""
import math, heapq, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib import cm, colors
import mpmath as mp

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 9, "axes.titlesize": 9.5,
    "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 7.5, "axes.linewidth": 0.6, "savefig.dpi": 300,
})
BLUE, RED, GREEN, GOLD, GREY, PURPLE = "#1f4e99", "#b2182b", "#1b7837", "#d08c00", "#555555", "#6a3d9a"

def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

def huffman_len(w, D=2):
    n = len(w)
    if n == 1:
        return 0.0
    h = list(w) + [0.0] * ((-(n - 1)) % (D - 1))
    heapq.heapify(h); cost = 0.0
    while len(h) > 1:
        t = sum(heapq.heappop(h) for _ in range(D)); cost += t; heapq.heappush(h, t)
    return cost

def H(p):
    p = np.asarray(p); p = p[p > 0]
    return float(-(p * np.log(p)).sum())

# ---------------------------------------------------------------- schedule3d
def fig_schedule3d():
    n = 16
    a = np.array([1.0 / (i + 1) ** 1.3 for i in range(n)]); A = a.sum(); p = a / A
    L = math.log(2)
    thetas = [1e-2, 1e-4, 1e-6, 1e-8]
    fig = plt.figure(figsize=(7.0, 2.9))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    cmap = plt.get_cmap("viridis")
    for j, th in enumerate(thetas):
        r = np.ceil(np.log(1 / (th * p)) / L)
        ax.bar3d(np.arange(n), np.full(n, j) - 0.3, np.zeros(n), 0.7, 0.6, r,
                 color=cmap(0.15 + 0.22 * j), edgecolor="k", linewidth=0.15, shade=True, alpha=0.95)
    ax.set_xlabel("item $i$ (cost decreasing)", labelpad=-2)
    ax.set_ylabel(r"budget $\theta$", labelpad=-1)
    ax.set_zlabel("repetitions $r_i$", labelpad=-3)
    ax.set_yticks(range(4)); ax.set_yticklabels([r"$10^{-2}$", r"$10^{-4}$", r"$10^{-6}$", r"$10^{-8}$"])
    ax.set_xticks([0, 5, 10, 15]); ax.set_xticklabels(["1", "6", "11", "16"])
    ax.tick_params(pad=-2)
    ax.view_init(elev=24, azim=-58)
    ax.set_title(r"(a) ceiling schedule, $a_i\propto i^{-1.3}$, $\varepsilon=1/2$", pad=2)
    ax2 = fig.add_subplot(1, 2, 2)
    ths = np.logspace(-12, -0.5, 60)
    for (lab, aa, col) in [("uniform, $n=16$", np.ones(n), BLUE), (r"$a_i\propto i^{-1.3}$", a, GREEN),
                           (r"$a_i\propto 2^{-i}$", np.array([2.0 ** -i for i in range(n)]), GOLD)]:
        AA = aa.sum(); pp = aa / AA; Hp = H(pp)
        V = [sum(x * math.ceil(math.log(1 / (t * q)) / L) for x, q in zip(aa, pp)) / AA for t in ths]
        lo = [(Hp + math.log(1 / t)) / L for t in ths]
        ax2.plot(np.log10(1 / ths), V, color=col, lw=1.2, label=lab + r", $V(r)/A$")
        ax2.plot(np.log10(1 / ths), lo, color=col, lw=0.8, ls="--")
    ax2.set_xlabel(r"$\log_{10}(1/\theta)$"); ax2.set_ylabel("verification cost per unit of cost")
    ax2.set_title(r"(b) ceiling schedule against $(H(p)+\log\frac{1}{\theta})/L$ (dashed)")
    ax2.legend(frameon=False, loc="upper left"); ax2.grid(alpha=0.25, lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_schedule3d")

# ---------------------------------------------------------------- huffman3d
def fig_huffman3d():
    rng = np.random.default_rng(5)
    dists = []
    names = []
    for n in [3, 5, 8, 12]:
        dists.append(np.ones(n) / n); names.append(f"U{n}")
    for z in [0.8, 1.2, 2.0]:
        w = np.array([1 / (i + 1) ** z for i in range(10)]); dists.append(w / w.sum()); names.append(f"Z{z}")
    for r in [0.5, 0.7, 0.9]:
        w = np.array([r ** i for i in range(14)]); dists.append(w / w.sum()); names.append(f"G{r}")
    for j in range(2):
        w = rng.dirichlet(np.ones(9) * 0.6); dists.append(w); names.append(f"R{j+1}")
    k = len(dists)
    Hb = [H(d) / math.log(2) for d in dists]
    Lh = [huffman_len(d) for d in dists]
    fig = plt.figure(figsize=(7.0, 2.8))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    rows = [(np.array(Hb), r"$H_2(p)$", BLUE), (np.array(Lh), "Huffman", GOLD), (np.array(Hb) + 1, r"$H_2(p)+1$", RED)]
    for j, (vals, lab, col) in enumerate(rows):
        ax.bar3d(np.arange(k) - 0.3, np.full(k, j) - 0.3, np.zeros(k), 0.6, 0.6, vals, color=col,
                 edgecolor="k", linewidth=0.15, alpha=0.9, shade=True)
    ax.set_yticks(range(3)); ax.set_yticklabels([r"$H_2$", r"$\bar\ell_{\rm Huff}$", r"$H_2{+}1$"])
    ax.set_xticks(range(0, k, 2)); ax.set_xticklabels([str(i + 1) for i in range(0, k, 2)], fontsize=6.5)
    ax.set_xlabel("distribution", labelpad=-4)
    ax.set_zlabel("bits", labelpad=-4); ax.tick_params(pad=-3)
    ax.view_init(elev=22, azim=-62)
    ax.set_title(r"(a) $V^*(2^{-k})/A-k$ equals the Huffman length", pad=2)
    ax2 = fig.add_subplot(1, 2, 2)
    red = [l - h for l, h in zip(Lh, Hb)]
    ax2.bar(range(k), red, color=[GOLD if x > 1e-12 else GREEN for x in red], edgecolor="k", lw=0.3)
    ax2.axhline(1, color=RED, lw=0.8, ls="--"); ax2.axhline(0, color=BLUE, lw=0.8)
    ax2.set_xticks(range(k)); ax2.set_xticklabels([f"{i+1}\n{nm}" for i, nm in enumerate(names)], fontsize=6)
    ax2.set_ylabel(r"$\bar\ell_{\rm Huff}-H_2(p)$ (bits)")
    ax2.set_ylim(-0.05, 1.1)
    ax2.set_title("(b) redundancy lies in $[0,1)$; zero exactly for dyadic $p$")
    ax2.grid(axis="y", alpha=0.25, lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_huffman3d")

# ---------------------------------------------------------------- gating
def fig_gating():
    fig = plt.figure(figsize=(7.0, 2.8))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    n = np.arange(1, 201); rho = np.linspace(0.005, 0.2, 60)
    N, R = np.meshgrid(n, rho)
    Z = -(N - 1) * np.log10(1 - R)
    ax.plot_surface(N, R, Z, cmap="magma", linewidth=0, antialiased=True, rstride=2, cstride=4, alpha=0.95)
    ax.set_xlabel("steps $n$", labelpad=-3); ax.set_ylabel(r"error $\rho$", labelpad=-2)
    ax.set_zlabel(r"$\log_{10}$ cost ratio", labelpad=-3); ax.tick_params(pad=-2)
    ax.view_init(elev=24, azim=-128)
    ax.set_title(r"(a) outcome/step cost $=(1-\rho)^{-(n-1)}$", pad=2)
    ax2 = fig.add_subplot(1, 2, 2)
    zeta = 0.1; ell = math.log(1 / (1 - zeta))
    nn = np.arange(2, 401)
    for rho_, col in [(0.02, BLUE), (0.05, GREEN), (0.1, RED)]:
        eta = 0.0
        dstep = (1 - rho_) * (1 - eta) * ell / (rho_ * nn)            # sufficient
        dnec = (1 - rho_) * (1 - eta) * ell / (rho_ * (nn - ell))      # necessary
        c = (1 - rho_) ** nn
        dout = zeta * c / ((1 - zeta) * (1 - c))
        ax2.fill_between(nn, dstep, np.minimum(dnec, 1), color=col, alpha=0.18, lw=0)
        ax2.plot(nn, np.minimum(dstep, 1), color=col, lw=1.1, label=rf"step, $\rho={rho_}$")
        ax2.plot(nn, dout, color=col, lw=1.1, ls="--", label=rf"outcome, $\rho={rho_}$")
    ax2.set_yscale("log"); ax2.set_ylim(1e-26, 2)
    ax2.set_xlabel("steps $n$"); ax2.set_ylabel(r"false-accept rate allowed")
    ax2.set_title(r"(b) verifier quality for precision $0.9$")
    ax2.legend(frameon=True, framealpha=1, edgecolor="0.7", ncol=2, loc="lower left", fontsize=6.5); ax2.grid(alpha=0.25, lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_gating")

# ---------------------------------------------------------------- price of soundness
def fig_price():
    mp.mp.dps = 25
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7))
    e = np.logspace(-3, 0.7, 70)
    Hs = []
    for x in e:
        p = 1 + x; z = mp.zeta(p); dz = mp.zeta(p, 1, 1)
        Hs.append(float(mp.log(z) - p * dz / z))
    Hs = np.array(Hs)
    for th, col in [(1e-3, BLUE), (1e-9, RED)]:
        ax.loglog(e, (Hs + math.log(1 / th)) / math.log(2), color=col, lw=1.2,
                  label=rf"$(H+\log\frac{{1}}{{\theta}})/\log 2$, $\theta=10^{{{int(round(math.log10(th)))}}}$")
    ax.loglog(e, 1 / (e * math.log(2)), color=GREY, lw=0.8, ls="--", label=r"$1/((p-1)\log 2)$")
    ax.loglog(e, Hs / math.log(2), color=GREEN, lw=1.0, ls=":", label=r"$H(p)/\log 2$")
    ax.set_xlabel(r"$p-1$ for costs $a_n=n^{-p}$"); ax.set_ylabel(r"lower bound for $V^*/A$ ($\varepsilon=\frac{1}{2}$)")
    ax.set_title("(a) price of soundness of a power-law takeoff")
    ax.legend(frameon=False, loc="lower left", fontsize=6.8); ax.grid(alpha=0.25, lw=0.4, which="both")
    # (b) logarithmic families, condensed partial sums
    K = np.arange(1, 400)
    for b, col in [(1.5, RED), (2.0, GOLD), (2.5, GREEN)]:
        x = K * math.log(2)
        ent = (x + b * np.log(x)) / x ** b              # condensed a log(1/a) at n = 2^k
        ax2.plot(K, np.cumsum(ent), color=col, lw=1.2, label=rf"$\sum a_n\log\frac{{1}}{{a_n}}$, $\beta={b}$")
        ax2.plot(K, np.cumsum(x ** (-b)), color=col, lw=0.9, ls="--", label=rf"$\sum a_n$, $\beta={b}$")
    ax2.set_xlabel(r"$k=\log_2 N$"); ax2.set_ylabel("condensed partial sums")
    ax2.set_title(r"(b) $a_n=1/(n\log^\beta n)$: the soundness gap $1<\beta\leq 2$")
    ax2.legend(frameon=True, framealpha=1, edgecolor="0.8", ncol=2, fontsize=6.3, loc="upper right"); ax2.grid(alpha=0.25, lw=0.4)
    ax2.set_ylim(0, 19)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_price")

# ---------------------------------------------------------------- branching
def survival_poisson(m):
    if m <= 1: return 0.0
    lo, hi = 1e-4 * (m - 1), 1.0
    g = lambda q: -math.expm1(-m * q) - q
    for _ in range(200):
        c = (lo + hi) / 2
        if g(c) > 0: lo = c
        else: hi = c
    return lo

def fig_branching():
    fig = plt.figure(figsize=(7.0, 2.8))
    ax = fig.add_subplot(1, 2, 1)
    ms = np.linspace(0.9, 2.0, 200)
    qs = np.array([survival_poisson(m) for m in ms])
    ax.plot(ms, qs, color=BLUE, lw=1.3, label="Poisson offspring, exact")
    ax.plot(ms, np.clip(2 * (ms - 1) / ms ** 2, 0, None), color=RED, lw=1.0, ls="--", label=r"lower bound $2(m-1)/f''(1)$")
    up = np.where(ms > 1, 2 * (ms - 1) / (ms ** 2 * (1 - qs)), 0)
    up = np.where(up <= 1.0, up, np.nan)
    ax.plot(ms, up, color=GREEN, lw=1.0, ls=":", label=r"upper bound $2(m-1)/f''(1-q)$")
    ax.axvline(1, color=GREY, lw=0.6)
    ax.set_xlabel("mean accepted good offspring $m$"); ax.set_ylabel("probability of takeoff")
    ax.set_title("(a) takeoff threshold and near-critical slope")
    ax.legend(frameon=False, loc="lower right", fontsize=6.8); ax.grid(alpha=0.25, lw=0.4); ax.set_ylim(0, 1.02)
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    m = np.linspace(1.05, 2.0, 40); K = np.arange(1, 41)
    M, KK = np.meshgrid(m, K)
    delta = 1e-3
    fixed = np.log10(delta * (M ** KK - 1) / (M - 1))
    amp = np.log10(np.array([[sum((mm ** k) * (2 * mm) ** (-k) for k in range(kk)) for mm in m] for kk in K]))
    ax2.plot_surface(M, KK, fixed, cmap="inferno", alpha=0.9, linewidth=0, rstride=1, cstride=1)
    ax2.plot_surface(M, KK, amp, color="#4daf4a", alpha=0.8, linewidth=0)
    ax2.set_xlabel("$m$", labelpad=-3); ax2.set_ylabel("generations $K$", labelpad=-3)
    ax2.set_zlabel(r"$\log_{10}\sum_{k<K} m^k\delta_k$", labelpad=-3); ax2.tick_params(pad=-2)
    ax2.view_init(elev=22, azim=-130)
    ax2.set_title(r"(b) fixed $\delta=10^{-3}$ (shaded), $\delta_k=(2m)^{-k}$ (green)", pad=2)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_branching")

# ---------------------------------------------------------------- renyi
def fig_renyi():
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.6))
    s = np.logspace(-3, 0.5, 80); th = 1e-2
    for (lab, a, col) in [("uniform, $n=1000$", np.ones(1000), BLUE),
                          (r"Zipf $a_i\propto i^{-1}$, $n=1000$", 1 / np.arange(1, 1001), GREEN),
                          (r"geometric $a_i\propto 0.9^i$", 0.9 ** np.arange(200), GOLD)]:
        A = a.sum(); p = a / A
        V = [th ** (-x) * (np.sum(p ** (1 / (1 + x)))) ** (1 + x) for x in s]
        ax.loglog(s, V, color=col, lw=1.2, label=lab)
        Hp = H(p)
        ax.loglog(s, 1 + s * (Hp + math.log(1 / th)), color=col, lw=0.8, ls="--")
    ax.set_xlabel("polynomial order $s$"); ax.set_ylabel(r"$V^*_s(\theta)/A$, $\theta=10^{-2}$")
    ax.set_title(r"(a) R\'enyi law and its Shannon tangent (dashed)".replace(r"\'e", "é"))
    ax.legend(frameon=False, loc="upper left"); ax.grid(alpha=0.25, lw=0.4, which="both")
    alphas = np.linspace(0.02, 0.999, 100)
    for (lab, a, col) in [("Zipf, $n=1000$", 1 / np.arange(1, 1001), GREEN),
                          (r"geometric $0.9^i$", 0.9 ** np.arange(200), GOLD)]:
        p = a / a.sum()
        Ha = [math.log(np.sum(p ** al)) / (1 - al) for al in alphas]
        ax2.plot(alphas, Ha, color=col, lw=1.2, label=lab)
        ax2.axhline(H(p), color=col, lw=0.6, ls=":")
    ax2.set_xlabel(r"$\alpha=1/(1+s)$"); ax2.set_ylabel(r"$H_\alpha(p)$ (nats)")
    ax2.set_title(r"(b) Rényi entropies decrease to $H(p)$ as $\alpha\to1$")
    ax2.legend(frameon=False); ax2.grid(alpha=0.25, lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_renyi")

# ---------------------------------------------------------------- takeoff
def H_additive(al):
    z = mp.zeta(al); dz = mp.zeta(al, derivative=1)
    return float(mp.log(z) + al * (-dz) / z)

def H_geometric(q):
    return math.log(1 / (1 - q)) + q / (1 - q) * math.log(1 / q)

def fig_takeoff():
    L = math.log(2); lam = 2.0
    al = np.linspace(1.05, 3.0, 40); lt = np.linspace(1, 12, 34)
    AL, LT = np.meshgrid(al, lt)
    Ha = np.array([H_additive(x) for x in al])
    Hg = np.array([H_geometric(lam ** (-(x - 1))) for x in al])
    Za = (Ha[None, :] + LT * math.log(10)) / L
    Zg = (Hg[None, :] + LT * math.log(10)) / L
    fig = plt.figure(figsize=(7.0, 2.9))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    ax.plot_surface(AL, LT, np.log10(Za), cmap="viridis", linewidth=0, antialiased=True, alpha=0.92)
    ax.plot_surface(AL, LT, np.log10(Zg), color=GOLD, linewidth=0, alpha=0.55)
    ax.set_xlabel(r"exponent $\alpha$", labelpad=-3)
    ax.set_ylabel(r"$\log_{10}(1/\theta)$", labelpad=-3)
    ax.set_zlabel(r"$\log_{10}$ runs per unit", labelpad=-4)
    ax.tick_params(pad=-2); ax.view_init(elev=22, azim=-128)
    ax.set_title(r"(a) $(H+\log\frac{1}{\theta})/L$: additive (surface), $\lambda=2$ (gold)", pad=2)
    ax2 = fig.add_subplot(1, 2, 2)
    th = 1e-6
    u = np.logspace(-3, math.log10(3.0), 300); a2 = 1 + u
    ea = [float(mp.zeta(x)) * (H_additive(x) + math.log(1 / th)) / L for x in a2]
    eg = [(lam - 1) / (1 - lam ** (-(x - 1))) * (H_geometric(lam ** (-(x - 1))) + math.log(1 / th)) / L for x in a2]
    u3 = u[u > 1.02]; a3 = 1 + u3
    pa = [float(mp.zeta(x / 2)) ** 2 / th for x in a3]
    ax2.loglog(u, ea, color=BLUE, lw=1.3, label="exponential checks, additive steps")
    ax2.loglog(u, eg, color=GOLD, lw=1.3, label=r"exponential checks, steps of factor $\lambda=2$")
    ax2.loglog(u3, pa, color=RED, lw=1.3, label=r"Chebyshev checks ($s=1$), additive steps")
    ax2.loglog(u, [1 / (x ** 2 * L) for x in u], color=BLUE, lw=0.8, ls="--", label=r"$1/((\alpha-1)^{2}L)$")
    ax2.axvline(1.0, color=RED, lw=0.6, ls=":")
    ax2.set_xlabel(r"$\alpha-1$, where $dI/dt=cI^{\alpha}$")
    ax2.set_ylabel(r"check time $\times\,c/\kappa$")
    ax2.set_title(r"(b) least check time of a sound takeoff, $\theta=10^{-6}$, $\varepsilon=\frac{1}{2}$")
    ax2.set_ylim(1, 1e9); ax2.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, 1.0), fontsize=6.6); ax2.grid(alpha=0.25, lw=0.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "fig_takeoff")

if __name__ == "__main__":
    fig_schedule3d(); fig_huffman3d(); fig_gating(); fig_price(); fig_branching(); fig_renyi(); fig_takeoff()
    print("done")
