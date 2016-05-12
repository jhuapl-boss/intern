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
from ndio.service.boss.v0_4.volume import VolumeService_0_4

class VolumeService(Service):
    """VolumeService routes calls to the appropriate API version.
    """
    def __init__(self, base_url):
        """Constructor.

        Args:
            base_url (string): Base url (host) of project service such as 'api.boss.io'.
        """
        super().__init__()
        self.base_url = base_url
        self._versions = {
            'v0.4': VolumeService_0_4()
        }

    def cutout_create(
        self, resource, resolution, x_range, y_range, z_range, numpyVolume):
        ps = self.get_api_impl(resource.version)
        return ps.cutout_create(
            resource, resolution, x_range, y_range, z_range, numpyVolume,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    def cutout_get(self, resource, resolution, x_range, y_range, z_range):
        ps = self.get_api_impl(resource.version)
        return ps.cutout_get(
            resource, resolution, x_range, y_range, z_range,
            self.url_prefix, self.auth, self.session, self.session_send_opts)
