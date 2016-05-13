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

from .base import Base
from ndio.ndresource.boss.resource import *

class MetadataService_0_4(Base):
    def __init__(self):
        super().__init__()

    @property
    def endpoint(self):
        return 'meta'

    def list(self, resource, url_prefix, auth, session, send_opts):
        req = self.get_request(
            resource, 'GET', 'application/json', url_prefix, auth, 
            proj_list_req = False)
        """List metadata keys associated with the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): List keys associated with this resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of key names.

        Raises:
            requests.HTTPError on failure.
        """
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            keys_dict = resp.json()
            return keys_dict['keys']

        print('List failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        resp.raise_for_status()

    def create(self, resource, keys_vals, url_prefix, auth, session, send_opts):
        """Create the given key-value pairs for the given resource.

        Will attempt to create all key-value pairs even if a failure is encountered.

        Args:
            resource (ndio.ndresource.boss.Resource): List keys associated with this resource.
            keys_vals (dictionary): The metadata to associate with the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (bool): True if create successful for all key-value pairs.
        """
        success = True
        for pair in keys_vals.items():
            key = pair[0]
            value = pair[1]
            req = self.get_metadata_request(
                resource, 'POST', 'application/json', url_prefix, auth, 
                key, value)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)
            if resp.status_code == 201:
                continue

            print(
                'Create failed for {}: {}:{}, got HTTP response: ({}) - {}'
                .format(resource.name, key, value, resp.status_code, resp.text))
            success = False

        return success

    def get(self, resource, keys, url_prefix, auth, session, send_opts):
        """Get metadata key-value pairs associated with the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): Get key-value pairs associated with this resource.
            keys (list): Keys to retrieve.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dictionary): The requested metadata for the given resource.

        Raises:
            requests.HTTPError on failure.
        """
        resDict = {}
        for key in keys:
            req = self.get_metadata_request(
                resource, 'GET', 'application/json', url_prefix, auth, key)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)
            if resp.status_code == 200:
                resDict[key] = resp.json()['value']
            else:
                resp.raise_for_status()

        return resDict

    def update(self, resource, keys_vals, url_prefix, auth, session, send_opts):
        """Update the given key-value pairs for the given resource.

        Keys must already exist before they may be updated.  Will attempt to 
        update all key-value pairs even if a failure is encountered.  

        Args:
            resource (ndio.ndresource.boss.Resource): Update values associated with this resource.
            keys_vals (dictionary): The metadata to update for the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (bool): True if update successful for all key-value pairs.
        """
        success = True
        for pair in keys_vals.items():
            key = pair[0]
            value = pair[1]
            req = self.get_metadata_request(
                resource, 'PUT', 'application/json', url_prefix, auth, 
                key, value)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)

            # Boss currently return 201 but will return 200.
            if resp.status_code == 200:
                continue

            print(
                'Update failed for {}: {}:{}, got HTTP response: ({}) - {}'
                .format(resource.name, key, value, resp.status_code, resp.text))
            success = False

        return success

    def delete(self, resource, keys, url_prefix, auth, session, send_opts):
        """Delete metadata key-value pairs associated with the given resource.

        Will attempt to delete all given key-value pairs even if a failure
        occurs.

        Args:
            resource (ndio.ndresource.boss.Resource): Delete key-value pairs associated with this resource.
            keys (list): Keys to delete.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (bool): True if delete successful for all key-value pairs.
        """
        success = True
        for key in keys:
            req = self.get_metadata_request(
                resource, 'DELETE', 'application/json', url_prefix, auth, key)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)
            # Boss currently return 201 but will return 200.
            if resp.status_code == 200:
                continue
            print(
                'Delete failed for {}: {}, got HTTP response: ({}) - {}'
                .format(resource.name, key, resp.status_code, resp.text))
            success = False

        return success
