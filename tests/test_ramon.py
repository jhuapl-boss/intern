import unittest
import ndio.remote.OCP as OCP
import ndio.ramon

class TestRAMON(unittest.TestCase):

    def setUp(self):
        oo = OCP()

    def test_get_ramon_ids(self):
        ids = oo.get_ramon_ids('ac4')
        self.assertEqual(self.default_ramon_segment.id, -1, "Unexpected default RAMON id.")

    def test_metadata(self):
        self.assertEqual(str(self.ramon_segment.id), '113')

if __name__ == '__main__':
    unittest.main()
