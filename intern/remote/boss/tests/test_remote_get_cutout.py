# Copyright 2018 The Johns Hopkins University Applied Physics Laboratory
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
from intern.resource.boss.resource import ChannelResource
from intern.service.boss.volume import VolumeService
from intern.service.boss.v1.volume import CacheMode
from mock import patch, ANY
import unittest


class TestRemoteGetCutout(unittest.TestCase):
    def setUp(self):
        config = {"protocol": "https",
                  "host": "test.theboss.io",
                  "token": "my_secret"}
        self.remote = BossRemote(config)

    @patch.object(VolumeService, 'get_cutout', autospec=True)
    def test_get_cutout_access_mode_defaults_no_cache(self, fake_volume):
        """
        Test that if no_cache not provided, it defaults to True when calling
        the volume service's get_cutout().
        """
        chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        self.remote.get_cutout(chan, resolution, x_range, y_range, z_range)
        fake_volume.assert_called_with(
            ANY, chan, resolution, x_range, y_range, z_range, ANY, ANY,
            CacheMode.no_cache, parallel=True)   # This should be the no_cache argument.

    @patch.object(VolumeService, 'get_cutout', autospec=True)
    def test_get_cutout_access_mode_raw(self, fake_volume):
        """
        Test that if no_cache not provided, it defaults to True when calling
        the volume service's get_cutout().
        """
        chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        self.remote.get_cutout(chan, resolution, x_range, y_range, z_range, access_mode=CacheMode.raw)
        fake_volume.assert_called_with(
            ANY, chan, resolution, x_range, y_range, z_range, ANY, ANY,
            CacheMode.raw, parallel=True)   # This should be the no_cache argument.

    @patch.object(VolumeService, 'get_cutout', autospec=True)
    def test_get_cutout_access_mode_cache(self, fake_volume):
        """
        Test that if no_cache not provided, it defaults to True when calling
        the volume service's get_cutout().
        """
        chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        self.remote.get_cutout(chan, resolution, x_range, y_range, z_range, access_mode=CacheMode.cache)
        fake_volume.assert_called_with(
            ANY, chan, resolution, x_range, y_range, z_range, ANY, ANY,
            CacheMode.cache, parallel=True)   # This should be the no_cache argument.


    ##REMOVE IN THE FUTURE, TESTS BACKWARDS COMPATABILITY
    @patch.object(VolumeService, 'get_cutout', autospec=True)
    def test_get_cutout_no_cache_True_backwards_compatability(self, fake_volume):
        """
        Test that if no_cache not provided, it defaults to True when calling
        the volume service's get_cutout().
        """
        chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        self.remote.get_cutout(chan, resolution, x_range, y_range, z_range, no_cache=True)
        fake_volume.assert_called_with(
            ANY, chan, resolution, x_range, y_range, z_range, ANY, ANY,
            CacheMode.no_cache, parallel=True)   # This should be the no_cache argument.

    @patch.object(VolumeService, 'get_cutout', autospec=True)
    def test_get_cutout_no_cache_False_backwards_compatability(self, fake_volume):
        """
        Test that if no_cache not provided, it defaults to True when calling
        the volume service's get_cutout().
        """
        chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        self.remote.get_cutout(chan, resolution, x_range, y_range, z_range, no_cache=False)
        fake_volume.assert_called_with(
            ANY, chan, resolution, x_range, y_range, z_range, ANY, ANY,
            CacheMode.cache, parallel=True)   # This should be the no_cache argument.
if __name__ == '__main__':
    unittest.main()