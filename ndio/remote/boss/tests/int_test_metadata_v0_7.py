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
 
from ndio.remote.boss.remote import *
from ndio.ndresource.boss.resource import *
from ndio.service.boss.httperrorlist import HTTPErrorList

import requests
from requests import Session, HTTPError
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import unittest

API_VER = 'v0.7'

class MetadataServiceTest_v0_7(unittest.TestCase):
    """Integration tests of the Boss metadata API.

    Because setup and teardown involves many REST calls, tests are only 
    divided into tests of the different types of data model resources.  All
    operations are performed within a single test of each resource.
    """

    @classmethod
    def setUpClass(cls):
        """Do an initial DB clean up in case something went wrong the last time.

        If a test failed really badly, the DB might be in a bad state despite
        attempts to clean up during tearDown().
        """
        cls.initialize(cls)
        cls.cleanup_db(cls)
        cls.rmt.project_create(cls.coll)
        coord_actual = cls.rmt.project_create(cls.coord)
        cls.exp.coord_frame = coord_actual.id;
        cls.rmt.project_create(cls.exp)
        chan_actual = cls.rmt.project_create(cls.chan)

    @classmethod
    def tearDownClass(cls):
        """Remove all data model objects created in the DB.
        """
        cls.initialize(cls)
        cls.cleanup_db(cls)

    def initialize(self):
        """Initialization for each test.

        Called by both setUp() and setUpClass().
        """
        self.rmt = Remote('test.cfg')

        # Turn off SSL cert verification.  This is necessary for interacting with
        # developer instances of the Boss.
        self.rmt.project_service.session_send_opts = { 'verify': False }
        self.rmt.metadata_service.session_send_opts = { 'verify': False }
        self.rmt.volume_service.session_send_opts = { 'verify': False }
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.coll = CollectionResource('collection2309', API_VER, 'bar')

        self.coord = CoordinateFrameResource(
            'BestFrame', API_VER, 'Test coordinate frame.', 0, 10, -5, 5, 3, 6, 
            1, 1, 1, 'nanometers', 0, 'nanoseconds')

        self.exp = ExperimentResource(
            'exp2309x2', self.coll.name, self.coord.name, API_VER, 'my experiment', 
            1, 'iso', 0)

        self.chan = ChannelResource(
            'myChan', self.coll.name, self.exp.name, 'image', API_VER, 'test channel', 
            0, 'uint8', 0)


    def cleanup_db(self):
        """Clean up the data model objects used by this test case.

        This method is used by both tearDownClass() and setUpClass().
        """
        try:
            self.rmt.project_delete(self.chan)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.exp)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coord)
        except HTTPError:
            pass
        try:
            self.rmt.project_delete(self.coll)
        except HTTPError:
            pass

    def setUp(self):
        self.initialize()

    def tearDown(self):
        pass

    def test_collection(self):
        actual_list = self.rmt.metadata_list(self.coll)
        self.assertEqual([], actual_list)

        keys_vals = { 'red': 'green', 'two': 'four', 'inside': 'out' }
        self.rmt.metadata_create(self.coll, keys_vals)

        actual = self.rmt.metadata_get(self.coll, list(keys_vals.keys()))
        self.assertCountEqual(keys_vals, actual)

        with self.assertRaises(HTTPErrorList):
            # Should fail when trying create keys that already exist.
            self.rmt.metadata_create(self.coll, keys_vals)

        update = { 'two': 'six', 'inside': 'upside-down' }
        self.rmt.metadata_update(self.coll, update)

        actual_upd = self.rmt.metadata_get(self.coll, list(update.keys()))
        self.assertCountEqual(update, actual_upd)

        actual_list_upd  = self.rmt.metadata_list(self.coll)
        self.assertCountEqual(list(keys_vals.keys()), actual_list_upd)

        with self.assertRaises(HTTPErrorList):
            # Try updating a non-existent key.
            self.rmt.metadata_update(self.coll, {'foo': 'bar'})

        self.rmt.metadata_delete(self.coll, list(keys_vals.keys()))

        with self.assertRaises(HTTPErrorList):
            # Try getting keys that don't exist.
            self.rmt.metadata_get(self.coll, ['foo', 'bar'])

        actual_list_end = self.rmt.metadata_list(self.coll)
        self.assertEqual([], actual_list_end)

    def test_experiment(self):
        actual_list = self.rmt.metadata_list(self.exp)
        self.assertEqual([], actual_list)

        keys_vals = { 'red': 'green', 'two': 'four', 'inside': 'out'}
        self.rmt.metadata_create(self.exp, keys_vals)
        actual = self.rmt.metadata_get(self.exp, list(keys_vals.keys()))
        self.assertCountEqual(keys_vals, actual)

        with self.assertRaises(HTTPErrorList):
            # Should fail when trying create keys that already exist.
            self.rmt.metadata_create(self.exp, keys_vals)

        update = { 'two': 'six', 'inside': 'upside-down' }
        self.rmt.metadata_update(self.exp, update)

        actual_upd = self.rmt.metadata_get(self.exp, list(update.keys()))
        self.assertCountEqual(update, actual_upd)

        actual_list_upd = self.rmt.metadata_list(self.exp)
        self.assertCountEqual(list(keys_vals.keys()), actual_list_upd)

        with self.assertRaises(HTTPErrorList):
            # Try updating a non-existent key.
            self.rmt.metadata_update(self.exp, {'foo': 'bar'})

        self.rmt.metadata_delete(self.exp, list(keys_vals.keys()))

        with self.assertRaises(HTTPErrorList):
            # Try getting keys that don't exist.
            self.rmt.metadata_get(self.exp, ['foo', 'bar'])

        actual_list_end = self.rmt.metadata_list(self.exp)
        self.assertEqual([], actual_list_end)

    def test_channel(self):
        actual_list = self.rmt.metadata_list(self.chan)
        self.assertEqual([], actual_list)

        keys_vals = { 'red': 'green', 'two': 'four', 'inside': 'out'}
        self.rmt.metadata_create(self.chan, keys_vals)
        actual = self.rmt.metadata_get(self.chan, list(keys_vals.keys()))
        self.assertCountEqual(keys_vals, actual)

        with self.assertRaises(HTTPErrorList):
            # Should fail when trying create keys that already exist.
            self.rmt.metadata_create(self.chan, keys_vals)

        update = { 'two': 'six', 'inside': 'upside-down' }
        self.rmt.metadata_update(self.chan, update)

        actual_upd = self.rmt.metadata_get(self.chan, list(update.keys()))
        self.assertCountEqual(update, actual_upd)

        actual_list_upd = self.rmt.metadata_list(self.chan)
        self.assertCountEqual(keys_vals, actual_list_upd)

        with self.assertRaises(HTTPErrorList):
            # Try updating a non-existent key.
            self.rmt.metadata_update(self.chan, {'foo': 'bar'})

        self.rmt.metadata_delete(self.chan, list(keys_vals.keys()))

        with self.assertRaises(HTTPErrorList):
            # Try getting keys that don't exist.
            self.rmt.metadata_get(self.chan, ['foo', 'bar'])

        actual_list_end = self.rmt.metadata_list(self.chan)
        self.assertEqual([], actual_list_end)


if __name__ == '__main__':
    unittest.main()
