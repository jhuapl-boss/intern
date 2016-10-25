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

import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v0.7'

class ProjectUserRoleTest_v0_7(unittest.TestCase):
    """Integration tests of the Boss user-role API.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        cls.initialize()
        cls.cleanup_db()
        cls.rmt.user_add(cls.user, 'John', 'Doe', 'jd@me.com', 'password')

    @classmethod
    def tearDownClass(cls):
        cls.initialize()
        cls.rmt.user_delete(cls.user)

    @classmethod
    def initialize(cls):
        """Initialization for each test.

        Called by both setUp() and setUpClass().
        """
        cls.rmt = BossRemote('test.cfg')
        cls.rmt.group_perm_api_version = API_VER

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        cls.rmt.project_service.session_send_opts = { 'verify': False }
        cls.rmt.metadata_service.session_send_opts = { 'verify': False }
        cls.rmt.volume_service.session_send_opts = { 'verify': False }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        cls.admin = 'admin'
        cls.user_mgr = 'user-manager'
        cls.rsrc_mgr = 'resource-manager'
        cls.user = 'role_test_user'

    @classmethod
    def cleanup_db(cls):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().  Don't do
        anything if an exception occurs during user_delete_role().  The role
        may not have existed for a particular test.
        """
        try:
            cls.rmt.user_delete_role(cls.user, cls.admin)
        except HTTPError:
            pass
        try:
            cls.rmt.user_delete_role(cls.user, cls.user_mgr)
        except HTTPError:
            pass
        try:
            cls.rmt.user_delete_role(cls.user, cls.rsrc_mgr)
        except HTTPError:
            pass

    def setUp(self):
        self.initialize()
        self.rmt.group_perm_api_version = API_VER

    def tearDown(self):
        self.cleanup_db()

    def test_add_role(self):
        self.rmt.user_add_role(self.user, self.admin)

    def test_add_multiple_roles(self):
        self.rmt.user_add_role(self.user, self.admin)
        self.rmt.user_add_role(self.user, self.user_mgr)
        self.rmt.user_add_role(self.user, self.rsrc_mgr)

        expected = [self.admin, self.user_mgr, self.rsrc_mgr]
        actual = self.rmt.user_get_roles(self.user)

        six.assertCountEqual(self, expected, actual)

    def test_add_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_add_role('foo', self.admin)

    def test_add_invalid_role(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_add_role(self.user, 'foo')

    def test_delete_role(self):
        self.rmt.user_add_role(self.user, self.admin)
        self.rmt.user_delete_role(self.user, self.admin)

        actual = self.rmt.user_get_roles(self.user)
        self.assertEqual([], actual)

    def test_delete_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_delete_role('foo', self.admin)

    def test_delete_invalid_role(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_delete_role(self.user, 'foo')

    def test_get_roles(self):
        actual = self.rmt.user_get_roles(self.user)
        self.assertEqual([], actual)

    def test_get_roles_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_get_roles('foo')


if __name__ == '__main__':
    unittest.main()
