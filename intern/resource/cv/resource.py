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

from intern.resource import Resource
from cloudvolume import CloudVolume, Vec

import numpy as np
from os import path

class CloudVolumeResource(Resource):

    """
    Base class for CloudVolume resources.
    """

    def __init__(self, protocol, cloudpath, **params):
        """
        Initializes intern.Resource parent class and creates a cloudvolume object

        Args:
            protocol (str) : protocol to use. Currently supports 'local', 'gs', and 's3'
            cloudpath (str) : in the form of "$BUCKET/$DATASET/$LAYER"
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
        
        protocol_map = {
            'local':'file://', 
            'gcp': 'gs://', 
            's3':'s3://',
            'boss':'boss://'
            }
        try:
            protokey = protocol_map[protocol]
        except KeyError:
            raise KeyError("{} is not a valid protocol. Supported protocols: 'local', 'gcp',  and 's3'".format(protocol))
        
        self.url = protokey+cloudpath
        self.mip = params.get('mip', 0)
        self.parallel = params.get('parallel', 1)
        self.info = params.get('info')
        
        if self.info == None:
            # Layer already exists 
            self.cloudvolume = CloudVolume(self.url, mip=self.mip, parallel=self.parallel)
        else:
            # Info file provided by user
            self.cloudvolume = CloudVolume(self.url, mip=self.mip, info=self.info, parallel=self.parallel)
            self.cloudvolume.commit_info() # generates protocol://bucket/dataset/layer/info json file

    def valid_volume(self):
        """Returns True if resource is something that can access the volume service.
        Args:
        Returns:
            (bool) : True if calls to volume service may be made.
        """
        return True

