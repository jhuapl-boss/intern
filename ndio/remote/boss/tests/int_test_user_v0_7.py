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

import configparser
import json
import requests
from requests import Session, HTTPError, Request
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import unittest
import warnings
import time

API_VER = 'v0.7'

class ProjectUserTest_v0_7(unittest.TestCase):
    """Integration tests of the Boss user API.
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
        cls.rmt.group_create(cls.group)

    @classmethod
    def tearDownClass(cls):
        cls.initialize(cls)
        cls.rmt.group_delete(cls.group)

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

        self.user = 'johndoe'
        self.first_name = 'john'
        self.last_name = 'doe'
        self.email = 'jd@me.com'
        self.password = 'password'

        self.group = 'int_user_test_group'

    def cleanup_db(self):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDown() and setUpClass().  Don't do
        anything if an exception occurs during user_delete().  The user
        may not have existed for a particular test.
        """
        try:
            self.rmt.user_delete(self.user)
        except HTTPError:
            pass

    def setUp(self):
        self.initialize()
        self.rmt.group_perm_api_version = API_VER

    def tearDown(self):
        self.cleanup_db()

    def test_add(self):
        self.rmt.user_add(
            self.user, self.first_name, self.last_name, self.email, 
            self.password)

    def test_delete(self):
        self.rmt.user_add(
            self.user, self.first_name, self.last_name, self.email, 
            self.password)
        self.rmt.user_delete(self.user)

    def test_delete_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_delete('foo')

    def test_get(self):
        self.rmt.user_add(
            self.user, self.first_name, self.last_name, self.email, 
            self.password)

        expected = {
            'username': self.user,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email }

        actual = self.rmt.user_get(self.user)

        # get also returns generated values that we cannot test for such 
        # as creation time.
        self.assertTrue(expected.items() <= actual.items())

    def test_get_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_get('foo')

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

    def get_access_token(self):
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
            'username': self.user,
            'password': self.password
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

    def test_get_groups(self):
        self.rmt.user_add(
            self.user, self.first_name, self.last_name, self.email, 
            self.password)
        token = self.get_access_token()
        self.login_user(token)

        self.rmt.group_add_user(self.group, self.user)

        expected = ['boss-public', self.group]
        actual = self.rmt.user_get_groups(self.user)
        self.assertCountEqual(expected, actual)

    def test_get_groups_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.user_get_groups('foo')


if __name__ == '__main__':
    unittest.main()
