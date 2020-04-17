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

from intern.service.dvid.project import ProjectService
from intern.resource.dvid.resource import DataInstanceResource
from intern.resource.dvid.resource import RepositoryResource
import numpy
from requests import HTTPError, PreparedRequest, Response, Session
import unittest
from mock import patch, ANY
import mock


class TestProject(unittest.TestCase):
    def setUp(self):

        self.UUID = "822524777d3048b8bd520043f90c1d28"
        self.DATA_INSTANCE = "grayscale"
        self.ALIAS = "grayscale"

        self.proj = ProjectService('https://emdata.janelia.org')
        
        self.name = "some_data_instance"

        self.data_instance_master = DataInstanceResource(self.name, UUID = self.UUID, datatype="uint8")
        self.repository_master = RepositoryResource(UUID = self.UUID, alias = self.ALIAS)

        self.data_instance_no_uuid = DataInstanceResource(self.name, datatype="uint8")
        self.repository_no_uuid = RepositoryResource(alias = self.ALIAS)

    def _mock_response(
            self,
            status=200,
            content="root'something else",
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
    def test_create_repository_rsrc_uuid_failure(self, mock_post):

        mock_resp = self._mock_response(status=200)
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.proj.create(self.repository_master)

    @patch('requests.post', autospec=True)
    def test_create_data_instance_uuid_success(self, mock_post):

        mock_resp = self._mock_response(status=200)
        mock_post.return_value = mock_resp

        self.proj.create(self.data_instance_master)

    @patch('requests.delete', autospec=True)
    def test_delete_data_instance_success(self, mock_delete):

        mock_resp = self._mock_response(status=200)
        mock_delete.return_value = mock_resp

        self.proj.delete(self.repository_no_uuid)

    @patch('requests.delete', autospec=True)
    def test_delete_repository_success(self, mock_delete):

        mock_resp = self._mock_response(status=200)
        mock_delete.return_value = mock_resp

        self.proj.delete(self.repository_no_uuid)

    @patch('requests.delete', autospec=True)
    def test_delete_data_instance_failure(self, mock_delete):

        mock_resp = self._mock_response(status=403)
        mock_delete.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.proj.delete(self.repository_no_uuid)

    @patch('requests.delete', autospec=True)
    def test_delete_repository_failure(self, mock_delete):

        mock_resp = self._mock_response(status=403)
        mock_delete.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.proj.delete(self.repository_no_uuid)

    @patch('requests.delete', autospec=True)
    def test_delete_wrong_resource_failure(self, mock_delete):

        mock_resp = self._mock_response(status=200)
        mock_delete.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.proj.delete(self.proj)

if __name__ == '__main__':
    unittest.main()