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
from intern.resource.boss.resource import ChannelResource

class TestChannelResource(unittest.TestCase):
    def setUp(self):
        self.chan = ChannelResource('mychan', 'foo', 'bar', 'image')

    def test_init_status_false(self):
        chan = ChannelResource('somechan', 'foo', 'bar')
        self.assertFalse(chan.cutout_ready)

    def test_channel_defaults_to_uint8(self):
        chan = ChannelResource('somechan', 'foo', 'bar')
        self.assertEqual('uint8', chan.datatype)

    def test_setting_datatype_means_cutout_ready_at_construction(self):
        chan = ChannelResource('somechan', 'foo', 'bar', datatype='uint8')
        self.assertTrue(chan.cutout_ready)

    def test_setting_datatype_means_cutout_ready(self):
        chan = ChannelResource('somechan', 'foo', 'bar')
        chan.datatype = 'uint16'
        self.assertTrue(chan.cutout_ready)

    def test_default_source_is_empty(self):
        self.assertEqual([], self.chan.sources)

    def test_default_related_is_empty(self):
        self.assertEqual([], self.chan.related)

    def test_source_string_stored_as_list(self):
        self.chan.sources = 'foo'
        self.assertEqual(['foo'], self.chan.sources)

    def test_related_string_stored_as_list(self):
        self.chan.related = 'foo'
        self.assertEqual(['foo'], self.chan.related)

    def test_source_list(self):
        self.chan.source = ['foo', 'bar']
        self.assertEqual(['foo', 'bar'], self.chan.source)

    def test_related_list(self):
        self.chan.related = ['foo', 'bar']
        self.assertEqual(['foo', 'bar'], self.chan.related)

    def test_valid_volume(self):
        self.assertTrue(self.chan.valid_volume())

    def test_get_route(self):
        self.assertEqual('{}/experiment/{}/channel/{}'.format(
            self.chan.coll_name, self.chan.exp_name, self.chan.name),
            self.chan.get_route())

    def test_get_list_route(self):
        self.assertEqual(
            '{}/experiment/{}/channel/'.format(self.chan.coll_name, self.chan.exp_name),
            self.chan.get_list_route())

    def test_validate_datatype_uint8(self):
        exp = 'uint8'
        self.assertEqual(exp, self.chan.validate_datatype(exp))

    def test_validate_datatype_uint16(self):
        exp = 'uint16'
        self.assertEqual(exp, self.chan.validate_datatype(exp))

    def test_validate_datatype_uint64(self):
        exp = 'uint64'
        self.assertEqual(exp, self.chan.validate_datatype(exp))

    def test_validate_datatype_bad(self):
        with self.assertRaises(ValueError):
            self.chan.validate_datatype('bigint')
