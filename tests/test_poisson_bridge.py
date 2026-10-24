import math
import unittest
from ebllm.construct import poisson_bridge as P
from ebllm.construct.brane_formfactor import ein


class TestPoissonBridge(unittest.TestCase):
    def test_constant_series_agrees_with_closed_form(self):
        # Integration by parts gives a separate special-function expression.
        for theta in (0.125,math.log(2),2.0):
            expected=(4/6)*(ein(theta)-1-math.expm1(-theta)/theta)
            self.assertAlmostEqual(P.correction_constant(-1,strength=theta),expected,places=13)

    def test_direct_quadrature_tends_to_independent_constant_series(self):
        for sign in (-1,1):
            limit=P.correction_constant(sign)
            self.assertGreater(limit,0)
            self.assertLess(abs(P.correction(64,sign)-limit),1e-8)
            self.assertLess(P.correction(1,sign),limit)

    def test_jensen_chain_and_positive_measure_obstruction(self):
        for x in (0.25,0.5,1,2,8):
            a=P.log_x_propagators(x)
            b=P.log_x_propagators(2*x)
            self.assertLess(a['reciprocal_mean'],a['skeleton'])
            self.assertLess(a['skeleton'],a['mean_reciprocal'])
            self.assertTrue(all(b[k]<a[k] for k in a))

    def test_tail_bounds_and_scope(self):
        a=P.asymptotics()
        self.assertLessEqual(a['B_minus'],4*math.log(2)/(2*6))
        self.assertLessEqual(a['B_plus'],4*math.log(2)*2/(2*6))
        self.assertTrue(a['four_dimensional_tadpole_finite'])
        self.assertFalse(P.asymptotics(n=1)['four_dimensional_tadpole_finite'])
        self.assertTrue(P.asymptotics(n=1.01)['four_dimensional_tadpole_finite'])
        self.assertFalse(P.summary()['interacting_field_theory_certified'])

    def test_parameters_and_zero_response(self):
        for value in (0,-1,float('inf'),float('nan'),True):
            with self.assertRaises(ValueError):
                P.asymptotics(n=value)
        with self.assertRaises(ValueError):
            P.asymptotics(strength=5)
        self.assertEqual(P.correction(0,-1),0)

    def test_raw_vacuum_cutoff_and_subtracted_finite_part(self):
        self.assertEqual(P.ein_cutoff_integral(0),0)
        self.assertAlmostEqual(P.ein_cutoff_integral(1e-4)/1e-8,0.5-1e-4/12,places=9)
        for W in (30,100,1000):
            raw=P.ein_cutoff_integral(W)
            subtraction=W*math.log(W)+(P.EULER-1)*W
            self.assertAlmostEqual(raw-subtraction,1,places=9)
            self.assertGreater(raw,10)
        self.assertTrue(P.summary()['raw_skeleton_vacuum_cutoff_diverges'])


if __name__=='__main__':
    unittest.main()
