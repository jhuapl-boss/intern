import unittest


class TestSanityCheck(unittest.TestCase):

    def test_sanity(self):
        self.assertEqual(1, 1)
        self.assertNotEqual(1, 2)

if __name__ == '__main__':
    unittest.main()
