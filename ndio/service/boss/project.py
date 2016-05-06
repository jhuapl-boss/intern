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
        ps = self.get_api_impl(resource.version)
        return ps.list(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def create(self, resource):
        ps = self.get_api_impl(resource.version)
        return ps.create(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def get(self, resource):
        ps = self.get_api_impl(resource.version)
        return ps.get(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)

    def update(self, old_resource, new_resource):
        ps = self.get_api_impl(old_resource.version)
        ps.update(
            old_resource, new_resource, self.url_prefix, self.auth, 
            self.session, self.session_send_opts)

    def delete(self, resource):
        ps = self.get_api_impl(resource.version)
        ps.delete(
            resource, self.url_prefix, self.auth, self.session,
            self.session_send_opts)
