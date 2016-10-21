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

from ndio.remote.boss import BossRemote
from ndio.remote.boss.remote import (
    CONFIG_PROJECT_SECTION, CONFIG_PROTOCOL, CONFIG_HOST, CONFIG_TOKEN,
    CONFIG_METADATA_SECTION, CONFIG_VOLUME_SECTION)
import unittest

class RemoteConfigTest(unittest.TestCase):
    def setUp(self):
        self.remote = BossRemote(cfg_file='examples/example.cfg')
        self.config = """[Project Service]
        protocol = https
        host = pro.theboss.io
        token = my_secret_token

        [Metadata Service]
        protocol = file
        host = meta.theboss.io
        token = my_secret_token2

        [Volume Service]
        protocol = http
        host = vol.theboss.io
        token = my_secret_token3
        """

    def test_init_with_file(self):
        """Exercise code path when cfg_file parameter used."""
        with self.assertRaises(FileNotFoundError):
            rmt = BossRemote(cfg_file='nofile.cfg')

    def test_init_with_config_str(self):
        rmt = BossRemote(cfg_str=self.config)
        actual_prj = rmt._config[CONFIG_PROJECT_SECTION]
        self.assertEqual('https', actual_prj[CONFIG_PROTOCOL])
        self.assertEqual('pro.theboss.io', actual_prj[CONFIG_HOST])
        self.assertEqual('my_secret_token', actual_prj[CONFIG_TOKEN])

        actual_meta = rmt._config[CONFIG_METADATA_SECTION]
        self.assertEqual('file', actual_meta[CONFIG_PROTOCOL])
        self.assertEqual('meta.theboss.io', actual_meta[CONFIG_HOST])
        self.assertEqual('my_secret_token2', actual_meta[CONFIG_TOKEN])

        actual_vol = rmt._config[CONFIG_VOLUME_SECTION]
        self.assertEqual('http', actual_vol[CONFIG_PROTOCOL])
        self.assertEqual('vol.theboss.io', actual_vol[CONFIG_HOST])
        self.assertEqual('my_secret_token3', actual_vol[CONFIG_TOKEN])

    def test_load_project_config(self):
        cfgParser = self.remote.load_config(self.config)
        actual = cfgParser[CONFIG_PROJECT_SECTION]
        self.assertEqual('https', actual[CONFIG_PROTOCOL])
        self.assertEqual('pro.theboss.io', actual[CONFIG_HOST])
        self.assertEqual('my_secret_token', actual[CONFIG_TOKEN])

    def test_load_metadata_config(self):
        cfgParser = self.remote.load_config(self.config)
        actual = cfgParser[CONFIG_METADATA_SECTION]
        self.assertEqual('file', actual[CONFIG_PROTOCOL])
        self.assertEqual('meta.theboss.io', actual[CONFIG_HOST])
        self.assertEqual('my_secret_token2', actual[CONFIG_TOKEN])

    def test_load_volume_config(self):
        cfgParser = self.remote.load_config(self.config)
        actual = cfgParser[CONFIG_VOLUME_SECTION]
        self.assertEqual('http', actual[CONFIG_PROTOCOL])
        self.assertEqual('vol.theboss.io', actual[CONFIG_HOST])
        self.assertEqual('my_secret_token3', actual[CONFIG_TOKEN])


if __name__ == '__main__':
    unittest.main()
