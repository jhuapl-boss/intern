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
from requests import Session

import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v0.7'

class ProjectPermissionTest_v0_5(unittest.TestCase):
    """Integration tests of the Boss permission API.

    Note that that there will be many "Delete failed" messages because DELETE
    requests are made on all potentially created groups/users during test teardown. 
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
        self.coord = CoordinateFrameResource(
            'BestFrame', API_VER, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6, 
            1, 1, 1, 'nanometers', 0, 'nanoseconds')

        # Coordinate frame of experiments needs to be set to a valid ID before
        # creating.
        self.exp = ExperimentResource(
            'exp2309-2', self.coll.name, API_VER, 'my experiment', 0, 1, 
            'iso', 0)

        self.chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, API_VER, 'test channel', 
            0, 'uint8', 0)

        # Layer's channel list needs to be given a valid channel ID before 
        # creating.
        self.lyr = LayerResource(
            'topLayer', self.coll.name, self.exp.name, API_VER, 'test layer',
            0, 'uint64', 0)

        self.grp_name = 'int_test_exists'

    def cleanup_db(self):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().
        """
        try:
            self.rmt.group_delete(self.grp_name)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.lyr)
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
        self.initialize()
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

        self.rmt.group_create(self.grp_name)

    def tearDown(self):
        self.cleanup_db()

    def test_add_permissions_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'read', 'add_volumetric_data'])

    def test_add_permissions_invalid_collection_perm(self):
        with self.assertRaises(HTTPError):
            self.rmt.permissions_add(
            self.grp_name, self.coll, ['update', 'read', 'add_volumetric_data'])

    def test_add_permissions_invalid_experiment_perm(self):
        with self.assertRaises(HTTPError):
            self.rmt.permissions_add(
            self.grp_name, self.exp, ['update', 'read_volumetric_data', 'read'])

    def test_add_volumetric_permission_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.lyr, ['read', 'read_volumetric_data'])

    def test_add_permissions_append_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'add_volumetric_data'])

        self.rmt.permissions_add( self.grp_name, self.chan, ['read'])

        expected = ['update', 'add_volumetric_data', 'read']
        actual = self.rmt.permissions_get(self.grp_name, self.chan)
        self.assertCountEqual(expected, actual)

    def test_permissions_get_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'read'])

        expected = ['update', 'read']
        actual = self.rmt.permissions_get(self.grp_name, self.chan)
        self.assertCountEqual(expected, actual)

    def test_permissions_delete_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'add_volumetric_data'])

        self.rmt.permissions_delete(
            self.grp_name, self.chan, ['add_volumetric_data'])

        expected = ['update']
        actual = self.rmt.permissions_get(self.grp_name, self.chan)
        self.assertCountEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

