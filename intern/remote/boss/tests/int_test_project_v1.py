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

API_VER = 'v1'

class ProjectServiceTest_v1(unittest.TestCase):
    """Integration tests of the Boss resource API.
    """

    def setUp(self):
        self.rmt = BossRemote('test.cfg', API_VER)

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        self.rmt.project_service.session_send_opts = { 'verify': False }
        self.rmt.metadata_service.session_send_opts = { 'verify': False }
        self.rmt.volume_service.session_send_opts = { 'verify': False }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        coll_name = 'collection2309-{}'.format(random.randint(0, 9999))
        self.coll = CollectionResource(coll_name, 'bar')
        coll_name_upd = '{}-{}'.format(coll_name, random.randint(0, 9999))
        self.coll_upd = CollectionResource(coll_name_upd, 'latest')

        cf_name = 'ProjTestFrame{}'.format(random.randint(0, 9999))
        self.coord = CoordinateFrameResource(
            cf_name, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6,
            1, 1, 1, 'nanometers')
        self.coord_upd = copy.copy(self.coord)
        self.coord_upd.name = 'MouseFrame{}'.format(random.randint(0, 9999))
        self.coord_upd.description = 'Mouse coordinate frame.'

        self.exp = ExperimentResource(
            'exp2309-2', self.coll.name, self.coord.name, 'my experiment',
            1, 'isotropic', time_step=2, time_step_unit='nanoseconds')
        self.exp_upd = ExperimentResource(
            'exp2309-2a', self.coll.name, self.coord.name,
            'my first experiment', 2, 'anisotropic')

        self.source_chan = ChannelResource(
            'sourceChan', self.coll.name, self.exp.name, 'image', 'test source channel',
            0, 'uint8', 0)
        self.related_chan = ChannelResource(
            'relatedChan', self.coll.name, self.exp.name, 'image', 'test related channel',
            0, 'uint8', 0)
        self.chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, 'annotation', 'test annotation channel',
            0, 'uint8', 0, sources=['sourceChan'], related=['relatedChan'])
        self.chan_upd = ChannelResource(
            'yourChan', self.coll.name, self.exp.name, 'annotation', 'your test annotation channel',
            0, 'uint8', 1, sources=['sourceChan'], related=['relatedChan'])

    def tearDown(self):
        try:
            self.rmt.delete_project(self.chan_upd)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.chan)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.related_chan)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.source_chan)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.exp_upd)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.exp)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.coord_upd)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.coord)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.coll_upd)
        except HTTPError:
            pass
        try:
            self.rmt.delete_project(self.coll)
        except HTTPError:
            pass

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

    def test_create_collection(self):
        c = self.rmt.create_project(self.coll)
        self.assertEqual(self.coll.name, c.name)
        self.assertEqual(self.coll.description, c.description)

    def test_create_experiment(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)
        self.assertEqual(self.exp.name, e.name)
        self.assertEqual(self.exp.description, e.description)
        self.assertEqual(self.coll.name, e.coll_name)
        self.assertEqual(self.exp.coord_frame, e.coord_frame)
        self.assertEqual(self.exp.hierarchy_method, e.hierarchy_method)
        self.assertEqual(self.exp.num_hierarchy_levels, e.num_hierarchy_levels)
        self.assertEqual(self.exp.num_time_samples, e.num_time_samples)
        self.assertEqual(self.exp.time_step, e.time_step)
        self.assertEqual(self.exp.time_step_unit, e.time_step_unit)

    def test_create_channel(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        ch = self.rmt.create_project(self.source_chan)
        self.assertEqual(self.source_chan.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.source_chan.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.source_chan.datatype, ch.datatype)
        self.assertEqual(self.source_chan.default_time_sample, ch.default_time_sample)
        self.assertEqual(self.source_chan.base_resolution, ch.base_resolution)

    def test_create_annotation_channel_without_source_fails(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        rel_ch = self.rmt.create_project(self.related_chan)

        chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, 'annotation', 'test annotation channel',
            0, 'uint8', 0, related=['relatedChan'])

        with self.assertRaises(HTTPError):
            self.rmt.create_project(chan)

    def test_create_annotation_channel(self):
        """Annotation channels require a source channel."""
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        ch = self.rmt.create_project(self.source_chan)

        rel_ch = self.rmt.create_project(self.related_chan)

        ann_ch = self.rmt.create_project(self.chan)

        self.assertEqual(self.chan.name, ann_ch.name)
        self.assertEqual(self.exp.name, ann_ch.exp_name)
        self.assertEqual(self.chan.description, ann_ch.description)
        self.assertEqual(self.coll.name, ann_ch.coll_name)
        self.assertEqual(self.chan.datatype, ann_ch.datatype)
        self.assertEqual(self.chan.default_time_sample, ann_ch.default_time_sample)
        self.assertEqual(self.chan.base_resolution, ann_ch.base_resolution)
        self.assertEqual(self.chan.sources, ann_ch.sources)
        self.assertEqual(self.chan.related, ann_ch.related)

    def test_get_collection(self):
        coll = self.rmt.create_project(self.coll)

        c = self.rmt.get_project(self.coll)
        self.assertEqual(self.coll.name, c.name)
        self.assertEqual(self.coll.description, c.description)

    def test_get_coord_frame(self):
        coord = self.rmt.create_project(self.coord)

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

    def test_get_experiment(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        exp = self.rmt.create_project(self.exp)

        e = self.rmt.get_project(self.exp)
        self.assertEqual(self.exp.name, e.name)
        self.assertEqual(self.exp.description, e.description)
        self.assertEqual(self.coll.name, e.coll_name)
        self.assertEqual(self.exp.coord_frame, e.coord_frame)
        self.assertEqual(self.exp.hierarchy_method, e.hierarchy_method)
        self.assertEqual(self.exp.num_hierarchy_levels, e.num_hierarchy_levels)
        self.assertEqual(self.exp.num_time_samples, e.num_time_samples)
        self.assertEqual(self.exp.time_step, e.time_step)
        self.assertEqual(self.exp.time_step_unit, e.time_step_unit)

    def test_get_channel(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        chan = self.rmt.create_project(self.source_chan)

        ch = self.rmt.get_project(self.source_chan)
        self.assertEqual(self.source_chan.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.source_chan.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.source_chan.datatype, ch.datatype)
        self.assertEqual(self.source_chan.default_time_sample, ch.default_time_sample)
        self.assertEqual(self.source_chan.base_resolution, ch.base_resolution)

    def test_get_channel_helper(self):
        """
        Test the helper get_channel() as opposed to getting a channel via get_project().
        """

        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        chan = self.rmt.create_project(self.source_chan)

        actual = self.rmt.get_channel(chan.name, chan.coll_name, chan.exp_name)

        # This is not an exhaustive list of attributes, but they are the
        # important ones for correct interaction with the volume service.
        self.assertTrue(actual.cutout_ready)
        self.assertEqual(chan.datatype, actual.datatype)
        self.assertEqual(chan.default_time_sample, actual.default_time_sample)
        self.assertEqual(chan.base_resolution, actual.base_resolution)
        self.assertEqual(chan.downsample_status, actual.downsample_status)
        self.assertEqual(chan.type, actual.type)
        self.assertEqual(chan.name, actual.name)
        self.assertEqual(chan.coll_name, actual.coll_name)
        self.assertEqual(chan.exp_name, actual.exp_name)

    def test_update_collection(self):
        coll = self.rmt.create_project(self.coll)

        c = self.rmt.update_project(self.coll.name, self.coll_upd)
        self.assertEqual(self.coll_upd.name, c.name)
        self.assertEqual(self.coll_upd.description, c.description)

    def test_update_coord_frame(self):
        c = self.rmt.create_project(self.coll)

        coord = self.rmt.create_project(self.coord)

        cf = self.rmt.update_project(self.coord.name, self.coord_upd)
        self.assertEqual(self.coord_upd.name, cf.name)
        self.assertEqual(self.coord_upd.description, cf.description)

    def test_update_experiment(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        eup = self.rmt.update_project(self.exp.name, self.exp_upd)
        self.assertEqual(self.exp_upd.name, eup.name)
        self.assertEqual(self.exp_upd.description, eup.description)
        self.assertEqual(self.coll.name, eup.coll_name)
        self.assertEqual(self.exp_upd.coord_frame, eup.coord_frame)
        self.assertEqual(self.exp_upd.hierarchy_method, eup.hierarchy_method)
        self.assertEqual(self.exp_upd.num_hierarchy_levels, eup.num_hierarchy_levels)
        self.assertEqual(self.exp_upd.num_time_samples, eup.num_time_samples)
        self.assertEqual(self.exp.time_step, eup.time_step)
        self.assertEqual(self.exp.time_step_unit, eup.time_step_unit)

    def test_update_channel(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        source_ch = self.rmt.create_project(self.source_chan)

        rel_ch = self.rmt.create_project(self.related_chan)

        chan = self.rmt.create_project(self.chan)

        ch = self.rmt.update_project(self.chan.name, self.chan_upd)
        self.assertEqual(self.chan_upd.name, ch.name)
        self.assertEqual(self.exp.name, ch.exp_name)
        self.assertEqual(self.chan_upd.description, ch.description)
        self.assertEqual(self.coll.name, ch.coll_name)
        self.assertEqual(self.chan_upd.datatype, ch.datatype)
        self.assertEqual(self.chan_upd.default_time_sample, ch.default_time_sample)
        self.assertEqual(self.chan_upd.base_resolution, ch.base_resolution)
        self.assertEqual(self.chan_upd.sources, ch.sources)
        self.assertEqual(self.chan_upd.related, ch.related)

    def test_list_collections(self):
        coll = self.rmt.create_project(self.coll)

        coll_list = self.rmt.list_collections()
        c = [name for name in coll_list if name == self.coll.name]
        self.assertEqual(1, len(c))
        self.assertEqual(self.coll.name, c[0])

    def test_list_coord_frames(self):
        cf = self.rmt.create_project(self.coord)

        cf_list = self.rmt.list_coordinate_frames()
        c = [name for name in cf_list if name == self.coord.name]
        self.assertEqual(1, len(c))
        self.assertEqual(self.coord.name, c[0])

    def test_list_experiments(self):
        c = self.rmt.create_project(self.coll)

        cf = self.rmt.create_project(self.coord)

        exp = self.rmt.create_project(self.exp)

        exp_list = self.rmt.list_experiments(self.coll.name)
        e = [name for name in exp_list if name == self.exp.name]
        self.assertEqual(1, len(e))
        self.assertEqual(self.exp.name, e[0])

    #def test_list_channels(self):
    #    c = self.rmt.create_project(self.coll)

    #    cf = self.rmt.create_project(self.coord)

    #    e = self.rmt.create_project(self.exp)

    #    chan = self.rmt.create_project(self.chan)

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

        cf = self.rmt.create_project(self.coord)

        e = self.rmt.create_project(self.exp)

        ch = self.rmt.create_project(self.source_chan)

        self.rmt.delete_project(self.source_chan)
        self.rmt.delete_project(self.exp)
        self.rmt.delete_project(self.coord)
        self.rmt.delete_project(self.coll)

if __name__ == '__main__':
    unittest.main()
