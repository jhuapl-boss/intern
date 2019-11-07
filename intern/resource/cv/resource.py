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
from cloudvolume import CloudVolume

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
            **params () : keyword-value arguments for info object

        Returns:
            CloudVolume : cloudvolume instance with specified parameters 
        """
        Resource.__init__(self)
        if new_layer:
            info = CloudVolume.create_new_info(
                num_channels = params.get('num_channels', 1),
                layer_type = params.get('layer_type', None), # 'image' or 'segmentation'
                data_type = params.get('data_type', 'uint8'), # can pick any popular uint, defaults to unit8
                encoding = params.get('encoding', None), # other options: 'jpeg', 'compressed_segmentation' (req. uint32 or uint64)
                resolution = params.get('resolution', [1,1,1]), # X,Y,Z values in nanometers
                voxel_offset = params.get('voxel_offset', [0,0,0]), # offset in X,Y,Z voxels
                chunk_size = params.get('chunk_size', None), # rechunk of image X,Y,Z in voxels
                volume_size = params.get('volume_size', [1,1,1]) # X,Y,Z size in voxels
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

    def create_cutout(self, data, x_range, y_range, z_range):
        """
            Method to upload a cutout of data
            Args:
                data (str) : Path to the data
                vol (CloudVolume) : Existing cloudvolume instance 
                x_range (list) : x range within the 3D space
                y_range (list) : y range within the 3D space
                z_range (list) : z range witinn the 3D space
            Retruns:
                message (str) : Uploading Data... message
        """
        if x_range==[] and y_range==[] and z_range==[]:
            self.cloudvolume[:,:,:] = data
        else:
            self.cloudvolume[x_range[0]:x_range[1], y_range[0]:y_range[1], z_range[0]:z_range[1]] = data
        print("Data uploaded.")

    def get_cutout(self, x_range, y_range, z_range):
        """
            Method to download a cutout of data
            Args:
                vol (CloudVolume) : Existing non-empty cloudvolume instance 
                x_range (list) : x range within the 3D space
                y_range (list) : y range within the 3D space
                z_range (list) : z range within the 3D space
            Retruns:
                data (numpy array) : image stack from the cloud or local system
        """
        if x_range== [] and y_range== [] and z_range == []:
            data = self.cloudvolume[:,:,:]
        else:
            data = self.cloudvolume[x_range[0]:x_range[1], y_range[0]:y_range[1], z_range[0]:z_range[1]]
        return data
