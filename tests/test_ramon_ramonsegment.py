import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon


class TestRAMONSegment(unittest.TestCase):

    def setUp(self):
        self.oo = neurodata()
        self.ramon_segment = self.oo.get_ramon('kasthuri2015_ramon_v4',
                                               'neurons', 3, 3,
                                               include_cutout=True)
        self.default_ramon_segment = ndio.ramon.RAMONSynapse()

    def test_metadata(self):
        self.assertEqual(str(self.ramon_segment.id), '3')

    def test_actually_got_cutout(self):
        self.assertEqual(self.ramon_segment.cutout.shape, (49, 54, 7))

if __name__ == '__main__':
    unittest.main()
