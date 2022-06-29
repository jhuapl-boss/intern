import unittest
import numpy as np
from intern.convenience.array import VolumeProvider, _BossDBVolumeProvider
from intern import array


class TestRemoteInferral(unittest.TestCase):
    def test_get_remote_type(self):
        data = array("bossdb://kasthuri2015/em/3cylneuron_v1")
        self.assertEqual(data.remote, "CloudVolumeOpenData")

    def test_precompute_inference_cvdb(self):
        data = array(
            "precomputed://s3://bossdb-open-data/wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image"
        )
        self.assertEqual(data.remote, "CloudVolumeOpenData")

    def test_can_guess_cvdb_channels(self):
        data = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image"
        )
        self.assertEqual(data.remote, "CloudVolumeOpenData")

    def test_axis_ording_cvdb_channels(self):
        data_xyz = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image",
            axis_order="XYZ",
        )
        data_zyx = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image",
            axis_order="ZYX",
        )
        self.assertTupleEqual(
            data_xyz.shape, (data_zyx.shape[2], data_zyx.shape[1], data_zyx.shape[0])
        )

    def test_get_data_cvdb_channels(self):
        data_boss = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image",
            volume_provider=_BossDBVolumeProvider(),
        )
        data_cv = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image",
        )
        excerpt_boss = data_boss[40:50, 40:50, 40:50]
        excerpt_cv = data_cv[40:50, 40:50, 40:50]

        self.assertTrue(np.array_equal(excerpt_boss, excerpt_cv))

    def test_get_data_cvdb_channels_rollaxes(self):
        data_xyz = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image",
            axis_order="XYZ",
        )
        data_zyx = array(
            "bossdb://wildenberg2021/VTA_dat12a_saline_control_Dendrites_6nm_aligned/image",
            axis_order="ZYX",
        )
        excerpt_xyz = data_xyz[40:50, 40:50, 40:50]
        excerpt_zyx = data_zyx[40:50, 40:50, 40:50]

        self.assertTrue(np.array_equal(excerpt_xyz, np.rollaxis(excerpt_zyx, 0, 2)))
