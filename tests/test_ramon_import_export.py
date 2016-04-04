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
        self.assertEqual(
            str(self.ramon_id),
            json.loads(ramon.to_json(r))['1']['id']
        )


if __name__ == '__main__':
    unittest.main()
