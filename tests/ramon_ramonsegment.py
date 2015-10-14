import unittest
import ndio.remote.OCP as OCP

class TestRAMONSegment(unittest.TestCase):

    def setUp(self):
        oo = OCP(hostname="brainviz1.cs.jhu.edu")
        self.ramon_segment = oo.get_ramon('kharris15apical', 'ramon_test', 113)

    def test_metadata(self):
        self.assertEqual(str(self.ramon_segment), '113')

if __name__ == '__main__':
    unittest.main()
