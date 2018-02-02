"""
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
"""
from intern.remote import Remote
from intern.resource.localFile.resource import *
from intern.service.localFile.metadata import MetadataService
import os.path

LATEST_VERSION = 'v0'
CONFIG_HOST = "host"
CONFIG_DATASTORE = "datastore"
filePath = ""
datastore = ""


class LocalRemote(Remote):

	def __init__(self, specs, version=None):
		"""
			Constructor:
			Checks for latest version. If no version is given, assigns version as none
			Protocol and host specifications are taken in as keys -values of dictionary.
			global hos and datastore values are assigned.
		"""

		if version is None:
			version = LATEST_VERSION

		host = specs[CONFIG_HOST]
		datastore = specs[CONFIG_DATASTORE]

		global filePath
		filePath = str(host)

		global datastore
		if os.path.isfile(filePath + datastore + ".hdf5") == True:
			datastore = h5py.File(filePath + datastore + ".hdf5")
		else:
			datastore = LocalResource.create_LocalFile(filePath,datastore)
			print("Your data store did not exist, so we created one.")

	def get_cutout(self, channelRes, res, xspan, yspan, zspan):
		"""
			Method to request a volume of data from local server

			Args:
				channelRes (string) : hiererchal path of where the data is located
				res (int) : data resolution
				xspan (int) : range of pixels in x axis ([1000:1500])
				yspan (int) : range of pixels in y axis ([1000:1500])
				zspan (int) : range of pixels in z axis ([1000:1010])

			Returns:
				array: numpy array representation of the requested volume

			Raises:
				(KeyError): if given invalid version.
		"""
		return LocalResource.get_cutout(datastore, channelRes, res, xspan, yspan, zspan)

	def get_channel(self, collection,channel,experiment=''):
		"""
			Method to reques specific collection/channel/experiment where the data is located

			Args:
				collection (string) : name of collection
				channel (string) : name of channel
				experiment (string) : name of experiement (actual dataset)

			Returns:
				channelSource (string) : amalgamation of all three parameters into a single path string

			Raises:
				(KeyError): if given invalid version
		"""
		return LocalResource.get_channel(collection,channel,experiment)

	def create_collection(self, groupName):
		"""
			Method to create a group space within local HDF5 datastore

			Args:
				groupName (string) : Desired name of the group which will be categorized 'collection'

			Raises:
				(KeyError): if given invalid version.
		"""
		return LocalResource.create_collection(datastore, groupName)

	def create_channel(self, groupName, subGroup):
		"""
			Method to create a sub-group space within local HDF5 datastore

			Args:
				groupName (string) : name of the group (collection) this sub-group (channel) will be created in
				subGroup (string) : Desired name of the sub-group which will be categorized as the channel

			Raises:
				(KeyError): if given invalid version.
		"""
		return LocalResource.create_channel(groupName, subGroup)

	def create_project(self, chan_setup):
		"""
			Method to reques specific collection/channel/experiment where the data is located

			Args:
				collection (string) : name of collection
				channel (string) : name of channel
				experiment (string) : name of experiement (actual dataset)

			Returns:
				channelSource (string) : amalgamation of all three parameters into a single path string

			Raises:
				(KeyError): if given invalid version
		"""

		return LocalResource.create_project(datastore,chan_setup)

	def create_cutout(self, subGroup, arrayName, dataArray):
		"""
			Method to create a dataset within local HDF5 datastore

			Args:
				subGroup (string) : name of the channel (sub-group) in which the data will be saved
				arrayName (string) : name of the data
				dataArray (array) : N-Dimensional array which is to be saved

			Raises:
				(KeyError): if given invalid version.
		"""
		return LocalResource.create_cutout(subGroup, arrayName, dataArray)

	def retrieve(self, path):
		"""
			Method to retrieve a specific file. Aimed at developer for quick file access

			Args:
				path (string): desired path to the HDF5 group created

			Raises:
				(KeyError): if given invalid version.
		"""
		return LocalResource.retrieve(datastore,path)

	def list(self):
		"""
			Method to retrieve a tree of hirerchy within datastore.

			Returns:
				printname (string) : list of all possible collections, channels and experiments
									 created in the current datastore

			Raises:
				(KeyError): if given invalid version.
		"""
		return LocalResource.list(datastore)

	def create_metadata(self, resource, keys_vals):

		"""
		Create the given key-value pairs for the given resource.

		Will attempt to create all key-value pairs even if a failure is encountered.

		Args:
			resource (intern.resource.boss.BossResource): List keys associated with this resource.
			keys_vals (dictionary): The metadata to associate with the resource.

		Raises:
			HTTPErrorList on failure.
			"""
		return MetadataService.create(resource,keys_vals)

	def get_metadata(self, resource, keys):

		"""
			Get metadata key-value pairs associated with the given resource.

			Args:
				resource (intern.resource.boss.BossResource): Get key-value pairs associated with this resource.
				keys (list): Keys to retrieve.

			Returns:
				(dictionary): The requested metadata for the given resource.

			Raises:
				HTTPErrorList on failure.
		"""
		return MetadataService.get(resource,keys)

	def update_metadata(self, resource, keys_vals):

		"""
			Update the given key-value pairs for the given resource.

			Keys must already exist before they may be updated.  Will attempt to
			update all key-value pairs even if a failure is encountered.

			Args:
				resource (intern.resource.boss.BossResource): Update values associated with this resource.
				keys_vals (dictionary): The metadata to update for the resource.

			Raises:
				HTTPErrorList on failure.
		"""

		return MetadataService.update(resource,keys_vals)

	def delete_metadata(self, resource, keys):

		"""
			Delete metadata key-value pairs associated with the given resource.

			Will attempt to delete all given key-value pairs even if a failure
			occurs.

			Args:
				resource (intern.resource.boss.BossResource): Delete key-value pairs associated with this resource.
				keys (list): Keys to delete.

			Raises:
				HTTPErrorList on failure.
		"""

		return MetadataService.delete(resource,keys)

	@classmethod
	def list_metadata(self,resource):
		"""
			Method to retrieve a tree of hirerchy within datastore.

			Args:
				resource (string): name of the resource of which metadata attributes will be listed

			Returns:
				printname (string) : list of all possible collections, channels and experiments
									 created in the current datastore

			Raises:
				(KeyError): if given invalid version.
		"""
		return MetadataService.list(resource)
