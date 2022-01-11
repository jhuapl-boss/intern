# Copyright 2020-2022 The Johns Hopkins University Applied Physics Laboratory
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

import numpy as np


class VolumeService(CloudVolumeService):
    """
    VolumeService for cloudvolume service.
    """

    def __init__(self):
        """Constructor.

        Args:
            base_url (str): Base url (host) of project service.

        Raises:
            (KeyError): if given invalid version.
        """
        CloudVolumeService.__init__(self)

    def create_cutout(self, resource, res, x_range, y_range, z_range, data):
        """
        Method to upload a cutout of data
        Args:
            data (str) : Path to the data
            vol (CloudVolume) : Existing cloudvolume instance
            x_range (list) : x range within the 3D space
            y_range (list) : y range within the 3D space
            z_range (list) : z range witinn the 3D space
        Retruns:
            None
        """
        resource.cloudvolume.mip = res
        resource.cloudvolume[
            x_range[0] : x_range[1], y_range[0] : y_range[1], z_range[0] : z_range[1]
        ] = data

    def get_cutout(self, resource, res, x_range, y_range, z_range):
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
        resource.cloudvolume.mip = res
        data = resource.cloudvolume[
            x_range[0] : x_range[1], y_range[0] : y_range[1], z_range[0] : z_range[1]
        ]

        # Remove channel dimension if num_channel = 1
        data = np.squeeze(data)
        return data

    def delete_data(self, resource, res, x_range, y_range, z_range):
        """
        Delete the chunks within a bounding box (must be aligned with chunks)

        Args:
            resource (CloudVolumeResource object)
            x_range,y_range,z_range (Tuples representing the bbox)
        Returns:
            None
        """
        resource.cloudvolume.mip = res
        x1, x2 = x_range
        y1, y2 = y_range
        z1, z2 = z_range
        resource.cloudvolume.delete(np.s_[x1:x2, y1:y2, z1:z2])
