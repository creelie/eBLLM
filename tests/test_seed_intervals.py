import copy
import json
import unittest
from ebllm.construct import seed_intervals as S
from ebllm.construct import reflexive as R

class TestSeedIntervals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle=json.loads((S.DATA/'seed_top346.json').read_text())
        cls.census=S.DATA/'seed_point_pairs.csv'
        cls.bounds=S.pair_bounds(S.load_census(cls.census))

    def test_complete_integer_certificate(self):
        result=S.verify_bundle(self.bundle,self.census)
        self.assertEqual(result['shortest_depth_upper_bound'],346)
        self.assertEqual(result['certificates_verified'],12)
        self.assertFalse(result['sharp_constant_known'])

    def test_missing_extreme_polytope_is_rejected(self):
        bad=copy.deepcopy(self.bundle);bad['certificates'].pop()
        with self.assertRaisesRegex(ValueError,'coverage'):S.verify_bundle(bad,self.census)

    def test_cut_and_cost_are_verified(self):
        bad=copy.deepcopy(self.bundle['certificates'][0]);bad['cut']=[0,0,0,0]
        with self.assertRaisesRegex(ValueError,'cut'):S.verify_interval(bad,self.bounds)
        bad=copy.deepcopy(self.bundle['certificates'][0]);bad['interval_cost']=0
        with self.assertRaisesRegex(ValueError,'cost'):S.verify_interval(bad,self.bounds)

    def test_point_enumerator_against_simple_integer_geometry(self):
        from itertools import product
        cube=list(product((-1,1),repeat=4))
        self.assertEqual(S.lattice_points(cube),set(product((-1,0,1),repeat=4)))
        simplex=[(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(-1,-1,-1,-1)]
        self.assertEqual(S.lattice_points(simplex),set(simplex)|{(0,0,0,0)})

    def test_independent_pair_bound_matches_small_reference(self):
        pairs={(8,3):1,(7,4):1,(7,5):1,(6,6):1,(5,5):1}
        self.assertEqual(max(S.pair_bounds(pairs).values()),R.pair_chain_bound(pairs))

    def test_equivalent_sources_in_different_bases_are_rejected(self):
        bad=copy.deepcopy(self.bundle)
        indices=[i for i,r in enumerate(bad['certificates']) if r['parent_pair']==[520,26]]
        source=bad['certificates'][indices[0]]['source']['vertices']
        bad['certificates'][indices[1]]['source']['vertices']=[[-x for x in v] for v in source]
        with self.assertRaisesRegex(ValueError,'minor spectra'):S.verify_bundle(bad,self.census)

if __name__=='__main__':unittest.main()
