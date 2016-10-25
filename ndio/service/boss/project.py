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

from ndio.service.boss.service import Service
from ndio.service.boss.v0_7.project import ProjectService_0_7

LATEST_VERSION='v0.7'

class ProjectService(Service):
    """ProjectService routes calls to the appropriate API version.
    """

    def __init__(self, base_url):
        """Constructor.

        Attributes:
            base_url (string): Base url to project service such as 'api.boss.io'.
        """
        super().__init__()
        self.base_url = base_url
        self._versions = {
            'v0.7': ProjectService_0_7()
        }

    def group_get(self, name, user_name=None, version=LATEST_VERSION):
        """Get information on the given group or whether or not a user is a member of the group.

        Args:
            name (string): Name of group to query.
            user_name (optional[string]): Supply None if not interested in determining if user is a member of the given group.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Returns:
            (mixed): Dictionary if getting group information or bool if a user name is supplied.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        ps = self.get_api_impl(version)
        return ps.group_get(
            name, user_name, self.url_prefix, self.auth, self.session, 
            self.session_send_opts)

    def group_create(self, name, version=LATEST_VERSION):
        """Create a new group.

        Args:
            name (string): Name of the group to create.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        ps = self.get_api_impl(version)
        ps.group_create(
            name, self.url_prefix, self.auth, self.session, 
            self.session_send_opts)

    def group_delete(self, name, user_name=None, version=LATEST_VERSION):
        """Delete given group or delete user from given group.

        If user_name is provided, the user will be removed from the group.
        Otherwise, the group, itself, is deleted.

        Args:
            name (string): Name of group.
            user_name (optional[string]): Defaults to None.  User to remove from group.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        ps = self.get_api_impl(version)
        ps.group_delete(
            name, user_name, self.url_prefix, self.auth, self.session, 
            self.session_send_opts)

    def group_add_user(self, name, user, version=LATEST_VERSION):
        """Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user_name (string): User to add to group.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        ps = self.get_api_impl(version)
        return ps.group_add_user(
            name, user, self.url_prefix, self.auth, self.session, 
            self.session_send_opts)

    def permissions_get(self, grp_name, resource, version=LATEST_VERSION):
        ps = self.get_api_impl(version)
        """Get permissions associated the group has with the given resource.

        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Returns:
            (list): List of permissions.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        return ps.permissions_get(
            grp_name, resource,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def permissions_add(
        self, grp_name, resource, permissions, version=LATEST_VERSION):
        """ Add additional permissions for the group associated with the given resource.

        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            permissions (list): List of permissions to add to the given resource.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        ps = self.get_api_impl(version)
        ps.permissions_add(
            grp_name, resource, permissions,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def permissions_delete(
        self, grp_name, resource, permissions, version=LATEST_VERSION):
        """Removes permissions from the group for the given resource.

        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            permissions (list): List of permissions to remove from the given resource.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')

        ps = self.get_api_impl(version)
        ps.permissions_delete(
            grp_name, resource, permissions,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_add_role(self, user, role, version=LATEST_VERSION):
        """Add role to given user.

        Args:
            user (string): User name.
            role (string): Role to assign.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        ps.user_add_role(
            user, role,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_delete_role(self, user, role, version=LATEST_VERSION):
        """Remove role from given user.

        Args:
            user (string): User name.
            role (string): Role to remove.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        ps.user_delete_role(
            user, role,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_get_roles(self, user, version=LATEST_VERSION):
        """Get roles associated with the given user.

        Args:
            user (string): User name.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Returns:
            (list): List of roles that user has.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        return ps.user_get_roles(
            user, self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_add(
        self, user, first_name=None, last_name=None, email=None, password=None,
        version=LATEST_VERSION):
        """Add a new user.

        Args:
            user (string): User name.
            first_name (optional[string]): User's first name.  Defaults to None.
            last_name (optional[string]): User's last name.  Defaults to None.
            email: (optional[string]): User's email address.  Defaults to None.
            password: (optional[string]): User's password.  Defaults to None.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        ps.user_add(
            user, first_name, last_name, email, password,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_get(self, user, version=LATEST_VERSION):
        """Get user's data (first and last name, email, etc).

        Args:
            user (string): User name.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        return ps.user_get(
            user, self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_get_groups(self, user, version=LATEST_VERSION):
        """Get user's group memberships.

        Args:
            user (string): User name.

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        return ps.user_get_groups(
            user, self.url_prefix, self.auth, self.session, self.session_send_opts)

    def user_delete(self, user, version=LATEST_VERSION):
        """Delete the given user.

        Args:
            user (string): User name.
            version (optional[string]): Version of the Boss API to use.  Defaults to the latest supported version.

        Raises:
            requests.HTTPError on failure.
        """
        if version == 'v0.4':
            raise NotImplementedError('ndio does not support this call for v0.4.')
        ps = self.get_api_impl(version)
        ps.user_delete(
            user, self.url_prefix, self.auth, self.session, self.session_send_opts)

    def list(self, resource=None, **kwargs):
        """List all resources of the same type as the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): List resources of the same type as this resource.

        Returns:
            (list): List of resources.

        Raises:
            requests.HTTPError on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.list(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def create(self, resource):
        """Create the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): Create a data model object with attributes matching those of the resource.

        Returns:
            (ndio.ndresource.boss.Resource): Returns resource of type requested on success.  Returns None on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.create(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def get(self, resource):
        """Get attributes of the data model object named by the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): resource.name as well as any parents must be identified to succeed.

        Returns:
            (ndio.resource.boss.Resource): Returns resource of type requested on success.  Returns None on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.get(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def update(self, resource_name, resource):
        """Updates an entity in the data model using the given resource.

        Args:
            resource_name (string): Current name of the resource (in case the resource is getting its name changed).
            resource (ndio.resource.boss.Resource): New attributes for the resource.

        Returns:
            (ndio.resource.boss.Resource): Returns updated resource of given type on success.  Returns None on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.update(
            resource_name, resource, self.url_prefix, self.auth, 
            self.session, self.session_send_opts)

    def delete(self, resource):
        """Deletes the entity described by the given resource.

        Args:
            resource (ndio.resource.boss.Resource)
        """
        ps = self.get_api_impl(resource.version)
        ps.delete(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)
