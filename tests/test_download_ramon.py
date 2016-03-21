import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon as ramon
import numpy
import h5py
import os


class TestDownloadRAMON(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()
        self.ramon_id = 1

    def test_download_single_ramon_file_count(self):
        token = 'kasthuri2015_ramon_v4'
        r = self.nd.get_ramon(token, 'neurons', [3], resolution=3)
        self.assertEqual(len(r), 1)

    def test_download_multi_ramon_file_count(self):
        token = 'kasthuri2015_ramon_v4'
        r = self.nd.get_ramon(token, 'neurons', [3, 4], resolution=3)
        self.assertEqual(len(r), 2)

    def test_download_multi_ramon_file_attr(self):
        token = 'kasthuri2015_ramon_v4'
        r = self.nd.get_ramon(token, 'neurons', [3, 4], resolution=3)
        self.assertEqual(True, "4" in [s.id for s in r])
        self.assertEqual(True, "3" in [s.id for s in r])

    def test_download_multi_ramon_file_metadata_only(self):
        token = 'kasthuri2015_ramon_v4'
        r = self.nd.get_ramon(token, 'neurons', [3], resolution=3)

        self.assertEqual(r[0].neuron, 10003)
        self.assertEqual(True, r[0].author in ['unspecified', b'unspecified'])


if __name__ == '__main__':
    unittest.main()
