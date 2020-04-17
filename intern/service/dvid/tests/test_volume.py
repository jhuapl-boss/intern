# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
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

from intern.service.dvid.volume import VolumeService
from intern.resource.dvid.resource import DataInstanceResource
import numpy
from requests import HTTPError, PreparedRequest, Response, Session
import unittest
from mock import patch, ANY
import mock


class TestVolume(unittest.TestCase):
    def setUp(self):

        UUID = "822524777d3048b8bd520043f90c1d28"
        DATA_INSTANCE = "grayscale"
        ALIAS = "grayscale"

        self.vol = VolumeService('https://emdata.janelia.org')
        self.data_instance = DataInstanceResource(DATA_INSTANCE, UUID, "uint8blk", ALIAS, "Example channel.", datatype="uint8")

    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):

        mock_resp = mock.Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = mock.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    @patch('requests.post', autospec=True)
    def test_create_cutout_success(self, mock_post):
        resolution = 0
        x_range = [3000, 3150]
        y_range = [3000, 3150]
        z_range = [2000, 2010]
        send_opts = {}

        data = numpy.random.randint(0, 255, (10, 150, 150), numpy.uint8)
        octet_data = data.tobytes()
        
        mock_resp = self._mock_response(status=200, content=octet_data)
        mock_post.return_value = mock_resp

        self.vol.create_cutout(
            self.data_instance, resolution, x_range, y_range, z_range, data, send_opts)

    @patch('requests.post', autospec=True)
    def test_create_cutout_failure(self, mock_post):
        resolution = 0
        x_range = [3000, 3150]
        y_range = [3000, 3150]
        z_range = [2000, 2010]
        send_opts = {}

        data = numpy.random.randint(0, 255, (10, 150, 150), numpy.uint8)
        octet_data = data.tobytes()
        
        mock_resp = self._mock_response(status=403, content=octet_data)
        mock_post.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.vol.create_cutout(
                self.data_instance, resolution, x_range, y_range, z_range, data, send_opts)

    @patch('requests.get', autospec=True)
    def test_get_cutout_success(self, mock_get):
        resolution = 0
        x_range = [3000, 3150]
        y_range = [3000, 3150]
        z_range = [2000, 2010]

        data = numpy.random.randint(0, 255, (10, 150, 150), numpy.uint8)
        octet_data = data.tobytes()
        
        mock_resp = self._mock_response(status=200, content=octet_data)
        mock_get.return_value = mock_resp

        actual = self.vol.get_cutout(
            self.data_instance, resolution, x_range, y_range, z_range)

        numpy.testing.assert_array_equal(data, actual)

    @patch('requests.get', autospec=True)
    def test_get_cutout_failure(self, mock_get):
        resolution = 0
        x_range = [3000, 3150]
        y_range = [3000, 3150]
        z_range = [2000, 2010]

        data = numpy.random.randint(0, 255, (10, 150, 150), numpy.uint8)
        octet_data = data.tobytes()
        
        mock_resp = self._mock_response(status=403, content=octet_data)
        mock_get.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.vol.get_cutout(
                self.data_instance, resolution, x_range, y_range, z_range)

    @patch('requests.get', autospec=True)
    def test_get_cutout_range_failure(self, mock_get):
        resolution = 0
        x_range = [3000, 3150]
        y_range = [3000, 3150]
        z_range = [2000, 2010]

        # Data range doesn't match ranges for some reason
        data = numpy.random.randint(0, 255, (10, 200, 150), numpy.uint8)
        octet_data = data.tobytes()
        
        mock_resp = self._mock_response(status=200, content=octet_data)
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.vol.get_cutout(
                self.data_instance, resolution, x_range, y_range, z_range)

if __name__ == '__main__':
    unittest.main()