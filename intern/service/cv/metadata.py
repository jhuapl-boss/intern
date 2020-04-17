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

from intern.service.cv import CloudVolumeService
from intern.resource.cv.resource import *
import json
import numpy as np


class MetadataService(CloudVolumeService):
    """
    MetadataService for cloud-volume service.
    """

    def __init__(self):
        """
        Constructor.
        """
        CloudVolumeService.__init__(self)

    def get_info(self, resource):
        """
        Returns a JSON of the resource properties.

        Args:
            resource (CloudVolumeResource object)

        Returns:
            (str): JSON format of properties
        """
        return resource.cloudvolume.info

    def get_cloudpath(self, resource):
        """
        Returns a string of the cloudpath of the resource.

        Args:
            resource (CloudVolumeResource object)

        Returns:
            (str): in the form of 'PROTOCOL://BUCKET/../DATASET/LAYER'
        """
        return resource.cloudvolume.layer_cloudpath

    def set_provenance(self, resource, **kwargs):
        """
        Sets the description and owners of the cloudvolume resource.

        Args:
            resource (CloudVolumeResource object)

            key-word arguments for:
                owners (list): list of authorship names and emails
                description (str): description of dataset
                sources (list): list of data source
                processing (list of dicts): any previous processing done on data
                    e.g [{ 'method': 'meshing', 'by': 'example2@princeton.edu', 'description': '512x512x512 mip 3 simplification factor 30' }]

        Returns:
            None
        """
        for arg in kwargs.keys():
            if (
                arg in ["owners", "description", "sources", "processing"]
                and kwargs.get(arg) is not None
            ):
                resource.cloudvolume.provenance[arg] = kwargs.get(arg)
        resource.cloudvolume.commit_provenance()

    def get_provenance(self, resource):
        """
        Returns the description and owners of the cloudvolume resource.

        Args:
            resource (CloudVolumeResource object)

        Returns:
            dict: desciption and owners values
        """
        return resource.cloudvolume.refresh_provenance()

    def _chunks_exist(self, resource, x_range, y_range, z_range):
        """
        Get a report on which chunks actually exist.

        Args:
            resource (CloudVolumeResource object)
            x_range,y_range,z_range (Tuples representing the bbox)

        Returns:
            dict: {chunk_file_name: boolean, ...}

        """
        x1, x2 = x_range
        y1, y2 = y_range
        z1, z2 = z_range
        return resource.cloudvolume.exists(np.s_[x1:x2, y1:y2, z1:z2])

    def list_res(self, resource):
        """
        What resolution(s) are available to read and write to in the current resource.

        Args:
            resource (CloudVolume Resource Object)

        Returns:
            (list) list of ints denoting mip levels
        """
        return resource.cloudvolume.available_mips

    def get_layer(self, resource):
        """
        Which data layer (e.g. image, segmentation) on S3, GS, or FS you're reading and writing to.
        Known as a "channel" in BOSS terminology.

        Args:
            resource (CloudVolume Resource Object)

        Returns:
            str: the resource channel

        """
        return resource.cloudvolume.layer

    def set_layer(self, resource, layer):
        """
        Set a new layer and commits it to the info file.

        Args:
            resource (CloudVolume Resource Object)
            layer (string)

        Returns:
            None
        """
        resource.cloudvolume.layer = str(layer)

    def get_dataset_name(self, resource):
        """
        Which dataset (e.g. test_v0, snemi3d_v0) on S3, GS, or FS you're reading and writing to.
        Known as an "experiment" in BOSS terminology. Writing to this property triggers an info refresh.

        Args:
            resource (CloudVolume Resource Object)

        Returns:
            str: current resource experiment
        """
        return resource.cloudvolume.dataset_name

    def set_dataset_name(self, resource, name):
        """
        Which dataset (e.g. test_v0, snemi3d_v0) on S3, GS, or FS you're reading and writing to.
        Known as an "experiment" in BOSS terminology. Writing to this property triggers an info refresh.

        Args:
            resource (CloudVolume Resource Object)
            name (str): dataset name

        Returns:
            None
        """
        resource.cloudvolume.dataset_name = str(name)

    def get_extents(self, resource):
        """
        Gets extents to a specific cloudvolume resource
        Args:
            resource : cloudvolume resource to which to relate metadata
        Returns:
             extents (list): [[x-min, x-max], [y-min, y-max], [z-min, z-max]]
        """
        info_json = json.loads(resource.cloudvolume.info)
        min_point = info_json["voxel_offset"]
        max_point = info_json["volume_size"]
        extents = [
            [min_point[0], max_point[0]],
            [min_point[1], max_point[1]],
            [min_point[2], max_point[2]],
        ]
        return extents
