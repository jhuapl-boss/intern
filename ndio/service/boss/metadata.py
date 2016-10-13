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
from ndio.service.boss.v0_4.metadata import MetadataService_0_4
from ndio.service.boss.v0_5.metadata import MetadataService_0_5
from ndio.service.boss.v0_6.metadata import MetadataService_0_6

class MetadataService(Service):
    """MetadataService routes calls to the appropriate API version.
    """

    def __init__(self, base_url):
        """Constructor.

        Attributes:
            base_url (string): Base url to project service such as 'api.boss.io'.
        """
        super().__init__()
        self.base_url = base_url
        self._versions = {
            'v0.4': MetadataService_0_4(),
            'v0.5': MetadataService_0_5(),
            'v0.6': MetadataService_0_6()
        }

    def list(self, resource):
        """List metadata keys associated with the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): List keys associated with this resource.

        Returns:
            (list): List of key names.

        Raises:
            requests.HTTPError on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.list(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def create(self, resource, keys_vals):
        """Create the given key-value pairs for the given resource.

        Will attempt to create all key-value pairs even if a failure is encountered.

        Args:
            resource (ndio.ndresource.boss.Resource): List keys associated with this resource.
            keys_vals (dictionary): The metadata to associate with the resource.

        Raises:
            requests.HTTPErrorList on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.create(
            resource, keys_vals, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def get(self, resource, keys):
        """Get metadata key-value pairs associated with the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): Get key-value pairs associated with this resource.
            keys (list): Keys to retrieve.

        Returns:
            (dictionary): The requested metadata for the given resource.

        Raises:
            requests.HTTPErrorList on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.get(
            resource, keys, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def update(self, resource, keys_vals):
        """Update the given key-value pairs for the given resource.

        Keys must already exist before they may be updated.  Will attempt to 
        update all key-value pairs even if a failure is encountered.  

        Args:
            resource (ndio.ndresource.boss.Resource): Update values associated with this resource.
            keys_vals (dictionary): The metadata to update for the resource.

        Raises:
            requests.HTTPErrorList on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.update(
            resource, keys_vals, self.url_prefix, self.auth, 
            self.session, self.session_send_opts)

    def delete(self, resource, keys):
        """Delete metadata key-value pairs associated with the given resource.

        Will attempt to delete all given key-value pairs even if a failure
        occurs.

        Args:
            resource (ndio.ndresource.boss.Resource): Delete key-value pairs associated with this resource.
            keys (list): Keys to delete.

        Raises:
            requests.HTTPErrorList on failure.
        """
        ps = self.get_api_impl(resource.version)
        return ps.delete(
            resource, keys, self.url_prefix, self.auth, self.session,
            self.session_send_opts)