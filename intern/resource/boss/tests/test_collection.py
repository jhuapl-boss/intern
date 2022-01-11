# Copyright 2022 The Johns Hopkins University Applied Physics Laboratory
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
from intern.resource.boss.resource import CollectionResource


class TestCollectionResource(unittest.TestCase):
    def setUp(self):
        self.coll = CollectionResource("foo")

    def test_not_valid_volume(self):
        self.assertFalse(self.coll.valid_volume())

    def test_get_route(self):
        self.assertEqual(self.coll.name, self.coll.get_route())

    def test_get_list_route(self):
        self.assertEqual("foo/", self.coll.get_list_route())
