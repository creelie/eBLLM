import unittest

try:
    import numpy as np
except ImportError:  # the scouts need numpy; the rest of the engine does not
    np = None

if np is not None:
    from ebllm.construct import vacuum_conditions as VC


def sample(**over):
    v = {"moduli_mass2_GeV2": [1e10, 4e9, 2e12], "Yu": VC.diag_yukawa(6.5e-6, 3.2e-3),
         "Yd": VC.diag_yukawa(8.7e-4, 1.6e-2), "Ye": VC.diag_yukawa(2.8e-4, 5.9e-2),
         "vus": 0.225, "m32_GeV": 1e4, "F_nonzero": True}
    v.update(over)
    return v


@unittest.skipUnless(np is not None, "numpy is not installed")
class TestVacuumConditions(unittest.TestCase):
    def test_central_vacuum_passes(self):
        self.assertEqual(VC.check(sample()), [])

    def test_refuter_catches_each_condition(self):
        self.assertTrue(any(s.startswith("(C7)") for s in VC.check(sample(moduli_mass2_GeV2=[1e4, 1e10]))))
        self.assertTrue(any("rank" in s for s in VC.check(sample(Yu=VC.diag_yukawa(0.0, 3.2e-3)))))
        self.assertTrue(any("c/t" in s for s in VC.check(sample(Yu=VC.diag_yukawa(6.5e-6, 0.5)))))
        self.assertTrue(any(s.startswith("(C9)") for s in VC.check(sample(F_nonzero=False))))
        self.assertTrue(any("gravitino" in s for s in VC.check(sample(m32_GeV=10.0))))

    def test_windows_are_editable(self):
        loose = VC.Windows(m0_GeV=1.0)
        self.assertEqual(VC.check(sample(moduli_mass2_GeV2=[2.0]), loose), [])
        self.assertIn("(C7)", VC.as_statement())


if __name__ == "__main__":
    unittest.main()
