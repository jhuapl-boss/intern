import unittest

from ...convenience import parse_fquri, InvalidURIError

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

    def test_can_get_shape_of_array(self):
        data = array("bossdb://Kasthuri/em/images")
        self.assertEqual(data.shape, (1856, 26624, 21504))

    def test_can_get_shape_of_array_with_resolution(self):
        res = 1
        data = array("bossdb://Kasthuri/em/images", resolution=res)
        self.assertEqual(data.shape, (1856, 26624 / 2, 21504 / 2))

    def test_can_retrieve_data_of_correct_shape(self):
        data = array("bossdb://Kasthuri/em/images", resolution=1)
        array_cutout = data[1000:1010, 10000:10011, 10000:10012]
        self.assertEqual(array_cutout.shape, (10, 11, 12))

    def test_can_retrieve_data_with_XYZ_order_of_correct_shape(self):
        data = array("bossdb://Kasthuri/em/images", resolution=1, axis_order="XYZ")
        array_cutout = data[10000:10012, 10000:10011, 1000:1010]
        self.assertEqual(array_cutout.shape, (12, 11, 10))


class TestFQURIParser(unittest.TestCase):
    """ """

    def test_empty_string_fails(self):
        with self.assertRaises(InvalidURIError):
            parse_fquri("")

    def test_boss_uri_fails_without_protocol(self):
        with self.assertRaises(InvalidURIError):
            parse_fquri("https://api.bossdb.io/Bock/bock11/image")

    def test_boss_uri_with_token(self):
        remote, resource = parse_fquri(
            "bossdb://https://api.bossdb.io/Bock/bock11/image", token="public"
        )
        self.assertEqual(remote._token_volume, "public")
