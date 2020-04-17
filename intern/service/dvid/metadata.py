# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
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

from intern.service.dvid import DVIDService
from intern.resource.dvid.resource import *
import requests
import json


class MetadataService(DVIDService):
    """MetadataService for DVID service.
    """

    def __init__(self, base_url):
        """Constructor.

        Attributes:
            base_url (str): Base url to project service.

        Raises:
            (KeyError): if given invalid version.
        """
        DVIDService.__init__(self)
        self.base_url = base_url

    def get_info(self, resource):
        """Returns JSON for just the repository with given root UUID.  The UUID str can be
            shortened as long as it is uniquely identifiable across the managed repositories.

        Args:
            UUID (str): UUID of the DVID repository (str)

        Returns:
            str: History information of the repository

        Raises:
            (HTTPError): on invalid HTTP request.

        """
        if isinstance(resource, DataInstanceResource):
            response = requests.get(
                "{}/api/node/{}/{}/info".format(
                    self.base_url, resource.UUID, resource.name
                )
            )
            if response.status_code != 200:
                raise requests.HTTPError(response.content)
            return response.json()

        if isinstance(resource, RepositoryResource):
            response = requests.get(
                "{}/api/repo/{}/info".format(self.base_url, resource.UUID)
            )
            if response.status_code != 200:
                raise requests.HTTPError(response.content)
            return response.json()

    def get_server_info(self):
        """Returns JSON for server properties
        """
        info = requests.get("{}/api/server/info".format(self.base_url))
        if info.status_code != 200:
            raise requests.HTTPError(info.content)
        return info.json()

    def get_server_types(self):
        """Returns JSON with datatypes of currently stored data instances
        """
        info = requests.get("{}/api/server/types".format(self.base_url))
        if info.status_code != 200:
            raise requests.HTTPError(info.content)
        return info.json()

    def get_server_compiled_types(self):
        """Returns JSON of all possible datatypes for this server
        """
        info = requests.get("{}/api/server/compiled-types".format(self.base_url))
        if info.status_code != 200:
            raise requests.HTTPError(info.content)
        return info.json()

    def server_reload_metadata(self):
        """Reloads the metadata from storage
        """
        info = requests.post("{}/api/server/reload-metadata".format(self.base_url))
        if info.status_code != 200:
            raise requests.HTTPError(info.content)

    def create_metadata(self, resource, metadata):
        """Posts metadata to a specific DataInstance resource

        Args:
            resource : DatInstance resource to which to relate metadata
            metadata (dict) : JSON format metadata to post
                Example:
                {
                    "MinTileCoord": [0, 0, 0],
                    "MaxTileCoord": [5, 5, 4],
                    "Levels": {
                        "0": {  "Resolution": [10.0, 10.0, 10.0], "TileSize": [512, 512, 512] },
                        "1": {  "Resolution": [20.0, 20.0, 20.0], "TileSize": [512, 512, 512] },
                        "2": {  "Resolution": [40.0, 40.0, 40.0], "TileSize": [512, 512, 512] },
                        "3": {  "Resolution": [80.0, 80.0, 80.0], "TileSize": [512, 512, 512] }
                    }
                }
        """
        resp = requests.post(
            "{}/api/node/{}/{}/metadata".format(
                self.base_url, resource.UUID, resource.name
            ),
            data=metadata,
        )
        if resp.status_code != 200:
            raise requests.HTTPError(resp.content)

    def get_metadata(self, resource):
        """Gets metadata to a specific DataInstance resource

        Args:
            resource : DatInstance resource to which to relate metadata

        Returns:
            metaddata (JSON): Metadata of specified resource in JSON format
        """
        resp = requests.get(
            "{}/api/node/{}/{}/metadata".format(
                self.base_url, resource.UUID, resource.name
            )
        )
        if resp.status_code != 200:
            raise requests.HTTPError(resp.content)
        return resp.json()

    def get_extents(self, resource):
        """Gets extents to a specific DataInstance resource

        Args:
            resource : DatInstance resource to which to relate metadata

        Returns:
            extents (array): [[x-min, x-max], [y-min, y-max], [z-min, z-max]]
        """
        metadata = self.get_metadata(resource)
        min_point = metadata["Properties"]["MinPoint"]
        max_point = metadata["Properties"]["MaxPoint"]
        extents = [
            [min_point[0], max_point[0]],
            [min_point[1], max_point[1]],
            [min_point[2], max_point[2]],
        ]
        return extents

    def create_default_metadata(self, resource):
        """Method to create default metadata on a DataInstance Resource.

        Args:
            resource : DatInstance resource to which to relate metadata
        """
        meta_data = json.dumps(
            {
                "MinTileCoord": [0, 0, 0],
                "MaxTileCoord": [128, 128, 128],
                "Levels": {"0": {"Resolution": [0, 0, 0], "TileSize": [128, 128, 1]}},
            }
        )
        self.create_metadata(resource, meta_data)
