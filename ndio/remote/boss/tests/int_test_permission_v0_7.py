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
import six
from ndio.remote.boss import BossRemote
from ndio.resource.boss.resource import *

import random
import requests
from requests import HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v0.7'


class ProjectPermissionTest_v0_7(unittest.TestCase):
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

        cf_name = 'BestFrame{}'.format(random.randint(0, 9999))
        cls.coord = CoordinateFrameResource(
            cf_name, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6,
            1, 1, 1, 'nanometers', 0, 'nanoseconds')

        cls.exp = ExperimentResource(
            'exp2309-2', cls.coll.name, cls.coord.name, 'my experiment', 1,
            'iso', 0)

        cls.chan = ChannelResource(
            'myChan', cls.coll.name, cls.exp.name, 'image', 'test channel',
            0, 'uint8', 0)

        cls.grp_name = 'int_test_exists'

    @classmethod
    def cleanup_db(cls):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().
        """
        try:
            cls.rmt.group_delete(cls.grp_name)
        except HTTPError:
            pass
        try:
            cls.rmt.project_delete(cls.chan)
        except HTTPError:
            pass
        try:
            cls.rmt.project_delete(cls.exp)
        except HTTPError:
            pass
        try:
            cls.rmt.project_delete(cls.coord)
        except HTTPError:
            pass
        try:
            cls.rmt.project_delete(cls.coll)
        except HTTPError:
            pass

    def setUp(self):
        self.rmt.project_create(self.coll)
        self.rmt.project_create(self.coord)
        self.rmt.project_create(self.exp)
        self.rmt.project_create(self.chan)
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
            self.grp_name, self.chan, ['read', 'read_volumetric_data'])

    def test_add_permissions_append_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'add_volumetric_data'])

        self.rmt.permissions_add( self.grp_name, self.chan, ['read'])

        expected = ['update', 'add_volumetric_data', 'read']
        actual = self.rmt.permissions_get(self.grp_name, self.chan)
        six.assertCountEqual(self, expected, actual)

    def test_permissions_get_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'read'])

        expected = ['update', 'read']
        actual = self.rmt.permissions_get(self.grp_name, self.chan)
        six.assertCountEqual(self, expected, actual)

    def test_permissions_delete_success(self):
        self.rmt.permissions_add(
            self.grp_name, self.chan, ['update', 'add_volumetric_data'])

        self.rmt.permissions_delete(
            self.grp_name, self.chan, ['add_volumetric_data'])

        expected = ['update']
        actual = self.rmt.permissions_get(self.grp_name, self.chan)
        six.assertCountEqual(self, expected, actual)


if __name__ == '__main__':
    unittest.main()
