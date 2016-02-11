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
        token = 'kasthuri2015_ramon_v1'
        r = self.nd.get_ramon(token, 'neurons', [3], resolution=3)
        self.assertEqual(len(r), 1)

    def test_download_multi_ramon_file_count(self):
        token = 'kasthuri2015_ramon_v1'
        r = self.nd.get_ramon(token, 'neurons', [3, 4], resolution=3)
        self.assertEqual(len(r), 2)

    def test_download_multi_ramon_file_attr(self):
        token = 'kasthuri2015_ramon_v1'
        r = self.nd.get_ramon(token, 'neurons', [3, 4], resolution=3)
        self.assertEqual(r[0].id, "3")
        self.assertEqual(r[1].id, "4")

    def test_download_multi_ramon_file_metadata_only(self):
        token = 'kasthuri2015_ramon_v1'
        r = self.nd.get_ramon(token, 'neurons', [3, 4], resolution=3, metadata_only=True)
        self.assertEqual(r[0].neuron, 10003)
        self.assertEqual(r[0].author, b'unspecified')


if __name__ == '__main__':
    unittest.main()
