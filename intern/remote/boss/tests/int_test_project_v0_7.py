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

import random
import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import copy
import unittest

API_VER = 'v0.7'

class ProjectServiceTest_v0_7(unittest.TestCase):
    """Integration tests of the Boss resource API.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        cls.initialize()
        cls.cleanup_db()

    @classmethod
    def initialize(cls):
        """Initialization for each test.

        Called by both setUp() and setUpClass().
        """
        cls.rmt = BossRemote('test.cfg', API_VER)

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        cls.rmt.project_service.session_send_opts = { 'verify': False }
        cls.rmt.metadata_service.session_send_opts = { 'verify': False }
        cls.rmt.volume_service.session_send_opts = { 'verify': False }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        coll_name = 'collection2309-{}'.format(random.randint(0, 9999))
        cls.coll = CollectionResource(coll_name, 'bar')
        coll_name_upd = '{}-{}'.format(coll_name, random.randint(0, 9999))
        cls.coll_upd = CollectionResource(coll_name_upd, 'latest')

        cf_name = 'ProjTestFrame{}'.format(random.randint(0, 9999))
        cls.coord = CoordinateFrameResource(
            cf_name, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6,
            1, 1, 1, 'nanometers', 2, 'nanoseconds')
        cls.coord_upd = copy.copy(cls.coord)
        cls.coord_upd.name = 'MouseFrame'
        cls.coord_upd.description = 'Mouse coordinate frame.'

        cls.exp = ExperimentResource(
            'exp2309-2', cls.coll.name, cls.coord.name, 'my experiment',
            1, 'iso', 1)
        cls.exp_upd = ExperimentResource(
            'exp2309-2a', cls.coll.name, cls.coord.name,
            'my first experiment', 2, 'slice', 3)

        cls.source_chan = ChannelResource(
            'sourceChan', cls.coll.name, cls.exp.name, 'image', 'test source channel',
            0, 'uint8', 0)
        cls.related_chan = ChannelResource(
            'relatedChan', cls.coll.name, cls.exp.name, 'image', 'test related channel',
            0, 'uint8', 0)
        cls.chan = ChannelResource(
            'myChan', cls.coll.name, cls.exp.name, 'annotation', 'test annotation channel',
            0, 'uint8', 0, sources=['sourceChan'], related=['relatedChan'])
        cls.chan_upd = ChannelResource(
            'yourChan', cls.coll.name, cls.exp.name, 'annotation', 'your test annotation channel',
            1, 'uint8', 1, sources=['sourceChan'], related=['relatedChan'])

    @classmethod
    def cleanup_db(cls):
        try:
            cls.rmt.delete_project(cls.chan_upd)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.related_chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.source_chan)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.exp_upd)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.exp)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.coord_upd)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.coord)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.coll_upd)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_project(cls.coll)
        except HTTPError:
            pass

    def setUp(self):
        pass

    def tearDown(self):
        self.cleanup_db()

    def test_create_coord_frame(self):
        cf = self.rmt.create_project(self.coord)
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
        c = self.rmt.create_project(self.coll)
        self.assertEqual(self.coll.name, c.name)
        self.assertEqual(self.coll.description, c.description)

    def test_create_experiment(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertEqual(self.exp.name, e.name)
        self.assertEqual(self.exp.description, e.description)
        self.assertEqual(self.coll.name, e.coll_name)
        self.assertEqual(self.exp.coord_frame, e.coord_frame)
        self.assertEqual(self.exp.hierarchy_method, e.hierarchy_method)
        self.assertEqual(self.exp.num_hierarchy_levels, e.num_hierarchy_levels)
        self.assertEqual(self.exp.max_time_sample, e.max_time_sample)

    def test_create_channel(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.create_project(self.source_chan)
        self.assertEqual(self.source_chan.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.source_chan.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.source_chan.datatype, ch.datatype)
        self.assertEqual(self.source_chan.default_time_step, ch.default_time_step)
        self.assertEqual(self.source_chan.base_resolution, ch.base_resolution)

    def test_create_annotation_channel_without_source_fails(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        rel_ch = self.rmt.create_project(self.related_chan)
        self.assertIsNotNone(rel_ch)

        chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, 'annotation', 'test annotation channel',
            0, 'uint8', 0, related=['relatedChan'])

        with self.assertRaises(HTTPError):
            self.rmt.create_project(chan)

    def test_create_annotation_channel(self):
        """Annotation channels require a source channel."""
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.create_project(self.source_chan)
        self.assertIsNotNone(ch)

        rel_ch = self.rmt.create_project(self.related_chan)
        self.assertIsNotNone(rel_ch)

        ann_ch = self.rmt.create_project(self.chan)

        self.assertEqual(self.chan.name, ann_ch.name)
        self.assertEqual(self.exp.name, ann_ch.exp_name)
        self.assertEqual(self.chan.description, ann_ch.description)
        self.assertEqual(self.coll.name, ann_ch.coll_name)
        self.assertEqual(self.chan.datatype, ann_ch.datatype)
        self.assertEqual(self.chan.default_time_step, ann_ch.default_time_step)
        self.assertEqual(self.chan.base_resolution, ann_ch.base_resolution)
        self.assertEqual(self.chan.sources, ann_ch.sources)
        self.assertEqual(self.chan.related, ann_ch.related)

    def test_get_collection(self):
        coll = self.rmt.create_project(self.coll)
        self.assertIsNotNone(coll)

        c = self.rmt.get_project(self.coll)
        self.assertEqual(self.coll.name, c.name)
        self.assertEqual(self.coll.description, c.description)

    def test_get_coord_frame(self):
        coord = self.rmt.create_project(self.coord)
        self.assertIsNotNone(coord)

        cf = self.rmt.get_project(self.coord)
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
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        exp = self.rmt.create_project(self.exp)
        self.assertIsNotNone(exp)

        e = self.rmt.get_project(self.exp)
        self.assertEqual(self.exp.name, e.name)
        self.assertEqual(self.exp.description, e.description)
        self.assertEqual(self.coll.name, e.coll_name)
        self.assertEqual(self.exp.coord_frame, e.coord_frame)
        self.assertEqual(self.exp.hierarchy_method, e.hierarchy_method)
        self.assertEqual(self.exp.num_hierarchy_levels, e.num_hierarchy_levels)
        self.assertEqual(self.exp.max_time_sample, e.max_time_sample)

    def test_get_channel(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        chan = self.rmt.create_project(self.source_chan)
        self.assertIsNotNone(chan)

        ch = self.rmt.get_project(self.source_chan)
        self.assertEqual(self.source_chan.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.source_chan.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.source_chan.datatype, ch.datatype)
        self.assertEqual(self.source_chan.default_time_step, ch.default_time_step)
        self.assertEqual(self.source_chan.base_resolution, ch.base_resolution)

    def test_update_collection(self):
        coll = self.rmt.create_project(self.coll)
        self.assertIsNotNone(coll)

        c = self.rmt.update_project(self.coll.name, self.coll_upd)
        self.assertEqual(self.coll_upd.name, c.name)
        self.assertEqual(self.coll_upd.description, c.description)

    def test_update_coord_frame(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        coord = self.rmt.create_project(self.coord)
        self.assertIsNotNone(coord)

        cf = self.rmt.update_project(self.coord.name, self.coord_upd)
        self.assertEqual(self.coord_upd.name, cf.name)
        self.assertEqual(self.coord_upd.description, cf.description)

    def test_update_experiment(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        eup = self.rmt.update_project(self.exp.name, self.exp_upd)
        self.assertEqual(self.exp_upd.name, eup.name)
        self.assertEqual(self.exp_upd.description, eup.description)
        self.assertEqual(self.coll.name, eup.coll_name)
        self.assertEqual(self.exp_upd.coord_frame, eup.coord_frame)
        self.assertEqual(self.exp_upd.hierarchy_method, eup.hierarchy_method)
        self.assertEqual(self.exp_upd.num_hierarchy_levels, eup.num_hierarchy_levels)
        self.assertEqual(self.exp_upd.max_time_sample, eup.max_time_sample)

    def test_update_channel(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        source_ch = self.rmt.create_project(self.source_chan)
        self.assertIsNotNone(source_ch)

        rel_ch = self.rmt.create_project(self.related_chan)
        self.assertIsNotNone(rel_ch)

        chan = self.rmt.create_project(self.chan)
        self.assertIsNotNone(chan)

        ch = self.rmt.update_project(self.chan.name, self.chan_upd)
        self.assertEqual(self.chan_upd.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.chan_upd.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.chan_upd.datatype, ch.datatype)
        self.assertEqual(self.chan_upd.default_time_step, ch.default_time_step)
        self.assertEqual(self.chan_upd.base_resolution, ch.base_resolution)
        self.assertEqual(self.chan_upd.sources, ch.sources)
        self.assertEqual(self.chan_upd.related, ch.related)

    def test_list_collections(self):
        coll = self.rmt.create_project(self.coll)
        self.assertIsNotNone(coll)

        coll_list = self.rmt.list_collections()
        c = [name for name in coll_list if name == self.coll.name]
        self.assertEqual(1, len(c))
        self.assertEqual(self.coll.name, c[0])

    def test_list_coord_frames(self):
        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        cf_list = self.rmt.list_coordinate_frames()
        c = [name for name in cf_list if name == self.coord.name]
        self.assertEqual(1, len(c))
        self.assertEqual(self.coord.name, c[0])

    def test_list_experiments(self):
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        exp = self.rmt.create_project(self.exp)
        self.assertIsNotNone(exp)

        exp_list = self.rmt.list_experiments(self.coll.name)
        e = [name for name in exp_list if name == self.exp.name]
        self.assertEqual(1, len(e))
        self.assertEqual(self.exp.name, e[0])

    #def test_list_channels(self):
    #    c = self.rmt.create_project(self.coll)
    #    self.assertIsNotNone(c)

    #    cf = self.rmt.create_project(self.coord)
    #    self.assertIsNotNone(cf)

    #    e = self.rmt.create_project(self.exp)
    #    self.assertIsNotNone(e)

    #    chan = self.rmt.create_project(self.chan)
    #    self.assertIsNotNone(chan)

    #    chan_list = self.rmt.list_channels(self.coll.name, self.exp.name)
    #    ch = [name for name in chan_list if name == self.chan.name]
    #    self.assertEqual(1, len(ch))
    #    self.assertEqual(self.chan.name, ch[0])

    def test_delete_all(self):
        """Formally test delete at all levels of the data model.

        Delete happens all the time in the tearDown() but specifically test
        it here.
        """
        c = self.rmt.create_project(self.coll)
        self.assertIsNotNone(c)

        cf = self.rmt.create_project(self.coord)
        self.assertIsNotNone(cf)

        e = self.rmt.create_project(self.exp)
        self.assertIsNotNone(e)

        ch = self.rmt.create_project(self.source_chan)
        self.assertIsNotNone(ch)

        self.rmt.delete_project(self.source_chan)
        self.rmt.delete_project(self.exp)
        self.rmt.delete_project(self.coord)
        self.rmt.delete_project(self.coll)

if __name__ == '__main__':
    unittest.main()
