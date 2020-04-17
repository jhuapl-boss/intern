# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
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
from intern.resource.dvid.resource import DataInstanceResource

class TestDataInstanceResource(unittest.TestCase):
    def setUp(self):

        UUID = "822524777d3048b8bd520043f90c1d28"
        ALIAS = "grayscale"
        
        self.name = "some_data_instance"
        self.uuid = UUID
        self.alias = ALIAS

        self.data_instance_master = DataInstanceResource(self.name, UUID = self.uuid, datatype="uint8")

    def test_init_status_false(self):
        data_instance = DataInstanceResource(self.name, UUID = self.uuid)
        self.assertFalse(data_instance.cutout_ready)

    def test_channel_defaults_to_uint8(self):
        data_instance = DataInstanceResource(self.name, UUID = self.uuid)
        self.assertEqual('uint8', data_instance.datatype)

    def test_channel_defaults_to_uint8blk_type(self):
        data_instance = DataInstanceResource(self.name, UUID = self.uuid)
        self.assertEqual('uint8blk', data_instance._type)
    
    def test_setting_datatype_means_cutout_ready_at_construction(self):
        data_instance = DataInstanceResource(self.name, UUID = self.uuid, datatype="uint8")
        self.assertTrue(data_instance.cutout_ready)

    def test_setting_datatype_means_cutout_ready(self):
        data_instance = DataInstanceResource(self.name, UUID = self.uuid)

        # First check should be false. 
        self.assertFalse(data_instance.cutout_ready)

        #Set the datatype now
        data_instance.datatype = 'uint16'

        # Now we should be ready
        self.assertTrue(data_instance.cutout_ready)

    def test_valid_volume(self):
        self.assertTrue(self.data_instance_master.valid_volume())

    def test_validate_datatype_uint8(self):
        exp = 'uint8'
        self.assertEqual(exp, self.data_instance_master.validate_datatype(exp))

    def test_validate_datatype_uint16(self):
        exp = 'uint16'
        self.assertEqual(exp, self.data_instance_master.validate_datatype(exp))

    def test_validate_datatype_uint64(self):
        exp = 'uint64'
        self.assertEqual(exp, self.data_instance_master.validate_datatype(exp))

    def test_validate_datatype_bad(self):
        with self.assertRaises(ValueError):
            self.data_instance_master.validate_datatype('bigint')

    def test_validate_type_image(self):
        exp = 'image'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_imagetile(self):
        exp = 'imagetile'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_googlevoxels(self):
        exp = 'googlevoxels'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_keyvalue(self):
        exp = 'keyvalue'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_roi(self):
        exp = 'roi'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_uint8blk(self):
        exp = 'uint8blk'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_uint16blk(self):
        exp = 'uint16blk'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_uint64blk(self):
        exp = 'uint64blk'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_labelblk(self):
        exp = 'labelblk'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_labelvol(self):
        exp = 'labelvol'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_annotation(self):
        exp = 'annotation'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_labelgraph(self):
        exp = 'labelgraph'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_multichan16(self):
        exp = 'multichan16'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_validate_type_rgba8blk(self):
        exp = 'rgba8blk'
        self.assertEqual(exp, self.data_instance_master.validate_type(exp))

    def test_invalidate_type_notreal(self):
        exp = 'notreal'
        with self.assertRaises(ValueError):
            self.assertEqual(exp, self.data_instance_master.validate_type(exp))