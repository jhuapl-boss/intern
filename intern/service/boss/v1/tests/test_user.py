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
from intern.service.boss.v1.project import ProjectService_1
from intern.resource.boss.resource import *
from requests import PreparedRequest, Response, Session, HTTPError
import unittest
from mock import patch


class TestUser(unittest.TestCase):
    def setUp(self):
        self.prj = ProjectService_1()

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_get_success(self, mock_session, mock_resp):
        expected = ['default']
        mock_resp.status_code = 200
        mock_resp.json.return_value = expected
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.get_user(
            'johndoe', url_prefix, auth, mock_session, send_opts)
        six.assertCountEqual(self, expected, actual)

    @patch('requests.Session', autospec=True)
    def test_get_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.get_user(
                'johndoe', url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_add_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 201
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        user = 'johndoe'
        first = 'john'
        last = 'doe'
        email = 'jd@me.com'
        pw = 'password'

        self.prj.add_user(
            user, first, last, email, pw,
            url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_add_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        user = 'johndoe'
        first = 'john'
        last = 'doe'
        email = 'jd@me.com'
        pw = 'password'

        with self.assertRaises(HTTPError):
            self.prj.add_user(
                user, first, last, email, pw,
                url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.delete_user(
            'johndoe', url_prefix, auth, mock_session, send_opts)



if __name__ == '__main__':
    unittest.main()
