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
from requests import Session, HTTPError, Request
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest
import warnings

API_VER = 'v0.7'

class ProjectGroupTest_v0_7(unittest.TestCase):
    """Integration tests of the Boss group API.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        warnings.filterwarnings('ignore')
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

        # This user will be created during at least one test.
        self.create_user = 'johndoe'

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
        try:
            self.rmt.user_delete(self.create_user)
        except HTTPError:
            pass

    def setUp(self):
        self.initialize()
        self.rmt.group_perm_api_version = API_VER
        self.rmt.group_create(self.existing_grp_name)

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

    def test_get_groups(self):
        password = 'myPassW0rd'
        self.rmt.user_add(
            self.create_user, 'Roger', 'Wilco', 'rwil@me.com', password)
        token = self.get_access_token(self.create_user, password)
        self.login_user(token)

        self.rmt.group_add_user(self.existing_grp_name, self.create_user)

        expected = ['boss-public', self.existing_grp_name]
        actual = self.rmt.user_get_groups(self.create_user)
        self.assertCountEqual(expected, actual)

    def test_get_groups_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_get_groups('foo')

    def login_user(self, token):
        """User must login once before user can be added to a group.

        Args:
            token (string): Bearer token used to for authentication.
        """
        parser = configparser.ConfigParser()
        parser.read('test.cfg')
        host = parser['Project Service']['host']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer ' + token
        }
        protocol = parser['Project Service']['protocol']

        # Hit one of the API endpoints to effectively, login.
        url = protocol + '://' + host + '/' + API_VER + '/collection/'
        session = Session()
        request = Request('GET', url, headers=headers)
        prep = session.prepare_request(request)
        response = session.send(prep, verify=False)

    def get_access_token(self, user_name, password):
        """Get the bearer token for the test user for login.

        Will assert or raise on a failure.

        Returns:
            (string): Bearer token.
        """
        parser = configparser.ConfigParser()
        parser.read('test.cfg')
        # Get the beginning of the VPC name that test is running in.
        (api_host, domain) = parser['Project Service']['host'].split('.', 1)
        host = api_host.replace('api', 'auth', 1) + '.' + domain
        protocol = parser['Project Service']['protocol']
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
        self.assertIn('access_token', jresp)
        return jresp['access_token']


if __name__ == '__main__':
    unittest.main()
