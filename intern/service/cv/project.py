# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
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

from intern.service.cv.service import CloudVolumeService
from intern.service.cv.metadata import MetadataService
from intern.resource.cv.resource import CloudVolumeResource

from cloudvolume import CloudVolume, Vec

class ProjectService(CloudVolumeService):
    """
    ProjectService for cloudvolume service.
    """

    def __init__(self, protocol, cloudpath):
        """Constructor.
        Args:
            base_url (str): Base url to project service.
        """
        CloudVolumeService.__init__(self)
        self.protocol = protocol
        self.cloudpath = cloudpath

    def cloudvolume(self, **params):
        """
        Creates resource
        """
        return CloudVolumeResource(self.protocol, self.cloudpath, **params)

    def create_new_info(self, **params):
        """
        Creates the info JSON necessary for a new cloudvolume resource. 

        """
        return CloudVolume.create_new_info(
                num_channels = params.get('num_channels'), # (int) 1 for grayscale, 3 for RGB 
                layer_type = params.get('layer_type'), # (str)'image' or 'segmentation'
                data_type = params.get('data_type'), # (str) e.g. 'uint8', 'uint16', 'uint32', 'float32'
                encoding = params.get('encoding'), # (str) default is precomputed. other options: 'jpeg', 'compressed_segmentation' (req. uint32 or uint64)
                resolution = params.get('resolution'), # (x,y,z) X,Y,Z voxel dimensions in nanometers
                voxel_offset = params.get('voxel_offset', (0,0,0)), # (x,y,z) voxel offset
                volume_size = params.get('volume_size'), # (x,y,z) extent of dataset from voxel offset
                chunk_size = params.get('chunk_size', (64,64,64)), # rechunk of image X,Y,Z in voxels
                mesh = params.get('mesh'), # (str) name of mesh directory, typically "mesh"
                skeletons = params.get('skeletons'), # (str) name of skeletons directory, typically "skeletons"
                compressed_segmentation_block_size = params.get('compressed_segmentation_block_size', (8,8,8)), #dimensions of each compressed sub-block (only used when encoding is 'compressed_segmentation')
                max_mip = params.get('max_mip', 0), #(int)the maximum mip level id
                factor = params.get('factor', Vec(2,2,1)) # (Vec)the downsampling factor for each mip level
            )