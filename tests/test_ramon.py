import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon as ramon
import numpy
import h5py
import os
import random


class TestRAMON(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()
        self.t = 'kasthuri2015_ramon_v4'
        self.c = 'neurons'
        self.ramon_id = 1

    def test_download_single_ramon(self):
        r = self.nd.get_ramon(self.t, self.c, "3")
        self.assertEqual(r.id, "3")

    def test_download_multi_ramon(self):
        r = self.nd.get_ramon(self.t, self.c, ["3", "4"])
        self.assertEqual(True, '3' in [s.id for s in r])

    def test_download_ramon_of_type(self):
        ids = self.nd.get_ramon_ids(self.t, self.c,
                                    ramon.AnnotationType.SEGMENT)
        randindex = random.randint(0, len(ids))
        # randomly pick one to check
        r = self.nd.get_ramon(self.t, self.c, ids[randindex])
        self.assertEqual(type(r), ramon.RAMONSegment)

        ids = self.nd.get_ramon_ids(self.t, self.c,
                                    ramon.AnnotationType.NEURON)
        randindex = random.randint(0, len(ids))
        # randomly pick one to check
        rn = self.nd.get_ramon(self.t, self.c, ids[randindex])
        self.assertEqual(type(rn), ramon.RAMONNeuron)


if __name__ == '__main__':
    unittest.main()
