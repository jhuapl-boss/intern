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

from ndio.service.boss.v0_4.project import ProjectService_0_4
from ndio.ndresource.boss.resource import *
from requests import HTTPError, PreparedRequest, Response, Session
import unittest
from unittest.mock import patch

class TestProject(unittest.TestCase):
    def setUp(self):
        self.prj = ProjectService_0_4()
        self.chan = ChannelResource('chan', 'foo', 'bar', datatype='uint16')

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_prj_list_success(self, mock_session, mock_resp):
        expected = [{'name': 'foo'}, {'name': 'bar'}]
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 200
        mock_resp.json.return_value = expected

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.list(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_prj_list_failure(self, mock_session, mock_resp):
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = HTTPError()

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.list(self.chan, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_prj_create_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 201

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.create(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertTrue(actual)

    @patch('requests.Session', autospec=True)
    def test_prj_create_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.create(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertFalse(actual)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_prj_get_success(self, mock_session, mock_resp):
        expected = { 'rock': 'foo', 'paper': 'bar' }
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.json.return_value = expected
        mock_resp.status_code = 200

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.get(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_prj_get_failure(self, mock_session, mock_resp):
        mock_session.prepare_request.return_value = PreparedRequest()
        mock_resp.status_code = 403
        mock_resp.raise_for_status.side_effect = HTTPError()

        mock_session.send.return_value = mock_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.prj.get(self.chan, url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_prj_update_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 200

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.update(self.chan.name, self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertTrue(actual)

    @patch('requests.Session', autospec=True)
    def test_prj_update_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.update(self.chan.name, self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertFalse(actual)

    @patch('requests.Session', autospec=True)
    def test_prj_delete_success(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 204

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.delete(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertTrue(actual)

    @patch('requests.Session', autospec=True)
    def test_prj_delete_failure(self, mock_session):
        mock_session.prepare_request.return_value = PreparedRequest()
        fake_resp = Response()
        fake_resp.status_code = 403

        mock_session.send.return_value = fake_resp

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        actual = self.prj.delete(self.chan, url_prefix, auth, mock_session, send_opts)

        self.assertFalse(actual)

    def test_get_resource_params_bad_type(self):
        with self.assertRaises(TypeError):
            self.prj._get_resource_params(None)

    def test_get_resource_params_collection(self):
        coll = CollectionResource('foo')
        actual = self.prj._get_resource_params(coll)
        self.assertEqual('foo', actual['name'])
        self.assertTrue('description' in actual)

    def test_get_resource_params_experiment(self):
        exp = ExperimentResource('foo', 'coll')
        actual = self.prj._get_resource_params(exp)
        self.assertEqual('foo', actual['name'])
        self.assertTrue('description' in actual)
        self.assertTrue('coord_frame' in actual)
        self.assertTrue('num_hierarchy_levels' in actual)
        self.assertTrue('hierarchy_method' in actual)
        self.assertTrue('max_time_sample' in actual)

    def test_get_resource_params_coord_frame(self):
        coord = CoordinateFrameResource('foo')
        actual = self.prj._get_resource_params(coord)
        self.assertEqual('foo', actual['name'])
        self.assertTrue('description' in actual)
        self.assertTrue('x_start' in actual)
        self.assertTrue('x_stop' in actual)
        self.assertTrue('y_start' in actual)
        self.assertTrue('y_stop' in actual)
        self.assertTrue('z_start' in actual)
        self.assertTrue('z_stop' in actual)
        self.assertTrue('x_voxel_size' in actual)
        self.assertTrue('y_voxel_size' in actual)
        self.assertTrue('z_voxel_size' in actual)
        self.assertTrue('voxel_unit' in actual)
        self.assertTrue('time_step' in actual)
        self.assertTrue('time_step_unit' in actual)

    def test_get_resource_params_channel(self):
        chan = ChannelResource('foo', 'coll', 'exp')
        actual = self.prj._get_resource_params(chan)
        self.assertEqual('foo', actual['name'])
        self.assertTrue(actual['is_channel'])
        self.assertTrue('description' in actual)
        self.assertTrue('default_time_step' in actual)
        self.assertTrue('datatype' in actual)
        self.assertTrue('base_resolution' in actual)

    def test_get_resource_params_layer(self):
        layer = LayerResource('foo', 'coll', 'exp')
        actual = self.prj._get_resource_params(layer)
        self.assertEqual('foo', actual['name'])
        self.assertFalse(actual['is_channel'])
        self.assertTrue('description' in actual)
        self.assertTrue('default_time_step' in actual)
        self.assertTrue('datatype' in actual)
        self.assertTrue('base_resolution' in actual)
        self.assertTrue('channels' in actual)
