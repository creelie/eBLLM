import copy
import unittest
from unittest.mock import patch
from pathlib import Path
from ebllm.construct import nilpotent_free as N
from ebllm.controls import load_controls
from ebllm.release import Label

class NilpotentFreeChecks(unittest.TestCase):
    def test_lower_bound_does_not_certify_upper_bound(self):
        result=N.verify_lower_bound()
        self.assertEqual(result['construction_dimension'],5)
        self.assertEqual(result['construction_elements_checked'],243)
        self.assertFalse(result['upper_bound_verified'])

    def test_corrupt_table_fails_closed(self):
        certificate=N.load_certificate()
        text='\n'.join('depth %d: nodes %d closed %d'%(d,n,c) for d,(n,c) in
            enumerate(zip(certificate['nodes_by_depth'],certificate['closed_by_depth'])))
        text+='\ntotal nodes 3109888; open leaves 0\nexact exhaustive upper-bound audit: PASS\n'
        self.assertTrue(N.check_tree_output(text,certificate)['upper_bound_verified'])
        for changed in (text.replace('nodes 486','nodes 487'),
                        text.replace('open leaves 0','open leaves 1'),
                        text.replace('depth 6:','depth 7:')):
            with self.assertRaises(ValueError):
                N.check_tree_output(changed,certificate)
        with self.assertRaises(ValueError):
            N.check_tree_output(text,certificate,returncode=1)

    def test_source_digest_is_checked(self):
        certificate=copy.deepcopy(N.load_certificate())
        N.verify_source(N.DATA/'nilpotent_free_f3.c',certificate)
        certificate['source_sha256']='0'*64
        with self.assertRaises(ValueError):
            N.verify_source(N.DATA/'nilpotent_free_f3.c',certificate)

    def test_windows_text_checkout_preserves_certificate(self):
        source=N.DATA/'nilpotent_free_f3.c'
        windows=source.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
        with patch.object(Path,'read_bytes',return_value=windows):
            N.verify_source(source,N.load_certificate())

    def test_native_evaluation_and_review_gates_are_preserved(self):
        control=next(c for c in load_controls() if c.slug=='nilpotent-free-f3')
        self.assertEqual(control.label,Label.CANDIDATE)
        self.assertIn('formal',control.blocking)
        self.assertIn('human',control.blocking)

    def test_complete_upper_and_lower_bound(self):
        try:
            N._compiler()
        except RuntimeError:
            self.skipTest('no C compiler available')
        result=N.verify_full()
        self.assertEqual(result['maximum_nilpotent_free_dimension'],5)
        self.assertEqual(result['search_nodes'],3109888)
        self.assertEqual(result['open_leaves'],0)

if __name__=='__main__':
    unittest.main()
