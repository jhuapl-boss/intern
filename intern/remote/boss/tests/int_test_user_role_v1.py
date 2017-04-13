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
import random

import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v1'

class ProjectUserRoleTest_v1(unittest.TestCase):
    """Integration tests of the Boss user-role API.
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

        cls.admin = 'admin'
        cls.user_mgr = 'user-manager'
        cls.rsrc_mgr = 'resource-manager'
        cls.user = 'role_test_user{}'.format(random.randint(0, 9999))

        cls.rmt.add_user(cls.user, 'John', 'Doe', 'jd{}@me.com'.format(random.randint(0, 9999)), 'password')
        cls.cleanup_db()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_db()
        # Currently can't delete users unless admin
        #cls.rmt.delete_user(cls.user)

    @classmethod
    def cleanup_db(cls):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().  Don't do
        anything if an exception occurs during delete_user_role().  The role
        may not have existed for a particular test.
        """
        try:
            cls.rmt.delete_user_role(cls.user, cls.user_mgr)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_user_role(cls.user, cls.rsrc_mgr)
        except HTTPError:
            pass

    def setUp(self):
        pass

    def tearDown(self):
        self.cleanup_db()

    def test_add_role(self):
        self.rmt.add_user_role(self.user, self.rsrc_mgr)

        expected = [self.rsrc_mgr]
        actual = self.rmt.get_user_roles(self.user)

        six.assertCountEqual(self, expected, actual)

    def test_fail_add_user_manager(self):
        # only admin can add a user manager
        with self.assertRaises(HTTPError):
            self.rmt.add_user_role(self.user, self.user_mgr)

    def test_add_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.add_user_role('foo', self.admin)

    def test_add_invalid_role(self):
        with self.assertRaises(HTTPError):
            self.rmt.add_user_role(self.user, 'foo')

    def test_add_invalid_admin_role(self):
        # only the root account has the admin role
        with self.assertRaises(HTTPError):
            self.rmt.add_user_role(self.user, self.admin)

    def test_delete_role(self):
        self.rmt.add_user_role(self.user, self.rsrc_mgr)
        self.rmt.delete_user_role(self.user, self.rsrc_mgr)

        actual = self.rmt.get_user_roles(self.user)
        self.assertEqual([], actual)

    def test_delete_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.delete_user_role('foo', self.admin)

    def test_delete_invalid_role(self):
        with self.assertRaises(HTTPError):
            self.rmt.delete_user_role(self.user, 'foo')

    def test_get_roles(self):
        actual = self.rmt.get_user_roles(self.user)
        self.assertEqual([], actual)

    def test_get_roles_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.get_user_roles('foo')


if __name__ == '__main__':
    unittest.main()
