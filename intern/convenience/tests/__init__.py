import unittest

from intern import array

from intern.convenience.array import _DEFAULT_BOSS_OPTIONS
from intern.remote.boss import BossRemote


class TestConvenienceProjectCreation(unittest.TestCase):
    def test_can_initialize_array_without_checks(self):
        array("bossdb://Kasthuri/em/images")

    def test_array_instantiation_with_channel(self):
        """
        Array can be instantiated.
        .
        """
        boss = BossRemote(_DEFAULT_BOSS_OPTIONS)
        _ = array(boss.get_channel("cc", "kasthuri2015", "em"))

    def test_array_instantiation_dtype(self):
        """
        Array can be instantiated with type.
        .
        """
        boss = BossRemote(_DEFAULT_BOSS_OPTIONS)
        test_array = array(boss.get_channel("cc", "kasthuri2015", "em"))
        self.assertEqual(test_array.dtype, "uint8")

    # TODO: check_exists=False is unimplemented.
    # def test_cannot_initialize_invalid_path_array(self):
    #     with self.assertRaises(LookupError):
    #         array("bossdb://Kasthuri/em/DNE_images")

    def test_can_get_shape_of_array(self):
        data = array("bossdb://Kasthuri/em/images")
        self.assertEqual(data.shape, (1850, 26624, 21504))

    def test_can_get_shape_of_array_with_resolution(self):
        res = 1
        data = array("bossdb://Kasthuri/em/images", resolution=res)
        self.assertEqual(data.shape, (1850, 26624 / (2 ** res), 21504 / (2 ** res)))

    def test_can_retrieve_data_of_correct_shape(self):
        data = array("bossdb://Kasthuri/em/images", resolution=1)
        array_cutout = data[1000:1010, 10000:10011, 10000:10012]
        self.assertEqual(array_cutout.shape, (10, 11, 12))

    def test_can_retrieve_data_with_XYZ_order_of_correct_shape(self):
        data = array("bossdb://Kasthuri/em/images", resolution=1, axis_order="XYZ")
        array_cutout = data[10000:10012, 10000:10011, 1000:1010]
        self.assertEqual(array_cutout.shape, (12, 11, 10))

    def test_can_retrieve_correct_u64_data(self):
        data = array("bossdb://kasthuri2015/em/3cylneuron_v1")
        boss = BossRemote(_DEFAULT_BOSS_OPTIONS)
        get_cutout_data = boss.get_cutout(
            boss.get_channel("3cylneuron_v1", "kasthuri2015", "em"),
            0,
            [6000, 6200],
            [12000, 12500],
            [923, 924],
        )
        self.assertTrue(
            (get_cutout_data == data[923:924, 12000:12500, 6000:6200]).all()
        )
