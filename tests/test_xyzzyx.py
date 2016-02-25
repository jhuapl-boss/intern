import unittest
import ndio.remote.neurodata as neurodata
import ndio.remote.errors
import numpy
import h5py
import os


class TestXYZZYX(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()

    def test_post_get(self):
        token = 'ndio_demos'
        channel = 'image'
        cutout = numpy.ones((5, 5, 5)).astype(int)
        cutout[2,3,4] = 42
        self.nd.post_cutout(token, channel, 20, 20, 20, cutout, resolution=0)
        pulldown = self.nd.get_cutout(token, channel, 20, 25, 20, 25, 20, 25, resolution=0)
        self.assertEqual(cutout[2,3,4], pulldown[2,3,4])


if __name__ == '__main__':
    unittest.main()
