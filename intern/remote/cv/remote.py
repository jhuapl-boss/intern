"""
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
"""
from intern.remote import Remote
from intern.resource.cv.resource import CloudVolumeResource
from intern.service.cv.volume import VolumeService
from intern.service.cv.metadata import MetadataService
from intern.service.cv.project import ProjectService


class CloudVolumeRemote(Remote):
    def __init__(
        self,
        cfg_file_or_dict=None,
    ):
        """Constructor.
        Protocol and host specifications are taken in as keys -values of dictionary.

        Args:
            cfg_file_or_dict (optional[string|dict]): Path to config file in
                INI format or a dict of config parameters.
        """
        cfg_file_or_dict = cfg_file_or_dict or {}
        Remote.__init__(self, cfg_file_or_dict)
        self.protocol = self._config["Default"]["protocol"]
        self.cloudpath = self._config["Default"]["cloudpath"]
        # Init the services
        self._volume = VolumeService()
        self._metadata = MetadataService()
        self._project = ProjectService(self.protocol, self.cloudpath)

    def cloudvolume(self, mip=0, info=None, parallel=1, cache=False, **kwargs):
        """
        Args:
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
        return self._project.cloudvolume(mip, info, parallel, cache, **kwargs)

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
        Required:
            num_channels: (int) 1 for grayscale, 3 for RGB
            layer_type: (str) typically "image" or "segmentation"
            data_type: (str) e.g. "uint8", "uint16", "uint32", "float32"
            resolution: int (x,y,z), x,y,z voxel dimensions in nanometers
            volume_size: int (x,y,z), extent of dataset in cartesian space from voxel_offset

        Optional:
            voxel_offset: int (x,y,z), beginning of dataset in positive cartesian space
            encoding: (str) "raw" for binaries like numpy arrays, "jpeg", "png"
            mesh: (str) name of mesh directory, typically "mesh"
            skeletons: (str) name of skeletons directory, typically "skeletons"
            chunk_size: int (x,y,z), dimensions of each downloadable 3D image chunk in voxels
            compressed_segmentation_block_size: (x,y,z) dimensions of each compressed sub-block
                (only used when encoding is 'compressed_segmentation')
            max_mip: (int), the maximum mip level id.
            factor: (tuple), the downsampling factor for each mip level

        Returns: dict representing a single mip level that's JSON encodable
        """
        return self._project.create_new_info(
            num_channels,
            layer_type,
            data_type,
            resolution,
            volume_size,
            voxel_offset,
            encoding,
            chunk_size,
            mesh,
            skeletons,
            compressed_segmentation_block_size,
            max_mip,
            factor,
        )

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
        return self._volume.create_cutout(
            resource, res, x_range, y_range, z_range, data
        )

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
            (str): JSON format of properties
        """
        return self._metadata.get_info(resource)

    def get_cloudpath(self, resource):
        """
        Returns a string of the cloudpath of the resource.

        Args:
            resource (CloudVolumeResource object)

        Returns:
            (str): in the form of 'PROTOCOL://BUCKET/../DATASET/LAYER'
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

    def set_provenance(self, resource, **kwargs):
        """
        Sets the description and owners of the cloudvolume resource.

        Args:
            resource (CloudVolumeResource object)
            owners (list): list of authorship names and emails
            description (str): description of dataset

        Returns:
            None
        """
        return self._metadata.set_provenance(resource, **kwargs)

    def delete_data(self, resource, res, x_range, y_range, z_range):
        """
        Delete the chunks within a bounding box (must be aligned with chunks)

        Args:
            resource (CloudVolumeResource object)
            x_range,y_range,z_range (Tuples representing the bbox)
        Returns:
            None
        """
        return self._volume.delete_data(resource, res, x_range, y_range, z_range)

    def list_res(self, resource):
        """
        What resolution(s) are available to read and write to in the current resource.

        Args:
            resource (CloudVolume Resource Object)

        Returns:
            list: list of ints denoting mip levels
        """
        return self._metadata.list_res(resource)

    def get_layer(self, resource):
        """
        Which data layer (e.g. image, segmentation) on S3, GS, or FS you're reading and writing to.
        Known as a "channel" in BOSS terminology. Writing to this property triggers an info refresh.

        Args:
            resource (CloudVolume Resource Object)

        Returns:
            str: current resource channel
        """
        return self._metadata.get_layer(resource)

    def set_layer(self, resource, layer):
        """
        Set a new layer and commits it to the info file.

        Args:
            resource (CloudVolume Resource Object)
            layer (string)

        Returns:
            None
        """
        return self._metadata.set_layer(resource, layer)

    def get_dataset_name(self, resource):
        """
        Which dataset (e.g. test_v0, snemi3d_v0) on S3, GS, or FS you're reading and writing to.
        Known as an "experiment" in BOSS terminology. Writing to this property triggers an info refresh.

        Args:
            resource (CloudVolume Resource Object)

        Returns:
            str: current resource experiment
        """
        return self._metadata.get_dataset_name(resource)

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
        return self._metadata.set_dataset_name(resource, name)

    def get_extents(self, resource):
        """
        Gets extents to a specific cloudvolume resource
        Args:
            resource (CloudVolume Resource Object)
        Returns:
            extents (list): [[x-min, x-max], [y-min, y-max], [z-min, z-max]]
        """
        return self._metadata.get_extents(resource)
