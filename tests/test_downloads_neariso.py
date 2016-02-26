import unittest
import ndio.remote.neurodata as neurodata
import ndio.remote.errors
import numpy
import random


class TestNeariso(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()
        self.nd_force_chunk = neurodata(chunk_threshold=0)

    def test_get_neariso(self):
        token = 'ndio_demos'
        channel = 'image'
        try:
            pulldown = self.nd.get_cutout(
                    token, channel,
                    20, 25, 20, 25, 20, 25,
                    resolution=0, neariso=True)
        except:
            self.fail("neariso download fails (no chunking).")

    def test_post_get_chunk(self):
        token = 'ndio_demos'
        channel = 'image'
        try:
            pulldown = self.nd_force_chunk.get_cutout(
                    token, channel,
                    20, 25, 20, 25, 20, 25,
                    resolution=0, neariso=True)
        except:
            self.fail("neariso download fails (chunking).")

if __name__ == '__main__':
    unittest.main()
