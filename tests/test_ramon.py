import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon as ramon
import numpy
import h5py
import os


class TestRAMON(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()
        self.ramon_id = 1

    # def test_create_ramon_file(self):
    #     r = ramon.RAMONSegment(id=self.ramon_id)
    #     r.cutout = numpy.zeros((3, 3, 3))
    #     self.h = ramon.ramon_to_hdf5(r)
    #     self.assertEqual(type(self.h), h5py.File)
    #
    #
    # def test_import_ramon_file(self):
    #     self.test_create_ramon_file()
    #     r = ramon.hdf5_to_ramon(self.h, self.ramon_id)
    #     assertEqual(r.id, self.ramon_id)


if __name__ == '__main__':
    unittest.main()
