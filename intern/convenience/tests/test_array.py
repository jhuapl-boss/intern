"""
Copyright 2018-2020 The Johns Hopkins University Applied Physics Laboratory.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
#!/usr/bin/env python3

import unittest

from intern.remote.boss import BossRemote
import numpy as np

from ..array import array, parse_bossdb_uri


class TestUtils(unittest.TestCase):
    """
    Verify that the utility functions work.
    .
    """

    def test_uri_parse(self):
        """
        Does a correct URI parse correctly.
        .
        """
        uri = parse_bossdb_uri("bossdb://foo/bar/baz")
        self.assertEqual(uri.collection, "foo")
        self.assertEqual(uri.experiment, "bar")
        self.assertEqual(uri.channel, "baz")


class TestArray(unittest.TestCase):
    """
    Test indexing methods and cache methods of the array.
    .
    """

    def test_array_instantiation(self):
        """
        Array can be instantiated.
        .
        """
        boss = BossRemote()
        _ = array(boss.get_channel("cc", "kasthuri2015", "em"))

    def test_array_instantiation_dtype(self):
        """
        Array can be instantiated with type.
        .
        """
        boss = BossRemote()
        test_array = array(boss.get_channel("cc", "kasthuri2015", "em"))
        self.assertEqual(test_array.dtype, "uint8")

    def test_array_instantiation_shape(self):
        """
        Array can be instantiated with size.
        .
        """
        boss = BossRemote()
        test_array = array(boss.get_channel("cc", "kasthuri2015", "em"))
        self.assertEqual(test_array.shape, (10752, 13312, 1849))

    def test_get_data(self):
        """
        Can the array retrieve data.
        .
        """
        boss = BossRemote()
        test_array = array(boss.get_channel("cc", "kasthuri2015", "em"))
        self.assertEqual(np.sum(test_array[0:10, 0:10, 0:10]), 0)

    def test_get_data_shape(self):
        """
        Can you retrieve data shape after cutout.
        .
        """
        boss = BossRemote()
        test_array = array(boss.get_channel("cc", "kasthuri2015", "em"))
        self.assertEqual(test_array[0:10, 0:10, 0:10].shape, (10, 10, 10))

    def test_get_data_dtype(self):
        """
        Does the array know its datatype.
        .
        """
        boss = BossRemote()
        test_array = array(boss.get_channel("cc", "kasthuri2015", "em"))
        self.assertEqual(test_array[0:10, 0:10, 0:10].dtype, test_array.dtype)
