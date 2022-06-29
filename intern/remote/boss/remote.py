"""
# Copyright 2016-2022 The Johns Hopkins University Applied Physics Laboratory
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
from intern.resource.boss.resource import *
from intern.service.boss.project import ProjectService
from intern.service.boss.metadata import MetadataService
from intern.service.boss.volume import VolumeService
from intern.service.boss.v1.volume import CacheMode
import warnings


CONFIG_PROJECT_SECTION = 'Project Service'
CONFIG_METADATA_SECTION = 'Metadata Service'
CONFIG_VOLUME_SECTION = 'Volume Service'
CONFIG_PROTOCOL = 'protocol'
# CONFIG_HOST example: api.theboss.io
CONFIG_HOST = 'host'
CONFIG_TOKEN = 'token'

LATEST_VERSION = 'v1'

class BossRemote(Remote):
    """
    Remote provides an SDK to the Boss API.

    Attributes:
        _token_project (string): Django Framework token for auth to the
            project service.
        _token_metadata (string): Django Framework token for auth to the
            metadata service.
        _token_volume (string): Django Framework token for auth to the
            volume service.
    """

    def __init__(self, cfg_file_or_dict=None, version=None):
        """
        Constructor.

        If not config arguments are passed in, ~/.intern/intern.cfg is read by
        default.  Config data is in INI format.  If both cfg_file and cfg_str
        are passed in, the value in cfg_str is used.

        Args:
            version (optional[string]): Version of Boss API to use.
            cfg_file_or_dict (optional[string|dict]): Path to config file in
                INI format or a dict of config parameters.

        Raises:
            (FileNotFoundError): if can't load given config file.
            (KeyError): if given invalid version.
        """
        Remote.__init__(self, cfg_file_or_dict)

        if version is None:
            version = LATEST_VERSION

        # Init the services
        self._init_project_service(version)
        self._init_metadata_service(version)
        self._init_volume_service(version)

    def __repr__(self):
        """
        Stringify the Remote.

        Returns a representation of the BossRemote that lists the host.
        """
        return "<intern.remote.BossRemote [" + self._config['Default']['host'] + "]>"

    def _init_project_service(self, version):
        """
        Method to initialize the Project Service from the config data

        Args:
            version (string): Version of Boss API to use.

        Returns:
            None

        Raises:
            (KeyError): if given invalid version.
        """
        project_cfg = self._load_config_section(CONFIG_PROJECT_SECTION)
        self._token_project = project_cfg[CONFIG_TOKEN]
        proto = project_cfg[CONFIG_PROTOCOL]
        host = project_cfg[CONFIG_HOST]

        self._project = ProjectService(host, version)
        self._project.base_protocol = proto
        self._project.set_auth(self._token_project)

    def _init_metadata_service(self, version):
        """
        Method to initialize the Metadata Service from the config data

        Args:
            version (string): Version of Boss API to use.

        Returns:
            None

        Raises:
            (KeyError): if given invalid version.
        """
        metadata_cfg = self._load_config_section(CONFIG_METADATA_SECTION)
        self._token_metadata = metadata_cfg[CONFIG_TOKEN]
        proto = metadata_cfg[CONFIG_PROTOCOL]
        host = metadata_cfg[CONFIG_HOST]

        self._metadata = MetadataService(host, version)
        self._metadata.base_protocol = proto
        self._metadata.set_auth(self._token_metadata)

    def _init_volume_service(self, version):
        """
        Method to initialize the Volume Service from the config data

        Args:
            version (string): Version of Boss API to use.

        Returns:
            None

        Raises:
            (KeyError): if given invalid version.
        """
        volume_cfg = self._load_config_section(CONFIG_VOLUME_SECTION)
        self._token_volume = volume_cfg[CONFIG_TOKEN]
        proto = volume_cfg[CONFIG_PROTOCOL]
        host = volume_cfg[CONFIG_HOST]

        self._volume = VolumeService(host, version)
        self._volume.base_protocol = proto
        self._volume.set_auth(self._token_volume)

    def _load_config_section(self, section_name):
        """
        Method to load the specific Service section from the config file if it
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
            raise KeyError((
                "'{}' was not found in the configuration file and no default " +
                "configuration was provided."
            ).format(section_name))

        # Make sure section is valid
        if "protocol" in section and "host" in section and "token" in section:
            return section
        else:
            raise KeyError(
                "Missing values in configuration data. " +
                "Must contain: protocol, host, token"
            )

    @property
    def token_project(self):
        """
        Returns the current token
        """
        return self._token_project

    @token_project.setter
    def token_project(self, value):
        self._token_project = value
        self.project_service.set_auth(self._token_project)

    @property
    def token_metadata(self):
        """
        Returns metadata for the current token
        """
        return self._token_metadata

    @token_metadata.setter
    def token_metadata(self, value):
        self._token_metadata = value
        self.metadata_service.set_auth(self._token_metadata)

    @property
    def token_volume(self):
        """
        Get the current token volume
        """
        return self._token_volume

    @token_volume.setter
    def token_volume(self, value):
        self._token_volume = value
        self.volume_service.set_auth(self._token_volume)

    def list_groups(self, filtr=None):
        """
        Get the groups the logged in user is a member of.

        Optionally filter by 'member' or 'maintainer'.

        Args:
            filtr (optional[string|None]): ['member'|'maintainer']

        Returns:
            (list[string]): List of group names.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.list_groups(filtr)

    def get_group(self, name, user_name=None):
        """
        Get information on the given group or whether or not a user is a member
        of the group.

        Args:
            name (string): Name of group to query.
            user_name (optional[string]): Supply None if not interested in
            determining if user is a member of the given group.

        Returns:
            (mixed): Dictionary if getting group information or bool if a user
                name is supplied.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_group(name, user_name)

    def create_group(self, name):
        """
        Create a new group.

        Args:
            name (string): Name of the group to create.

        Returns:
            (bool): True on success.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.create_group(name)

    def delete_group(self, name):
        """
        Delete given group.

        Args:
            name (string): Name of group.

        Returns:
            (bool): True on success.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.delete_group(name)

    def list_group_members(self, name):
        """
        Get the members of a group.

        Args:
            name (string): Name of group to query.

        Returns:
            (list[string]): List of member names.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.list_group_members(name)

    def add_group_member(self, grp_name, user):
        """
        Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user_name (string): User to add to group.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.add_group_member(grp_name, user)

    def delete_group_member(self, grp_name, user):
        """
        Delete the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user_name (string): User to delete from the group.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete_group_member(grp_name, user)

    def get_is_group_member(self, grp_name, user):
        """
        Check if the given user is a member of the named group.

        Note that a group maintainer is not considered a member unless the
        user is also explicitly added as a member.

        Args:
            name (string): Name of group.
            user_name (string): User of interest.

        Returns:
            (bool): False if user not a member.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_is_group_member(grp_name, user)

    def list_group_maintainers(self, name):
        """
        Get the maintainers of a group.

        Args:
            name (string): Name of group to query.

        Returns:
            (list[string]): List of maintainer names.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.list_group_maintainers(name)

    def add_group_maintainer(self, name, user):
        """
        Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user (string): User to add to group.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.add_group_maintainer(name, user)

    def delete_group_maintainer(self, grp_name, user):
        """
        Delete the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user (string): User to add to group.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete_group_maintainer(grp_name, user)

    def get_is_group_maintainer(self, grp_name, user):
        """
        Check if the given user is a member of the named group.

        Args:
            name (string): Name of group.
            user (string): User of interest.

        Returns:
            (bool): False if user not a member.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_is_group_maintainer(grp_name, user)

    def list_permissions(self, group_name=None, resource=None):
        """
        List permission sets associated filtering by group and/or resource.

        Args:
            group_name (string): Name of group.
            resource (intern.resource.boss.Resource): Identifies which data
                model object to operate on.

        Returns:
            (list): List of permissions.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.list_permissions(group_name, resource)

    def get_permissions(self, grp_name, resource):
        """
        Get permissions associated the group has with the given resource.

        Args:
            grp_name (string): Name of group.
            resource (intern.resource.boss.Resource): Identifies which data
                model object to operate on.

        Returns:
            (list): List of permissions.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_permissions(grp_name, resource)

    def add_permissions(self, grp_name, resource, permissions):
        """
        Add additional permissions for the group associated with the resource.

        Args:
            grp_name (string): Name of group.
            resource (intern.resource.boss.Resource): Identifies which data
                model object to operate on.
            permissions (list): List of permissions to add to the given resource

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.add_permissions(grp_name, resource, permissions)

    def update_permissions(self, grp_name, resource, permissions):
        """
        Update permissions for the group associated with the given resource.

        Args:
            grp_name (string): Name of group.
            resource (intern.resource.boss.Resource): Identifies which data
                model object to operate on
            permissions (list): List of permissions to add to the given resource

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.update_permissions(grp_name, resource, permissions)

    def delete_permissions(self, grp_name, resource):
        """
        Removes permissions from the group for the given resource.

        Args:
            grp_name (string): Name of group.
            resource (intern.resource.boss.Resource): Identifies which data
                model object to operate on.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete_permissions(grp_name, resource)

    def get_user_roles(self, user):
        """
        Get roles associated with the given user.

        Args:
            user (string): User name.

        Returns:
            (list): List of roles that user has.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_user_roles(user)

    def add_user_role(self, user, role):
        """
        Add role to given user.

        Args:
            user (string): User name.
            role (string): Role to assign.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.add_user_role(user, role)

    def delete_user_role(self, user, role):
        """
        Remove role from given user.

        Args:
            user (string): User name.
            role (string): Role to remove.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete_user_role(user, role)

    def get_user(self, user):
        """
        Get user's data (first and last name, email, etc).

        Args:
            user (string): User name.

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_user(user)

    def get_user_groups(self, user):
        """
        Get user's group memberships.

        Args:
            user (string): User name.

        Returns:
            (list): User's groups.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get_user_groups(user)

    def add_user(
            self, user,
            first_name=None, last_name=None,
            email=None, password=None
        ):
        """
        Add a new user.

        Args:
            user (string): User name.
            first_name (optional[string]): User's first name.  Defaults to None.
            last_name (optional[string]): User's last name.  Defaults to None.
            email: (optional[string]): User's email address.  Defaults to None.
            password: (optional[string]): User's password.  Defaults to None.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.add_user(
            user, first_name, last_name, email, password)

    def delete_user(self, user):
        """
        Delete the given user.

        Args:
            user (string): User name.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete_user(user)

    def _list_resource(self, resource):
        """
        List all instances of the given resource type.

        Use the specific list_<resource>() methods instead:
            list_collections()
            list_experiments()
            list_channels()
            list_coordinate_frames()

        Args:
            resource (intern.resource.boss.BossResource): resource.name may be
                an empty string.

        Returns:
            (list)

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return super(BossRemote, self).list_project(resource=resource)

    def list_collections(self):
        """
        List all collections.

        Returns:
            (list)

        Raises:
            requests.HTTPError on failure.
        """
        coll = CollectionResource(name='')
        return self._list_resource(coll)

    def list_experiments(self, collection_name):
        """
        List all experiments that belong to a collection.

        Args:
            collection_name (string): Name of the parent collection.

        Returns:
            (list)

        Raises:
            requests.HTTPError on failure.
        """
        exp = ExperimentResource(
            name='', collection_name=collection_name, coord_frame='foo')
        return self._list_resource(exp)

    def list_channels(self, collection_name, experiment_name):
        """
        List all channels belonging to the named experiment that is part
        of the named collection.

        Args:
            collection_name (string): Name of the parent collection.
            experiment_name (string): Name of the parent experiment.

        Returns:
            (list)

        Raises:
            requests.HTTPError on failure.
        """
        dont_care = 'image'
        chan = ChannelResource(
            name='', collection_name=collection_name,
            experiment_name=experiment_name, type=dont_care)
        return self._list_resource(chan)

    def list_coordinate_frames(self):
        """
        List all coordinate_frames.

        Returns:
            (list)

        Raises:
            requests.HTTPError on failure.
        """
        cf = CoordinateFrameResource(name='')
        return self._list_resource(cf)

    def get_channel(self, chan_name, coll_name, exp_name):
        """
        Helper that gets a fully initialized ChannelResource for an *existing* channel.

        Args:
            chan_name (str): Name of channel.
            coll_name (str): Name of channel's collection.
            exp_name (str): Name of channel's experiment.

        Returns:
            (intern.resource.boss.ChannelResource)
        """
        chan = ChannelResource(chan_name, coll_name, exp_name)
        return self.get_project(chan)

    def create_project(self, resource):
        """
        Create the entity described by the given resource.

        Args:
            resource (intern.resource.boss.BossResource)

        Returns:
            (intern.resource.boss.BossResource): Returns resource of type
                requested on success.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.create(resource)

    def get_project(self, resource):
        """
        Get attributes of the data model object named by the given resource.

        Args:
            resource (intern.resource.boss.BossResource): resource.name as well
                as any parents must be identified to succeed.

        Returns:
            (intern.resource.boss.BossResource): Returns resource of type
                requested on success.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get(resource)

    def update_project(self, resource_name, resource):
        """
        Updates an entity in the data model using the given resource.

        Args:
            resource_name (string): Current name of the resource (in case the
                resource is getting its name changed).
            resource (intern.resource.boss.BossResource): New attributes for
                the resource.

        Returns:
            (intern.resource.boss.BossResource): Returns updated resource of
                given type on success.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.update(resource_name, resource)

    def delete_project(self, resource):
        """
        Deletes the entity described by the given resource.

        Args:
            resource (intern.resource.boss.BossResource)

        Raises:
            requests.HTTPError on a failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete(resource)

    def list_metadata(self, resource):
        """
        List all keys associated with the given resource.

        Args:
            resource (intern.resource.boss.BossResource)

        Returns:
            (list)

        Raises:
            requests.HTTPError on a failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.list(resource)

    def create_metadata(self, resource, keys_vals):
        """
        Associates new key-value pairs with the given resource.

        Will attempt to add all key-value pairs even if some fail.

        Args:
            resource (intern.resource.boss.BossResource)
            keys_vals (dictionary): Collection of key-value pairs to assign to
                given resource.

        Raises:
            HTTPErrorList on failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        self.metadata_service.create(resource, keys_vals)

    def get_metadata(self, resource, keys):
        """
        Gets the values for given keys associated with the given resource.

        Args:
            resource (intern.resource.boss.BossResource)
            keys (list)

        Returns:
            (dictionary)

        Raises:
            HTTPErrorList on failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.get(resource, keys)

    def update_metadata(self, resource, keys_vals):
        """
        Updates key-value pairs with the given resource.

        Will attempt to update all key-value pairs even if some fail.
        Keys must already exist.

        Args:
            resource (intern.resource.boss.BossResource)
            keys_vals (dictionary): Collection of key-value pairs to update on
                the given resource.

        Raises:
            HTTPErrorList on failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        self.metadata_service.update(resource, keys_vals)

    def delete_metadata(self, resource, keys):
        """
        Deletes the given key-value pairs associated with the given resource.

        Will attempt to delete all key-value pairs even if some fail.

        Args:
            resource (intern.resource.boss.BossResource)
            keys (list)

        Raises:
            HTTPErrorList on failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        self.metadata_service.delete(resource, keys)

    def parse_bossURI(self, uri): # type: (str) -> Resource
        """
        Parse a bossDB URI and handle malform errors.

        Arguments:
            uri (str): URI of the form bossdb://<collection>/<experiment>/<channel>

        Returns:
            Resource

        """
        t = uri.split("://")[1].split("/")
        if len(t) == 3:
            return self.get_channel(t[2], t[0], t[1])
        raise ValueError("Cannot parse URI " + uri + ".")

    def get_cutout(self, resource, resolution, x_range, y_range, z_range, time_range=None, id_list=[], no_cache=None, access_mode=CacheMode.no_cache, parallel: bool = True, **kwargs):
            """Get a cutout from the volume service.

            Note that access_mode=no_cache is desirable when reading large amounts of
            data at once.  In these cases, the data is not first read into the
            cache, but instead, is sent directly from the data store to the
            requester.

            Args:
                resource (intern.resource.boss.resource.ChannelResource | str): Channel or layer Resource. If a
                    string is provided instead, BossRemote.parse_bossURI is called instead on a URI-formatted
                    string of the form `bossdb://collection/experiment/channel`.
                resolution (int): 0 indicates native resolution.
                x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
                y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
                z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
                time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
                id_list (optional [list[int]]): list of object ids to filter the cutout by.
                no_cache (optional [boolean or None]): Deprecated way to specify the use of cache to be True or False.
                    access_mode should be used instead
                access_mode (optional [Enum]): Identifies one of three cache access options:
                    cache = Will check both cache and for dirty keys
                    no_cache = Will skip cache check but check for dirty keys
                    raw = Will skip both the cache and dirty keys check
                parallel (bool: True): Whether downloads should be parallelized using multiprocessing

                TODO: Add mode to documentation


            Returns:
                (numpy.array): A 3D or 4D (time) numpy matrix in (time)ZYX order.

            Raises:
                requests.HTTPError on error.
            """
            if no_cache is not None:
                warnings.warn("The no-cache option has been deprecated and will not be used in future versions of intern.")
                warnings.warn("Please from intern.service.boss.volume import CacheMode and use access_mode=CacheMode.[cache,no-cache,raw] instead.")
            if no_cache and access_mode != CacheMode.no_cache:
                warnings.warn("Both no_cache and access_mode were used, please use access_mode only. As no_cache has been deprecated. ")
                warnings.warn("Your request will be made using the default mode no_cache.")
                access_mode=CacheMode.no_cache
            if no_cache:
                access_mode=CacheMode.no_cache
            elif no_cache == False:
                access_mode=CacheMode.cache
            return self._volume.get_cutout(
                resource, resolution,
                x_range, y_range, z_range, time_range,
                id_list, access_mode,
                parallel=parallel, **kwargs
            )
    
    def create_cutout_to_black(self, resource, resolution, x_range, y_range, z_range, time_range=None):
        """Post a black cutout to the volume service.

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.

        Returns:
            (): Return type depends on volume service's implementation.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.
        """
        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')
        return self._volume.create_cutout_to_black(
            resource, resolution, x_range, y_range, z_range, time_range)
        
    def get_experiment(self, coll_name, exp_name):
        """
        Convenience method that gets experiment resource.

        Args:
            coll_name (str): Collection name
            exp_name (str): Experiment name

        Returns:
            (ExperimentResource)
        """
        exp = ExperimentResource(exp_name, coll_name)
        return self.get_project(exp)

    def get_coordinate_frame(self, name):
        """
        Convenience method that gets coordinate frame resource

        Args:
            name (str): Name of the coordinate frame

        Returns:
            (CoordinateFrameResource)
        """
        cf = CoordinateFrameResource(name)
        return self.get_project(cf)

    def get_neuroglancer_link(self, resource, resolution, x_range, y_range, z_range, **kwargs):
            """
            Get a neuroglancer link of the cutout specified from the host specified in the remote configuration step.

            Args:
                resource (intern.resource.Resource): Resource compatible with cutout operations.
                resolution (int): 0 indicates native resolution.
                x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
                y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
                z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.

            Returns:
                (string): Return neuroglancer link.

            Raises:
                RuntimeError when given invalid resource.
                Other exceptions may be raised depending on the volume service's implementation.
            """
            return self._volume.get_neuroglancer_link(resource, resolution, x_range, y_range, z_range, **kwargs)

    def get_extents(self, resource):
            """Get extents of the reource

            Args:
                resource (intern.resource.boss.BossResource.ExperimentResource)

            Returns:
                extents (array): [[x-min, max-x], [y-min, max-y], [z-min, max-z]]

            Raises:
                requests.HTTPError on failure.
            """
            coord_frame = self.get_coordinate_frame(resource.coord_frame)
            min_point = [coord_frame.x_start, coord_frame.y_start, coord_frame.z_start]
            max_point = [coord_frame.x_stop, coord_frame.y_stop, coord_frame.z_stop]
            extents = [[min_point[0],max_point[0]],[min_point[1],max_point[1]],[min_point[2],max_point[2]]]

            return extents