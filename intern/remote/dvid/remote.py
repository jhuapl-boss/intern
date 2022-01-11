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
from intern.resource.dvid.resource import *
from intern.service.dvid.project import ProjectService
from intern.service.dvid.metadata import MetadataService
from intern.service.dvid.volume import VolumeService
from intern.service.dvid.versioning import VersioningService

CONFIG_METADATA_SECTION = "Metadata Service"
CONFIG_VERSIONING_SECTION = "Versioning Service"
CONFIG_PROJECT_SECTION = "Project Service"
CONFIG_VOLUME_SECTION = "Volume Service"
CONFIG_PROTOCOL = "protocol"
CONFIG_HOST = "host"


class DVIDRemote(Remote):
    """Remote provides an SDK to the DVID API.
	"""

    def __init__(self, cfg_file_or_dict=None):
        """Constructor.
		Protocol and host specifications are taken in as keys -values of dictionary.
		
        Args:
            cfg_file_or_dict (optional[string|dict]): Path to config file in
                INI format or a dict of config parameters.
		"""
        Remote.__init__(self, cfg_file_or_dict)

        # Init the services
        self._init_project_service()
        self._init_metadata_service()
        self._init_volume_service()
        self._init_versioning_service()

    def _init_project_service(self):
        """Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
        project_cfg = self._load_config_section(CONFIG_PROJECT_SECTION)
        proto = project_cfg[CONFIG_PROTOCOL]
        host = project_cfg[CONFIG_HOST]
        api = proto + "://" + host

        self._project = ProjectService(api)
        self._project.base_protocol = proto

    def _init_metadata_service(self):
        """Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
        metadata_cfg = self._load_config_section(CONFIG_METADATA_SECTION)
        proto = metadata_cfg[CONFIG_PROTOCOL]
        host = metadata_cfg[CONFIG_HOST]
        api = proto + "://" + host

        self._metadata = MetadataService(api)
        self._metadata.base_protocol = proto

    def _init_volume_service(self):
        """Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
        volume_cfg = self._load_config_section(CONFIG_VOLUME_SECTION)
        proto = volume_cfg[CONFIG_PROTOCOL]
        host = volume_cfg[CONFIG_HOST]
        api = proto + "://" + host

        self._volume = VolumeService(api)
        self._volume.base_protocol = proto

    def _init_versioning_service(self):
        """Method to initialize the Volume Service from the config data

		Args:
			None

		Returns:
			None

		Raises:
			(KeyError): if given invalid version.
		"""
        versioning_cfg = self._load_config_section(CONFIG_VERSIONING_SECTION)
        proto = versioning_cfg[CONFIG_PROTOCOL]
        host = versioning_cfg[CONFIG_HOST]
        api = proto + "://" + host

        self._versioning = VersioningService(api)
        self._versioning.base_protocol = proto

    def __repr__(self):
        """Stringify the Remote.

		Returns a representation of the DVIDRemote that lists the host.
		"""
        return "<intern.remote.DVIDRemote [" + self._config["Default"]["host"] + "]>"

    def _load_config_section(self, section_name):
        """Method to load the specific Service section from the config file if it
		exists, or fall back to the default

		Args:
			section_name (str): The desired service section name

		Returns:
			(dict): the section parameters
		"""
        if self._config.has_section(section_name):
            # Load specific section
            section = dict(self._config.items(section_name))
        elif self._config.has_section("Default"):
            # Load Default section
            section = dict(self._config.items("Default"))
        else:
            raise KeyError(
                (
                    "'{}' was not found in the configuration file and no default "
                    + "configuration was provided."
                ).format(section_name)
            )

        # Make sure section is valid
        if "protocol" in section and "host" in section:
            return section
        else:
            raise KeyError(
                "Missing values in configuration data. "
                + "Must contain: protocol, host"
            )

    def get_instance(self, UUID, data_instance, datatype=""):
        """Method to input all data instance hierarchy requirememnts, works as a dummy
        for DVIDRemote Parallelism.

		Args:
			UUID (str) : Root UUID of the repository
			data_instance (str): Name of data instance within repository
			datatype (str): data type of the instance (uint8, uint16, uint64) defaults to uint8
		Returns:
			resource (intern.resource.dvid.DvidResource)
		"""
        return DataInstanceResource(data_instance, UUID, datatype=datatype)

    def get_cutout(self, resource, res, xrange, yrange, zrange, **kwargs):
        """Method to request a volume of data from DVID server

		Args:
			resource (intern.resource.dvid.resource.DataInstanceResource | str): Data Instance Resource. If a
				string is provided instead, DvidRemote.parse_dvidURI is called instead on a URI-formatted
				string of the form `dvid://UUID/data_instance`.
			xrange (int) : range of pixels in x axis ([1000:1500])
			yrange (int) : range of pixels in y axis ([1000:1500])
			zrange (int) : range of pixels in z axis ([1000:1010])

		Returns:
			array: numpy array representation of the requested volume

		Raises:
			(KeyError): if given invalid version.
		"""
        return self._volume.get_cutout(resource, res, xrange, yrange, zrange, **kwargs)

    def parse_dvidURI(self, uri):  # type: (str) -> Resource
        """Parse a DVID URI and handle malform errors.

		Arguments:
			uri (str): URI of the form dvid://<UUID>/<DataInstance>

		Returns:
			Resource

		"""
        t = uri.split("://")[1].split("/")
        if len(t) == 3:
            return self.get_instance(t[0], t[1])
        raise ValueError("Cannot parse URI " + uri + ".")

    def get_project(self, resource):
        """Get attributes of the data model object named by the given resource.

		Args:
			resource (intern.resource.dvid.DVIDResource): resource.name as well
				as any parents must be identified to succeed.

		Returns:
			(intern.resource.dvid.DVIDResource): Returns resource of type
				requested on success.

		Raises:
			requests.HTTPError on failure.
		"""
        return self._project.get(resource)

    def create_project(self, resource):
        """Method to create a project space in the DVID server

		Args:
			resource (intern.resource.dvid.DVIDResource): dvid resource for which to create a project

		Returns:
			str: Confirmation message

		Raises:
			(KeyError): if given invalid version.
		"""
        return self._project.create(resource)

    def delete_project(self, resource):
        """Method to delete a project

        Args:
			resource (intern.resource.dvid.DVIDResource)

        Returns:
            (str) : Confirmation message
		"""

        return self._project.delete(resource)

    def get_extents(self, resource):
        """Get extents of the reource

		Args:
			resource (intern.resource.dvid.DVIDResource): resource.name as well
				as any parents must be identified to succeed.

		Returns:
			extents (array): [[x-min, max-x], [y-min, max-y], [z-min, max-z]]

		Raises:
			requests.HTTPError on failure.
		"""
        return self._metadata.get_extents(resource)

    def get_metadata(self, resource):
        """Get metadata of the reource

		Args:
			resource (intern.resource.dvid.DVIDResource): resource.name as well
				as any parents must be identified to succeed.

		Returns:
			(JSON): returns json containing data instance metadata

		Raises:
			requests.HTTPError on failure.
		"""
        return self._metadata.get_metadata(resource)

    def get_info(self, UUID):
        """Method to obtain information on the requested repository

		Args:
			UUID (str): UUID of the DVID repository

		Returns:
			str: History information of the repository

		Raises:
			HTTPError if request status code is not 200
		"""
        return self._metadata.get_info(UUID)

    def get_log(self, UUID):
        """The log is a list of strings that will be appended to the repo's log.  They should be
		descriptions for the entire repo and not just one node.

		Args:
			UUID (str): UUID of the DVID repository

		Returns:
			str: list of all log recordings related to the DVID repository

		Raises:
			(ValueError): if given invalid UUID.
		"""
        return self._versioning.get_log(UUID)

    def post_log(self, UUID, log1):
        """Allows the user to write a short description of the content in the repository
		{ "log": [ "provenance data...", "provenance data...", ...] }

		Args:
			UUID (str): UUID of the DVID repository (str)
			log_m (str): Message to record on the repositories history log (str)

		Returns:
			HTTP Response

		Raises:
			(ValueError): if given invalid UUID or log.
		"""
        return self._versioning.post_log(UUID, log1)

    def get_server_types(self):
        """Method to obtain information about the server

		Args:
		    none

		Returns:
		    JSON with datatypes of currently stored data instances

		Raises:
		    HTTPError if request status code is not 200
		"""
        return self._metadata.get_server_types()

    def get_server_compiled_types(self):
        """Method to obtain information about the server

		Args:
		    none

		Returns:
		    JSON of all possible datatypes for this server

		Raises:
		    HTTPError if request status code is not 200
		"""
        return self._metadata.get_server_compiled_types()

    def server_reload_metadata(self):
        """Method to reload metadat from storage

		Args:
		    none

		Returns:
		    HTTTP Response

		Raises:
		    HTTPError if request status code is not 200
		"""
        return self._metadata.server_reload_metadata()

    def get_server_info(self):
        """Method to obtain information about the server

		Args:
		    none

		Returns:
		    JSON for server properties

		Raises:
		    HTTPError if request status code is not 200
		"""
        return self._metadata.get_server_info()

    def merge(self, UUID, parents, mergeType="conflict-free", note=""):
        """Creates a conflict-free merge of a set of committed parent UUIDs into a child.  Note
		the merge will not necessarily create an error immediately

		Args:
			mergeType (str) = "conflict-free"
			parents (array) = [ "parent-uuid1", "parent-uuid2", ... ]
			note (str) = this is a description of what I did on this commit

		Returns:
			merge_child_uuid (str): child generated uuid after merge

		Raises:
			HTTPError: On non 200 status code
		"""
        return self._versioning.merge(UUID, parents, mergeType, note)

    def resolve(self, UUID, data, parents, note=""):
        """Forces a merge of a set of committed parent UUIDs into a child by specifying a
		UUID order that establishes priorities in case of conflicts

		Args:
			data (array) = [ "instance-name-1", "instance-name2", ... ],
			parents (array): [ "parent-uuid1", "parent-uuid2", ... ],
			note (str): this is a description of what I did on this commit

		Returns:
			resolve_child_uuid (str): child generated uuid after resolution

		Raises:
			HTTPError: On non 200 status code
		"""

        return self._versioning.resolve(UUID, data, parents, note)

    def commit(self, UUID, note="", log_m=""):
        """Allows the user to write a short description of the content in the repository

		Args:
			UUID (str): UUID of the DVID repository (str)
			note (str): human-readable commit message
			log_m (str): Message to record on the repositories history log (str)

		Returns:
			commit_uuid (str): commit hash

		Raises:
			(ValueError): if given invalid UUID.
		"""

        return self._versioning.commit(UUID, note, log_m)

    def branch(self, UUID, note=""):
        """Allows the user to write a short description of the content in the repository

		Args:
			UUID (str): UUID of the DVID repository (str)
			note (str): Message to record when branching

		Returns:
			branch_uuid (str): The child branch UUID

		Raises:
			(KeyError): if given invalid version.
		"""

        return self._versioning.branch(UUID, note)

