# Copyright 2017 The Johns Hopkins University Applied Physics Laboratory
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

from intern.resource import Resource
from cloudvolume import CloudVolume, Vec

import numpy as np
from os import path

class CloudVolumeResource(Resource):

    """
    Base class for CloudVolume resources.
    """

    def __init__(self, protocol, path, new_layer, parallel, **params):
        """
        Initializes intern.Resource parent class and creates a cloudvolume object

        Args:
            protocol (str) : protocol to use. Currently supports 'local', 'gs', and 's3'
            path (str) : in the form of "/$BUCKET/$DATASET/$LAYER"
            new_layer (bool): True indicates a new info file and therefore a new layer, is needed
            parallel (int: 1, bool): Number of extra processes to launch, 1 means only 
                    use the main process. If parallel is True use the number of CPUs 
                    returned by multiprocessing.cpu_count(). When parallel > 1, shared
                    memory (Linux) or emulated shared memory via files (other platforms) 
                    is used by the underlying download.
            **params () : keyword-value arguments for info object --> dict representing single mip level thats JSON encodable 

        Returns:
            CloudVolume : cloudvolume instance with specified parameters 
        """
        Resource.__init__(self)
        if new_layer:
            info = CloudVolume.create_new_info(
                num_channels = params.get('num_channels'), # (int) 1 for grayscale, 3 for RGB 
                layer_type = params.get('layer_type'), # (str)'image' or 'segmentation'
                data_type = params.get('data_type'), # (str) e.g. 'uint8', 'uint16', 'uint32', 'float32'
                encoding = params.get('encoding'), # (str) other options: 'jpeg', 'compressed_segmentation' (req. uint32 or uint64)
                resolution = params.get('resolution'), # (x,y,z) X,Y,Z voxel dimensions in nanometers
                voxel_offset = params.get('voxel_offset'), # (x,y,z) voxel offset
                volume_size = params.get('volume_size'), # (x,y,z) extent of dataset from voxel offset
                chunk_size = params.get('chunk_size', (64,64,64)), # rechunk of image X,Y,Z in voxels
                mesh = params.get('mesh'), # (str) name of mesh directory, typically "mesh"
                skeletons = params.get('skeletons'), # (str) name of skeletons directory, typically "skeletons"
                compressed_segmentation_block_size = params.get('compressed_segmentation_block_size', (8,8,8)), #dimensions of each compressed sub-block (only used when encoding is 'compressed_segmentation')
                max_mip = params.get('max_mip', 0), #(int)the maximum mip level id
                factor = params.get('factor', Vec(2,2,1)), # (Vec)the downsampling factor for each mip level
                redirect = params.get('redirect') #(str)If this volume has moved, you can set an automatic redirect by specifying a cloudpath here.
            )
            owners = params.get('owners', []) # list of contact email addresses
            description = params.get('description', 'No description provided')
            
        else:
            info = None
        if protocol == 'local':
            vol = CloudVolume('file://' + path, mip = params.get('mip', 0), info = info, parallel = parallel)

        elif protocol == 'gs':
            vol = CloudVolume('gs:/' + path, mip = params.get('mip', 0), info = info, parallel = parallel)
            
        elif protocol == 's3':
            vol = CloudVolume('s3:/' + path, mip = params.get('mip', 0), info = info, parallel = parallel)
            
        else:
            raise Exception("{} is not a valid protocol. Supported protocols: 'local', 'gs', 's3'".format(protocol))

        vol.provenance.description = description
        vol.provenance.owners = owners
        vol.commit_provenance() # generates protocol://bucket/dataset/layer/provenance json file
        vol.commit_info() # generates protocol://bucket/dataset/layer/info json file
        self.cloudvolume = vol

    def valid_volume(self):
        """Returns True if resource is something that can access the volume service.
        Args:
        Returns:
            (bool) : True if calls to volume service may be made.
        """
        return True
