import unittest

from ebllm.construct.book_ramsey import N58, book_ok, star_ok


class BookRamseyTest(unittest.TestCase):
    def test_n58_star(self):
        self.assertTrue(star_ok(58, N58["A"], N58["B"]))

    def test_n58_direct(self):
        self.assertTrue(book_ok(58, N58["A"], N58["B"]))

    def test_refuter(self):
        B = list(N58["B"])
        B[0] = 1  # move one element of B
        self.assertFalse(star_ok(58, N58["A"], B))
        self.assertFalse(book_ok(58, N58["A"], B))


if __name__ == "__main__":
    unittest.main()
