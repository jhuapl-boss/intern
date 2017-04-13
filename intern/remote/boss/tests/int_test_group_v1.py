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
from requests import Session, HTTPError, Request
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest
import warnings

API_VER = 'v1'


class ProjectGroupTest_v1(unittest.TestCase):
    """Integration tests of the Boss group API.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        warnings.filterwarnings('ignore')
        cls.rmt = BossRemote('test.cfg', API_VER)

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        cls.rmt.project_service.session_send_opts = {'verify': False}
        cls.rmt.metadata_service.session_send_opts = {'verify': False}
        cls.rmt.volume_service.session_send_opts = {'verify': False}
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        cls.create_grp_name = 'int_test_group{}'.format(random.randint(0, 9999))
        cls.existing_grp_name = 'int_test_group_exists{}'.format(random.randint(0, 9999))

        cls.rmt.create_group(cls.existing_grp_name)

        cls.user_name = 'bossadmin'

        # Create a new user because the user tests run under, will
        # automatically be a member and maintainer of any groups created
        # during testing.
        cls.created_user = 'group_test_johndoeski{}'.format(random.randint(0, 9999))

        password = 'myPassW0rd'
        cls.rmt.add_user(cls.created_user, 'John', 'Doeski', 'jdoe{}@rime.com'.format(random.randint(0, 9999)),
                         password)
        token = cls.get_access_token(cls.created_user, password)
        cls.login_user(token)

    @classmethod
    def tearDownClass(cls):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().  Don't do
        anything if an exception occurs during delete_group().  The group
        may not have existed for a particular test.
        """
        try:
            cls.rmt.delete_group(cls.create_grp_name)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_group(cls.existing_grp_name)
        except HTTPError:
            pass
        try:
            cls.rmt.delete_user(cls.created_user)
        except HTTPError:
            pass

    def tearDown(self):
        try:
            self.rmt.delete_group(self.create_grp_name)
        except HTTPError:
            pass

    @classmethod
    def login_user(self, token):
        """User must login once before user can be added to a group.

        Args:
            token (string): Bearer token used to for authentication.
        """
        if "Project Service" in self.rmt._config.sections():
            host = self.rmt._config.get("Project Service", "host")
            protocol = self.rmt._config.get("Project Service", "protocol")
        else:
            host = self.rmt._config.get("Default", "host")
            protocol = self.rmt._config.get("Default", "protocol")

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + token
        }

        # Hit one of the API endpoints to effectively, login.
        url = protocol + '://' + host + '/' + API_VER + '/collection/'
        session = Session()
        request = Request('GET', url, headers=headers)
        prep = session.prepare_request(request)
        response = session.send(prep, verify=False)

    @classmethod
    def get_access_token(cls, user_name, password):
        """Get the bearer token for the test user for login.

        Will assert or raise on a failure.

        Returns:
            (string): Bearer token.
        """
        if "Project Service" in cls.rmt._config.sections():
            (api_host, domain) = cls.rmt._config.get("Project Service", "host").split('.', 1)
            protocol = cls.rmt._config.get("Project Service", "protocol")
        else:
            (api_host, domain) = cls.rmt._config.get("Default", "host").split('.', 1)
            protocol = cls.rmt._config.get("Default", "protocol")

        host = api_host.replace('api', 'auth', 1) + '.' + domain
        url = protocol + '://' + host + '/auth/realms/BOSS/protocol/openid-connect/token'
        data = {
            'grant_type': 'password',
            'client_id': 'endpoint',
            'username': user_name,
            'password': password
            }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        session = Session()
        request = Request('POST', url, data=data, headers=headers)
        prep = session.prepare_request(request)
        response = session.send(prep, verify=False)
        jresp = response.json()
        assert 'access_token' in jresp
        return jresp['access_token']

    def test_list_groups(self):
        actual = self.rmt.list_groups()
        self.assertIn(self.existing_grp_name, actual)

    def test_create_group(self):
        self.rmt.create_group(self.create_grp_name)

    def test_get_group(self):
        actual = self.rmt.get_group(self.existing_grp_name)

        # Don't assume who the owner (user tests are running under) is;
        # only check for presence of owner in dictionary.
        self.assertIn('owner', actual)
        self.assertEqual(self.existing_grp_name, actual['name'])
        self.assertEqual([], actual['resources'])

    def test_get_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.get_group('foo')

    def test_delete_group(self):
        self.rmt.create_group(self.create_grp_name)

        self.rmt.delete_group(self.create_grp_name)
        with self.assertRaises(HTTPError):
            self.rmt.get_group(self.create_grp_name)

    def test_delete_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.delete_group('foo')

    def test_add_group_member(self):
        self.rmt.create_group(self.create_grp_name)
        self.rmt.add_group_member(self.create_grp_name, self.created_user)
        self.assertTrue(self.rmt.get_is_group_member(
            self.create_grp_name, self.created_user))

    def test_add_group_member_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.add_group_member('foo', self.created_user)

    def test_list_group_members(self):
        self.rmt.create_group(self.create_grp_name)
        self.rmt.add_group_member(self.create_grp_name, self.created_user)
        actual = self.rmt.list_group_members(self.create_grp_name)
        self.assertIn(self.created_user, actual)

    def test_list_group_members_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.list_group_members('foo')

    def test_group_membership(self):
        self.rmt.create_group(self.create_grp_name)

        # Test not in the group
        self.assertFalse(self.rmt.get_is_group_member(
            self.create_grp_name, self.created_user))

        # Add to group
        self.rmt.add_group_member(self.create_grp_name, self.created_user)
        self.assertTrue(self.rmt.get_is_group_member(
            self.create_grp_name, self.created_user))

    def test_get_group_membership_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.get_is_group_member(self.existing_grp_name, 'foo')

    def test_delete_group_member(self):
        self.rmt.create_group(self.create_grp_name)
        self.rmt.add_group_member(self.create_grp_name, self.created_user)
        self.assertTrue(self.rmt.get_is_group_member(
            self.create_grp_name, self.created_user))

        self.rmt.delete_group_member(self.create_grp_name, self.created_user)

        self.assertFalse(self.rmt.get_is_group_member(
            self.create_grp_name, self.created_user))

    def test_delete_group_member_user_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.delete_group_member(self.existing_grp_name, 'foo')

    def test_add_group_maintainer(self):
        self.rmt.create_group(self.create_grp_name)
        self.rmt.add_group_maintainer(self.create_grp_name, self.created_user)
        self.assertTrue(self.rmt.get_is_group_maintainer(
            self.create_grp_name, self.created_user))

    def test_add_group_maintainer_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.add_group_maintainer('foo', self.created_user)

    def test_list_group_maintainers(self):
        self.rmt.create_group(self.create_grp_name)
        self.rmt.add_group_maintainer(self.create_grp_name, self.created_user)
        actual = self.rmt.list_group_maintainers(self.create_grp_name)
        self.assertIn(self.created_user, actual)

    def test_list_group_maintainers_group_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.list_group_maintainers('foo')

    def test_delete_group_maintainer(self):
        self.rmt.create_group(self.create_grp_name)
        self.rmt.add_group_maintainer(self.create_grp_name, self.created_user)
        self.assertTrue(self.rmt.get_is_group_maintainer(
            self.create_grp_name, self.created_user))

        self.rmt.delete_group_maintainer(self.create_grp_name, self.created_user)

        self.assertFalse(self.rmt.get_is_group_maintainer(
            self.create_grp_name, self.created_user))

    def test_delete_group_maintainer_user_doesnt_exist(self):
        with self.assertRaises(HTTPError):
            self.rmt.delete_group_maintainer(self.existing_grp_name, 'foo')

if __name__ == '__main__':
    unittest.main()
