import unittest
import ndio.remote.neurodata as neurodata


class TestRAMONSegment(unittest.TestCase):

    def setUp(self):
        self.n = neurodata()
        self.t = 'kasthuri2015_ramon_v4'
        self.c = 'neurons'

    def test_get_bounding_box(self):
        self.assertEqual(
            self.n.get_ramon_bounding_box(self.t, self.c, 3555),
            (10240, 11264, 15360, 17408, 1104, 1152)
        )

if __name__ == '__main__':
    unittest.main()
