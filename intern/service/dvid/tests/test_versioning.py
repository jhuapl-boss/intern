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

from intern.service.dvid.versioning import VersioningService
from intern.resource.dvid.resource import DataInstanceResource
import numpy
from requests import HTTPError, PreparedRequest, Response, Session
import unittest
from mock import patch, ANY
import mock


class TestVersioning(unittest.TestCase):
    def setUp(self):

        self.UUID = "822524777d3048b8bd520043f90c1d28"
        self.DATA_INSTANCE = "grayscale"
        self.ALIAS = "grayscale"

        self.parent_uuid = ["1234567891011121314151617", "39782892"]
        self.data_instances = ["data_instance_a", "data_instance_b", "data_instance_c"]

        self.ver = VersioningService('https://emdata.janelia.org')

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
    def test_merge_failure(self, mock_post):

        mock_resp = self._mock_response(status=403)
        mock_post.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.ver.merge(self.UUID, self.parent_uuid, "conflict_free", "some note")

    @patch('requests.post', autospec=True)
    def test_resolve_failure(self, mock_post):

        mock_resp = self._mock_response(status=403)
        mock_post.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.ver.resolve(self.UUID, self.data_instances, self.parent_uuid, "some note")

    @patch('requests.get', autospec=True)
    def test_get_log_success(self, mock_get):

        mock_resp = self._mock_response(status=200)
        mock_get.return_value = mock_resp

        self.ver.get_log(self.UUID)

    @patch('requests.get', autospec=True)
    def test_get_log_failure(self, mock_get):

        mock_resp = self._mock_response(status=403)
        mock_get.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.ver.get_log(self.UUID)

    @patch('requests.get', autospec=True)
    def test_get_log_no_uuid_failure(self, mock_get):

        mock_resp = self._mock_response(status=200)
        mock_get.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.ver.get_log("")

    @patch('requests.post', autospec=True)
    def test_post_log_failure(self, mock_post):

        mock_resp = self._mock_response(status=403)
        mock_post.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.ver.post_log(self.UUID, "some log msg")

    @patch('requests.post', autospec=True)
    def test_post_log_no_uuid_failure(self, mock_post):

        mock_resp = self._mock_response(status=200)
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.ver.post_log("", "some log msg")

    @patch('requests.post', autospec=True)
    def test_post_log_no_log_msg_failure(self, mock_post):

        mock_resp = self._mock_response(status=200)
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.ver.post_log(self.UUID, "")

    @patch('requests.post', autospec=True)
    def test_branch_failure(self, mock_post):

        mock_resp = self._mock_response(status=403)
        mock_post.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.ver.branch(self.UUID)

    @patch('requests.post', autospec=True)
    def test_branch_no_uuid_failure(self, mock_post):

        mock_resp = self._mock_response(status=200)
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.ver.branch("")

    @patch('requests.post', autospec=True)
    def test_commit_failure(self, mock_post):

        mock_resp = self._mock_response(status=403)
        mock_post.return_value = mock_resp

        with self.assertRaises(HTTPError):
            self.ver.commit(self.UUID)

    @patch('requests.post', autospec=True)
    def test_commit_no_uuid_failure(self, mock_post):

        mock_resp = self._mock_response(status=200)
        mock_post.return_value = mock_resp

        with self.assertRaises(ValueError):
            self.ver.commit("")

if __name__ == '__main__':
    unittest.main()