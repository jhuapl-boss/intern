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
import blosc

class VolumeService_0_4(Base):
    def __init__(self):
        super().__init__()

    @property
    def endpoint(self):
        return 'cutout'

    def create_cutout(
        self, resource, resolution, x_range, y_range, z_range, numpyVolume,
        url_prefix, auth, session, send_opts):

        compressed = blosc.pack_array(numpyVolume)
        req = self.get_cutout_request(
            resource, 'POST', 'application/blosc-python',
            url_prefix, auth, resolution, x_range, y_range, z_range, compressed)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        
        if resp.status_code == 201:
            return True

        print('Create cutout failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        return False

    def get_cutout(
        self, resource, resolution, x_range, y_range, z_range,
        url_prefix, auth, session, send_opts):
        pass