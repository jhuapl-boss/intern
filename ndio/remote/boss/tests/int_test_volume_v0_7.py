# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 
from ndio.remote.boss import BossRemote
from ndio.ndresource.boss.resource import *
from ndio.service.boss.httperrorlist import HTTPErrorList
import numpy

import random
import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v0.7'

class VolumeServiceTest_v0_7(unittest.TestCase):
    """Integration tests of the Boss volume service API.

    Because setup and teardown involves many REST calls, tests are only 
    divided into tests of the different types of data model resources.  All
    operations are performed within a single test of each resource.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        cls.initialize(cls)
        cls.cleanup_db(cls)
        cls.rmt.project_create(cls.coll)
        coord_actual = cls.rmt.project_create(cls.coord)
        cls.rmt.project_create(cls.exp)
        cls.rmt.project_create(cls.chan16)
        cls.rmt.project_create(cls.chan)
        cls.rmt.project_create(cls.ann_chan)

    @classmethod
    def tearDownClass(cls):
        """Remove all data model objects created in the DB.
        """
        cls.initialize(cls)
        cls.cleanup_db(cls)

    def initialize(self):
        """Initialization for each test.

        Called by both setUp() and setUpClass().
        """
        self.rmt = BossRemote(cfg_file='test.cfg')

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        self.rmt.project_service.session_send_opts = { 'verify': False }
        self.rmt.metadata_service.session_send_opts = { 'verify': False }
        self.rmt.volume_service.session_send_opts = { 'verify': False }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        coll_name = 'collection2323-{}'.format(random.randint(0, 9999))
        self.coll = CollectionResource(coll_name, API_VER, 'bar')

        cf_name = 'BestFrame{}'.format(random.randint(0, 9999))
        self.coord = CoordinateFrameResource(
            cf_name, API_VER, 'Test coordinate frame.', 0, 100, 0, 50, 0, 20, 
            1, 1, 1, 'nanometers', 0, 'nanoseconds')

        # self.exp.coord_frame must be set with valid id before creating.
        self.exp = ExperimentResource(
            'exp2323x2', self.coll.name, 'BestFrame', API_VER, 'my experiment', 
            1, 'iso', 0)

        self.chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, 'image', API_VER, 'test channel', 
            0, 'uint8', 0)

        self.chan16 = ChannelResource(
            'my16bitChan', self.coll.name, self.exp.name, 'image', API_VER,
            '16 bit test channel', 0, 'uint16', 0)

        self.ann_chan = ChannelResource(
            'annChan', self.coll.name, self.exp.name, 'annotation', API_VER, 
            'annotation test channel', 0, 'uint64', 0, source=[self.chan.name])

    def cleanup_db(self):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDownClass() and setUpClass().
        """
        try:
            self.rmt.project_delete(self.ann_chan)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.chan16)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.chan)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.exp)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coord)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coll)
        except HTTPError:
            pass

    def setUp(self):
        #self.initialize()
        self.rmt = BossRemote(cfg_file='test.cfg')

    def tearDown(self):
        pass

    def test_upload_and_download_to_channel(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]

        data = numpy.random.randint(0, 3000, (5, 4, 8))
        data = data.astype(numpy.uint8)

        self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.cutout_get(self.chan, 0, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_subsection_to_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 19]

        sub_x = [12, 14]
        sub_y = [7, 10]
        sub_z = [12, 17]

        data = numpy.random.randint(0, 3000, (9, 5, 10))
        data = data.astype(numpy.uint8)

        self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.cutout_get(self.chan, 0, sub_x, sub_y, sub_z)
        numpy.testing.assert_array_equal(data[2:7, 2:5, 2:4], actual)

    def test_upload_to_x_edge_of_channel(self):
        x_rng = [10, 100]
        y_rng = [5, 10]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 5, 90))
        data = data.astype(numpy.uint8)

        self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_y_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 50]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 45, 10))
        data = data.astype(numpy.uint8)

        self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_z_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 20]

        data = numpy.random.randint(0, 3000, (10, 5, 10))
        data = data.astype(numpy.uint8)

        self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_x_edge_of_channel(self):
        x_rng = [10, 101]
        y_rng = [5, 10]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 5, 91))
        data = data.astype(numpy.uint8)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_y_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 51]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 46, 10))
        data = data.astype(numpy.uint8)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_z_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 21]

        data = numpy.random.randint(0, 3000, (11, 5, 10))
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_and_download_to_channel_16bit(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]

        data = numpy.random.randint(0, 3000, (5, 4, 8))
        data = data.astype(numpy.uint16)

        self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.cutout_get(self.chan16, 0, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_subsection_to_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 19]

        sub_x = [12, 14]
        sub_y = [7, 10]
        sub_z = [12, 17]

        data = numpy.random.randint(0, 3000, (9, 5, 10))
        data = data.astype(numpy.uint16)

        self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.cutout_get(self.chan16, 0, sub_x, sub_y, sub_z)
        numpy.testing.assert_array_equal(data[2:7, 2:5, 2:4], actual)

    def test_upload_to_x_edge_of_channel_16bit(self):
        x_rng = [10, 100]
        y_rng = [5, 10]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 5, 90))
        data = data.astype(numpy.uint16)

        self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_y_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 50]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 45, 10))
        data = data.astype(numpy.uint16)

        self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_z_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 20]

        data = numpy.random.randint(0, 3000, (10, 5, 10))
        data = data.astype(numpy.uint16)

        self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_x_edge_of_channel_16bit(self):
        x_rng = [10, 101]
        y_rng = [5, 10]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 5, 91))
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_y_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 51]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 46, 10))
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_z_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 21]

        data = numpy.random.randint(0, 3000, (11, 5, 10))
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_and_download_to_layer(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]

        data = numpy.random.randint(0, 3000, (5, 4, 8))
        data = data.astype(numpy.uint64)

        self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.cutout_get(self.ann_chan, 0, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_subsection_to_layer(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 19]

        sub_x = [12, 14]
        sub_y = [7, 10]
        sub_z = [12, 17]

        data = numpy.random.randint(0, 3000, (9, 5, 10))
        data = data.astype(numpy.uint64)

        self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.cutout_get(self.ann_chan, 0, sub_x, sub_y, sub_z)
        numpy.testing.assert_array_equal(data[2:7, 2:5, 2:4], actual)

    def test_upload_to_x_edge_of_layer(self):
        x_rng = [10, 100]
        y_rng = [5, 10]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 5, 90))
        data = data.astype(numpy.uint64)

        self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_y_edge_of_layer(self):
        x_rng = [10, 20]
        y_rng = [5, 50]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 45, 10))
        data = data.astype(numpy.uint64)

        self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_z_edge_of_layer(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 20]

        data = numpy.random.randint(0, 3000, (10, 5, 10))
        data = data.astype(numpy.uint64)

        self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_x_edge_of_layer(self):
        x_rng = [10, 101]
        y_rng = [5, 10]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 5, 91))
        data = data.astype(numpy.uint64)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_y_edge_of_layer(self):
        x_rng = [10, 20]
        y_rng = [5, 51]
        z_rng = [10, 19]

        data = numpy.random.randint(0, 3000, (9, 46, 10))
        data = data.astype(numpy.uint64)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_z_edge_of_layer(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 21]

        data = numpy.random.randint(0, 3000, (11, 5, 10))
        data = data.astype(numpy.uint64)

        with self.assertRaises(HTTPError):
            self.rmt.cutout_create(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

if __name__ == '__main__':
    unittest.main()
