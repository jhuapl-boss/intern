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

from intern.service.boss.v1.metadata import MetadataService_1
from intern.resource.boss.resource import ChannelResource
from intern.service.boss.httperrorlist import HTTPErrorList
from requests import HTTPError, PreparedRequest, Response, Session
import unittest
from mock import patch


class TestMetadata_v1(unittest.TestCase):
    def setUp(self):
        self.meta = MetadataService_1()
        self.chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_meta_list_success(self, mock_session, mock_resp):
        expected = ['foo', 'bar']
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'keys': expected }

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.meta.list(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_meta_list_failure(self, mock_session, mock_resp):
        expected = ['foo', 'bar']
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = HTTPError()

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.meta.list(self.chan, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_meta_create_success(self, mock_session):
        key_vals = {'foo': 'bar', 'day': 'night'}
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 201

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.meta.create(self.chan, key_vals, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_meta_create_failure(self, mock_session):
        key_vals = {'foo': 'bar', 'day': 'night'}
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPErrorList):
            self.meta.create(self.chan, key_vals, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_meta_get_success(self, mock_session, mock_resp):
        expected = {'foo': 'bar'}
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.json.return_value = { 'key': 'foo', 'value': 'bar' }
        mock_resp.status_code = 200

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.meta.get(self.chan, expected.keys(), url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_meta_get_failure(self, mock_session, mock_resp):
        expected = {'foo': 'bar'}
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = HTTPError()

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPErrorList):
            self.meta.get(self.chan, expected.keys(), url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_meta_update_success(self, mock_session):
        key_vals = {'foo': 'bar'}
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 200

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.meta.update(self.chan, key_vals, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_meta_update_failure(self, mock_session):
        key_vals = {'foo': 'bar'}
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPErrorList):
            self.meta.update(self.chan, key_vals, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_meta_delete_success(self, mock_session):
        keys = ['foo']
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        self.meta.delete(self.chan, keys, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_meta_delete_failure(self, mock_session):
        keys = ['foo']
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPErrorList):
            self.meta.delete(self.chan, keys, url_prefix, auth, mock_session, send_opts)

if __name__ == '__main__':
    unittest.main()
