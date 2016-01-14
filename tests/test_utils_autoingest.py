import unittest
import ndio.remote.OCP as OCP
import ndio.ramon
import ndio.utils.autoingest
import numpy

class TestAutoIngest(unittest.TestCase):

    SERVER_SITE = ''
    DATA_SITE = 'http://54.200.215.161/'
    def setUp(self):
        self.ai = autoingest.AutoIngest()
        self.ai.add_channel('image', 'uint32', 'image',
                    DATA_SITE, 'SLICE', 'tif')

        self.ai.add_project('ndio_test', 'ndio_test')
        self.ai.add_dataset('ndio_test', (660, 528, 1), (0, 0, 0))
        self.ai.add_metadata('')

        self.ai.post_data(SERVER_SITE)


    def test_pull_data(self):

        self.oo = OCP(SERVER_SITE)
        numpy_download = self.oo.get_cutout('ndio_test', 'image',
                                            0, 660,
                                            0, 528,
                                            0, 0,
                                            resolution=0)

        self.assertEqual(type(numpy_download), numpy.ndarray)

if __name__ == '__main__':
    unittest.main()
