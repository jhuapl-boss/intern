import unittest
import ndio.remote.OCP as OCP
import ndio.ramon
import ndio.utils.autoingest as AutoIngest
import numpy
import datetime
import requests

SERVER_SITE = 'http://ec2-54-200-49-141.us-west-2.compute.amazonaws.com/'
DATA_SITE = 'http://ec2-54-200-215-161.us-west-2.compute.amazonaws.com/'

class TestAutoIngest(unittest.TestCase):

    def setUp(self):
        self.oo = OCP(SERVER_SITE)
        self.i = datetime.datetime.now()


    def test_pull_data(self):
        data_name_1 = "ndiotest1%s%s%s%s%s" % (self.i.year, self.i.month, self.i.day, self.i.hour, self.i.second)
        #data_name_1 = "ndio_test_1"

        ai_1 = AutoIngest.AutoIngest()
        ai_1.add_channel(data_name_1, 'uint32', 'image', DATA_SITE, 'SLICE', 'tif')
        ai_1.add_project(data_name_1, data_name_1, 1)
        ai_1.add_dataset(data_name_1, (660, 528, 1), (1.0, 1.0, 1.0))
        ai_1.add_metadata('')

        response = requests.get("{}/ocp/ca/{}/{}/npz/0/0,660/0,528/0,1/".format(SERVER_SITE,data_name_1, data_name_1))

        self.assertEqual(response.headers['content-type'], 'product/npz')
        #Verify its the same image?
        self.oo.delete_channel(data_name_1, data_name_1)


    def test_post_json(self):
        data_name_2 = "ndiotest2%s%s%s%s%s" % (self.i.year, self.i.month, self.i.day, self.i.hour, self.i.second)
        #data_name_2 = "ndio_test_2"

        ai_2 = AutoIngest.AutoIngest()
        ai_2.add_channel(data_name_2, 'uint32', 'image',
                    DATA_SITE, 'SLICE', 'tif')

        ai_2.add_project(data_name_2, data_name_2, 1)
        ai_2.add_dataset(data_name_2, (660, 528, 1), (1.0, 1.0, 1.0))
        ai_2.add_metadata('')

        ai_2.output_json()

        ai_3 = AutoIngest.AutoIngest()
        ai_3.post_data(SERVER_SITE, "/tmp/ND.json")

        response = requests.get("{}/ocp/ca/{}/{}/npz/0/0,660/0,528/0,1/".format(SERVER_SITE,data_name_2, data_name_2))

        self.assertEqual(response.headers['content-type'], 'product/npz')

        self.oo.delete_channel(data_name_2, data_name_2)

if __name__ == '__main__':
    unittest.main()
