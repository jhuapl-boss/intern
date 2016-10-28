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

from intern.remote import Remote
from intern.remote.boss import BossRemote
import unittest
from mock import patch


class TestRemoteListMethods(unittest.TestCase):
    def setUp(self):
        config = {"protocol": "https",
                  "host": "test.theboss.io",
                  "token": "my_secret"}
        self.remote = BossRemote(config)

    def test_list_collections(self):
        with patch.object(Remote, 'list_project') as list_prj_fake:
            list_prj_fake.return_value = []

            actual = self.remote.list_collections()
            self.assertEqual([], actual)

    def test_list_experiments(self):
        with patch.object(Remote, 'list_project') as list_prj_fake:
            list_prj_fake.return_value = []

            actual = self.remote.list_experiments('collection_alpha')
            self.assertEqual([], actual)

    def test_list_channels(self):
        with patch.object(Remote, 'list_project') as list_prj_fake:
            list_prj_fake.return_value = []

            actual = self.remote.list_channels('collection_alpha', 'experiment_beta')
            self.assertEqual([], actual)

    def test_list_coordinate_frames(self):
        with patch.object(Remote, 'list_project') as list_prj_fake:
            list_prj_fake.return_value = []

            actual = self.remote.list_coordinate_frames()
            self.assertEqual([], actual)

if __name__ == '__main__':
    unittest.main()
