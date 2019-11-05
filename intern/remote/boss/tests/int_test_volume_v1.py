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

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
from intern.service.boss.httperrorlist import HTTPErrorList
import numpy

import random
import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest
import time

API_VER = 'v1'


class VolumeServiceTest_v1(unittest.TestCase):
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
        cls.rmt = BossRemote('test.cfg', API_VER)

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        cls.rmt.project_service.session_send_opts = {'verify': False}
        cls.rmt.metadata_service.session_send_opts = {'verify': False}
        cls.rmt.volume_service.session_send_opts = {'verify': False}
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        coll_name = 'collection2323{}'.format(random.randint(0, 9999))
        cls.coll = CollectionResource(coll_name, 'bar')

        cf_name = 'BestFrame{}'.format(random.randint(0, 9999))
        cls.coord = CoordinateFrameResource(
            cf_name, 'Test coordinate frame.', 0, 2048, 0, 2048, 0, 100,
            1, 1, 1, 'nanometers', 0, 'nanoseconds')

        # cls.exp.coord_frame must be set with valid id before creating.
        cls.exp = ExperimentResource(
            'exp2323x2', cls.coll.name, cls.coord.name, 'my experiment',
            1, 'isotropic', 10)

        cls.chan = ChannelResource(
            'myVolChan', cls.coll.name, cls.exp.name, 'image', 'test channel',
            0, 'uint8', 0)

        cls.chan16 = ChannelResource(
            'myVol16bitChan', cls.coll.name, cls.exp.name, 'image',
            '16 bit test channel', 0, 'uint16', 0)

        cls.ann_chan = ChannelResource(
            'annVolChan2', cls.coll.name, cls.exp.name, 'annotation',
            'annotation test channel', 0, 'uint64', 0, sources=[cls.chan.name])

        # This channel reserved for testing get_ids_in_region().  This is a
        # separate channel so we don't have to worry about ids written by
        # other tests.
        cls.ann_region_chan = ChannelResource(
            'annRegionChan2', cls.coll.name, cls.exp.name, 'annotation',
            'annotation ids in region test channel', 0, 'uint64', 0,
            sources=[cls.chan.name])

        # This channel reerved for testing tight bounding boxes.
        cls.ann_bounding_chan = ChannelResource(
            'annRegionChan3', cls.coll.name, cls.exp.name, 'annotation',
            'annotation ids in bounding box test channel', 0, 'uint64', 0,
            sources=[cls.chan.name])

        cls.rmt.create_project(cls.coll)
        cls.rmt.create_project(cls.coord)
        cls.rmt.create_project(cls.exp)
        cls.rmt.create_project(cls.chan16)
        cls.rmt.create_project(cls.chan)
        cls.rmt.create_project(cls.ann_chan)
        cls.rmt.create_project(cls.ann_region_chan)
        cls.rmt.create_project(cls.ann_bounding_chan)

    @classmethod
    def tearDownClass(cls):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDownClass() and setUpClass().
        """
        try:
            cls.rmt.delete_project(cls.ann_bounding_chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.ann_region_chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.ann_chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.chan16)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.exp)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.coord)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.coll)
        except HTTPError:
            pass

    def setUp(self):
        self.rmt = BossRemote('test.cfg')

    def tearDown(self):
        pass

    def test_reserve_ids(self):
        first_id = self.rmt.reserve_ids(self.ann_chan, 20)
        self.assertTrue(first_id > 0)

    def test_get_bounding_box_id_doesnt_exist(self):
        resolution = 0
        id = 12345678
        with self.assertRaises(HTTPError) as err:
            self.rmt.get_bounding_box(self.ann_chan, resolution, id, 'loose')
            expected_msg_prefix = 'Reserve ids failed'
            self.assertTrue(err.message.startwswith(expected_msg_prefix))

    @unittest.skip('Skipping - currently indexing disabled')
    def test_get_bounding_box_spans_cuboids_in_x(self):
        x_rng = [511, 515]
        y_rng = [0, 8]
        z_rng = [0, 5]
        t_rng = [0, 1]

        id = 77555

        data = numpy.zeros((5, 8, 4), dtype='uint64')
        data[1][0][0] = id
        data[2][1][1] = id
        data[3][2][3] = id

        resolution = 0

        self.rmt.create_cutout(
            self.ann_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual = self.rmt.get_cutout(self.ann_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

        expected = {
            'x_range': [0, 1024],
            'y_range': [0, 512],
            'z_range': [0, 16],
            't_range': [0, 1]
        }

        actual = self.rmt.get_bounding_box(self.ann_chan, resolution, id, 'loose')

        self.assertEqual(expected, actual)

    @unittest.skip('Skipping - currently indexing disabled')
    def test_get_bounding_box_spans_cuboids_in_y(self):
        x_rng = [0, 8]
        y_rng = [511, 515]
        z_rng = [0, 5]
        t_rng = [0, 1]

        id = 77666

        data = numpy.zeros((5, 4, 8), dtype='uint64')
        data[1][0][0] = id
        data[2][1][0] = id
        data[3][2][0] = id

        resolution = 0

        self.rmt.create_cutout(
            self.ann_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual = self.rmt.get_cutout(self.ann_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

        expected = {
            'x_range': [0, 512],
            'y_range': [0, 1024],
            'z_range': [0, 16],
            't_range': [0, 1]
        }

        actual = self.rmt.get_bounding_box(self.ann_chan, resolution, id, 'loose')

        self.assertEqual(expected, actual)

    @unittest.skip('Skipping - currently indexing disabled')
    def test_get_bounding_box_spans_cuboids_in_z(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [30, 35]
        t_rng = [0, 1]

        id = 77888

        data = numpy.zeros((5, 4, 8), dtype='uint64')
        data[1][0][0] = id
        data[2][1][0] = id
        data[3][2][0] = id

        resolution = 0

        self.rmt.create_cutout(
            self.ann_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual = self.rmt.get_cutout(self.ann_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

        expected = {
            'x_range': [0, 512],
            'y_range': [0, 512],
            'z_range': [16, 48],
            't_range': [0, 1]
        }

        actual = self.rmt.get_bounding_box(self.ann_chan, resolution, id, 'loose')

        self.assertEqual(expected, actual)

    @unittest.skip('Skipping - currently indexing disabled')
    def test_tight_bounding_box_x_axis(self):
        """Test tight bounding box with ids that span three cuboids along the x axis."""
        resolution = 0
        x_rng = [511, 1025]
        y_rng = [512, 1024]
        z_rng = [16, 32]
        t_rng = [0, 1]

        data = numpy.zeros((16, 512, 514), dtype='uint64')

        x_id = 123
        y_id = 127
        z_id = 500000000000000000

        # Id in partial region on x axis closest to origin.
        data[1][1][0] = x_id
        # Id in partial region on x axis furthest from origin.
        data[1][1][513] = x_id

        # Id in cuboid aligned region.
        data[2][2][21] = x_id
        data[2][1][22] = y_id
        data[4][24][72] = z_id

        expected = {'x_range': [511, 1025], 'y_range': [513, 515], 'z_range': [17, 19]}

        self.rmt.create_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_bounding_box(
            self.ann_bounding_chan, resolution, x_id, bb_type='tight')

    @unittest.skip('Skipping - currently indexing disabled')
    def test_tight_bounding_box_y_axis(self):
        """Test tight bounding box with ids that span three cuboids along the x axis."""
        resolution = 0
        x_rng = [512, 1024]
        y_rng = [511, 1025]
        z_rng = [16, 32]
        t_rng = [0, 1]

        data = numpy.zeros((16, 514, 512), dtype='uint64')

        x_id = 123
        y_id = 127
        z_id = 500000000000000000

        # Id in partial region on y axis closest to origin.
        data[1][0][10] = y_id
        # Id in partial region on y axis furthest from origin.
        data[1][513][13] = y_id

        # Id in cuboid aligned region.
        data[2][2][21] = y_id
        data[2][3][20] = x_id
        data[4][25][71] = z_id

        expected = {'x_range': [522, 526], 'y_range': [511, 1025], 'z_range': [17, 19]}

        self.rmt.create_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_bounding_box(
            self.ann_bounding_chan, resolution, y_id, bb_type='tight')

    @unittest.skip('Skipping - currently indexing disabled')
    def test_tight_bounding_box_z_axis(self):
        """Test tight bounding box with ids that span three cuboids along the x axis."""
        resolution = 0
        x_rng = [512, 1024]
        y_rng = [512, 1024]
        z_rng = [15, 33]
        t_rng = [0, 1]

        data = numpy.zeros((18, 512, 512), dtype='uint64')

        x_id = 123
        y_id = 127
        z_id = 500000000000000000

        # Id in partial region on z axis closest to origin.
        data[0][22][60] = z_id
        # Id in partial region on z axis furthest from origin.
        data[17][23][63] = z_id

        # Id in cuboid aligned region.
        data[5][24][71] = z_id
        data[3][2][20] = x_id
        data[3][1][21] = y_id

        expected = {'x_range': [572, 583], 'y_range': [534, 537], 'z_range': [15, 33]}

        self.rmt.create_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_bounding_box(
            self.ann_bounding_chan, resolution, z_id, bb_type='tight')

    def test_get_ids_in_region_none(self):
        """Run on region that hasn't been written with ids, yet."""
        resolution = 0
        x_rng = [1536, 1540]
        y_rng = [1536, 1540]
        z_rng = [48, 56]
        t_rng = [0, 1]

        data = numpy.zeros((8, 4, 4), dtype='uint64')

        expected = []

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_bounding_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_ids_in_region(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)

        self.assertEqual(expected, actual)

    def test_filtered_cutout(self):
        """Test filtered cutout using same data written for get_ids_in_region_x_axis."""
        resolution = 0
        x_rng = [511, 1025]
        y_rng = [512, 1024]
        z_rng = [16, 32]
        t_rng = [0, 1]

        data = numpy.zeros((16, 512, 514), dtype='uint64')

        # Id in partial region on x axis closest to origin.
        data[1][1][0] = 123
        # Id in partial region on x axis furthest from origin.
        data[1][1][513] = 321

        # Id in cuboid aligned region.
        data[10][20][21] = 55555

        expected = [123, 321, 55555]

        self.rmt.create_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Should get back the exact data given in create_cutout().
        filtered_data1 = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng,
            id_list=[123, 321, 55555])
        numpy.testing.assert_array_equal(data, filtered_data1)

        # Filter on id 123.
        expected_data_123 = numpy.zeros((16, 512, 514), dtype='uint64')
        expected_data_123[1][1][0] = 123

        filtered_data_123 = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng, id_list=[123])
        numpy.testing.assert_array_equal(expected_data_123, filtered_data_123)

        # Filter on id 321.
        expected_data_321 = numpy.zeros((16, 512, 514), dtype='uint64')
        expected_data_321[1][1][513] = 321

        filtered_data_321 = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng, id_list=[321])
        numpy.testing.assert_array_equal(expected_data_321, filtered_data_321)

        # Filter on ids 123 and 55555.
        expected_data_123_55555 = numpy.zeros((16, 512, 514), dtype='uint64')
        expected_data_123_55555[1][1][0] = 123
        expected_data_123_55555[10][20][21] = 55555

        filtered_data_123_55555 = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng,
            id_list=[123, 55555])
        numpy.testing.assert_array_equal(
            expected_data_123_55555, filtered_data_123_55555)

    @unittest.skip('Skipping - currently indexing disabled')
    def test_get_ids_in_region_x_axis(self):
        """Test using a region that's cuboid aligned except for the x axis."""
        resolution = 0
        x_rng = [511, 1025]
        y_rng = [512, 1024]
        z_rng = [16, 32]
        t_rng = [0, 1]

        data = numpy.zeros((16, 512, 514), dtype='uint64')

        # Id in partial region on x axis closest to origin.
        data[1][1][0] = 123
        # Id in partial region on x axis furthest from origin.
        data[1][1][513] = 321

        # Id in cuboid aligned region.
        data[10][20][21] = 55555

        expected = [123, 321, 55555]

        self.rmt.create_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_ids_in_region(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)

        self.assertEqual(expected, actual)

    @unittest.skip('Skipping - currently indexing disabled')
    def test_get_ids_in_region_y_axis(self):
        """Test using a region that's cuboid aligned except for the y axis."""
        resolution = 0
        x_rng = [512, 1024]
        y_rng = [511, 1025]
        z_rng = [16, 32]
        t_rng = [0, 1]

        data = numpy.zeros((16, 514, 512), dtype='uint64')

        # Id in partial region on y axis closest to origin.
        data[1][0][1] = 456
        # Id in partial region on y axis furthest from origin.
        data[1][513][1] = 654

        # Id in cuboid aligned region.
        data[10][21][20] = 55555

        # expected = [123, 321, 456, 654, 789, 987, 55555]
        expected = [456, 654, 55555]

        self.rmt.create_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_ids_in_region(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)

        self.assertEqual(expected, actual)

    @unittest.skip('Skipping - currently indexing disabled')
    def test_get_ids_in_region_z_axis(self):
        """Test using a region that's cuboid aligned except for the z axis."""
        resolution = 0
        x_rng = [512, 1024]
        y_rng = [512, 1024]
        z_rng = [15, 33]
        t_rng = [0, 1]

        data = numpy.zeros((18, 512, 512), dtype='uint64')

        # Id in partial region on z axis closest to origin.
        data[0][1][1] = 789
        # Id in partial region on z axis furthest from origin.
        data[17][1][1] = 987

        # Id in cuboid aligned region.
        data[11][20][20] = 55555

        expected = [789, 987, 55555]

        self.rmt.create_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng, data)

        # Get cutout to make sure data is done writing and indices updated.
        actual_data = self.rmt.get_cutout(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual_data)

        # Method under test.
        actual = self.rmt.get_ids_in_region(
            self.ann_region_chan, resolution, x_rng, y_rng, z_rng)

        self.assertEqual(expected, actual)


    def test_upload_and_download_to_channel(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]

        data = numpy.random.randint(1, 254, (5, 4, 8))
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.get_cutout(self.chan, 0, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_to_channel_with_time(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]
        t_rng = [3, 6]

        data = numpy.random.randint(1, 254, (3, 5, 4, 8))
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data, time_range=t_rng)
        actual = self.rmt.get_cutout(self.chan, 0, x_rng, y_rng, z_rng, time_range=t_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_subsection_to_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 19]

        sub_x = [12, 14]
        sub_y = [7, 10]
        sub_z = [12, 17]

        data = numpy.random.randint(1, 10, (9, 5, 10))
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.get_cutout(self.chan, 0, sub_x, sub_y, sub_z)
        numpy.testing.assert_array_equal(data[2:7, 2:5, 2:4], actual)

    def test_upload_to_x_edge_of_channel(self):
        x_rng = [10, 2048]
        y_rng = [5, 10]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_y_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 2048]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_z_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 100]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_x_edge_of_channel(self):
        x_rng = [10, 2049]
        y_rng = [5, 10]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint8)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_y_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 2049]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint8)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_z_edge_of_channel(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 101]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_and_download_to_channel_16bit(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.get_cutout(self.chan16, 0, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_subsection_to_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 19]

        sub_x = [12, 14]
        sub_y = [7, 10]
        sub_z = [12, 17]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.get_cutout(self.chan16, 0, sub_x, sub_y, sub_z)
        numpy.testing.assert_array_equal(data[2:7, 2:5, 2:4], actual)

    def test_upload_to_x_edge_of_channel_16bit(self):
        x_rng = [2000, 2048]
        y_rng = [5, 10]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_y_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [2000, 2048]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_z_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 100]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_x_edge_of_channel_16bit(self):
        x_rng = [2000, 2049]
        y_rng = [5, 10]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_y_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [2000, 2049]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_z_edge_of_channel_16bit(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 101]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint16)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.chan16, 0, x_rng, y_rng, z_rng, data)

    def test_upload_and_download_to_anno_chan(self):
        x_rng = [0, 8]
        y_rng = [0, 4]
        z_rng = [0, 5]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.get_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng)
        numpy.testing.assert_array_equal(data, actual)

    def test_upload_and_download_subsection_to_anno_chan(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 19]

        sub_x = [12, 14]
        sub_y = [7, 10]
        sub_z = [12, 17]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)
        actual = self.rmt.get_cutout(self.ann_chan, 0, sub_x, sub_y, sub_z)
        numpy.testing.assert_array_equal(data[2:7, 2:5, 2:4], actual)

    def test_upload_to_x_edge_of_anno_chan(self):
        x_rng = [2000, 2048]
        y_rng = [5, 10]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_y_edge_of_anno_chan(self):
        x_rng = [10, 20]
        y_rng = [2000, 2048]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_to_z_edge_of_anno_chan(self):
        x_rng = [10, 100]
        y_rng = [5, 10]
        z_rng = [10, 100]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_x_edge_of_anno_chan(self):
        x_rng = [10, 2049]
        y_rng = [5, 10]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_y_edge_of_anno_chan(self):
        x_rng = [10, 991]
        y_rng = [5, 2049]
        z_rng = [10, 19]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_past_z_edge_of_anno_chan(self):
        x_rng = [10, 20]
        y_rng = [5, 10]
        z_rng = [10, 101]

        shape = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint64)

        with self.assertRaises(HTTPError):
            self.rmt.create_cutout(self.ann_chan, 0, x_rng, y_rng, z_rng, data)

    def test_upload_and_download_to_channel_4D(self):
        x_rng = [600, 680]
        y_rng = [600, 640]
        z_rng = [50, 55]
        t_rng = [0, 1]

        shape = (t_rng[1]-t_rng[0], z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

        data = numpy.random.randint(1, 10, shape)
        data = data.astype(numpy.uint8)

        self.rmt.create_cutout(self.chan, 0, x_rng, y_rng, z_rng, data, time_range=t_rng)
        actual = self.rmt.get_cutout(self.chan, 0, x_rng, y_rng, z_rng, time_range=t_rng)
        numpy.testing.assert_array_equal(data, actual)

if __name__ == '__main__':
    unittest.main()
