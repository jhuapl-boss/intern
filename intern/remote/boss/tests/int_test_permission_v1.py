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
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *

import random
import requests
from requests import HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v1'


class ProjectPermissionTest_v1(unittest.TestCase):
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
        cls.rmt = BossRemote('test.cfg', API_VER)

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        cls.rmt.project_service.session_send_opts = {'verify': False}
        cls.rmt.metadata_service.session_send_opts = {'verify': False}
        cls.rmt.volume_service.session_send_opts = {'verify': False}
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        coll_name = 'collection_perm_test-{}'.format(random.randint(0, 9999))
        cls.coll = CollectionResource(coll_name, 'bar')

        cf_name = 'PermissionTestFrame{}'.format(random.randint(0, 9999))
        cls.coord = CoordinateFrameResource(
            cf_name, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6,
            1, 1, 1, 'nanometers', 0, 'nanoseconds')

        cls.exp = ExperimentResource(
            'perm_test_exp', cls.coll.name, cls.coord.name, 'my experiment', 1,
            'isotropic', 1)

        cls.chan = ChannelResource(
            'perm_test_ch', cls.coll.name, cls.exp.name, 'image', 'test channel',
            0, 'uint8', 0)

        cls.grp_name = 'int_perm_test_group{}'.format(random.randint(0, 9999))

        cls.rmt.create_project(cls.coll)
        cls.rmt.create_project(cls.coord)
        cls.rmt.create_project(cls.exp)
        cls.rmt.create_project(cls.chan)
        cls.rmt.create_group(cls.grp_name)

    @classmethod
    def tearDownClass(cls):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().
        """
        try:
            cls.rmt.delete_group(cls.grp_name)
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

    def tearDown(self):
        """Delete the permission set if is there (from a previous error)"""
        try:
            self.rmt.delete_permissions(self.grp_name, self.chan)
        except HTTPError:
            pass
        try:
            self.rmt.delete_permissions(self.grp_name, self.coll)
        except HTTPError:
            pass

    def test_list_permissions(self):

        query_result = self.rmt.list_permissions()

        self.assertEqual(len(query_result) >= 3, True)

        # Make sure the stuff you just created is in there
        found_channel = False
        fount_count = 0
        for perm_set in query_result:
            if perm_set["collection"] == self.coll.name:
                fount_count += 1
                if "experiment" in perm_set:
                    if "channel" in perm_set:
                        if perm_set["experiment"] == self.exp.name and perm_set["channel"] == self.chan.name:
                            found_channel = True
                            self.assertEqual(set(perm_set["permissions"]),
                                             set(['read', 'update', 'delete', 'add', 'remove_group', 'assign_group']))

        self.assertTrue(found_channel)
        self.assertEqual(fount_count, 3)

    def test_list_permissions_filter_resource(self):

        # Filter on the collection
        query_result = self.rmt.list_permissions(resource=self.coll)

        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0]["collection"], self.coll.name)
        self.assertTrue("experiment" not in query_result[0])
        self.assertEqual(set(query_result[0]["permissions"]),
                         set(['read', 'update', 'delete', 'add', 'remove_group', 'assign_group']))

        # Filter on the experiment
        query_result = self.rmt.list_permissions(resource=self.exp)

        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0]["experiment"], self.exp.name)
        self.assertTrue("channel" not in query_result[0])
        self.assertEqual(set(query_result[0]["permissions"]),
                         set(['read', 'update', 'delete', 'add', 'remove_group', 'assign_group']))

        # Filter on the channel
        query_result = self.rmt.list_permissions(resource=self.chan)
        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0]["channel"], self.chan.name)
        self.assertEqual(set(query_result[0]["permissions"]),
                         set(['add', 'assign_group', 'read', 'update', 'add_volumetric_data',
                             'read_volumetric_data', 'remove_group', 'delete_volumetric_data', 'delete']))

    def test_add_get_delete_permissions(self):

        result = self.rmt.get_permissions(self.grp_name, self.chan)

        self.assertEqual(len(result), 0)

        self.rmt.add_permissions(self.grp_name, self.chan, ['update', 'read', 'add_volumetric_data'])

        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), set(['update', 'read', 'add_volumetric_data']))

        self.rmt.delete_permissions(self.grp_name, self.chan)
        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 0)

    def test_list_permissions_filter_group(self):

        self.rmt.add_permissions(self.grp_name, self.chan, ['read'])

        # Filter on the collection
        query_result = self.rmt.list_permissions(group_name=self.grp_name)

        self.assertEqual(len(query_result), 1)
        self.assertEqual(query_result[0]["channel"], self.chan.name)
        self.assertEqual(query_result[0]["group"], self.grp_name)
        self.assertEqual(set(query_result[0]["permissions"]), set(['read']))

        self.rmt.delete_permissions(self.grp_name, self.chan)
        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 0)

    def test_add_permissions_invalid_collection_perm(self):
        with self.assertRaises(HTTPError):
            self.rmt.add_permissions(self.grp_name, self.coll, ['update', 'read', 'add_volumetric_data'])

    def test_add_permissions_invalid_experiment_perm(self):
        with self.assertRaises(HTTPError):
            self.rmt.add_permissions(self.grp_name, self.exp, ['update', 'read_volumetric_data', 'read'])

    def test_update_permissions(self):
        # Check you have no permissions
        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 0)

        self.rmt.add_permissions(self.grp_name, self.chan, ['update', 'add', 'add_volumetric_data'])

        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), set(['update', 'add', 'add_volumetric_data']))

        # Update
        self.rmt.update_permissions(self.grp_name, self.chan, ['read'])

        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 1)
        self.assertEqual(set(result), set(['read']))

        # Cleanup
        self.rmt.delete_permissions(self.grp_name, self.chan)
        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 0)

    def test_get_group_with_permissions(self):
        # Check you have no permissions
        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 0)

        self.rmt.add_permissions(self.grp_name, self.chan, ['update', 'add', 'add_volumetric_data'])
        self.rmt.add_permissions(self.grp_name, self.coll, ['update', 'add'])

        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 3)
        self.assertEqual(set(result), set(['update', 'add', 'add_volumetric_data']))

        # Check that the group sees the resource now
        group = self.rmt.get_group(self.grp_name)
        self.assertEqual(len(group["resources"][0].keys()), 1)
        self.assertEqual(len(group["resources"][1].keys()), 3)

        # Cleanup
        self.rmt.delete_permissions(self.grp_name, self.chan)
        self.rmt.delete_permissions(self.grp_name, self.coll)
        result = self.rmt.get_permissions(self.grp_name, self.chan)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
