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

from intern.service.service import Service
from cloudvolume import CloudVolume

import numpy as np

class CloudVolumeService(Service):

	"""
		Partial implementation of intern.service.service.Service for the CloudVolume services.
	"""

	def __init__(self):
		Service.__init__(self)

	@classmethod
	def get_info(self, resource):
		"""
		Returns a JSON of the resource properties.

		Args:
		resource (CloudVolumeResource object)

		Returns:
		string: JSON format of properties
		"""
		return resource.cloudvolume.info

	@classmethod
	def get_cloudpath(self, resource):
		"""
		Returns a string of the cloudpath of the resource.

		Args:
		resource (CloudVolumeResource object)

		Returns:
		string: in the form of 'PROTOCOL//:BUCKET/../DATASET/LAYER'
		"""
		return resource.cloudvolume.layer_cloudpath

	@classmethod
	def get_provenance(self, resource):
		"""
		Returns the description and owners of the cloudvolume resource.

		Args:
		resource (CloudVolumeResource object)

		Returns:
		dict: desciption and owners values
		"""
		return resource.cloudvolume.refresh_provenance()

	@classmethod
	def _chunks_exist(self, resource, x_range, y_range, z_range):
		"""
		Get a report on which chunks actually exist.

		Args:
		resource (CloudVolumeResource object)
		x_range,y_range,z_range (Tuples representing the bbox)

		Returns: {chunk_file_name: boolean, ...}

		"""
		x1,x2 = x_range
		y1,y2 = y_range
		z1,z2 = z_range
		return resource.cloudvolume.exists( np.s_[x1:x2, y1:y2, z1:z2] ) 

	@classmethod 
	def delete_data(self, resource, x_range, y_range, z_range):
		"""
		Delete the chunks within a bounding box (must be aligned with chunks)

		Args:
		resource (CloudVolumeResource object)
		x_range,y_range,z_range (Tuples representing the bbox)
		"""
		x1,x2 = x_range
		y1,y2 = y_range
		z1,z2 = z_range
		resource.cloudvolume.delete( np.s_[x1:x2, y1:y2, z1:z2] )
		print('Files successfully deleted')

	@classmethod
	def which_res(self, resource):
		"""
		What resolution(s) are available to read and write to in the current resource. 

		Args:
		resource (CloudVolume Resource Object)

		Returns: (list) list of ints denoting mip levels
		"""
		return resource.cloudvolume.mip

	@classmethod
	def get_channel(self, resource, channel):
		"""
		Which data layer (e.g. image, segmentation) on S3, GS, or FS you're reading and writing to. 
		Known as a "channel" in BOSS terminology. Writing to this property triggers an info refresh.
		
		Args:
		resource (CloudVolume Resource Object)
		channel (str): can be 'image' or 'segmentation'

		Returns:
		str: the resource channel 

		"""	

		if channel == None:
			return resource.cloudvolume.layer
		else:
			if channel not in ['image', 'segmentation']:
				raise ValueError('{} is not a valid layer'.format(channel))
			else:
				resource.layer = channel
				return resource.cloudvolume.layer

	@classmethod
	def get_experiment(self, resource, experiment):
		"""
		Which dataset (e.g. test_v0, snemi3d_v0) on S3, GS, or FS you're reading and writing to. 
		Known as an "experiment" in BOSS terminology. Writing to this property triggers an info refresh.
		
		Args: 
		resource (CloudVolume Resource Object)
		experiment (str): experiment name 

		Returns:
		str: current resource experiment
		"""
		if experiment == None:
			return resource.cloudvolume.dataset_name
		else:
			resource.dataset_name = experiment
			return resource.cloudvolume.dataset_name


