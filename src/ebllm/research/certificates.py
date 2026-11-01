"""Exact positive-semidefinite certificates over Q, with separate reconstruction.

This certifies a finite rational matrix. It makes no assertion about an
infinite family of matrices, a continuum limit, or a conjecture's closure.
"""

import re
from fractions import Fraction


def rational(value):
    if type(value) is int:
        return Fraction(value)
    if isinstance(value, str) and re.fullmatch(r'[+-]?\d+(?:/[1-9]\d*)?', value):
        return Fraction(value)
    raise ValueError('Use integers or exact rational strings, such as "-3/7"; floats are not accepted.')


def matrix(values):
    if not isinstance(values, list) or not values or len(values) > 128:
        raise ValueError('The matrix must have between 1 and 128 rows.')
    n = len(values)
    if any(not isinstance(row, list) or len(row) != n for row in values):
        raise ValueError('The matrix must be square.')
    result = [[rational(value) for value in row] for row in values]
    if any(result[i][j] != result[j][i] for i in range(n) for j in range(i)):
        raise ValueError('The matrix must be symmetric.')
    return result


def verify_psd(values, certificate):
    """Independently reconstruct A = L diag(d) L^T using exact arithmetic."""
    try:
        a = matrix(values)
        n = len(a)
        raw_l, raw_d = certificate['L'], certificate['D']
        if len(raw_l) != n or len(raw_d) != n or any(len(row) != n for row in raw_l):
            return False
        lower = [[rational(value) for value in row] for row in raw_l]
        diagonal = [rational(value) for value in raw_d]
        if any(value < 0 for value in diagonal):
            return False
        if any(lower[i][i] != 1 for i in range(n)):
            return False
        if any(lower[i][j] for i in range(n) for j in range(i + 1, n)):
            return False
        return all(
            a[i][j] == sum(lower[i][k] * diagonal[k] * lower[j][k] for k in range(n))
            for i in range(n) for j in range(n)
        )
    except (KeyError, ValueError, TypeError, IndexError, ZeroDivisionError):
        return False


def certify_psd(values):
    a = matrix(values)
    n = len(a)
    lower = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    diagonal = []
    for k in range(n):
        pivot = a[k][k] - sum(lower[k][j] ** 2 * diagonal[j] for j in range(k))
        if pivot < 0:
            raise ValueError('The matrix is not positive semidefinite: a negative exact pivot was found.')
        diagonal.append(pivot)
        for i in range(k + 1, n):
            residual = a[i][k] - sum(lower[i][j] * lower[k][j] * diagonal[j] for j in range(k))
            if not pivot:
                if residual:
                    raise ValueError('The matrix is not positive semidefinite: a zero pivot has a nonzero residual column.')
                lower[i][k] = Fraction(0)
            else:
                lower[i][k] = residual / pivot
    certificate = {
        'format': 'anaxia-rational-psd-v1',
        'L': [[str(value) for value in row] for row in lower],
        'D': [str(value) for value in diagonal],
        'rank': sum(value > 0 for value in diagonal),
        'scope': 'This finite rational matrix only.',
    }
    if not verify_psd(values, certificate):
        raise ArithmeticError('The independent exact reconstruction rejected the candidate factorization.')
    return certificate
