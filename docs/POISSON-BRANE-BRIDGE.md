# A precise bridge from linear branes to zero-free exponential branes

24 October 2026. Working mathematical addition to the merger of *Ghosts in Poisson Brane Gases* and the divergence-cancellation manuscript. Sources: https://hexagonmath.org/2610.00342v1, https://hexagonmath.org/2610.00342v2 and https://doi.org/10.5281/zenodo.23601921. Authors of the source manuscripts: Deep Bhattacharjee and Ushashi Bhattacharya. The derivation below was prepared with OpenAI Codex assistance. Priority has not been certified.

This note proves statements about random entire functions and propagators in explicit models. Its perturbative field-theory application requires the additional vertex, subtraction and BRST arguments of the cancellation paper. It supplies no interacting nonperturbative quantum gravity construction.

## 1. The linear model is a different model

Let Pi be Poisson on (0,infinity) with intensity nu and integral min(1,1/t) nu(dt) finite. Then F_Pi(z)=product(1+z/t) converges locally uniformly almost surely. Its reciprocal propagator has poles at the negative brane masses. On the slit plane the Poisson product formula gives

    E[1/(z F_Pi(z))] = exp[-integral z/(z+t) nu(dt)]/z.

This is distinct from 1/(z E F_Pi(z)). For a nonzero intensity, x times the actual averaged propagator strictly decreases on x>0. Hence it cannot have a representation c/x + integral mu(ds)/(x+s) with c>=0 and mu>=0: multiplying such a representation by x gives a nondecreasing function.

Two corrections are needed when carrying the original Ghosts text into a merger. The Poisson-kernel integral is pi/2 - arctan(x/y), with a minus sign. The negative total massive-weight formula is a conclusion **if a finite signed Stieltjes measure exists**. The general intensity hypotheses do not themselves prove existence of such a measure. In particular an atomic intensity creates an essential singularity in the averaged function, and some discontinuous scale-free profiles have a nonintegrable boundary density. A boundary discontinuity alone must not be called a finite signed measure.

## 2. An explicit zero-free gas

Set w=z/M^2, with M>0. Fix n,theta0,zeta>0 and put

    theta(tau)=theta0 tau^zeta,
    nu(d tau)=n d tau/[theta(tau) tau],       0<tau<=1,
    psi(u)=1-exp(-u^2),
    H_Pi(w)=sum_{tau in Pi} theta(tau) psi(tau w),
    a_Pi(w)=exp H_Pi(w).

This replaces the linear factor by exp[theta psi]. It does not turn the linear-factor model into a zero-free model by averaging.

**Theorem 1 (entire construction).** Almost surely H_Pi is entire, H_Pi(0)=0 and a_Pi is entire and zero-free. Its positive-axis values are at least one.

**Proof.** On any disk |w|<=R, |psi(tau w)|<=C_R tau^2. The expected sum of theta C_R tau^2 is n C_R integral_0^1 tau d tau, which is finite. Therefore the sum of suprema converges almost surely on every disk of integer radius. The series converges locally uniformly and defines an entire function. Exponentiation proves the zero-free assertion. On the real axis each summand is real and nonnegative. QED.

Define

    Hhat(w)=E H_Pi(w)=(n/2) Ein(w^2),
    R(w)=H_Pi(w)-Hhat(w),
    Ein(v)=sum_{k>=1} (-1)^(k+1) v^k/(k k!).

The expectation follows by absolutely convergent integration, followed by the power series or the substitution u=tau^2.

## 3. Almost-sure asymptotics with an explicit rate

**Theorem 2 (quenched asymptotics).** There is a real random variable R_infinity of mean zero and variance n theta0/zeta such that, almost surely, for every delta in (0,zeta/2),

    R(w)-R_infinity = O(|w|^(-zeta/2+delta))

uniformly on each closed cone |arg(+w)|<=pi/4-alpha or |arg(-w)|<=pi/4-alpha, alpha>0. Consequently on x>0,

    a_Pi(x)/x^n -> exp[n gamma_E/2+R_infinity].

