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

class VolumeService_0_5(Base):
    def __init__(self):
        super().__init__()

    @property
    def endpoint(self):
        return 'cutout'

    def cutout_create(
        self, resource, resolution, x_range, y_range, z_range, time_range, numpyVolume,
        url_prefix, auth, session, send_opts):
        """Upload a cutout to the Boss data store.

        Args:
            resource (ndio.ndresource.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (string): x range such as '10:20' which means x>=10 and x<20.
            y_range (string): y range such as '10:20' which means y>=10 and y<20.
            z_range (string): z range such as '10:20' which means z>=10 and z<20.
            time_range (string): None or time range such as 30:40 which means t>=30 and t<40.
            numpyVolume (numpy.array): A 3D or 4D (time) numpy matrix in (time)ZYX order.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (bool): True on success.
        """

        compressed = blosc.pack_array(numpyVolume)
        req = self.get_cutout_request(
            resource, 'POST', 'application/blosc-python',
            url_prefix, auth,
            resolution, x_range, y_range, z_range, time_range, compressed)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        
        if resp.status_code == 201:
            return True

        print('Create cutout failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        return False

    def cutout_get(
        self, resource, resolution, x_range, y_range, z_range, time_range,
        url_prefix, auth, session, send_opts):
        """Upload a cutout to the Boss data store.

        Args:
            resource (ndio.ndresource.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (string): x range such as '10:20' which means x>=10 and x<20.
            y_range (string): y range such as '10:20' which means y>=10 and y<20.
            z_range (string): z range such as '10:20' which means z>=10 and z<20.
            time_range (string): None or time range such as 30:40 which means t>=30 and t<40.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (numpy.array): A 3D or 4D numpy matrix in ZXY(time) order.

        Raises:
            requests.HTTPError
        """

        req = self.get_cutout_request(
            resource, 'GET', 'application/blosc-python',
            url_prefix, auth, resolution, x_range, y_range, z_range, time_range)
        prep = session.prepare_request(req)
        # Hack in Accept header for now.
        prep.headers['Accept'] = 'application/blosc-python'
        #resp = session.send(prep, stream = True, **send_opts)
        resp = session.send(prep, **send_opts)
        
        if resp.status_code == 200:
            return blosc.unpack_array(resp.content)

        resp.raise_for_status()
