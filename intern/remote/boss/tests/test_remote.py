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

from intern.remote.boss import BossRemote
import tempfile
import os


from intern.remote.boss.remote import (
    CONFIG_PROJECT_SECTION, CONFIG_PROTOCOL, CONFIG_HOST, CONFIG_TOKEN,
    CONFIG_METADATA_SECTION, CONFIG_VOLUME_SECTION)
import unittest


class RemoteConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method to setup test class once"""
        default_cfg = tempfile.NamedTemporaryFile(mode='wt', delete=False)
        specific_cfg = tempfile.NamedTemporaryFile(mode='wt', delete=False)
        missing_cfg = tempfile.NamedTemporaryFile(mode='wt', delete=False)

        cls.default_cfg = default_cfg.name
        cls.specific_cfg = specific_cfg.name
        cls.missing_cfg = missing_cfg.name

        with open(cls.default_cfg, "wt") as default_writer:
            default_writer.write("""[Default]\nprotocol = https\nhost = default.theboss.io\ntoken = default_secret_token\n[Metadata Service]\nprotocol = file\nhost = meta.theboss.io\ntoken = my_secret_token2""")

        with open(cls.specific_cfg, "wt") as specific_writer:
            specific_writer.write("""[Default]\nprotocol = https\nhost = default.theboss.io\ntoken = default_secret_token\n[Project Service]\nprotocol = https\nhost = pro.theboss.io\ntoken = my_secret_token\n[Metadata Service]\nprotocol = file\nhost = meta.theboss.io\ntoken = my_secret_token2\n[Volume Service]\nprotocol = http\nhost = vol.theboss.io\ntoken = my_secret_token3""")

        with open(cls.missing_cfg, "wt") as missing_writer:
            missing_writer.write("""[Defaultttt]\nprotocol = https\nhost = default.theboss.io\ntoken = default_secret_token""")

    @classmethod
    def tearDownClass(cls):
        """Method to tear down test class once"""
        os.remove(cls.default_cfg)
        os.remove(cls.specific_cfg)
        os.remove(cls.missing_cfg)

    # def test_init_with_missing_file(self):
    #     """Test when a non-existent config file is provided"""
    #     with self.assertRaises(OSError):
    #         rmt = BossRemote('nofile.cfg')

    def test_init_with_malformed_file(self):
        """Test when a bad config file is provided"""
        with self.assertRaises(KeyError):
            rmt = BossRemote(self.missing_cfg)

    def test_init_with_bad_config_dict(self):
        """Method testing configuration with a malformed config dictionary"""
        config = {"host": "api.test.com"}
        with self.assertRaises(KeyError):
            rmt = BossRemote(config)

    def test_init_with_config_dict(self):
        config = {"protocol": "https",
                  "host": "api.test.com",
                  "token": "asdlsdj2192isja"}

        rmt = BossRemote(config)
        actual_prj = dict(rmt._config.items("Default"))
        self.assertEqual('https', actual_prj[CONFIG_PROTOCOL])
        self.assertEqual('api.test.com', actual_prj[CONFIG_HOST])
        self.assertEqual('asdlsdj2192isja', actual_prj[CONFIG_TOKEN])

        actual_meta = dict(rmt._config.items("Default"))
        self.assertEqual('https', actual_meta[CONFIG_PROTOCOL])
        self.assertEqual('api.test.com', actual_meta[CONFIG_HOST])
        self.assertEqual('asdlsdj2192isja', actual_meta[CONFIG_TOKEN])

        actual_vol = dict(rmt._config.items("Default"))
        self.assertEqual('https', actual_vol[CONFIG_PROTOCOL])
        self.assertEqual('api.test.com', actual_vol[CONFIG_HOST])
        self.assertEqual('asdlsdj2192isja', actual_vol[CONFIG_TOKEN])

        rmt.token_metadata = actual_meta[CONFIG_TOKEN]
        rmt.token_volume = actual_vol[CONFIG_TOKEN]
        rmt.token_project = actual_prj[CONFIG_TOKEN]

    def test_init_with_default_file(self):
        rmt = BossRemote(self.default_cfg)
        actual_default = dict(rmt._config.items("Default"))
        self.assertEqual('https', actual_default[CONFIG_PROTOCOL])
        self.assertEqual('default.theboss.io', actual_default[CONFIG_HOST])
        self.assertEqual('default_secret_token', actual_default[CONFIG_TOKEN])

        actual_meta = dict(rmt._config.items(CONFIG_METADATA_SECTION))
        self.assertEqual('file', actual_meta[CONFIG_PROTOCOL])
        self.assertEqual('meta.theboss.io', actual_meta[CONFIG_HOST])
        self.assertEqual('my_secret_token2', actual_meta[CONFIG_TOKEN])

        rmt.token_metadata = actual_meta[CONFIG_TOKEN]
        rmt.token_volume = actual_default[CONFIG_TOKEN]
        rmt.token_project = actual_default[CONFIG_TOKEN]

    def test_init_with_specific_file(self):
        rmt = BossRemote(self.specific_cfg)
        actual_prj = dict(rmt._config.items(CONFIG_PROJECT_SECTION))
        self.assertEqual('https', actual_prj[CONFIG_PROTOCOL])
        self.assertEqual('pro.theboss.io', actual_prj[CONFIG_HOST])
        self.assertEqual('my_secret_token', actual_prj[CONFIG_TOKEN])

        actual_meta = dict(rmt._config.items(CONFIG_METADATA_SECTION))
        self.assertEqual('file', actual_meta[CONFIG_PROTOCOL])
        self.assertEqual('meta.theboss.io', actual_meta[CONFIG_HOST])
        self.assertEqual('my_secret_token2', actual_meta[CONFIG_TOKEN])

        actual_vol = dict(rmt._config.items(CONFIG_VOLUME_SECTION))
        self.assertEqual('http', actual_vol[CONFIG_PROTOCOL])
        self.assertEqual('vol.theboss.io', actual_vol[CONFIG_HOST])
        self.assertEqual('my_secret_token3', actual_vol[CONFIG_TOKEN])

        rmt.token_metadata = actual_meta[CONFIG_TOKEN]
        rmt.token_volume = actual_vol[CONFIG_TOKEN]
        rmt.token_project = actual_prj[CONFIG_TOKEN]


if __name__ == '__main__':
    unittest.main()
