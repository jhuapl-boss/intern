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

from ndio.remote import Remote
from ndio.service.boss.project import ProjectService
from ndio.service.boss.metadata import MetadataService
from ndio.service.boss.volume import VolumeService
import configparser
import os

CONFIG_FILE='~/.ndio/ndio.cfg'
CONFIG_PROJECT_SECTION = 'Project Service'
CONFIG_METADATA_SECTION = 'Metadata Service'
CONFIG_VOLUME_SECTION = 'Volume Service'
CONFIG_PROTOCOL = 'protocol'
# CONFIG_HOST example: api.theboss.io
CONFIG_HOST = 'host'
CONFIG_TOKEN = 'token'

LATEST_VERSION='v0.7'


class BossRemote(Remote):
    """Remote provides an SDK to the Boss API.

    The methods for working with groups, users, and permissions use the 
    group_perm_api_version property to determine which version of the Boss
    API to use.  If not set, it defaults to using the latest version.

    Note that ndio support for groups, users, and permissions was first added
    in v0.5.

    Attributes:
        _token_project (string): Django Rest Framework token for auth to the project service.
        _token_metadata (string): Django Rest Framework token for auth to the metadata service.
        _token_volume (string): Django Rest Framework token for auth to the volume service.
        _group_perm_api_version (string): Boss API version to use when calling group_*() and permissions_*() methods.
    """

    def __init__(self, cfg_file=CONFIG_FILE):
        """Constructor.

        Args:
            cfg_file (string): Path to config file in INI format.
        """

        self._token_project = None
        self._token_metadata = None
        self._token_volume = None
        self._group_perm_api_version = LATEST_VERSION

        try:
            self._config = self.load_config_file(os.path.expanduser(cfg_file))
            self._init_project_service()
            self._init_metadata_service()
            self._init_volume_service()
        except FileNotFoundError:
            print('Config file {} not found.'.format(cfg_file))
        except KeyError as k:
            print('Could not find key {} in {}'.format(k, cfg_file))

    def _init_project_service(self):
        project_cfg = self._config[CONFIG_PROJECT_SECTION]
        self._token_project = project_cfg[CONFIG_TOKEN]
        proto = project_cfg[CONFIG_PROTOCOL]
        host = project_cfg[CONFIG_HOST]

        self._project = ProjectService(host)
        self._project.base_protocol = proto
        self._project.set_auth(self._token_project)

    def _init_metadata_service(self):
        metadata_cfg = self._config[CONFIG_METADATA_SECTION]
        self._token_metadata = metadata_cfg[CONFIG_TOKEN]
        proto = metadata_cfg[CONFIG_PROTOCOL]
        host = metadata_cfg[CONFIG_HOST]

        self._metadata = MetadataService(host)
        self._metadata.base_protocol = proto
        self._metadata.set_auth(self._token_metadata)

    def _init_volume_service(self):
        volume_cfg = self._config[CONFIG_VOLUME_SECTION]
        self._token_volume = volume_cfg[CONFIG_TOKEN]
        proto = volume_cfg[CONFIG_PROTOCOL]
        host = volume_cfg[CONFIG_HOST]

        self._volume = VolumeService(host)
        self._volume.base_protocol = proto
        self._volume.set_auth(self._token_volume)

    def load_config(self, config_str):
        """Load config data for the Remote.

        Args:
            config_str (string): Config data encoded in a string.

        Returns:
            (configparser.ConfigParser)
        """
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read_string(config_str)
        return cfg_parser

    def load_config_file(self, path):
        """Load config data for Remote from file.

        Args:
            path (string): Path (and filename) to config file.

        Returns:
            (configparser.ConfigParser)

        Raises:
            FileNotFoundError
        """
        with open(path, 'r') as f:
            data = f.read()
            return self.load_config(data)

    @property
    def token_project(self):
        return self._token_project

    @token_project.setter
    def token_project(self, value):
        self._token_project = value
        self.project_service.set_auth(self._token_project)

    @property
    def token_metadata(self):
        return self._token_metadata

    @token_metadata.setter
    def token_metadata(self, value):
        self._token_metadata = value
        self.metadata_service.set_auth(self._token_metadata)

    @property
    def token_volume(self):
        return self._token_volume

    @token_volume.setter
    def token_volume(self, value):
        self._token_volume = value
        self.volume_service.set_auth(self._token_volume)

    @property
    def group_perm_api_version(self):
        return self._group_perm_api_version

    @group_perm_api_version.setter
    def group_perm_api_version(self, value):
        self._group_perm_api_version = value

    def group_get(self, name, user_name=None):
        """Get information on the given group or whether or not a user is a member of the group.

        Args:
            name (string): Name of group to query.
            user_name (optional[string]): Supply None if not interested in determining if user is a member of the given group.

        Returns:
            (mixed): Dictionary if getting group information or bool if a user name is supplied.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.group_get(
            name, user_name, self.group_perm_api_version)

    def group_create(self, name):
        """Create a new group.

        Args:
            name (string): Name of the group to create.

        Returns:
            (bool): True on success.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.group_create(
            name, self.group_perm_api_version)

    def group_delete(self, name, user_name=None):
        """Delete given group or delete user from given group.

        If user_name is provided, the user will be removed from the group.
        Otherwise, the group, itself, is deleted.

        Args:
            name (string): Name of group.
            user_name (optional[string]): Defaults to None.  User to remove from group.

        Returns:
            (bool): True on success.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.group_delete(
            name, user_name, self.group_perm_api_version)

    def group_add_user(self, grp_name, user):
        """Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user_name (string): User to add to group.

        Returns:
            (bool): True on success.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.group_add_user(
            grp_name, user, self.group_perm_api_version)

    def permissions_get(self, grp_name, resource):
        """Get permissions associated the group has with the given resource.

        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.

        Returns:
            (list): List of permissions.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.permissions_get(
            grp_name, resource, self.group_perm_api_version)

    def permissions_add(self, grp_name, resource, permissions):
        """Add additional permissions for the group associated with the given resource.

        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            permissions (list): List of permissions to add to the given resource.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.permissions_add(
            grp_name, resource, permissions, self.group_perm_api_version)

    def permissions_delete(self, grp_name, resource, permissions):
        """Removes permissions from the group for the given resource.

        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            permissions (list): List of permissions to remove from the given resource.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.permissions_delete(
            grp_name, resource, permissions, self.group_perm_api_version)

    def user_get_roles(self, user):
        """Get roles associated with the given user.

        Args:
            user (string): User name.

        Returns:
            (list): List of roles that user has.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.user_get_roles(user, self.group_perm_api_version)

    def user_add_role(self, user, role):
        """Add role to given user.

        Args:
            user (string): User name.
            role (string): Role to assign.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.user_add_role(user, role, self.group_perm_api_version)

    def user_delete_role(self, user, role):
        """Remove role from given user.

        Args:
            user (string): User name.
            role (string): Role to remove.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.user_delete_role(user, role, self.group_perm_api_version)

    def user_get(self, user):
        """Get user's data (first and last name, email, etc).

        Args:
            user (string): User name.

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.user_get(user, self.group_perm_api_version)

    def user_get_groups(self, user):
        """Get user's group memberships.

        Args:
            user (string): User name.

        Returns:
            (list): User's groups.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.user_get_groups(user, self.group_perm_api_version)

    def user_add(
        self, user, first_name=None, last_name=None, email=None, password=None):
        """Add a new user.

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
        self.project_service.user_add(
            user, first_name, last_name, email, password, 
            self.group_perm_api_version)

    def user_delete(self, user):
        """Delete the given user.

        Args:
            user (string): User name.

        Raises:
            requests.HTTPError on failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.user_delete(user, self.group_perm_api_version)

    def project_list(self, resource):
        """List all instances of the given resource type.

        Args:
            resource (ndio.resource.boss.Resource): resource.name may be an empty string.

        Returns:
            (list)
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.list(resource)

    def project_create(self, resource):
        """Create the entity described by the given resource.

        Args:
            resource (ndio.resource.boss.Resource)

        Returns:
            (ndio.ndresource.boss.Resource): Returns resource of type requested on success.  Returns None on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.create(resource)

    def project_get(self, resource):
        """Get attributes of the data model object named by the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): resource.name as well as any parents must be identified to succeed.

        Returns:
            (ndio.resource.boss.Resource): Returns resource of type requested on success.  Returns None on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.get(resource)

    def project_update(self, resource_name, resource):
        """Updates an entity in the data model using the given resource.

        Args:
            resource_name (string): Current name of the resource (in case the resource is getting its name changed).
            resource (ndio.resource.boss.Resource): New attributes for the resource.

        Returns:
            (ndio.resource.boss.Resource): Returns updated resource of given type on success.  Returns None on failure.
        """
        self.project_service.set_auth(self._token_project)
        return self.project_service.update(resource_name, resource)

    def project_delete(self, resource):
        """Deletes the entity described by the given resource.

        Args:
            resource (ndio.resource.boss.Resource)

        Raises:
            requests.HTTPError on a failure.
        """
        self.project_service.set_auth(self._token_project)
        self.project_service.delete(resource)

    def metadata_list(self, resource):
        """List all keys associated with the given resource.

        Args:
            resource (ndio.resource.boss.Resource)

        Returns:
            (list)

        Raises:
            requests.HTTPError on a failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.list(resource)

    def metadata_create(self, resource, keys_vals):
        """Associates new key-value pairs with the given resource.

        Will attempt to add all key-value pairs even if some fail.

        Args:
            resource (ndio.resource.boss.Resource)
            keys_vals (dictionary): Collection of key-value pairs to assign to given resource.

        Raises:
            requests.HTTPError on a failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.create(resource, keys_vals)

    def metadata_get(self, resource, keys):
        """Gets the values for given keys associated with the given resource.

        Args:
            resource (ndio.resource.boss.Resource)
            keys (list)

        Returns:
            (dictionary)

        Raises:
            requests.HTTPError on a failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.get(resource, keys)

    def metadata_update(self, resource, keys_vals):
        """Updates key-value pairs with the given resource.

        Will attempt to update all key-value pairs even if some fail.
        Keys must already exist.

        Args:
            resource (ndio.resource.boss.Resource)
            keys_vals (dictionary): Collection of key-value pairs to update on the given resource.

        Raises:
            requests.HTTPError on a failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.update(resource, keys_vals)

    def metadata_delete(self, resource, keys):
        """Deletes the given key-value pairs associated with the given resource.

        Will attempt to delete all key-value pairs even if some fail.

        Args:
            resource (ndio.resource.boss.Resource)
            keys (list)

        Raises:
            requests.HTTPError on a failure.
        """
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.delete(resource, keys)
