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

from intern.service.service import Service
from enum import IntEnum
import numpy as np

class VoxelUnits(IntEnum):
    """Enum with valid VoxelUnits
    """
    nm = 1
    um = 1000
    mm = 1000000
    cm = 10000000
    nanometers = 1
    micrometers = 1000
    millimeters = 1000000
    centimeters = 10000000


class MeshService(Service):
    """ Partial implementation of intern.service.service.Service for the Meshing' services.
	"""

    def __init__(self):
        """Constructor
        """

        Service.__init__(self)

    def set_auth(self):
        """ No auth for Meshing
		"""
        self._auth = None

    def create(self, volume,
            x_range, y_range, z_range, time_range=None, 
            id_list=[], voxel_unit=VoxelUnits.nm, 
            voxel_size=[4,4,40], simp_fact=0, max_simplification_error=60,
            normals=False, **kwargs):
        """Generate a mesh of the specified IDs

        Args:
            volume ([array]): Numpy array volume.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            id_list (optional [list]): list of object ids to filter the volume by.
            voxel_unit (optional VoxelUnit): voxel unit of measurement to derive conversion factor. 
            voxel_size (optional [list]): list in form [x,y,z] of voxel size. Defaults to 4x4x40nm
            simp_fact (optional int): mesh simplification factor, reduces triangles by given factor
            max_simplification_error (optional int): Max tolerable error in physical distance
            normals (optional bool): if true will calculate normals

        Returns:
            (): Return type depends on volume service's implementation.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.

        """

        from zmesh import Mesher
        if np.unique(volume).shape[0] == 1:
            raise ValueError("The volume provided only has one unique ID (0). ID 0 is considered background.")

        conv_factor = self._get_conversion_factor(voxel_unit)
        
        # Get voxel_sizes
        x_voxel_size = float(voxel_size[0]) * conv_factor
        y_voxel_size = float(voxel_size[1]) * conv_factor
        z_voxel_size = float(voxel_size[2]) * conv_factor

        # Mesh
        mesher = Mesher((x_voxel_size,y_voxel_size,z_voxel_size))
        mesher.mesh(volume)

        # If the list is empty then just default to all ID's found in the volume
        if (id_list == []):
            id_list = mesher.ids()

        # Run the mesher on all specified ID's
        for oid in id_list:
            mesh = mesher.get_mesh(
                oid, 
                normals=normals, 
                simplification_factor=simp_fact,
                max_simplification_error= max_simplification_error,
                )
            mesh.vertices += [x_range[0]*conv_factor, y_range[0]*conv_factor, z_range[0]*conv_factor]

        return Mesh([volume, mesh])

    def _get_conversion_factor(self, voxel_unit):
        """
        Validate the voxel unit type and derive conversion factor from it if valid

        Arguments:
            voxel_unit (VoxelUnits): 'nanometers', 'millimeters', <etc>

        Returns:
            int: conversion factor to use by meshing service

        Raises:
            ValueError
        """
        if not isinstance(voxel_unit, VoxelUnits):
            raise ValueError("{} is not a valid voxel unit".format(voxel_unit))
        else:
            return voxel_unit.value

class Mesh:
    def __init__(self, data):
        """Constructor.

        Args:
            data (tuple[raw_volume, mesh]): tuple containing the raw data and the mesh data
        """
        self._raw_vol = data[0]
        self._mesh = data[1]

    def ng_mesh(self):
        """Convert mesh to precompute format for Neuroglancer visualization

        Args:
            mesh: mesh to convert.

        Returns:
            (): Returns mesh precompute format

        """
        return self._mesh.to_precomputed()
        
    def obj_mesh(self):
        """Convert mesh to obj

        Args:
            mesh: mesh to convert.

        Returns:
            (): Returns mesh obj format

        """
        return self._mesh.to_obj()
