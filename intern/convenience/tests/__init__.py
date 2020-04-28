import unittest

from intern import array

class TestConvenienceProjectCreation(unittest.TestCase):

    def test_can_initialize_array_without_checks(self):
        array("bossdb://Kasthuri/em/images")

    # TODO: check_exists=False is unimplemented.
    # def test_cannot_initialize_invalid_path_array(self):
    #     with self.assertRaises(LookupError):
    #         array("bossdb://Kasthuri/em/DNE_images")


    def test_can_get_shape_of_array(self):
        data = array("bossdb://Kasthuri/em/images")
        self.assertEqual(
            data.shape,
            (1850, 26624, 21504)
        )

    def test_can_get_shape_of_array_with_resolution(self):
        res = 1
        data = array("bossdb://Kasthuri/em/images", resolution=res)
        self.assertEqual(
            data.shape,
            (1850, 26624/(2**res), 21504/(2**res))
        )

    def test_can_retrieve_data(self):
        data = array("bossdb://Kasthuri/em/images", resolution=1)
        array_cutout = data[1000:1010, 10000:10011, 10000:10012]
        self.assertEqual(array_cutout.shape, (10, 11, 12))

    def test_can_retrieve_data_with_XYZ_order(self):
        data = array("bossdb://Kasthuri/em/images", resolution=1, axis_order="XYZ")
        array_cutout = data[10000:10012, 10000:10011, 1000:1010]
        self.assertEqual(array_cutout.shape, (12, 11, 10))