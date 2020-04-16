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

    def __init__(self, protocol, cloudpath, mip, info, parallel, cache, **kwargs):
        """
        Initializes intern.Resource parent class and creates a cloudvolume object

        Args:
            protocol (str) : protocol to use. Currently supports 'local', 'gs', and 's3'
            cloudpath (str) : in the form of "$BUCKET/../$DATASET/$LAYER"
            info (dict) : json-encodable dictionary of layer parameters. Necessary for creating a
                new cloudvolume instance.
            mip (int): which mip layer to access
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
            CloudVolume : cloudvolume instance with specified parameters
        """
        Resource.__init__(self)

        protocol_map = {
            "local": "file://",
            "gcp": "gs://",
            "s3": "s3://",
        }
        try:
            protokey = protocol_map[protocol]
        except KeyError:
            raise KeyError(
                "{} is not a valid protocol. Supported protocols: 'local', 'gcp',  and 's3'".format(
                    protocol
                )
            )

        self.url = protokey + cloudpath
        self.cloudvolume = CloudVolume(
            self.url, mip=mip, info=info, parallel=parallel, cache=cache, **kwargs
        )

        if info is not None:
            self.cloudvolume.commit_info()

    def valid_volume(self):
        """Returns True if resource is something that can access the volume service.
        Args:
        Returns:
            (bool) : True if calls to volume service may be made.
        """
        return True
