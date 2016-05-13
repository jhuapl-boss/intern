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
from ndio.service.boss.v0_4.project import ProjectService_0_4

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
            'v0.4': ProjectService_0_4()
        }

    def list(self, resource):
        """List all resources of the same type as the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): List resources of the same type as this..

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
            (bool): True if create successful.
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
            (dictionary): Dictionary containing the entity's attributes.

        Raises:
            requests.HTTPError on failure.
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
            (bool): True on success.
        """
        ps = self.get_api_impl(resource.version)
        return ps.update(
            resource_name, resource, self.url_prefix, self.auth, 
            self.session, self.session_send_opts)

    def delete(self, resource):
        """Deletes the entity described by the given resource.

        Args:
            resource (ndio.resource.boss.Resource)

        Returns:
            (bool): True on success.
        """
        ps = self.get_api_impl(resource.version)
        return ps.delete(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)
