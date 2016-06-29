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
 
from ndio.remote.boss.remote import *
from ndio.ndresource.boss.resource import *

import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import copy
import unittest

API_VER = 'v0.4'

class ProjectServiceTest_v0_4(unittest.TestCase):
    """Integration tests of the Boss resource API.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        cls.initialize(cls)
        cls.cleanup_db(cls)

    def initialize(self):
        """Initialization for each test.

        Called by both setUp() and setUpClass().
        """
        self.rmt = Remote('test.cfg')

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        self.rmt.project_service.session_send_opts = { 'verify': False }
        self.rmt.metadata_service.session_send_opts = { 'verify': False }
        self.rmt.volume_service.session_send_opts = { 'verify': False }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.coll = CollectionResource('collection2309', API_VER, 'bar')
        self.coll_upd = CollectionResource('collection2310', API_VER, 'latest')

        self.coord = CoordinateFrameResource(
            'BestFrame', API_VER, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6, 
            1, 1, 1, 'nanometers', 0, 'nanoseconds')
        self.coord_upd = copy.copy(self.coord)
        self.coord_upd.name = 'MouseFrame'
        self.coord_upd.description = 'Mouse coordinate frame.'

        # Coordinate frame of experiments needs to be set to a valid ID before
        # creating.
        self.exp = ExperimentResource(
            'exp2309-2', self.coll.name, API_VER, 'my experiment', 0, 1, 
            'iso', 0)
        self.exp_upd = ExperimentResource(
            'exp2309-2a', self.coll.name, API_VER, 'my first experiment', 
            0, 2, 'slice', 1)

        self.chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, API_VER, 'test channel', 
            0, 'uint8', 0)
        self.chan_upd = ChannelResource(
            'yourChan', self.coll.name, self.exp.name, API_VER, 'your test channel', 
            1, 'uint8', 1)

        # Layer's channel list needs to be given a valid channel ID before 
        # creating.
        self.lyr = LayerResource(
            'topLayer', self.coll.name, self.exp.name, API_VER, 'test layer',
            0, 'uint64', 0)
        self.lyr_upd = LayerResource(
            'upperLayer', self.coll.name, self.exp.name, API_VER, 'test upper layer',
            1, 'uint64', 1)

    def cleanup_db(self):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().
        """
        try:
            self.rmt.project_delete(self.lyr_upd)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.lyr)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.chan_upd)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.chan)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.exp_upd)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.exp)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coord_upd)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coord)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coll_upd)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coll)
        except HTTPError:
            pass

    def setUp(self):
        self.initialize()

    def tearDown(self):
        self.cleanup_db()

    def test_create_coord_frame(self):
        cf = self.rmt.project_create(self.coord)
        self.assertEqual(self.coord.name, cf.name)
        self.assertEqual(self.coord.description, cf.description)
        self.assertEqual(self.coord.x_start, cf.x_start)
        self.assertEqual(self.coord.x_stop, cf.x_stop)
        self.assertEqual(self.coord.y_start, cf.y_start)
        self.assertEqual(self.coord.y_stop, cf.y_stop)
        self.assertEqual(self.coord.z_start, cf.z_start)
        self.assertEqual(self.coord.z_stop, cf.z_stop)
        self.assertEqual(self.coord.x_voxel_size, cf.x_voxel_size)
        self.assertEqual(self.coord.y_voxel_size, cf.y_voxel_size)
        self.assertEqual(self.coord.z_voxel_size, cf.z_voxel_size)
        self.assertEqual(self.coord.voxel_unit, cf.voxel_unit)
        self.assertEqual(self.coord.time_step, cf.time_step)
        self.assertEqual(self.coord.time_step_unit, cf.time_step_unit)

    def test_create_collection(self):
        c = self.rmt.project_create(self.coll)
        self.assertEqual(self.coll.name, c.name)
        self.assertEqual(self.coll.description, c.description)

    def test_create_experiment(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertEqual(self.exp.name, e.name)
        self.assertEqual(self.exp.description, e.description)
        self.assertEqual(self.coll.name, e.coll_name)
        self.assertEqual(self.exp.coord_frame, e.coord_frame)
        self.assertEqual(self.exp.hierarchy_method, e.hierarchy_method)
        self.assertEqual(self.exp.num_hierarchy_levels, e.num_hierarchy_levels)
        self.assertEqual(self.exp.max_time_sample, e.max_time_sample)

    def test_create_channel(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.project_create(self.chan)
        self.assertEqual(self.chan.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.chan.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.chan.datatype, ch.datatype)
        self.assertEqual(self.chan.default_time_step, ch.default_time_step)
        self.assertEqual(self.chan.base_resolution, ch.base_resolution)

    def test_create_layer(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.project_create(self.chan)
        self.assertIsNotNone(ch)

        self.lyr.channels = [ch.id]
        lyr = self.rmt.project_create(self.lyr)
        self.assertEqual(self.lyr.name, lyr.name)
        self.assertEqual(self.exp.name, lyr.exp_name)
        self.assertEqual(self.lyr.description, lyr.description)
        self.assertEqual(self.coll.name, lyr.coll_name)
        self.assertEqual(self.lyr.datatype, lyr.datatype)
        self.assertEqual(self.lyr.default_time_step, lyr.default_time_step)
        self.assertEqual(self.lyr.base_resolution, lyr.base_resolution)

    def test_get_collection(self):
        coll = self.rmt.project_create(self.coll)
        self.assertIsNotNone(coll)

        c = self.rmt.project_get(self.coll)
        self.assertEqual(self.coll.name, c.name)
        self.assertEqual(self.coll.description, c.description)

    def test_get_coord_frame(self):
        coord = self.rmt.project_create(self.coord)
        self.assertIsNotNone(coord)

        cf = self.rmt.project_get(self.coord)
        self.assertEqual(self.coord.name, cf.name)
        self.assertEqual(self.coord.description, cf.description)
        self.assertEqual(self.coord.x_start, cf.x_start)
        self.assertEqual(self.coord.x_stop, cf.x_stop)
        self.assertEqual(self.coord.y_start, cf.y_start)
        self.assertEqual(self.coord.y_stop, cf.y_stop)
        self.assertEqual(self.coord.z_start, cf.z_start)
        self.assertEqual(self.coord.z_stop, cf.z_stop)
        self.assertEqual(self.coord.x_voxel_size, cf.x_voxel_size)
        self.assertEqual(self.coord.y_voxel_size, cf.y_voxel_size)
        self.assertEqual(self.coord.z_voxel_size, cf.z_voxel_size)
        self.assertEqual(self.coord.voxel_unit, cf.voxel_unit)
        self.assertEqual(self.coord.time_step, cf.time_step)
        self.assertEqual(self.coord.time_step_unit, cf.time_step_unit)

    def test_get_experiment(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        exp = self.rmt.project_create(self.exp)
        self.assertIsNotNone(exp)

        e = self.rmt.project_get(self.exp)
        self.assertEqual(self.exp.name, e.name)
        self.assertEqual(self.exp.description, e.description)
        self.assertEqual(self.coll.name, e.coll_name)
        self.assertEqual(self.exp.coord_frame, e.coord_frame)
        self.assertEqual(self.exp.hierarchy_method, e.hierarchy_method)
        self.assertEqual(self.exp.num_hierarchy_levels, e.num_hierarchy_levels)
        self.assertEqual(self.exp.max_time_sample, e.max_time_sample)

    def test_get_channel(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        chan = self.rmt.project_create(self.chan)
        self.assertIsNotNone(chan)

        ch = self.rmt.project_get(self.chan)
        self.assertEqual(self.chan.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.chan.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.chan.datatype, ch.datatype)
        self.assertEqual(self.chan.default_time_step, ch.default_time_step)
        self.assertEqual(self.chan.base_resolution, ch.base_resolution)

    def test_get_layer(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.project_create(self.chan)
        self.assertIsNotNone(ch)

        self.lyr.channels = [ch.id]
        layer = self.rmt.project_create(self.lyr)
        self.assertIsNotNone(layer)

        lyr = self.rmt.project_get(self.lyr)
        self.assertEqual(self.lyr.name, lyr.name)
        self.assertEqual(self.exp.name, lyr.exp_name)
        self.assertEqual(self.lyr.description, lyr.description)
        self.assertEqual(self.coll.name, lyr.coll_name)
        self.assertEqual(self.lyr.datatype, lyr.datatype)
        self.assertEqual(self.lyr.default_time_step, lyr.default_time_step)
        self.assertEqual(self.lyr.base_resolution, lyr.base_resolution)

    def test_update_collection(self):
        coll = self.rmt.project_create(self.coll)
        self.assertIsNotNone(coll)

        c = self.rmt.project_update(self.coll.name, self.coll_upd)
        self.assertEqual(self.coll_upd.name, c.name)
        self.assertEqual(self.coll_upd.description, c.description)

    def test_update_coord_frame(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        coord = self.rmt.project_create(self.coord)
        self.assertIsNotNone(coord)

        cf = self.rmt.project_update(self.coord.name, self.coord_upd)
        self.assertEqual(self.coord_upd.name, cf.name)
        self.assertEqual(self.coord_upd.description, cf.description)

    def test_update_experiment(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        self.exp_upd.coord_frame = cf.id
        eup = self.rmt.project_update(self.exp.name, self.exp_upd)
        self.assertEqual(self.exp_upd.name, eup.name)
        self.assertEqual(self.exp_upd.description, eup.description)
        self.assertEqual(self.coll.name, eup.coll_name)
        self.assertEqual(self.exp_upd.coord_frame, eup.coord_frame)
        self.assertEqual(self.exp_upd.hierarchy_method, eup.hierarchy_method)
        self.assertEqual(self.exp_upd.num_hierarchy_levels, eup.num_hierarchy_levels)
        self.assertEqual(self.exp_upd.max_time_sample, eup.max_time_sample)

    def test_update_channel(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        chan = self.rmt.project_create(self.chan)
        self.assertIsNotNone(chan)

        ch = self.rmt.project_update(self.chan.name, self.chan_upd)
        self.assertEqual(self.chan_upd.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.chan_upd.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.chan_upd.datatype, ch.datatype)
        self.assertEqual(self.chan_upd.default_time_step, ch.default_time_step)
        self.assertEqual(self.chan_upd.base_resolution, ch.base_resolution)

    def test_update_layer(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.project_create(self.chan)
        self.assertIsNotNone(ch)

        self.lyr.channels = [ch.id]
        layer = self.rmt.project_create(self.lyr)
        self.assertIsNotNone(layer)

        lyr = self.rmt.project_update(self.lyr.name, self.lyr_upd)
        self.assertEqual(self.lyr_upd.name, lyr.name)
        self.assertEqual(self.exp.name, lyr.exp_name)
        self.assertEqual(self.lyr_upd.description, lyr.description)
        self.assertEqual(self.coll.name, lyr.coll_name)
        self.assertEqual(self.lyr_upd.datatype, lyr.datatype)
        self.assertEqual(self.lyr_upd.default_time_step, lyr.default_time_step)
        self.assertEqual(self.lyr_upd.base_resolution, lyr.base_resolution)

    def test_list_collection(self):
        coll = self.rmt.project_create(self.coll)
        self.assertIsNotNone(coll)

        coll_list = self.rmt.project_list(self.coll)
        c = [i for i in coll_list if i['name'] == self.coll.name]
        self.assertEqual(1, len(c))
        self.assertEqual(self.coll.name, c[0]['name'])

    def test_list_coord_frame(self):
        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        cf_list = self.rmt.project_list(self.coord)
        c = [i for i in cf_list if i['name'] == self.coord.name]
        self.assertEqual(1, len(c))
        self.assertEqual(self.coord.name, c[0]['name'])

    def test_list_experiment(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        exp = self.rmt.project_create(self.exp)
        self.assertIsNotNone(exp)

        exp_list = self.rmt.project_list(self.exp)
        e = [i for i in exp_list if i['name'] == self.exp.name]
        self.assertEqual(1, len(e))
        self.assertEqual(self.exp.name, e[0]['name'])

    def test_list_channel(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        chan = self.rmt.project_create(self.chan)
        self.assertIsNotNone(chan)

        chan_list = self.rmt.project_list(self.chan)
        ch = [i for i in chan_list if i['name'] == self.chan.name]
        self.assertEqual(1, len(ch))
        self.assertEqual(self.chan.name, ch[0]['name'])

    def test_list_layer(self):
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.project_create(self.chan)
        self.assertIsNotNone(ch)

        self.lyr.channels = [ch.id]
        layer = self.rmt.project_create(self.lyr)
        self.assertIsNotNone(layer)

        lyr_list = self.rmt.project_list(self.lyr)
        l = [i for i in lyr_list if i['name'] == self.lyr.name]
        self.assertEqual(1, len(l))
        self.assertEqual(self.lyr.name, l[0]['name'])

    def test_delete_all(self):
        """Formally test delete at all levels of the data model.
        
        Delete happens all the time in the tearDown() but specifically test
        it here.
        """
        c = self.rmt.project_create(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.project_create(self.coord)
        self.assertIsNotNone(cf)

        self.exp.coord_frame = cf.id
        e = self.rmt.project_create(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.project_create(self.chan)
        self.assertIsNotNone(ch)

        self.lyr.channels = [ch.id]
        layer = self.rmt.project_create(self.lyr)
        self.assertIsNotNone(layer)
        
        self.rmt.project_delete(self.lyr)
        self.rmt.project_delete(self.chan)
        self.rmt.project_delete(self.exp)
        self.rmt.project_delete(self.coord)
        self.rmt.project_delete(self.coll)

if __name__ == '__main__':
    unittest.main()
