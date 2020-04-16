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
            protocol (str) : protocol to use. Currently supports 'local', 'gs', and 's3'
            cloudpath (str) : in the form of "$BUCKET/../$DATASET/$LAYER"
        """
        CloudVolumeService.__init__(self)
        self.protocol = protocol
        self.cloudpath = cloudpath

    def cloudvolume(self, mip, info, parallel, cache, **kwargs):
        """
        Creates cloud-volume resource

        Args:
            mip (int): which mip layer to access
            info (dict) : json-encodable dictionary of layer parameters. Necessary for creating a
                new cloudvolume instance.
            parallel (int: 1, bool): Number of extra processes to launch, 1 means only
                use the main process. If parallel is True use the number of CPUs
                returned by multiprocessing.cpu_count(). When parallel > 1, shared
                memory (Linux) or emulated shared memory via files (other platforms)
                is used by the underlying download.
            cache (bool or str) Store downs and uploads in a cache on disk
                and preferentially read from it before redownloading.
                - False: no caching will occur.
                - True: cache will be located in a standard location.
                - non-empty string: cache is located at this file path
            kwargs: optional arguments (https://github.com/seung-lab/cloud-volume#cloudvolume-constructor)

        Returns:
            CloudVolume Object
        """
        return CloudVolumeResource(
            self.protocol,
            self.cloudpath,
            mip=mip,
            info=info,
            parallel=parallel,
            cache=cache,
            **kwargs
        )

    def create_new_info(
        self,
        num_channels,
        layer_type,
        data_type,
        resolution,
        volume_size,
        voxel_offset=(0, 0, 0),
        encoding="raw",
        chunk_size=(64, 64, 64),
        mesh=None,
        skeletons=None,
        compressed_segmentation_block_size=(8, 8, 8),
        max_mip=0,
        factor=(2, 2, 1),
    ):
        """
        Creates the info JSON necessary for a new cloudvolume resource.
        Args:
            Required:
                num_channels: (int) 1 for grayscale, 3 for RGB
                layer_type: (str) typically "image" or "segmentation"
                data_type: (str) e.g. "uint8", "uint16", "uint32", "float32"
                resolution: int (x,y,z), x,y,z voxel dimensions in nanometers
                volume_size: int (x,y,z), extent of dataset in cartesian space from voxel_offset

            Optional:
                voxel_offset: int (x,y,z), beginning of dataset in positive cartesian space
                encoding: (str) "raw" for binaries like numpy arrays, "jpeg"
                mesh: (str) name of mesh directory, typically "mesh"
                skeletons: (str) name of skeletons directory, typically "skeletons"
                chunk_size: int (x,y,z), dimensions of each downloadable 3D image chunk in voxels
                compressed_segmentation_block_size: (x,y,z) dimensions of each compressed sub-block
                    (only used when encoding is 'compressed_segmentation')
                max_mip: (int), the maximum mip level id.
                factor: (tuple), the downsampling factor for each mip level

        Returns: dict representing a single mip level that's JSON encodable
        """
        return CloudVolume.create_new_info(
            num_channels,
            layer_type,
            data_type,
            encoding,
            resolution,
            voxel_offset,
            volume_size,
            mesh,
            skeletons,
            chunk_size,
            compressed_segmentation_block_size,
            max_mip,
            factor,
        )
