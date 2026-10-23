import unittest
from ebllm.bllm.hodge import check_hodge
from ebllm.bllm.targets import Con

def check(*parts,gives='link-class'):
    return check_hodge(Con('scope-check','hodge',gives,parts=parts))

class TestHodgeScope(unittest.TestCase):
    def test_motivated_does_not_become_algebraic(self):
        r=check('p.link','l.andre')
        self.assertEqual(r.outcome,'stopped')
        self.assertTrue(r.measurement['motivated'])
        self.assertFalse(r.measurement['algebraic_representative'])

    def test_cover_cannot_erase_the_original_defect(self):
        r=check('p.surgery')
        self.assertFalse(r.measurement['defect_can_decrease'])
        self.assertFalse(r.measurement['representative_supplied'])

    def test_graph_survivors_are_not_semiregular_objects(self):
        r=check('p.convolution4','p.cmext',gives='ext2-57')
        self.assertEqual(r.outcome,'stopped')
        self.assertEqual(r.measurement['surviving_arrangements'],31)
        self.assertIn('Maurer-Cartan',r.statement)

    def test_split_weil_sixfolds_are_not_called_open(self):
        r=check('p.propagation','l.bbf',gives='f2-lift')
        self.assertIn('split Weil sixfolds are established',r.statement)
