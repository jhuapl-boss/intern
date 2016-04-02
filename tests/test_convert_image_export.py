# import unittest
# import ndio.remote.neurodata as neurodata
# import ndio.ramon
# import ndio.convert.png as ndpng
# import ndio.convert.tiff as ndtiff
# import numpy
#
#
# class TestDownload(unittest.TestCase):
#
#     def setUp(self):
#         self.oo = neurodata()
#
#     def test_export_load(self):
#         # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
#         image_download = self.oo.get_image('kasthuri11', 'image',
#                                            1000, 1100,
#                                            1000, 1100,
#                                            1000,
#                                            resolution=3)
#
#         # if returns string, successful export
#         self.assertEqual(
#                 ndpng.export_png("tests/trash/download.png", image_download),
#                 "tests/trash/download.png")
#
#         # now confirm import works too
#         self.assertEqual(ndpng.load("tests/trash/download.png")[0][0],
#                          image_download[0][0])
#         self.assertEqual(ndpng.load("tests/trash/download.png")[10][10],
#                          image_download[10][10])
#
#     def test_export_load(self):
#         # kasthuri11/image/xy/3/1000,1100/1000,1100/1000/
#         image_download = self.oo.get_image('kasthuri11', 'image',
#                                            1000, 1100,
#                                            1000, 1100,
#                                            1000,
#                                            resolution=3)
#
#         # if returns string, successful export
#         self.assertEqual(
#                 ndtiff.save("tests/trash/download-1.tiff",
#                                    image_download),
#                 "tests/trash/download-1.tiff")
#
#         # now confirm import works too
#         self.assertEqual(
#                 ndtiff.load("tests/trash/download-1.tiff")[0][0],
#                 image_download[0][0])
#         self.assertEqual(
#                 ndtiff.load("tests/trash/download-1.tiff")[10][10],
#                 image_download[10][10])
#
#
# if __name__ == '__main__':
#     unittest.main()
