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
import numpy as np
import unittest

class TestVolumeService(unittest.TestCase):
    """
    Test the VolumeService class that is common to all API versions.  There
    are also specific test cases for each API version.
    """

    def setUp(self):
        self.vs = VolumeService('some.host.name', LATEST_VERSION)

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
