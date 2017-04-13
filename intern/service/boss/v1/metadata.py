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
from intern.resource.boss.resource import *
from intern.service.boss.httperrorlist import HTTPErrorList
from requests import HTTPError
from intern.service.boss import BaseVersion
from intern.service.boss.v1 import BOSS_API_VERSION


class MetadataService_1(BaseVersion):
    def __init__(self):
        BaseVersion.__init__(self)

    @property
    def version(self):
        """Return the API Version for this implementation
        """
        return BOSS_API_VERSION

    def list(self, resource, url_prefix, auth, session, send_opts):
        """List metadata keys associated with the given resource.

        Args:
            resource (intern.resource.boss.BossResource): List keys associated with this resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of key names.

        Raises:
            requests.HTTPError on failure.
        """

        req = self.get_metadata_request(
            resource, 'GET', 'application/json', url_prefix, auth)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            keys_dict = resp.json()
            return keys_dict['keys']

        err = ('List failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def create(self, resource, keys_vals, url_prefix, auth, session, send_opts):
        """Create the given key-value pairs for the given resource.

        Will attempt to create all key-value pairs even if a failure is encountered.

        Args:
            resource (intern.resource.boss.BossResource): List keys associated with this resource.
            keys_vals (dictionary): The metadata to associate with the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            HTTPErrorList on failure.
        """
        success = True
        exc = HTTPErrorList('At least one key-value create failed.')

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

            err = (
                'Create failed for {}: {}:{}, got HTTP response: ({}) - {}'
                .format(resource.name, key, value, resp.status_code, resp.text))
            exc.http_errors.append(HTTPError(err, request=req, response=resp))
            success = False

        if not success:
            raise exc

    def get(self, resource, keys, url_prefix, auth, session, send_opts):
        """Get metadata key-value pairs associated with the given resource.

        Args:
            resource (intern.resource.boss.BossResource): Get key-value pairs associated with this resource.
            keys (list): Keys to retrieve.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dictionary): The requested metadata for the given resource.

        Raises:
            HTTPErrorList on failure.
        """
        resDict = {}
        success = True
        exc = HTTPErrorList('At least one key-value update failed.')

        for key in keys:
            req = self.get_metadata_request(
                resource, 'GET', 'application/json', url_prefix, auth, key)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)
            if resp.status_code == 200:
                resDict[key] = resp.json()['value']
            else:
                err = ('Get failed on {}, got HTTP response: ({}) - {}'.format(
                    resource.name, resp.status_code, resp.text))
                exc.http_errors.append(HTTPError(err, request=req, response=resp))
                success = False

        if not success:
            raise exc

        return resDict

    def update(self, resource, keys_vals, url_prefix, auth, session, send_opts):
        """Update the given key-value pairs for the given resource.

        Keys must already exist before they may be updated.  Will attempt to
        update all key-value pairs even if a failure is encountered.

        Args:
            resource (intern.resource.boss.BossResource): Update values associated with this resource.
            keys_vals (dictionary): The metadata to update for the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            HTTPErrorList on failure.
        """
        success = True
        exc = HTTPErrorList('At least one key-value update failed.')

        for pair in keys_vals.items():
            key = pair[0]
            value = pair[1]
            req = self.get_metadata_request(
                resource, 'PUT', 'application/json', url_prefix, auth,
                key, value)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)

            if resp.status_code == 200:
                continue

            err = (
                'Update failed for {}: {}:{}, got HTTP response: ({}) - {}'
                .format(resource.name, key, value, resp.status_code, resp.text))
            exc.http_errors.append(HTTPError(err, request=req, response=resp))
            success = False

        if not success:
            raise exc

    def delete(self, resource, keys, url_prefix, auth, session, send_opts):
        """Delete metadata key-value pairs associated with the given resource.

        Will attempt to delete all given key-value pairs even if a failure
        occurs.

        Args:
            resource (intern.resource.boss.BossResource): Delete key-value pairs associated with this resource.
            keys (list): Keys to delete.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            HTTPErrorList on failure.
        """
        success = True
        exc = HTTPErrorList('At least one key-value update failed.')

        for key in keys:
            req = self.get_metadata_request(
                resource, 'DELETE', 'application/json', url_prefix, auth, key)
            prep = session.prepare_request(req)
            resp = session.send(prep, **send_opts)
            if resp.status_code == 204:
                continue
            err = (
                'Delete failed for {}: {}, got HTTP response: ({}) - {}'
                .format(resource.name, key, resp.status_code, resp.text))
            exc.http_errors.append(HTTPError(err, request=req, response=resp))
            success = False

        if not success:
            raise exc
