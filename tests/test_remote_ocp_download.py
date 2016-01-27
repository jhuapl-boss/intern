import unittest
import ndio.remote.neurodata as neurodata
import ndio.ramon
import numpy


class TestDownload(unittest.TestCase):

    def setUp(self):
        self.oo = neurodata()

    def test_get_cutout_type(self):
        # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
        numpy_download = self.oo.get_cutout('kasthuri11', 'image',
                                            1000, 1100,
                                            1000, 1100,
                                            1000, 1001,
                                            resolution=3)

        self.assertEqual(type(numpy_download), numpy.ndarray)

    def test_get_cutout(self):
        # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
        numpy_download = self.oo.get_cutout('kasthuri11', 'image',
                                            1000, 1100,
                                            1000, 1100,
                                            1000, 1001,
                                            resolution=3)

        # We know this pixel is 132
        self.assertEqual(numpy_download[0][0][0], 132)

    def test_get_volume_type(self):
        # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
        ramon_download = self.oo.get_volume('kasthuri11', 'image',
                                            1000, 1100,
                                            1000, 1100,
                                            1000, 1001,
                                            resolution=3)

        self.assertEqual(type(ramon_download), ndio.ramon.RAMONVolume)

    def test_get_volume(self):
        # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
        ramon_download = self.oo.get_volume('kasthuri11', 'image',
                                            1000, 1100,
                                            1000, 1100,
                                            1000, 1001,
                                            resolution=3)

        self.assertEqual(ramon_download.xyz_offset[0], 1000)
        self.assertEqual(ramon_download.resolution, 3)
        self.assertEqual(ramon_download.cutout[0][0][0], 132)

    def test_get_image_type(self):
        # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
        image_download = self.oo.get_image('kasthuri11', 'image',
                                           1000, 1100,
                                           1000, 1100,
                                           1000,
                                           resolution=3)

        self.assertEqual(type(image_download), numpy.ndarray)
        self.assertEqual(image_download.shape, (100, 100))


if __name__ == '__main__':
    unittest.main()
