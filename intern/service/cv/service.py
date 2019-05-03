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
		"""
		return resource.cloudvolume.info

	@classmethod
	def get_cloudpath(self, resource):
		"""
		Returns a string of the cloudpath of the resource.

		PROTOCOL//:BUCKET/../DATASET/LAYER
		"""
		return resource.cloudvolume.layer_cloudpath 
