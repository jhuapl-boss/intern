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

from ndio.remote.remote import Remote as NdRemote

class Remote(NdRemote):
    def __init__(self):
        # Get token.
        # Init services.
        # Pass token to services.
        pass

    def _load_token_from_disk(self, path):
        pass

    def set_resource(self, resource, **kwargs):
        self._resource = resource

    def set_token(self, token):
        pass

    def project_list(self):
        self._project.list(self._resource)

    def project_create(self):
        self._project.create(self._resource)

    def project_get(self):
        self._project.get(self._resource)

    def project_update(self):
        self._project.update(self._resource)

    def project_delete(self):
        self._project.delete(self._resource)

    def list_metadata(self):
        self._metadata.list(self._resource)

    def create_metadata(self, key, val):
        self._metadata.create(self._resource, key, val)

    def get_metadata(self, key):
        return self._metadata.get(self._resource, key)

    def update_metadata(self, key, val):
        self._metadata.update(self._resource, key, val)

    def delete_metadata(self, key):
        self._metadata.delete(self._resource, key)
