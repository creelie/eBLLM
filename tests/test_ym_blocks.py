import unittest

try:
    import numpy as np
except ImportError:  # the scouts need numpy; the rest of the engine does not
    np = None

if np is not None:
    from ebllm.bllm import ym_blocks as Y


@unittest.skipUnless(np is not None, "numpy is not installed")
class TestYMBlocks(unittest.TestCase):
    def test_forest_geometry(self):
        o = (0, 0, 0, 0)
        e = [(o, mu) for mu in range(4) if not Y.is_F((o, mu))][0]
        self.assertEqual([sum(Y.is_F(m) for m, _ in p) for p in Y.plaquettes_of(e)], [1] * 6)
        partners = {m for p in Y.plaquettes_of(e) for m, _ in p if m != e and not Y.is_F(m)}
        self.assertEqual(len(partners), 12)               # the 12 active partners of forest.md

    def test_transport_coupling_near_the_sharp_quarter(self):
        rng = np.random.default_rng(0)
        b, d = np.zeros(4), np.array([0, 1e-3, 0, 0])
        r = np.mean([np.linalg.norm(Y.heat_bath(b + d, z) - Y.heat_bath(b, z))
                     for z in (Y.random_su2(rng) for _ in range(4000))]) / 1e-3
        self.assertGreater(r, 0.25 - 0.02)                # no coupling beats W1, whose sharp value is 1/4
        self.assertLess(r, 0.31)

    def test_blocks_drop_forest_links(self):
        V, bd = Y.block_and_boundary(Y.unit_cube4())
        self.assertEqual(len(V), 24)
        self.assertFalse(any(Y.is_F(l) for l in V + bd))

    def test_scout_reading(self):
        self.assertAlmostEqual(Y.scout_crossing("single link"), 1 / 3, delta=0.01)    # calibration reproduces the ceiling
        self.assertLess(Y.scout_crossing("plaquette (3 active links)"), 0.36)          # small blocks barely move it
        self.assertIsNone(Y.scout_crossing("unit 4-cube (24 active links)"))           # no crossing measured up to 0.4
        self.assertGreater(Y.scout_crossing("unit 4-cube (24 active links)", calibrated=False), 0.36)

    def test_adversarial_boundaries_stay_below_one_at_036(self):
        self.assertLess(max(Y.ADVERSARY_4CUBE_036.values()), 1.0)

    def test_small_run_is_finite(self):
        a, nv, nb, _ = Y.alpha_block([((0, 0, 0, 0), 1)], 0.3 / 4, np.random.default_rng(1), n_eta=1, sweeps=20, burn=5)
        self.assertEqual((nv, nb), (1, 12))
        self.assertTrue(0 < a < 3)


if __name__ == "__main__":
    unittest.main()
