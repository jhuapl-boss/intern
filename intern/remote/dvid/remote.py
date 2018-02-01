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
from intern.resource.dvid.resource import *
from intern.service.dvid.service import *

LATEST_VERSION = 'v0'
CONFIG_PROTOCOL = 'protocol'
CONFIG_HOST = 'host'
api = ""


class DVIDRemote(Remote):

	def __init__(self, specs, version=None):
		"""
			Constructor.

			Checks for latest version. If no version is given, assigns version as none
			Protocol and host specifications are taken in as keys -values of dictionary.
			global api variable is named and used for every command that requires api.
		"""

		if version is None:
			version = LATEST_VERSION

		protocol = specs[CONFIG_HOST]
		host = specs[CONFIG_PROTOCOL]


		global api
		api = host + "://" + protocol


	def get_UUID(self, ID, repos):
		"""
			Method to obtain requested channel

			Args:
				ID (string): UUID assigned to DVID repository
				repos (string): name of the repository assigned by the user when instance was created

			Returns:
				(String touple)

			Raises:
				(KeyError): if given invalid version.
		"""
		return DvidResource.get_UUID(ID,repos)

	def get_channel(self, UUID, coll, exp = ""):
		"""
            Method to input all channel hierarchy requirememnts, works as a dummy
            for BossRemote Parallelism.

            Args:
                UUID (str) : Root UUID of the repository
                col (str) : Name of collection
                exp (str) : Name of experiment

            Returns:
                chan (str) : String of UUID/col/exp
		"""
		return DvidResource.get_channel(UUID,coll,exp)

	def get_cutout(self, chan, res, xspan, yspan, zspan):
		"""
			Method to request a volume of data from dvid server uploaded through command window

			Args:
				IDrepos (string) : UUID assigned to DVID repository and repository name
				xspan (int) : range of pixels in x axis ([1000:1500])
				yspan (int) : range of pixels in y axis ([1000:1500])
				zspan (int) : range of pixels in z axis ([1000:1010])

			Returns:
				array: numpy array representation of the requested volume

			Raises:
				(KeyError): if given invalid version.
		"""
		return DvidResource.get_cutout(api, chan, res, xspan, yspan, zspan)

	def get_cutoutI(self, chan, res, xspan, yspan, zspan):
		"""
			Method to request a volume of data from dvid server of data uploaded by intern

			Args:
				IDrepos (string) : UUID assigned to DVID repository and repository name
				xspan (int) : range of pixels in x axis ([1000:1500])
				yspan (int) : range of pixels in y axis ([1000:1500])
				zspan (int) : range of pixels in z axis ([1000:1010])

			Returns:
				array: numpy array representation of the requested volume

			Raises:
				(KeyError): if given invalid version.
		"""
		return DvidResource.get_cutoutI(api, chan, res, xspan, yspan, zspan)


	def create_project(self, chan):
		"""
			Method to create a project space in the dvid server

			Args:
				typename (string): describes data type stored (labelblk, labelvol, imagetile)
				dataname (string): user desired name of the instance
				version (int): describes the version of the instance the user is creating (default: 0)

			Returns:
				string: Confirmation message

			Raises:
				(KeyError): if given invalid version.
		"""
		return DvidResource.create_project(api, chan)

	def create_cutout(self, chan, xrang, yrang, zrang, volume):
		"""
			Method to upload data onto the dvid server.

			Args:
				UUID (string): ID of the DVID repository where the instance is found
				typename (string): type of data accepted by the project space
				dataname (string): user assigned name of the project space
				version (string): describes the version of the instance the user is creating (default: 0)
				fileDir (string): direcotry to the file of png to upload

			Returns:
				string: Confirmation message

			Raises:
				(KeyError): if given invalid version.
		"""
		return DvidResource.create_cutout(api, chan, xrang, yrang, zrang, volume)

	def ChannelResource(self, coll, exp, chan, des, datatype =  "uint8blk"):
		"""
		Method to create a channel within specified collection, experiment and of a known datatype

		Args:
			Coll (str) : Alias of the UUID
			exp (str) : Name of the instance of data that will be created
			des (str) : Description of what is saved under the given UUID
			datatype (str) : Type of data that will be uploaded. Deafaults to uint8blk

		Returns:
			chan (str) : composed of UUID, exp and chan for use in create_cutout function
		"""

		return DvidResource.ChannelResource(api, coll, exp, chan, des, datatype)

	def get_info(self, UUID):
		"""
			Method to obtain information on the requested repository

			Args:
				UUID (string): UUID of the DVID repository (str)

			Returns:
				string: History information of the repository

			Raises:
				(KeyError): if given invalid version.
		"""
		return DvidService.get_info(api,UUID)

	def get_log(self, UUID):
		"""
		Method to obtain log of all previous messages related to the repository

		Args:
		    UUID (string): UUID of the DVID repository (str)

		Returns:
		    string: list of all log recordings related to the DVID repository

		Raises:
		    (KeyError): if given invalid version.
		"""
		return DvidService.get_log(api,UUID)

	def post_log(self, UUID,log1):
		"""
		Method to post new log information to the repository

		Args:
		    UUID (string): UUID of the DVID repository (str)
		    log1 (string): Message to record on the repositories history log (str)

		Returns:
		    string: Confirmation message

		Raises:
		    (KeyError): if given invalid version.
		"""
		return DvidService.post_log(api,UUID,log1)

	def get_server_info(self):
		"""
		Method to obtain information about the server

		Args:
		    none

		Returns:
		    string: Server information

		Raises:
		    (KeyError): if given invalid version.
		"""
		return DvidService.get_server_info(api)

	def create_project_addon(self, UUID, typename, dataname, sync, version=0):
		"""
		Method create a project add-on

		Args:
		    UUID (string): UUID of Dvid repository
		    typename (string): type of add on:
		    	labelblk
		    	labelvol
		    	imagetile
		    dataname (string): name of addon
		    sync (string): name of instance (dataname) to which this addon is related
		    version (int): version of repository (dafaults to 1)

		Returns:
		    string: Server information

		Raises:
		    (KeyError): if given invalid version.
		"""

		return DvidService.create_project_addon(api,UUID,typename,dataname,sync,version)

	def merge(self, UUID, parents, note):
		"""
			Method to obtain information about the server

			Args:
			    UUID (string): UUID of Dvid repository
			    parents (string array) : a list of the parent UUIDs to be merged
				note (string) : any note the user wants to identify the merger

			Returns:
			    string: Merger information

			Raises:
			    (Runtime error)
		"""
		return DvidService.merge(api, UUID, mergeType, parents, note)

	def resolve(self, UUID, data, parents, note):
		"""
			Method to obtain information about the server

			Args:
			    UUID (string): UUID of Dvid repository
				data (string array) : a list of the data instance names to be scanned for possible conflicts
				parents (string array) : a list of the parent UUIDs to be merged in order of priority
				note (string) : any note the user wants to identify the merger

			Returns:
			    string: Resolution information

			Raises:
			    (Runtime error)
		"""

		return DvidService.resolve(api, UUID, data, parents, note)

	def delete_project(self, UUID):
		"""
        Method to delete a project

        Args:
            UUID (str) : hexadecimal character long string characterizing the project

        Returns:
            (str) : Confirmation message
		"""

		return DvidService.delete_project(api, UUID)

	def delete_data(self, api, UUID,dataname):
		"""
			Method to obtain information about the server

			Args:
			    UUID (string): UUID of Dvid repository

			Returns:
			    string: Server information

			Raises:
			    (Runtime error)
		"""

		return DvidService.delete_data(api, UUID, dataname)

	def change_server_setting(self,gc1,throt1):
		"""
		NOT IMPLEMENTED
		Method to change the server settings

		Args:
		    version (string): Version of Boss API to use.

		Returns:
		    None

		Raises:
		    (KeyError): if given invalid version.
		"""
		return DvidService.change_server_setting(api,gc1,throt1)
