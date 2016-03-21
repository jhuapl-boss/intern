import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon as ramon
import numpy
import h5py
import os
import random

import json


class TestRAMON(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata()
        self.t = 'kasthuri2015_ramon_v4'
        self.c = 'neurons'
        self.ramon_id = 1

    def test_json_export(self):
        r = self.nd.get_ramon(self.t, self.c, self.ramon_id)

        json_str = '{"1": {"type": "segment", "metadata": {"status": 0, "confidence": 1.0, "segmentclass": 2, "author": "unspecified", "neuron": 10017, "kvpairs": {"spine_str": "0", "segment_subtype": "spiny", "is_spine": "0"}, "parentseed": 0}}}'

        self.assertEqual('1', json.loads(ramon.to_json(r))['1']['id'])
    #
    # def test_json_import(self):
    #     json_str = '{"1": {"confidence": 1.0, "segment_class": 2, "author": "unspecified", "_status": 0, "xyz_offset": [0, 0, 0], "neuron": 10017, "organelles": [], "synapses": [], "kvpairs": {"spine_str": "0", "is_spine": "0", "segment_subtype": "spiny"}, "voxels": null, "cutout": null, "resolution": 0, "id": "1"}}'
    #     self.assertEqual(10017, ramon.from_json(json_str))
    #


if __name__ == '__main__':
    unittest.main()
