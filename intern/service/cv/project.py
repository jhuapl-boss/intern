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

from intern.service.cv.service import CloudVolumeService
from intern.service.cv.metadata import MetadataService
from intern.resource.cv.resource import CloudVolumeResource

from cloudvolume import CloudVolume, Vec

class ProjectService(CloudVolumeService):
    """
    ProjectService for cloudvolume service.
    """

    def __init__(self, protocol, cloudpath):
        """
        Constructor.
        Args:
            base_url (str): Base url to project service.
        """
        CloudVolumeService.__init__(self)
        self.protocol = protocol
        self.cloudpath = cloudpath

    def cloudvolume(self, mip, info, parallel, cache, **kwargs):
        """
        Creates cloud-volume resource

        Arguments
        Returns
        """
        return CloudVolumeResource(self.protocol, self.cloudpath, mip = mip,
        info = info, parallel = parallel, cache = cache, **kwargs)
    
    def create_new_info(self, num_channels, layer_type, data_type, encoding, resolution, voxel_offset, 
        volume_size, chunk_size, mesh, skeletons, compressed_segmentation_block_size, max_mip, factor):
        """
        Creates the info JSON necessary for a new cloudvolume resource. 
        Required:
            num_channels: (int) 1 for grayscale, 3 for RGB 
            layer_type: (str) typically "image" or "segmentation"
            data_type: (str) e.g. "uint8", "uint16", "uint32", "float32"
            encoding: (str) "raw" for binaries like numpy arrays, "jpeg"
            resolution: int (x,y,z), x,y,z voxel dimensions in nanometers
            voxel_offset: int (x,y,z), beginning of dataset in positive cartesian space
            volume_size: int (x,y,z), extent of dataset in cartesian space from voxel_offset
            
        Optional:
            mesh: (str) name of mesh directory, typically "mesh"
            skeletons: (str) name of skeletons directory, typically "skeletons"
            chunk_size: int (x,y,z), dimensions of each downloadable 3D image chunk in voxels
            compressed_segmentation_block_size: (x,y,z) dimensions of each compressed sub-block
                (only used when encoding is 'compressed_segmentation')
            max_mip: (int), the maximum mip level id.
            factor: (tuple), the downsampling factor for each mip level
        
        Returns: dict representing a single mip level that's JSON encodable
        """
        factor = Vec(*factor)
        return CloudVolume.create_new_info(num_channels, layer_type, data_type, encoding, resolution, voxel_offset, volume_size,
            mesh, skeletons, chunk_size, compressed_segmentation_block_size, max_mip, factor)
