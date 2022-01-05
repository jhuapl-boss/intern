import unittest

from intern import array


class TestRemoteInferral(unittest.TestCase):
    def test_get_remote_type(self):
        data = array("bossdb://kasthuri2015/em/3cylneuron_v1")
        self.assertEqual(data.remote, "BossDB")

    def test_precompute_inference_cvdb(self):
        data = array(
            "precomputed://s3://bossdb-open-data/wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image"
        )
        self.assertEqual(data.remote, "CloudVolumeOpenData")
