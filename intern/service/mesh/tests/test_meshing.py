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

from intern.service.mesh.service import MeshService
from intern.service.mesh.service import VoxelUnits
import numpy
import unittest
from mock import patch, ANY
import mock


class TestMesh(unittest.TestCase):
    def setUp(self):

        self.mesh = MeshService()
        self._mesh_id = 2

        self.volume = numpy.random.randint(0, 2, (10, 200, 150), numpy.uint64)
        self.x_rng = [4500, 5500]
        self.y_rng = [3600, 4600]
        self.z_rng = [0, 162] 

    def test_invalid_voxel_unit(self):
        voxel_unit = "something_wrong"
        with self.assertRaises(ValueError):
            self.mesh.create(self.volume, self.x_rng, self.y_rng, self.z_rng, voxel_unit=voxel_unit)
 
    def test_valid_voxel_units(self):
        voxel_unit = VoxelUnits.nanometers
        voxel_conv = 1
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.micrometers
        voxel_conv = 1000
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.millimeters
        voxel_conv = 1000000
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.centimeters
        voxel_conv = 10000000
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.nm
        voxel_conv = 1
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.um
        voxel_conv = 1000
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.mm
        voxel_conv = 1000000
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))
        voxel_unit = VoxelUnits.cm
        voxel_conv = 10000000
        self.assertEqual(voxel_conv, self.mesh._get_conversion_factor(voxel_unit))