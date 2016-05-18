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
from ndio.ndresource.boss.resource import LayerResource

class TestLayerResource(unittest.TestCase):
    def setUp(self):
        self.lyr = LayerResource('mylyr', 'foo', 'bar')

    def test_valid_volume(self):
        self.assertTrue(self.lyr.valid_volume())

    def test_get_route(self):
        self.assertEqual('{}/{}/{}'.format(
            self.lyr.coll_name, self.lyr.exp_name, self.lyr.name), 
            self.lyr.get_route())

    def test_get_project_list_route(self):
        self.assertEqual(
            '{}/{}/layers'.format(self.lyr.coll_name, self.lyr.exp_name), 
            self.lyr.get_project_list_route())
