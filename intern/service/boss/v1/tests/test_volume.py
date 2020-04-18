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

from intern.service.boss.v1.volume import VolumeService_1
from intern.service.boss import BaseVersion
from intern.service.boss.v1.volume import CacheMode
from intern.resource.boss.resource import ChannelResource
import blosc
import numpy
from requests import HTTPError, PreparedRequest, Response, Session
import unittest
from mock import patch, ANY


class TestVolume_v1(unittest.TestCase):
    def setUp(self):
        self.vol = VolumeService_1()
        self.chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        self.anno_chan = ChannelResource('anno_chan', 'foo', 'bar', 'annotation', datatype='uint64', sources=['chan'])

    @patch('requests.Session', autospec=True)
    def test_create_cutout_success(self, mock_session):
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'

        mock_session.prepare_request.return_value = PreparedRequest()
        fake_response = Response()
        fake_response.status_code = 201
        mock_session.send.return_value = fake_response
        send_opts = {}

        self.vol.create_cutout(
            self.chan, resolution, x_range, y_range, z_range, time_range, data,
            url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_create_large_cutout_success(self, mock_session):
        resolution = 0
        x_range = [3000, 6000]
        y_range = [3000, 6000]
        z_range = [30, 63]
        time_range = [10, 25]
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'

        mock_session.prepare_request.return_value = PreparedRequest()
        fake_response = Response()
        fake_response.status_code = 201
        mock_session.send.return_value = fake_response
        send_opts = {}

        self.vol.create_cutout(
            self.chan, resolution, x_range, y_range, z_range, time_range, data,
            url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_create_cutout_failure(self, mock_session):
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'

        mock_session.prepare_request.return_value = PreparedRequest()
        fake_response = Response()
        fake_response.status_code = 403
        mock_session.send.return_value = fake_response
        send_opts = {}

        with self.assertRaises(HTTPError):
            self.vol.create_cutout(
                self.chan, resolution, x_range, y_range, z_range, time_range, data,
                url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_success(self, mock_session):
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        id_list = []
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'

        fake_prepped_req = PreparedRequest()
        fake_prepped_req.headers = {}
        mock_session.prepare_request.return_value = fake_prepped_req

        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response = Response()
        fake_response.status_code = 200
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        actual = self.vol.get_cutout(
            self.chan, resolution, x_range, y_range, z_range, time_range, id_list,
            url_prefix, auth, mock_session, send_opts)

        numpy.testing.assert_array_equal(data, actual)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_failure(self, mock_session):
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        id_list = []
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'

        fake_prepped_req = PreparedRequest()
        fake_prepped_req.headers = {}
        mock_session.prepare_request.return_value = fake_prepped_req
        fake_response = Response()
        fake_response.status_code = 403
        mock_session.send.return_value = fake_response
        send_opts = {}

        with self.assertRaises(HTTPError):
            actual = self.vol.get_cutout(
                self.chan, resolution, x_range, y_range, z_range, time_range, id_list,
                url_prefix, auth, mock_session, send_opts)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_access_mode_defaults_no_cache_small_cutout(self, mock_session):
        """Ensure no-cache defaults to True."""
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        id_list = []

        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.prepare_request.return_value.headers = {}

        fake_response = Response()
        fake_response.status_code = 200
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        with patch.object(
                BaseVersion, 'get_cutout_request', autospec=True, wraps=BaseVersion.get_cutout_request) as req_spy:
            self.vol.get_cutout(self.chan, resolution, x_range, y_range, z_range,
                time_range, id_list, url_prefix, auth, mock_session, send_opts)
            req_spy.assert_called_with(ANY, ANY, 'GET', ANY, url_prefix, auth, resolution,
                x_range, y_range, z_range, time_range, id_list=[], access_mode=CacheMode.no_cache)
            self.assertEqual(1, req_spy.call_count)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_access_mode_defaults_no_cache_large_cutout(self, mock_session):
        """Ensure no-cache defaults to True for all recursive calls generated
        by get_cutout."""
        resolution = 0
        x_range = [20, 1045]
        y_range = [50, 1075]
        z_range = [30, 33]
        time_range = [10, 11]
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        id_list = []

        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.prepare_request.return_value.headers = {}

        fake_response = Response()
        fake_response.status_code = 200
        data = numpy.random.randint(0, 3000, (1, 3, 1025, 1025), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        with patch.object(
                BaseVersion, 'get_cutout_request', autospec=True, wraps=BaseVersion.get_cutout_request) as req_spy:
            self.vol.get_cutout(self.chan, resolution, x_range, y_range, z_range,
                time_range, id_list, url_prefix, auth, mock_session, send_opts)
            req_spy.assert_called_with(ANY, ANY, 'GET', ANY, url_prefix, auth, resolution,
                ANY, ANY, ANY, ANY, id_list=[], access_mode=CacheMode.no_cache)
            # Verify that chunking occured.
            self.assertTrue(req_spy.call_count > 0)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_access_mode_raw_small_cutout(self, mock_session):
        """Ensure no-cache defaults to True."""
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        id_list = []

        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.prepare_request.return_value.headers = {}

        fake_response = Response()
        fake_response.status_code = 200
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        with patch.object(
                BaseVersion, 'get_cutout_request', autospec=True, wraps=BaseVersion.get_cutout_request) as req_spy:
            self.vol.get_cutout(self.chan, resolution, x_range, y_range, z_range,
                time_range, id_list, url_prefix, auth, mock_session, send_opts, access_mode=CacheMode.raw)
            req_spy.assert_called_with(ANY, ANY, 'GET', ANY, url_prefix, auth, resolution,
                x_range, y_range, z_range, time_range, id_list=[], access_mode=CacheMode.raw)
            self.assertEqual(1, req_spy.call_count)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_access_mode_raw_large_cutout(self, mock_session):
        """Ensure no-cache defaults to True."""
        resolution = 0
        x_range = [20, 1045]
        y_range = [50, 1075]
        z_range = [30, 33]
        time_range = [10, 11]
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        id_list = []

        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.prepare_request.return_value.headers = {}

        fake_response = Response()
        fake_response.status_code = 200
        data = numpy.random.randint(0, 3000, (1, 3, 1025, 1025), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        with patch.object(
                BaseVersion, 'get_cutout_request', autospec=True, wraps=BaseVersion.get_cutout_request) as req_spy:
            self.vol.get_cutout(self.chan, resolution, x_range, y_range, z_range,
                time_range, id_list, url_prefix, auth, mock_session, send_opts, access_mode=CacheMode.raw)
            req_spy.assert_called_with(ANY, ANY, 'GET', ANY, url_prefix, auth, resolution,
                x_range, y_range, z_range, time_range, id_list=[], access_mode=CacheMode.raw)
            self.assertEqual(1, req_spy.call_count)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_access_mode_raw_small_cutout(self, mock_session):
        """Ensure no-cache defaults to True."""
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        time_range = [10, 25]
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        id_list = []

        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.prepare_request.return_value.headers = {}

        fake_response = Response()
        fake_response.status_code = 200
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        with patch.object(
                BaseVersion, 'get_cutout_request', autospec=True, wraps=BaseVersion.get_cutout_request) as req_spy:
            self.vol.get_cutout(self.chan, resolution, x_range, y_range, z_range,
                time_range, id_list, url_prefix, auth, mock_session, send_opts, access_mode=CacheMode.cache)
            req_spy.assert_called_with(ANY, ANY, 'GET', ANY, url_prefix, auth, resolution,
                x_range, y_range, z_range, time_range, id_list=[], access_mode=CacheMode.cache)
            self.assertEqual(1, req_spy.call_count)

    @patch('requests.Session', autospec=True)
    def test_get_cutout_access_mode_cache_large_cutout(self, mock_session):
        """Ensure no-cache defaults to True."""
        resolution = 0
        x_range = [20, 1045]
        y_range = [50, 1075]
        z_range = [30, 33]
        time_range = [10, 11]
        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        id_list = []

        mock_session.prepare_request.return_value = PreparedRequest()
        mock_session.prepare_request.return_value.headers = {}

        fake_response = Response()
        fake_response.status_code = 200
        data = numpy.random.randint(0, 3000, (1, 3, 1025, 1025), numpy.uint16)
        compressed_data = blosc.compress(data, typesize=16)
        fake_response._content = compressed_data
        mock_session.send.return_value = fake_response
        send_opts = {}

        with patch.object(
                BaseVersion, 'get_cutout_request', autospec=True, wraps=BaseVersion.get_cutout_request) as req_spy:
            self.vol.get_cutout(self.chan, resolution, x_range, y_range, z_range,
                time_range, id_list, url_prefix, auth, mock_session, send_opts, access_mode=CacheMode.cache)
            req_spy.assert_called_with(ANY, ANY, 'GET', ANY, url_prefix, auth, resolution,
                x_range, y_range, z_range, time_range, id_list=[], access_mode=CacheMode.cache)
            self.assertEqual(1, req_spy.call_count)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_get_bounding_box_success(self, mock_session, mock_resp):
        resolution = 0
        id = 44444
        bb_type = 'loose'

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        fake_prepped_req = PreparedRequest()
        fake_prepped_req.headers = {}
        mock_session.prepare_request.return_value = fake_prepped_req
        mock_session.send.return_value = mock_resp

        mock_resp.status_code = 200
        mock_resp.json.return_value = expected = {
            'x_range': [0, 10],
            'y_range': [0, 10],
            'z_range': [0, 10],
            't_range': [0, 10]
        }

        actual = self.vol.get_bounding_box(
            self.anno_chan, resolution, id, bb_type,
            url_prefix, auth, mock_session, send_opts)

        self.assertEqual(expected, actual)

    @patch('requests.Response', autospec=True)
    @patch('requests.Session', autospec=True)
    def test_get_ids_in_region_success(self, mock_session, mock_resp):
        resolution = 0
        x_range = [0, 100]
        y_range = [10, 50]
        z_range = [20, 42]
        t_range = [0, 1]

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        fake_prepped_req = PreparedRequest()
        fake_prepped_req.headers = {}
        mock_session.prepare_request.return_value = fake_prepped_req
        mock_session.send.return_value = mock_resp

        mock_resp.status_code = 200
        mock_resp.json.return_value = { 'ids': ['1', '10'] }

        actual = self.vol.get_ids_in_region(
            self.anno_chan, resolution, x_range, y_range, z_range, t_range,
            url_prefix, auth, mock_session, send_opts)

        expected = [1, 10]

        self.assertEqual(expected, actual)

    @patch('requests.Session', autospec=True)
    def test_get_ids_in_region_failure(self, mock_session):
        resolution = 0
        x_range = [0, 100]
        y_range = [10, 50]
        z_range = [20, 42]
        t_range = [0, 1]

        url_prefix = 'https://api.theboss.io'
        auth = 'mytoken'
        send_opts = {}

        fake_prepped_req = PreparedRequest()
        fake_prepped_req.headers = {}
        mock_session.prepare_request.return_value = fake_prepped_req
        fake_response = Response()
        fake_response.status_code = 403
        mock_session.send.return_value = fake_response
        send_opts = {}

        with self.assertRaises(HTTPError):
            actual = self.vol.get_ids_in_region(
                self.anno_chan, resolution, x_range, y_range, z_range, t_range,
                url_prefix, auth, mock_session, send_opts)
