from intern.service.mesh.service import MeshService
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
        voxel_unit = "nanometers"
        voxel_conv = 1
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "micrometers"
        voxel_conv = 1000
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "millimeters"
        voxel_conv = 1000000
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "centimeters"
        voxel_conv = 10000000
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "nm"
        voxel_conv = 1
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "um"
        voxel_conv = 1000
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "mm"
        voxel_conv = 1000000
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))
        voxel_unit = "cm"
        voxel_conv = 10000000
        self.assertEqual(voxel_conv, self.mesh.validate_voxel_unit(voxel_unit))