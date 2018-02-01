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
import requests


class DvidService(Service):

	"""
		Partial implementation of intern.service.service.Service for the Dvid' services.

	"""

	def __init__(self):
		Service.__init__(self)

	@classmethod
	def get_info(self,api, UUID):

		"""
			Returns JSON for just the repository with given root UUID.  The UUID string can be
			shortened as long as it is uniquely identifiable across the managed repositories.
		"""
		if UUID is '':
			raise ValueError('The UUID was not specified')
		else:
			availability = requests.get(api + "/api/repo/" + UUID + "/info")
			avalM = availability.content
			return(avalM)

	@classmethod
	def get_log(self,api, UUID):

		"""
			The log is a list of strings that will be appended to the repo's log.  They should be
			descriptions for the entire repo and not just one node.  For particular versions, use
			node-level logging (below).
		"""
		if UUID is '':
			raise ValueError('The UUID was not specified')
		else:
			log = requests.get(api+ "/api/node/" + UUID + "/log")
			logM = log.content
			return(logM)

	@classmethod
	def post_log(self,api, UUID,log1):

		"""
			Allows the user to write a short description of the content in the repository
			{ "log": [ "provenance data...", "provenance data...", ...] }
		"""

		if  UUID is '':
			raise ValueError('The UUID was not specified')
		elif log1 is '':
			raise ValueError('Your log submission cannot be empty')
		else:
			log = requests.post(api + "/api/node/" + UUID + "/log",
				json = {"log" : [log1] })
			return("The log has been updated.")

	@classmethod
	def get_server_info(self,api):

		"""
			Returns JSON for server properties
		"""
		# raise RuntimeError('Something went wrong when trying to get your server info')
		info = requests.get(api + "/api/server")
		infoM = info.content
		return infoM


	@classmethod
	def create_project_addon(self, api, UUID, typename, dataname, sync, version=0):

		"""
		    Creates an instance within an existing repository
		"""
		# raise RuntimeError('Unable to sync project spaces')

		dat1 = requests.post(api + "/api/repo/"+ UUID + "/instance",
		    data=json.dumps({"typename": typename,
		        "dataname" : dataname,
		        "versioned": version,
		        "sync": sync
		    }))

		return (dat1.content)

	@classmethod
	def merge(self, api, UUID, parents, note):
		"""
			Creates a conflict-free merge of a set of committed parent UUIDs into a child.  Note
			the merge will not necessarily create an error immediately, but later GETs that
			detect conflicts will produce an error at that time.  These can be resolved by
			doing a POST on the "resolve" endpoint below.

			"mergeType": "conflict-free",
			"parents": [ "parent-uuid1", "parent-uuid2", ... ],
			"note": "this is a description of what I did on this commit"
		"""
		# raise RuntimeError('Unidentified API')

		merge1 = requests.post(api + "/api/repo/" + UUID + "/merge",
			mergeType = "conflict-free",
			parents = parents,
			note = note
			)

		return ("Your merge was successfully completed")

	@classmethod
	def resolve(self, api, UUID, data, parents, note):
		"""
			Forces a merge of a set of committed parent UUIDs into a child by specifying a
			UUID order that establishes priorities in case of conflicts (see "parents" description
			below.

			Unlike the very fast but lazily-enforced 'merge' endpoint, this request spawns an
			asynchronous routine that checks all data for the given data instances (see "data" in
			JSON post), creates versions to delete conflicts, and then performs the conflict-free
			merge to a final child.

			"data": [ "instance-name-1", "instance-name2", ... ],
			"parents": [ "parent-uuid1", "parent-uuid2", ... ],
			"note": "this is a description of what I did on this commit"
		"""
		# raise RuntimeError('Unidentified API')

		resolve1 = requests.post(api + "/api/repo/" + UUID + "/resolve",
			data = data,
			parents = parents,
			note = note
			)
		return ("You resolved the merger conflict.")

	@classmethod
	def delete_project(self, api, UUID):
		"""
			Deletes the repository holding a node with the given UUID.
		"""
		del1 = requests.delete(api + "/api/repo/" + UUID + "?imsure=true")
		return ("The repository with UUID: " + UUID + " has been successfully deleted.")

	@classmethod
	def delete_data(self, api, UUID, dataname):
		"""
			Deletes a data instance of given dataname within the given UUID.
		"""
		# raise RuntimeError('One of your inputs is not correct')
		del2 = requests. delete(api + "/api/repo/" + UUID + "/" + dataname + "?imsure=true")
		return ("The instance: " + dataname + " within UUID: " + UUID + " has been successfully deleted.")

	@classmethod
	def change_server_setting(self,api,gc1,throt1):

		"""
			Sets server parameters.  Expects JSON to be posted with optional keys denoting parameters:
			{
			"gc": 500,
			"throttle": 2
			}
			Possible keys:
			gc        Garbage collection target percentage.  This is a low-level server tuning
			            request that can affect overall request latency.
			            See: https://golang.org/pkg/runtime/debug/#SetGCPercent
			throttle  Maximum number of CPU-intensive requests that can be executed under throttle mode.
			            See imageblk and labelblk GET 3d voxels and POST voxels.
		"""

		setting = requests.post(api,
			gc = {"gc": [gc1]},
			throttle = {"throttle": [throt1]}
			)
		settingM = setting.content
		return ("Your settings have been changed.")
		raise NotImplemented
