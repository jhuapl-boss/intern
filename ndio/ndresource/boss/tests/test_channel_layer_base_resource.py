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

import unittest
from ndio.ndresource.boss.resource import ChannelLayerBaseResource

class ChanLyrImpl(ChannelLayerBaseResource):
    def get_project_list_route(self):
        return ''

    def get_route(self):
        return ''

class TestChannelLayerBaseResource(unittest.TestCase):
    def setUp(self):
        self.clb = ChanLyrImpl('foo', 'bar', 'exp')

    def test_valid_volume(self):
        self.assertTrue(self.clb.valid_volume())

    def test_validate_datatype_uint8(self):
        exp = 'uint8'
        self.assertEqual(exp, self.clb.validate_datatype(exp))

    def test_validate_datatype_uint16(self):
        exp = 'uint16'
        self.assertEqual(exp, self.clb.validate_datatype(exp))

    def test_validate_datatype_uint64(self):
        exp = 'uint64'
        self.assertEqual(exp, self.clb.validate_datatype(exp))

    def test_validate_datatype_bad(self):
        with self.assertRaises(ValueError):
            self.clb.validate_datatype('bigint')
