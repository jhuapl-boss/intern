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

import unittest

API_VER = 'v0.5'

class ProjectGroupTest_v0_5(unittest.TestCase):
    """Integration tests of the Boss group API.
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

        self.create_grp_name = 'int_test_group'
        self.existing_grp_name = 'int_test_exists'
        self.user_name = 'bossadmin'

    def cleanup_db(self):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().  Don't do
        anything if an exception occurs during group_delete().  The group
        may not have existed for a particular test.
        """
        try:
            self.rmt.group_delete(self.create_grp_name)
        except HTTPError:
            pass
        try:
            self.rmt.group_delete(self.existing_grp_name)
        except HTTPError:
            pass

    def setUp(self):
        self.initialize()
        self.rmt.group_create(self.existing_grp_name)
        self.rmt.group_perm_api_version = API_VER

    def tearDown(self):
        self.cleanup_db()

    def test_create_group(self):
        self.rmt.group_create(self.create_grp_name)

    def test_get_group(self):
        actual = self.rmt.group_get(self.existing_grp_name)
        self.assertTrue(actual)

    def test_get_group_doesnt_exist(self):
        actual = self.rmt.group_get('foo')
        self.assertFalse(actual)

    def test_delete_group(self):
        self.rmt.group_delete(self.existing_grp_name)

    def test_delete_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.group_delete('foo')

    def test_group_add_user(self):
        self.rmt.group_add_user(self.existing_grp_name, self.user_name)

    def test_group_add_user_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.group_add_user('foo', self.user_name)

    def test_group_get_user(self):
        self.rmt.group_add_user(self.existing_grp_name, self.user_name)
        self.assertTrue(self.rmt.group_get(self.existing_grp_name, self.user_name))

    def test_group_get_user_not_a_member(self):
        self.assertFalse(self.rmt.group_get(self.existing_grp_name, self.user_name))

    def test_group_get_user_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.group_get(self.existing_grp_name, 'foo')

    def test_group_delete_user(self):
        self.rmt.group_delete(self.existing_grp_name, self.user_name)

    def test_group_delete_user_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.group_delete(self.existing_grp_name, 'foo')


if __name__ == '__main__':
    unittest.main()
