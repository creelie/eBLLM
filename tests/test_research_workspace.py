import copy
import contextlib
import io
import unittest

from ebllm.research.catalogue import load, portfolio, routes, upstreams
from ebllm.research.certificates import certify_psd, verify_psd


class ExactCertificates(unittest.TestCase):
    def test_positive_definite_rational(self):
        a = [['2', '1/3'], ['1/3', '1']]
        c = certify_psd(a)
        self.assertTrue(verify_psd(a, c))
        self.assertEqual(c['D'], ['2', '17/18'])

    def test_singular_and_zero_pivots(self):
        a = [[0, 0, 0], [0, 1, 2], [0, 2, 4]]
        c = certify_psd(a)
        self.assertEqual(c['rank'], 1)
        self.assertTrue(verify_psd(a, c))

    def test_exact_near_singular(self):
        a = [[1, 1], [1, '100000000000000000001/100000000000000000000']]
        self.assertEqual(certify_psd(a)['D'][1], '1/100000000000000000000')

    def test_indefinite_positive_entries(self):
        with self.assertRaises(ValueError):
            certify_psd([[1, 2], [2, 1]])

    def test_zero_diagonal_nonzero_column(self):
        with self.assertRaises(ValueError):
            certify_psd([[0, 1], [1, 2]])

    def test_rejects_inexact_and_invalid_inputs(self):
        for a in ([[1.0]], [[True]], [['1/0']], [[1, 0]], [[1, 2], [0, 1]], []):
            with self.subTest(a=a), self.assertRaises(ValueError):
                certify_psd(a)

    def test_tampering_rejected(self):
        a = [[2, 1], [1, 2]]
        c = certify_psd(a)
        c['D'][1] = '1'
        self.assertFalse(verify_psd(a, c))

    def test_upper_triangle_tampering_rejected(self):
        a = [[1, 0], [0, 1]]
        c = certify_psd(a)
        c['L'][0][1] = '1'
        self.assertFalse(verify_psd(a, c))

    def test_generated_gram_matrices(self):
        # Independently construct PSD inputs as B^T B, including deficient rank.
        for n in range(1, 8):
            b = [[((i + 2) * (j + 3) % 11) - 5 for j in range(n)] for i in range(max(1, n - 1))]
            a = [[sum(row[i] * row[j] for row in b) for j in range(n)] for i in range(n)]
            self.assertTrue(verify_psd(a, certify_psd(a)))


class ResearchCatalogue(unittest.TestCase):
    def test_public_watch_covers_all_requested_owners(self):
        watch = load('public-upstream-watch.json')
        self.assertEqual(set(watch['owners']), {'google','google-deepmind','quantumlib','creelie'})
        self.assertEqual(watch['repository_count'], len(watch['repositories']))
        self.assertTrue(upstreams('quantumlib', 5))

    def test_cli_json_is_portable_to_nonunicode_windows_pipes(self):
        from ebllm.cli import main
        buffer = io.BytesIO()
        text = io.TextIOWrapper(buffer, encoding='ascii', errors='strict')
        with contextlib.redirect_stdout(text):
            self.assertEqual(main(['portfolio', 'seed', '-k', '144']), 0)
        text.flush()
        self.assertIn(b'"name": "seed"', buffer.getvalue())

    def test_every_snapshot_is_pinned_and_explicitly_unreviewed(self):
        data = load('portfolio.json')
        self.assertEqual(data['repository_count'], len(data['repositories']))
        self.assertGreaterEqual(len(data['repositories']), 144)
        for item in data['repositories']:
            self.assertEqual(item['review_status'], 'source-recorded-not-independently-audited')
            if item['readme_url']:
                self.assertIn(item['commit'], item['readme_url'])

    def test_keyword_search_finds_latest_seed_record(self):
        result = portfolio('seed', 144)
        seed = next(item for item in result if item['name'] == 'seed')
        self.assertIn('50', seed['scope_note'])
        self.assertIn('exact', seed['scope_note'])

    def test_routes_have_obligations_and_failure_checks(self):
        data = load('construction-atlas.json')
        self.assertGreaterEqual(len(data['routes']), 12)
        for item in data['routes']:
            self.assertTrue(item['obligations'])
            self.assertTrue(item['failure_check'])
            self.assertTrue(item['sources'])
        self.assertTrue(routes('Yang-Mills'))
