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

from intern.service.boss import BossService
from intern.service.boss.v1.metadata import MetadataService_1


class MetadataService(BossService):
    """MetadataService routes calls to the appropriate API version.
    """

    def __init__(self, base_url, version):
        """Constructor.

        Attributes:
            base_url (string): Base url to project service such as 'api.boss.io'.
            version (string): Version of Boss API to use.

        Raises:
            (KeyError): if given invalid version.
        """
        BossService.__init__(self)
        self.base_url = base_url
        self._versions = {
            'v1': MetadataService_1()
        }
        self.service = self.get_api_impl(version)

    def list(self, resource):
        """List metadata keys associated with the given resource.

        Args:
            resource (intern.resource.boss.BossResource): List keys associated with this resource.

        Returns:
            (list): List of key names.

        Raises:
            requests.HTTPError on failure.
        """
        return self.service.list(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def create(self, resource, keys_vals):
        """Create the given key-value pairs for the given resource.

        Will attempt to create all key-value pairs even if a failure is encountered.

        Args:
            resource (intern.resource.boss.BossResource): List keys associated with this resource.
            keys_vals (dictionary): The metadata to associate with the resource.

        Raises:
            HTTPErrorList on failure.
        """
        self.service.create(
            resource, keys_vals, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def get(self, resource, keys):
        """Get metadata key-value pairs associated with the given resource.

        Args:
            resource (intern.resource.boss.BossResource): Get key-value pairs associated with this resource.
            keys (list): Keys to retrieve.

        Returns:
            (dictionary): The requested metadata for the given resource.

        Raises:
            HTTPErrorList on failure.
        """
        return self.service.get(
            resource, keys, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def update(self, resource, keys_vals):
        """Update the given key-value pairs for the given resource.

        Keys must already exist before they may be updated.  Will attempt to
        update all key-value pairs even if a failure is encountered.

        Args:
            resource (intern.resource.boss.BossResource): Update values associated with this resource.
            keys_vals (dictionary): The metadata to update for the resource.

        Raises:
            HTTPErrorList on failure.
        """
        self.service.update(
            resource, keys_vals, self.url_prefix, self.auth,
            self.session, self.session_send_opts)

    def delete(self, resource, keys):
        """Delete metadata key-value pairs associated with the given resource.

        Will attempt to delete all given key-value pairs even if a failure
        occurs.

        Args:
            resource (intern.resource.boss.BossResource): Delete key-value pairs associated with this resource.
            keys (list): Keys to delete.

        Raises:
            HTTPErrorList on failure.
        """
        self.service.delete(
            resource, keys, self.url_prefix, self.auth, self.session,
            self.session_send_opts)
