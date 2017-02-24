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
from intern.resource.boss.resource import CoordinateFrameResource

class TestCoordFrameResource(unittest.TestCase):
    def setUp(self):
        self.cf = CoordinateFrameResource('frame')

    def test_not_valid_volume(self):
        self.assertFalse(self.cf.valid_volume())

    def test_get_route(self):
        self.assertEqual(
            '{}'.format(self.cf.name), self.cf.get_route())

    def test_get_list_route(self):
        self.assertEqual('', self.cf.get_list_route())

    def test_voxel_unit_setter(self):
        exp = 'millimeters'
        self.cf.voxel_unit = exp
        self.assertEqual(exp, self.cf.voxel_unit)

    def test_validate_voxel_units_nm(self):
        exp = 'nanometers'
        self.assertEqual(exp, self.cf.validate_voxel_units(exp))

    def test_validate_voxel_units_micro(self):
        exp = 'micrometers'
        self.assertEqual(exp, self.cf.validate_voxel_units(exp))

    def test_validate_voxel_units_mm(self):
        exp = 'millimeters'
        self.assertEqual(exp, self.cf.validate_voxel_units(exp))

    def test_validate_voxel_units_cm(self):
        exp = 'centimeters'
        self.assertEqual(exp, self.cf.validate_voxel_units(exp))

    def test_validate_voxel_units_bad(self):
        with self.assertRaises(ValueError):
            self.cf.validate_voxel_units('centimet')