**Proof.** Construct N(t)=integral_(0,t] theta(tau)(Pi-nu)(d tau) as an L2 compensated integral. Its variance is n theta0 t^zeta/zeta. For a self-contained version of the construction, truncate at epsilon_j with epsilon_j^zeta=2^(-4j). The differences of truncated processes are martingales with total second moment at most C 2^(-4j). The maximal inequality P(sup|X|>r)<=E|X(1)|^2/r^2 and Borel--Cantelli show uniform almost-sure convergence along these truncations, with thresholds 2^(-j). The limit is right-continuous, N(0)=0, and has the stated independent increments and variance. Set R_infinity=N(1).

Apply the same maximal inequality to N on [0,2^(-j)], with threshold 2^(-j(zeta/2-delta)). The resulting probabilities are at most C 2^(-2j delta), a summable series. Thus |N(t)|<=C_delta t^(zeta/2-delta) almost surely, after enlarging the random constant for the remainder of [0,1].

Integration by parts, first for the finite truncations and then in L2, gives

    R(w)-R_infinity
      = - exp(-w^2) N(1)
        - 2 w^2 integral_0^1 tau exp(-w^2 tau^2) N(tau) d tau.

On a specified cone Re(w^2)>=c_alpha |w|^2. Substitution u=|w| tau in the last integral proves the rate. The identity initially agrees with the absolutely convergent compensated integral for R, so the entire version makes it valid simultaneously for w. The standard positive-axis identity Ein(x^2)=2 log x+gamma_E+E1(x^2), with E1 exponentially small, proves the final limit. QED.

The same argument gives the exact mean-square difference

    E|R(x)-R_infinity|^2
      = n theta0 integral_0^1 tau^(zeta-1) exp(-2x^2 tau^2) d tau
      <= n theta0 Gamma(zeta/2) x^(-zeta)/2^(1+zeta/2).

Cauchy's estimate on a slightly larger cone yields the corresponding derivative bounds, losing one power of |w| for each derivative. The real-axis comparison constants follow by continuity on compact intervals and the positive finite limit at infinity. For zeta>4, choose delta so that zeta/2-delta>2; the realization's relative remainder is then smaller than x^(-2). This is the explicit construction relevant to the cancellation paper's analytic hypotheses, not a proof of all of its field-theory consequences.

## 4. The actual averaged propagator of the zero-free gas

Write G_Pi(z)=1/[z a_Pi(z/M^2)]. Define entire functions

    C_plus(w) = n integral_0^1
       [exp(theta psi(tau w))-1-theta psi(tau w)]/[theta tau] d tau,
    C_minus(w) = n integral_0^1
       [exp(-theta psi(tau w))-1+theta psi(tau w)]/[theta tau] d tau.

**Theorem 3 (three distinct averages).** On the punctured plane,

    E a_Pi(w) = exp[Hhat(w)+C_plus(w)],
    E[1/a_Pi(w)] = exp[-Hhat(w)+C_minus(w)].

Both are entire and zero-free, normalized to one at zero. In particular

    E G_Pi(z) = exp[-Hhat(z/M^2)+C_minus(z/M^2)]/z,

which has no pole other than the massless pole of residue one. On x>0,

    1/[x E a_Pi(x)] <= 1/[x exp Hhat(x)] <= E[1/(x a_Pi(x))].

**Proof.** On a compact w-set the integrands in the logarithms of the Poisson product formula are integrable: theta is bounded, psi(tau w)=O(tau^2), and the error after its linear term is O(theta^2 tau^4). The expectation of the absolute product is finite by the same estimate applied to its real exponent. The product formula can therefore be passed from finite truncations by domination. Splitting off its linear term gives the formulas. The integral remainders are locally uniformly convergent power series, hence entire. On the positive axis theta psi>=0, and exp(u)>=1+u makes both corrections nonnegative, giving the inequalities. QED.

**Theorem 4 (exact ultraviolet coefficient).** Let

    B_plus = (n/zeta) integral_0^theta0 (exp(u)-1-u)/u^2 d u,
    B_minus = (n/zeta) integral_0^theta0 (exp(-u)-1+u)/u^2 d u.

