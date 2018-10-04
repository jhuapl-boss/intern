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

from intern.remote.boss import LATEST_VERSION
from intern.resource.boss import ChannelResource, PartialChannelResourceError
from intern.service.boss.volume import VolumeService
from intern.service.boss.v1.volume import VolumeService_1
from mock import patch, ANY
import numpy as np
import unittest

class TestVolumeService(unittest.TestCase):
    """
    Test the VolumeService class that is common to all API versions.  There
    are also specific test cases for each API version.
    """

    def setUp(self):
        self.url = 'some.host.name'
        self.vs = VolumeService(self.url, LATEST_VERSION)

    def test_given_invalid_channel(self):
        with self.assertRaises(RuntimeError):
            vol = np.ones((100, 100, 100))
            self.vs.create_cutout(
                'not a channel', 0, [0, 100], [0, 100], [0, 100], vol)

    def test_given_partially_initialized_channel(self):
        with self.assertRaises(PartialChannelResourceError):
            chan = ChannelResource('myChan', 'myCol', 'myExp')
            vol = np.ones((100, 100, 100))
            self.vs.create_cutout(
                chan, 0, [0, 100], [0, 100], [0, 100], vol)

    @patch.object(VolumeService_1, 'get_cutout', autospec=True)
    def test_get_cutout_no_cache_defaults_true_v1(self, fake_volume):
        """
        Test that if no_cache not provided, it defaults to True when calling
        the VolumeService_1's get_cutout().
        """
        chan = ChannelResource('chan', 'foo', 'bar', 'image', datatype='uint16')
        resolution = 0
        x_range = [20, 40]
        y_range = [50, 70]
        z_range = [30, 50]
        t_range = [0,1]
        id_list = []
        self.vs.get_cutout(chan, resolution, x_range, y_range, z_range, t_range)
        fake_volume.assert_called_with(
            ANY, chan, resolution, x_range, y_range, z_range, t_range, id_list,
            ANY, ANY, ANY, ANY,    # Session related args.
            True)   # This should be the no_cache argument.
