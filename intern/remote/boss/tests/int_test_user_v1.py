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
import random

import requests
from requests import HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import unittest
import warnings

API_VER = 'v1'


class ProjectUserTest_v1(unittest.TestCase):
    """Integration tests of the Boss user API.
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

        cls.user = 'user_test_user{}'.format(random.randint(0, 9999))
        cls.first_name = 'john'
        cls.last_name = 'doe'
        cls.email = 'jd{}@me.com'.format(random.randint(0, 9999))
        cls.password = 'password'

    @classmethod
    def tearDownClass(cls):
        try:
            # TODO: Only admin can delete users now. Update test to enable cleaning up
            pass
            #cls.rmt.delete_user(cls.user)
        except HTTPError:
            pass

    def tearDown(self):
        try:
            # TODO: Only admin can delete users now. Update test to enable cleaning up
            pass
            # self.rmt.delete_user(self.user)
        except HTTPError:
            pass

    def test_add_user_already_exists(self):
        # Combine create, get, dup create in 1 test since you can't delete users as a non-admin
        self.rmt.add_user(
            self.user, self.first_name, self.last_name, self.email,
            self.password)

        expected = {
            'username': self.user,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email}

        actual = self.rmt.get_user(self.user)

        # get also returns generated values that we cannot test for such
        # as creation time.
        self.assertTrue(len(expected.items()) <= len(actual.items()))
        self.assertEqual(expected["email"], actual["email"])
        self.assertEqual(expected["username"], actual["username"])
        self.assertEqual(expected["firstName"], actual["firstName"])
        self.assertEqual(expected["lastName"], actual["lastName"])

        with self.assertRaises(HTTPError):
            self.rmt.add_user(
                self.user, self.first_name, self.last_name, self.email,
                self.password)

    def test_delete_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.delete_user('foo')

    # def test_get(self):
    #     self.rmt.add_user(
    #         self.user, self.first_name, self.last_name, self.email,
    #         self.password)
    #
    #     expected = {
    #         'username': self.user,
    #         'firstName': self.first_name,
    #         'lastName': self.last_name,
    #         'email': self.email }
    #
    #     actual = self.rmt.get_user(self.user)
    #
    #     # get also returns generated values that we cannot test for such
    #     # as creation time.
    #     self.assertTrue(len(expected.items()) <= len(actual.items()))
    #     self.assertEqual(expected["email"], actual["email"])
    #     self.assertEqual(expected["username"], actual["username"])
    #     self.assertEqual(expected["firstName"], actual["firstName"])
    #     self.assertEqual(expected["lastName"], actual["lastName"])

    def test_get_invalid_user(self):
        with self.assertRaises(HTTPError):
            self.rmt.get_user('foo')


if __name__ == '__main__':
    unittest.main()
