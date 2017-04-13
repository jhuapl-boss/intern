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

from intern.service.boss.v1.project import ProjectService_1
from intern.resource.boss.resource import *
from requests import PreparedRequest, Response, Session, HTTPError
import unittest
from mock import patch


class TestGroup(unittest.TestCase):
    def setUp(self):
        self.prj = ProjectService_1()

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_list_groups_success(self, mock_session, mock_resp):
        expected =  ['g1', 'g2'] 
        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'groups': expected }
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.list_groups(
            None, url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Session', autospec=True)
    def test_list_groups_failure(self, mock_session):
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.list_groups(None, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_create_group_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 201
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.create_group(
            'mygroup', url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_create_group_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.create_group(
            'mygroup', url_prefix, auth, mock_session, send_opts)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_get_group_success(self, mock_session, mock_resp):
        grp_name = 'mygroup'
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 200
        mock_resp.json.return_value = True
        mock_session.send.return_value = mock_resp

        user = None
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.get_group(
            grp_name, user, url_prefix, auth, mock_session, send_opts)

        self.assertTrue(actual)

    @patch('requests.Session', autospec=True)
    def test_get_group_failure(self, mock_session):
        grp_name = 'mygroup'
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 404
        mock_session.send.return_value = fake_resp

        user = None
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.get_group(
                grp_name, user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_group_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204
        mock_session.send.return_value = fake_resp

        user = None
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.delete_group(
            'mygroup', url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_group_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        user = None
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.delete_group(
            'mygroup', url_prefix, auth, mock_session, send_opts)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_list_group_members_success(self, mock_session, mock_resp):
        expected =  ['john', 'mary'] 
        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'members': expected }
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = mock_resp

        group = 'fire'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.list_group_members(
            group, url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Session', autospec=True)
    def test_list_group_members_failure(self, mock_session):
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = fake_resp

        group = 'fire'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.list_group_members(
                group, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_add_group_member_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.add_group_member(
            'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_add_group_member_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.add_group_member(
                'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_get_is_group_member_success(self, mock_session, mock_resp):
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'result': True }
        mock_session.send.return_value = mock_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.assertTrue(self.prj.get_is_group_member(
            'mygroup', user, url_prefix, auth, mock_session, send_opts))

    @patch('requests.Session', autospec=True)
    def test_get_is_group_member_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 404
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.get_group(
                'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_group_member_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.delete_group_member(
            'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_group_member_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.delete_group_member(
                'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_list_group_maintainers_success(self, mock_session, mock_resp):
        expected =  ['john', 'mary'] 
        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'maintainers': expected }
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = mock_resp

        group = 'fire'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.list_group_maintainers(
            group, url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Session', autospec=True)
    def test_list_group_maintainers_failure(self, mock_session):
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.send.return_value = fake_resp

        group = 'fire'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.list_group_maintainers(
                group, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_add_group_maintainer_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.add_group_maintainer(
            'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_add_group_maintainer_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.add_group_maintainer(
                'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_get_is_group_maintainer_success(self, mock_session, mock_resp):
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'result': True }
        mock_session.send.return_value = mock_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.assertTrue(self.prj.get_is_group_maintainer(
            'mygroup', user, url_prefix, auth, mock_session, send_opts))

    @patch('requests.Session', autospec=True)
    def test_get_is_group_maintainer_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 404
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.get_is_group_maintainer(
                'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_group_maintainer_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.prj.delete_group_maintainer(
            'mygroup', user, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_delete_group_member_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403
        mock_session.send.return_value = fake_resp

        user = 'you'
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.delete_group_maintainer(
                'mygroup', user, url_prefix, auth, mock_session, send_opts)


if __name__ == '__main__':
    unittest.main()
