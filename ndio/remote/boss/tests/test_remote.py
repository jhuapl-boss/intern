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

from ndio.remote.boss.remote import Remote
import unittest

class RemoteConfigTest(unittest.TestCase):
    def setUp(self):
        self.remote = Remote()
        self.config = """[Project Service]
        protocol = https
        location = pro.theboss.io
        token = my_secret_token

        [Metadata Service]
        protocol = file
        location = meta.theboss.io
        token = my_secret_token2

        [Volume Service]
        protocol = http
        location = vol.theboss.io
        token = my_secret_token3
        """

    def test_load_project_config(self):
        cfgParser = self.remote.load_config(self.config)
        actual = cfgParser['Project Service']
        self.assertEqual('https', actual['protocol'])
        self.assertEqual('pro.theboss.io', actual['location'])
        self.assertEqual('my_secret_token', actual['token'])

    def test_load_metadata_config(self):
        cfgParser = self.remote.load_config(self.config)
        actual = cfgParser['Metadata Service']
        self.assertEqual('file', actual['protocol'])
        self.assertEqual('meta.theboss.io', actual['location'])
        self.assertEqual('my_secret_token2', actual['token'])

    def test_load_volume_config(self):
        cfgParser = self.remote.load_config(self.config)
        actual = cfgParser['Volume Service']
        self.assertEqual('http', actual['protocol'])
        self.assertEqual('vol.theboss.io', actual['location'])
        self.assertEqual('my_secret_token3', actual['token'])
