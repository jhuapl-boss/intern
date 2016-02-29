import unittest
import ndio.remote.neurodata as neurodata
import ndio.remote.errors
import numpy
import h5py
import os


class TestReserveIds(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()

    def test_reserve_ids(self):
        self.assertEqual(
            len(self.nd.reserve_ids('ndio_demos', 'ramontests', 10)),
            10)


if __name__ == '__main__':
    unittest.main()
