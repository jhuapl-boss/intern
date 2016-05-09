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
from ndio.service.boss.baseversion import BaseVersion
from ndio.ndresource.boss.resource import CollectionResource

VER = 'v0.4'

class BaseImpl(BaseVersion):
    """Create a concrete implementation of BaseVersion so it can be tested.
    """

    @property
    def version(self):
        return VER

    @property
    def endpoint(self):
        return 'manage-data'

class BaseVersionTest(unittest.TestCase):
    def setUp(self):
        self.resource = CollectionResource('coll1', VER)
        self.sut = BaseImpl()
        self.url_prefix = 'https://api.theboss.io'

    def test_build_url_for_list(self):
        """A list operation's URL is different than any other operation.  It
        uses the plural form of the resource's type name rather than the
        resource's name.
        """
        actual = self.sut.build_url(self.resource, self.url_prefix, list_req=True)
        self.assertEqual(
            self.url_prefix + '/' + self.sut.version + '/' + self.sut.endpoint +
            '/collections',
            actual)

    def test_build_url_not_list(self):
        """Test standard use of BaseVersion.build_url().
        """
        actual = self.sut.build_url(self.resource, self.url_prefix, list_req=False)
        self.assertEqual(
            self.url_prefix + '/' + self.sut.version + '/' + self.sut.endpoint +
            '/' + self.resource.name,
            actual)

    def test_get_headers_gives_dict_with_content_type(self):
        actual = self.sut.get_headers('application/json', 'my_token')
        self.assertTrue('Content-Type' in actual)
        self.assertEqual('application/json', actual['Content-Type'])

    def test_get_headers_gives_dict_with_authorization(self):
        actual = self.sut.get_headers('application/json', 'my_token')
        self.assertTrue('Authorization' in actual)
        self.assertEqual('Token: my_token', 'Authorization')
