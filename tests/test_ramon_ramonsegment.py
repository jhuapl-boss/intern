import unittest
import ndio.remote.OCP as OCP
import ndio.ramon

class TestRAMONSegment(unittest.TestCase):

    def setUp(self):
        oo = OCP(hostname="brainviz1.cs.jhu.edu")
        self.ramon_segment = oo.get_ramon('kharris15apical', 'ramon_test', 113)
        self.default_ramon_segment = ndio.ramon.RAMONSynapse()

    def test_defaults(self):
        self.assertEqual(self.default_ramon_segment.id, -1, "Unexpected default RAMON id.")

    def test_metadata(self):
        self.assertEqual(str(self.ramon_segment.id), '113')

if __name__ == '__main__':
    unittest.main()
