import unittest
import ndio.remote.neurodata as nd
import ndio.utils.autoingest as AutoIngest
import datetime
import requests
import json
import os
import numpy

SERVER_SITE = 'http://ec2-54-191-191-26.us-west-2.compute.amazonaws.com/'
DATA_SITE = 'http://ec2-54-200-215-161.us-west-2.compute.amazonaws.com/'
S3_SITE = 'http://ndios3test.s3.amazonaws.com/'

class TestAutoIngest(unittest.TestCase):

    def setUp(self):
        self.i = datetime.datetime.now()
        self.oo = nd('ec2-54-191-191-26.us-west-2.compute.amazonaws.com')


    def test_pull_data(self):

        data_name_1 = "ndiotest1%s%s%s%s%s" % (self.i.year, self.i.month, self.i.day, self.i.hour, self.i.second)

        ai_1 = AutoIngest.AutoIngest()
        ai_1.add_channel(data_name_1, 'uint8', 'image', DATA_SITE, 'SLICE', 'tif')
        ai_1.add_project(data_name_1, data_name_1, 1)
        ai_1.add_dataset(data_name_1, (512, 512, 1), (1.0, 1.0, 10.0))
        ai_1.add_metadata('')
        ai_1.post_data(site_host=SERVER_SITE, verifytype='Slice')

        response = requests.get("{}/ocp/ca/{}/{}/npz/0/0,500/0,500/0,1/".format(SERVER_SITE,data_name_1, data_name_1))

        try:
            self.assertEqual(response.headers['content-type'], 'product/npz')
        except:
            raise ValueError(response.content, "{}/ocp/ca/{}/{}/npz/0/0,500/0,500/0,1/".format(SERVER_SITE,data_name_1, data_name_1))


    def test_post_data(self):
        data_name_5 = "ndioawstest5%s%s%s%s%sf" % (self.i.year, self.i.month, self.i.day, self.i.hour, self.i.second)

        ai_5 = AutoIngest.AutoIngest()
        ai_5.add_channel(data_name_5, 'uint8', 'image', S3_SITE, 'SLICE', 'tif')
        ai_5.add_project(data_name_5, data_name_5, 1)
        ai_5.add_dataset(data_name_5, (512, 512, 1), (1.0, 1.0, 1.0))
        ai_5.add_metadata('')
        ai_5.post_data(site_host=SERVER_SITE, verifytype='Folder')

        response = requests.get("{}/ocp/ca/{}/{}/npz/0/0,500/0,500/0,1/".format(SERVER_SITE,data_name_5, data_name_5))

        try:
            self.assertEqual(response.headers['content-type'], 'product/npz')
        except:
            raise ValueError(response.content, "{}/ocp/ca/{}/{}/npz/0/0,500/0,500/0,1/".format(SERVER_SITE,data_name_5, data_name_5))

        #self.assertEqual()


    def test_post_json(self):
        try:
            os.remove("/tmp/ND.json")
        except:
            print("")

        data_name_2 = "ndiotest2%s%s%s%s%sf" % (self.i.year, self.i.month, self.i.day, self.i.hour, self.i.second)

        ai_2 = AutoIngest.AutoIngest()
        ai_2.add_channel(data_name_2, 'uint8', 'image', DATA_SITE, 'SLICE', 'tif')

        ai_2.add_project(data_name_2, data_name_2, 1)
        ai_2.add_dataset(data_name_2, (512, 512, 1), (1.0, 1.0, 1.0))
        ai_2.add_metadata('')

        ai_2.output_json()

        ai_3 = AutoIngest.AutoIngest()
        ai_3.post_data(site_host=SERVER_SITE, verifytype='Folder', file_name="/tmp/ND.json")

        response = requests.get("{}/ocp/ca/{}/{}/npz/0/0,500/0,500/0,1/".format(SERVER_SITE,data_name_2, data_name_2))

        try:
            self.assertEqual(response.headers['content-type'], 'product/npz')
        except:
            raise ValueError(response.content, "{}/ocp/ca/{}/{}/npz/0/0,500/0,500/0,1/".format(SERVER_SITE,data_name_2, data_name_2))

    def test_output_json(self):
        data_name_3 = "ndio_test_3"

        ai_3 = AutoIngest.AutoIngest()
        ai_3.add_channel(data_name_3, 'uint8', 'image', DATA_SITE, 'SLICE', 'tif')

        ai_3.add_project(data_name_3, data_name_3, 1)
        ai_3.add_dataset(data_name_3, (512, 512, 1), (1.0, 1.0, 1.0))
        ai_3.add_metadata('')

        ai_3.output_json("/tmp/ND2.json")

        with open("/tmp/ND2.json") as data_file:
                    test_json  = json.load(data_file)

        truth_json = {
            "channels": {
                "ndio_test_3": {
                    "data_url": "http://ec2-54-200-215-161.us-west-2.compute.amazonaws.com/",
                    "file_type": "tif",
                    "file_format": "SLICE",
                    "datatype": "uint32",
                    "channel_type": "image",
                    "channel_name": "ndio_test_3",
                    "readonly": 0,
                    "exceptions": 0,
                    "resolution": 0
                }
            },
            "project": {
                "project_name": "ndio_test_3",
                "public": 1,
                "token_name": "ndio_test_3"
            },
            "metadata": "",
            "dataset": {
                "imagesize": [500, 500, 1],
                "voxelres": [1.0, 1.0, 1.0],
                "timerange": [0, 0],
                "scaling": 0,
                "scalinglevels": 0,
                "offset": [0, 0, 0],
                "dataset_name": "ndio_test_3"
            }
        }

        try:
            self.assertEqual(list(test_json.copy().keys()).sort(),
                list(truth_json.copy().keys()).sort())
        except:
            raise ValueError(list(test_json.copy().keys()).sort(), "\nVersus\n", list(truth_json.copy().keys()).sort())



if __name__ == '__main__':
    unittest.main()
