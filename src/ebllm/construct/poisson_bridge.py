"""Numerical diagnostics for the explicit zero-free Poisson-gas construction.

theta(tau)=strength*tau**zeta, nu(dtau)=n*dtau/(theta*tau),
psi(tau*x)=1-exp(-(tau*x)**2).  The written proof establishes the
Poisson expectation formulas and their almost-sure asymptotics.  This
module independently compares their integral and series evaluations;
it does not certify an interacting quantum field theory.
"""
from __future__ import annotations

import math
from .brane_formfactor import ein, EULER


def _parameters(n, strength, zeta):
    if any(isinstance(v, bool) or not math.isfinite(v) or v <= 0
           for v in (n, strength, zeta)):
        raise ValueError('n, strength and zeta must be finite and positive')
    if strength > 4:
        raise ValueError('this numerical implementation supports strength <= 4')


def _remainder(u, sign):
    """exp(sign*u)-1-sign*u, avoiding small-u cancellation."""
    if u < 0.01:
        term = u*u/2
        total = term
        for k in range(3, 24):
            term *= sign*u/k
            total += term
        return total
    return math.expm1(sign*u)-sign*u


def _simpson(f, left, right, tol=1e-12):
    mid = (left+right)/2
    a, b, c = f(left), f(mid), f(right)
    area = (right-left)*(a+4*b+c)/6

    def refine(l, r, fl, fm, fr, old, eps, depth):
        m = (l+r)/2
        p, q = (l+m)/2, (m+r)/2
        fp, fq = f(p), f(q)
        s1 = (m-l)*(fl+4*fp+fm)/6
        s2 = (r-m)*(fm+4*fq+fr)/6
        error = s1+s2-old
        if abs(error) <= 15*eps:
            return s1+s2+error/15
        if depth == 0:
            raise ArithmeticError('quadrature failed to reach its tolerance')
        return (refine(l,m,fl,fp,fm,s1,eps/2,depth-1)
                +refine(m,r,fm,fq,fr,s2,eps/2,depth-1))
    return refine(left,right,a,b,c,area,tol,24)


def correction_constant(sign, n=4.0, strength=math.log(2), zeta=6.0):
    """B_sign by its convergent series; sign=1 for E[a], -1 for E[1/a]."""
    _parameters(n,strength,zeta)
    if sign not in (-1,1):
        raise ValueError('sign must be -1 or 1')
    total = 0.0
    term = strength/2
    for k in range(2,120):
        total += (sign**k)*term/(k-1)
        term *= strength/(k+1)
    return n*total/zeta


def correction(x, sign, n=4.0, strength=math.log(2), zeta=6.0):
    """C_sign(x) by independent quadrature in log size.

    The omitted tail is bounded by 1e-13.  The adaptive quadrature is a
    floating-point diagnostic, not a rigorous interval certificate.
    """
    _parameters(n,strength,zeta)
    if sign not in (-1,1) or not math.isfinite(x) or x < 0:
        raise ValueError('sign must be +/-1 and x finite and nonnegative')
    if x == 0:
        return 0.0
    bound = n*strength*(math.exp(strength) if sign==1 else 1)/(2*zeta)
    upper = max(12.0,(math.log(max(bound,1e-300)/1e-13)+1)/zeta)
    log_x = math.log(x)

    def integrand(y):
        theta = strength*math.exp(-zeta*y)
        if theta == 0:
            return 0.0
        log_arg = log_x-y
        psi = 1.0 if log_arg > 3 else -math.expm1(-math.exp(2*log_arg))
        return n*_remainder(theta*psi,sign)/theta
    return _simpson(integrand,0.0,upper)


def log_x_propagators(x, n=4.0, strength=math.log(2), zeta=6.0):
    """Logarithms of x times three different propagators, at M=1."""
    _parameters(n,strength,zeta)
    if not math.isfinite(x) or x <= 0 or x > 1e150:
        raise ValueError('x must lie in (0, 1e150] for this numerical diagnostic')
    skeleton = -0.5*n*ein(x*x)
    return {'reciprocal_mean':skeleton-correction(x,1,n,strength,zeta),
            'skeleton':skeleton,
            'mean_reciprocal':skeleton+correction(x,-1,n,strength,zeta)}


def asymptotics(n=4.0, strength=math.log(2), zeta=6.0):
    """Positive-axis averaged coefficients, with dimensionless x=z/M^2."""
    _parameters(n,strength,zeta)
    bp=correction_constant(1,n,strength,zeta)
    bm=correction_constant(-1,n,strength,zeta)
    return {'B_plus':bp,'B_minus':bm,
            'log_mean_a_coefficient':n*EULER/2+bp,
            'log_mean_propagator_coefficient':-n*EULER/2+bm,
            'mean_propagator_power_in_z':-n-1,
            'four_dimensional_tadpole_finite':n>1,
            'variance_R_infinity':n*strength/zeta}


def summary():
    samples={str(x):log_x_propagators(x) for x in (0.5,1.0,2.0,8.0)}
    return {'scope':'explicit Poisson form factors and propagators',
            'parameters':{'n':4,'strength':math.log(2),'zeta':6},
            'samples_log_xG':samples,'asymptotics':asymptotics(),
            'additional_poles_in_exponential_model':False,
            'standard_positive_stieltjes_representation':False,
            'interacting_field_theory_certified':False,
            'numerical_trust':'floating point; general statements have written proofs',
            'preprints':['https://hexagonmath.org/2610.00342v1',
                         'https://hexagonmath.org/2610.00342v2'],
            'archive':'https://doi.org/10.5281/zenodo.23601921'}


def main(argv=None):
    import argparse,json
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    print(json.dumps(summary(),indent=2))


if __name__=='__main__':
    main()
