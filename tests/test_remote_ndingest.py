import unittest
import ndio.remote.neurodata as nd
import ndio.remote.ndingest as NDIngest
import datetime
import requests
import json
import os
import numpy
import sys

SERVER_SITE = 'http://ec2-54-201-19-176.us-west-2.compute.amazonaws.com/'
DATA_SITE = 'http://ec2-54-200-215-161.us-west-2.compute.amazonaws.com/'
S3_SITE = 'http://ndios3test.s3.amazonaws.com/'


class TestNDIngest(unittest.TestCase):

    def setUp(self):
        self.i = datetime.datetime.now()
        self.oo = nd(SERVER_SITE[len('http://'):])

    def test_remote_exists(self):
        self.assertEqual(self.oo.ping(), 200)

    def test_bad_channel(self):
        # Test channel misnamed/not preset
        data_name_1 = 'ndio_test_1'
        ai_1 = NDIngest.NDIngest()
        ai_1.add_channel('data_name_1', 'uint8', 'image', DATA_SITE, 'SLICE',
                         'tif')
        ai_1.add_project(data_name_1, data_name_1, 1)
        ai_1.add_dataset(data_name_1, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_1.add_metadata('')
        self.assertRaises(OSError, ai_1.output_json)

    def test_bad_token(self):
        # Test naming not correct
        data_name_4 = 'ndio_test_1'
        ai_4 = NDIngest.NDIngest()
        ai_4.add_channel(data_name_4, 'uint8', 'image', DATA_SITE, 'SLICE',
                         'tif')
        ai_4.add_project(data_name_4, 'ndiotest120162251533152', 1)
        ai_4.add_dataset(data_name_4, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_4.add_metadata('')

        self.assertRaises(OSError, ai_4.output_json)

        # Test not available in remote (Name already taken)OS
        data_name_5 = 'ndio_test_1'
        ai_5 = NDIngest.NDIngest()
        ai_5.add_channel(data_name_5, 'uint8', 'image', DATA_SITE, 'SLICE',
                         'tif')
        ai_5.add_project('ndiotest120162251533152', 'ndiotest120162251533152',
                         1)
        ai_5.add_dataset(data_name_5, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_5.add_metadata('')
        self.assertRaises(OSError, ai_5.output_json)

    def test_bad_url(self):
        # Test URL not HTTP available
        data_name_7 = 'ndio_test_1'
        ai_7 = NDIngest.NDIngest()
        ai_7.add_channel(data_name_7, 'uint8', 'image', "openconnectome",
                         'SLICE', 'tif')
        ai_7.add_project(data_name_7, data_name_7, 1)
        ai_7.add_dataset(data_name_7, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_7.add_metadata('')
        self.assertRaises(ValueError, ai_7.output_json)

    def test_bad_image(self):
        # Test mismatched dimensions
        data_name_8 = 'ndio_test_1'
        ai_8 = NDIngest.NDIngest()
        ai_8.add_channel(data_name_8, 'uint8', 'image', DATA_SITE,
                         'SLICE', 'tif')
        ai_8.add_project(data_name_8, data_name_8, 1)
        ai_8.add_dataset(data_name_8, (510, 510, 1), (1.0, 1.0, 10.0))
        ai_8.add_metadata('')
        self.assertRaises(ValueError, ai_8.output_json)

        # Test naming not correct (offset and max)
        data_name_9 = 'ndio_test_2'
        ai_9 = NDIngest.NDIngest()
        ai_9.add_channel(data_name_9, 'uint8', 'image', DATA_SITE,
                         'SLICE', 'tif')
        ai_9.add_project(data_name_9, data_name_9, 1)
        ai_9.add_dataset(data_name_9, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_9.add_metadata('')
        self.assertRaises(OSError, ai_9.output_json)

        # Test incorrect image type
        data_name_11 = 'ndio_test_1'
        ai_11 = NDIngest.NDIngest()
        ai_11.add_channel(data_name_11, 'uint8', 'image', DATA_SITE,
                          'SLICE', 'TIF')
        ai_11.add_project(data_name_11, data_name_11, 1)
        ai_11.add_dataset(data_name_11, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_11.add_metadata('')
        self.assertRaises(ValueError, ai_11.output_json)

    def test_bad_name(self):
        # Test a forbidden character
        data_name_10 = 'ndio@test@1'
        ai_10 = NDIngest.NDIngest()
        ai_10.add_channel(data_name_10, 'uint8', 'image', DATA_SITE,
                          'SLICE', 'tif')
        ai_10.add_project(data_name_10, data_name_10, 1)
        ai_10.add_dataset(data_name_10, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_10.add_metadata('')
        with self.assertRaises(ValueError):
            ai_10.output_json()

if __name__ == '__main__':
    unittest.main()