Then

    x^(-n) E a_Pi(x) -> exp[n gamma_E/2+B_plus],
    x^(n+1) E[1/(x a_Pi(x))] -> exp[-n gamma_E/2+B_minus].

Moreover 0<=B_minus<=n theta0/(2 zeta) and 0<=B_plus<=n theta0 exp(theta0)/(2 zeta).

**Proof.** For x>0, 0<=psi<=1 and psi(tau x)->1 at every tau>0. The elementary bounds exp(-u)-1+u<=u^2/2 and exp(u)-1-u<=exp(theta0)u^2/2, for 0<=u<=theta0, dominate the correction integrands by constants times theta(tau)/tau. This is integrable, with integral theta0/zeta. Dominated convergence followed by u=theta0 tau^zeta gives B_plus and B_minus. Combine with Hhat(x)=n log x+n gamma_E/2+o(1). QED.

Useful independent evaluation formulas are

    B_minus=(n/zeta)[Ein(theta0)-1+(1-exp(-theta0))/theta0],
    B_plus=(n/zeta)[-Ein(-theta0)+1-(exp(theta0)-1)/theta0],
    B_plus/minus=(n/zeta) sum_{k>=2} (+/-1)^k theta0^(k-1)/[(k-1)k!].

In the original dimensional variable x=z/M^2 the averaged propagator is asymptotic to exp[-n gamma_E/2+B_minus] M^(2n) z^(-n-1). Its four-dimensional Euclidean tadpole is finite exactly when n>1; near the origin the radial integrand tends to a constant, and at infinity it is a positive constant times x^(-n).

## 5. What the replacement does not evade

**Theorem 5 (positive-measure obstruction).** For n,theta0,zeta>0, neither the frozen propagator, nor the actual averaged propagator, nor the reciprocal-mean propagator has a standard positive Stieltjes/Kallen--Lehmann representation with a nonnegative massless residue and nonnegative massive measure.

**Proof.** For every positive x and every brane, psi(tau x) is strictly increasing in x. Almost surely there are branes (in fact infinitely many), so xG_Pi(x)=exp[-H_Pi(x)] is strictly decreasing. Expectation preserves the strict inequality. The same holds for 1/E a_Pi(x). A positive Stieltjes representation makes xG(x) nondecreasing, by direct comparison of x/(x+s) at two positive arguments. This is a contradiction. Alternatively the residue is one while xG(x)->0. QED.

Thus zero-free factors remove the additional diagrammatic poles of the linear-factor model. They do not make this same off-shell function a standard positive spectral two-point function. The established nonlocal-field literature distinguishes a diagrammatic Green function from a time-ordered correlator; the obstruction above applies only to the stated standard representation of the same function. It is not a proof that every nonlocal S-matrix prescription is nonunitary. Relevant published comparison: Briscese, Calcagni, Modesto and Nardelli, JHEP 08 (2024) 204, https://doi.org/10.1007/JHEP08(2024)204.

## 6. Field-theory statements still to be discharged in a final merger

- A negative overall superficial degree does not remove one-loop subdivergences. The convergence statement must refer to subdivergence-subtracted graphs.
- The three-by-three pole matrix can be checked exactly. Its invertibility proves the algebraic tuning once the asserted full one-loop response has been established; it does not by itself certify every Hessian, gauge-fixing and subtraction step.
- The skeleton vacuum integral gives 3nM^4/(64pi^2) in the specified dimensional-regularization or matched asymptotic-subtraction convention. Raw cutoffs diverge. A finite cosmological counterterm changes an absolute vacuum-energy value. The subtraction convention must be named when discussing regulator independence.
- All-order cutting rules and BRST cohomology must be verified for the exact random action and continuation prescription. Pole absence alone does not prove them.
- An interacting nonperturbative theory remains unconstructed.

These are the remaining audit obligations, not claimed counterexamples to all of the cancellation manuscript's perturbative arguments. The present note closes the explicitly stated stochastic and averaging calculations.
