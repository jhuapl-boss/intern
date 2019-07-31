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
from intern.resource.cv.resource import *
from intern.service.cv.service import *

LATEST_VERSION = 'v1'

class CloudVolumeRemote(Remote):
    def __init__(self, version=None):
        if version is None:
            version = LATEST_VERSION

    def cloudvolume(self, protocol, path, new_layer = True, **params):
    	"""
    	Creates a cloudvolume object

        Args:
            protocol (str) : protocol to use. Currently supports 'local', 'gs', and 's3'
            path (str) : in the form of "/$BUCKET/$DATASET/$LAYER"
			new_layer (bool): boolean indicating if new info file is needed
            **params () : keyword-value arguments for info object

        Returns:
            CloudVolume : cloudvolume instance with specified parameters 
        """
        return CloudVolumeResource(protocol, path, new_layer, **params)

    def create_cutout(self, cv, data, xrang= None, yrang = None, zrang = None):
    	"""
            Method to upload a cutout of data
            Args:
                data (str) : Path to the data
                vol (CloudVolume) : Existing cloudvolume instance 
                xrang (list) : x range within the 3D space
                yrang (list) : y range within the 3D space
                zrang (list) : z range witinn the 3D space
            Retruns:
                message (str) : Uploading Data... message
        """
        return cv.create_cutout(data, xrang, yrang, zrang)

    def get_cutout(self, cv, xrang = None, yrang = None, zrang = None):
    	"""
            Method to download a cutout of data
            Args:
                vol (CloudVolume) : Existing non-empty cloudvolume instance 
                xrang (list) : x range within the 3D space
                yrang (list) : y range within the 3D space
                zrang (list) : z range within the 3D space
            Retruns:
                data (numpy array) : image stack from the cloud or local system
        """
        return cv.get_cutout(data, xrang, yrang, zrang)

    def get_info(self, cv):
    	"""
		Returns a JSON of the resource properties.

		Args:
		resource (CloudVolumeResource object)

		Returns:
		string: JSON format of properties
		"""
        return CloudVolumeService.get_info(cv)

    def get_cloudpath(self, cv):
    	"""
		Returns a string of the cloudpath of the resource.

		Args:
		resource (CloudVolumeResource object)

		Returns:
		string: in the form of 'PROTOCOL//:BUCKET/../DATASET/LAYER'
		"""
        return CloudVolumeService.get_cloudpath(cv)

    def get_provenance(self, cv):
    	"""
		Returns the description and owners of the cloudvolume resource.

		Args:
		resource (CloudVolumeResource object)

		Returns:
		dict: desciption and owners values
		"""
        return CloudVolumeService.get_provenance(cv)

    def delete_data(self, cv, xrang, yrang, zrang):
    	"""
		Delete the chunks within a bounding box (must be aligned with chunks)

		Args:
		resource (CloudVolumeResource object)
		xrang,yrang,zrang (Tuples representing the bbox)
		"""
        return CloudVolumeService.deleta_data(cv)
