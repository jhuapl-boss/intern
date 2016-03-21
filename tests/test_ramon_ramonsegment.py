import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon


class TestRAMONSegment(unittest.TestCase):

    def setUp(self):
        self.oo = neurodata()
        self.ramon_segment = self.oo.get_ramon('kasthuri2015_ramon_v4',
                                               'neurons', 3, 3)[0]
        self.default_ramon_segment = ndio.ramon.RAMONSynapse()

    def test_metadata(self):
        self.assertEqual(str(self.ramon_segment.id), '3')

if __name__ == '__main__':
    unittest.main()
