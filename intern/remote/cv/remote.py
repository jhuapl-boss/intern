"""
# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
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
"""
from intern.remote import Remote
from intern.resource.cv.resource import CloudVolumeResource
from intern.service.cv.volume import VolumeService
from intern.service.cv.metadata import MetadataService
from intern.service.cv.project import ProjectService


class CloudVolumeRemote(Remote):
    
    def __init__(self, cfg_file_or_dict=None,):
        """Constructor.
        Protocol and host specifications are taken in as keys -values of dictionary.
        """
        Remote.__init__(self, cfg_file_or_dict)
        self.protocol = self._config['Default']['protocol']
        self.cloudpath = self._config['Default']['cloudpath']
        # Init the services
        self._volume = VolumeService()
        self._metadata = MetadataService()
        self._project = ProjectService(self.protocol, self.cloudpath)
    
    def cloudvolume(self, **params):
        return self._project.cloudvolume(**params)
    
    def create_new_info(self, **params):
        return self._project.create_new_info(**params)

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
                message (str) : Uploading Data... message
        """
        return self._volume.create_cutout(resource, res, x_range, y_range, z_range, data)

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
        return self._volume.get_cutout(resource, res, x_range, y_range, z_range)

    def get_info(self, resource):
        """
        Returns a JSON of the resource properties.

        Args:
        resource (CloudVolumeResource object)

        Returns:
        string: JSON format of properties
        """
        return self._metadata.get_info(resource)

    def get_cloudpath(self, resource):
        """
        Returns a string of the cloudpath of the resource.

        Args:
        resource (CloudVolumeResource object)

        Returns:
        string: in the form of 'PROTOCOL//:BUCKET/../DATASET/LAYER'
        """
        return self._metadata.get_cloudpath(resource)

    def get_provenance(self, resource):
        """
        Returns the description and owners of the cloudvolume resource.

        Args:
        resource (CloudVolumeResource object)

        Returns:
        dict: desciption and owners values
        """
        return self._metadata.get_provenance(resource)

    def delete_data(self, resource, x_range, y_range, z_range):
        """
        Delete the chunks within a bounding box (must be aligned with chunks)

        Args:
        resource (CloudVolumeResource object)
        x_range,y_range,z_range (Tuples representing the bbox)
        """
        return self._volume.delete_data(resource, x_range, y_range, z_range)

    def which_res(self, resource):
        """
        What resolution(s) are available to read and write to in the current resource. 

        Args:
        resource (CloudVolume Resource Object)

        Returns: (list) list of ints denoting mip levels
        """
        return self._metadata.which_res(resource)

    def get_channel(self, resource, channel = None):
        """
        Which data layer (e.g. image, segmentation) on S3, GS, or FS you're reading and writing to. 
        Known as a "channel" in BOSS terminology. Writing to this property triggers an info refresh.
        
        Args:
        resource (CloudVolume Resource Object)
        channel (str): can be 'image' or 'segmentation'

        Returns:
        str: current resource channel
        """ 
        return self._metadata.get_channel(resource, channel)

    def get_experiment(self, resource, experiment = None):
        """
        Which dataset (e.g. test_v0, snemi3d_v0) on S3, GS, or FS you're reading and writing to. 
        Known as an "experiment" in BOSS terminology. Writing to this property triggers an info refresh.
        
        Args: 
        resource (CloudVolume Resource Object)
        experiment (str): experiment name 

        Returns:
        str: current resource experiment
        """
        return self._metadata.get_experiment(resource, experiment)
