# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
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

from intern.resource.dvid import DataInstanceResource, RepositoryResource
from intern.service.dvid import DVIDService
from intern.utils.parallel import *
from requests import HTTPError
import requests
import numpy as np
import json
import blosc

def check_channel(fcn):
    """Decorator that ensures a valid channel passed in.

    Args:
        fcn (function): Function that has a ChannelResource as its second argument.

    Returns:
        (function): Wraps given function with one that checks for a valid channel.
    """

    def wrapper(*args, **kwargs):
        if not isinstance(args[1], DataInstanceResource):
            raise RuntimeError('resource must be an instance of intern.resource.intern.ChannelResource.')
        return fcn(*args, **kwargs)

    return wrapper

class VolumeService(DVIDService):
    """
        VolumeService for DVID service.
    """
    def __init__(self, base_url):
        """Constructor.

        Args:
            base_url (str): Base url (host) of project service.

        Raises:
            (KeyError): if given invalid version.
        """
        DVIDService.__init__(self)
        self.base_url = base_url

    @check_channel
    def get_cutout(self, resource, resolution, x_range, y_range, z_range, **kwargs):

        """
        Upload a cutout to the Boss data store.

        Args:
            resource (intern.resource.resource.Resource): Resource compatible
                with cutout operations
            resolution (int): 0 (not applicable on DVID Resource).
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            chunk_size (optional Tuple[int, int, int]): The chunk size to request

        Returns:
            (numpy.array): A 3D or 4D numpy matrix in ZXY(time) order.

        Raises:
            requests.HTTPError
        """
        chunk_size = kwargs.pop("chunk_size", (512, 512, 16 * 8))
        # TODO: magic number
        chunk_limit = (chunk_size[0] * chunk_size[1] * chunk_size[2]) * 1.2

        cutout_size = (
                (x_range[1] - x_range[0]) *
                (y_range[1] - y_range[0]) *
                (z_range[1] - z_range[0])
            )
        
        if cutout_size > chunk_limit:
            blocks = block_compute(
                x_range[0], x_range[1],
                y_range[0], y_range[1],
                z_range[0], z_range[1],
                block_size=chunk_size
            )

            result = np.ndarray((
                z_range[1] - z_range[0],
                y_range[1] - y_range[0],
                x_range[1] - x_range[0]
            ), dtype=resource.datatype)

            for b in blocks:
                _data = self.get_cutout(
                    resource, resolution, b[0], b[1], b[2], **kwargs
                )

                result[
                    b[2][0] - z_range[0] : b[2][1] - z_range[0],
                    b[1][0] - y_range[0] : b[1][1] - y_range[0],
                    b[0][0] - x_range[0] : b[0][1] - x_range[0]
                ] = _data

            return result
        
        x_size = x_range[1] - x_range[0]
        y_size = y_range[1] - y_range[0]
        z_size = z_range[1] - z_range[0]
        # Make the request
        resp = requests.get('{}/api/node/{}/{}/tile/xy/{}/{}_{}_{}'.format(
            self.base_url,
            resource.UUID,
            resource.name,
            resolution,
            x_range[0], y_range[0], z_range[0]
        ))

        if resp.status_code != 200 or resp.status_code == 201:
            msg = ('Get cutout failed on {}, got HTTP response: ({}) - {}'.format(
                resource.name, resp.status_code, resp.text))
            raise HTTPError(msg, response=resp)
        
        cutout = blosc.unpack_array(resp.content)
        return cutout

    @check_channel
    def create_cutout(self, resource, resolution, x_range, y_range, z_range, numpyVolume, send_opts):
        """Upload a cutout to the volume service.
            NOTE: This method will fail if no metadata has been added to the channel. 

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            numpyVolume (numpy.array): A 3D or 4D (time) numpy matrix in (time)ZYX order.
            send_opts (dictionary): Additional arguments to pass to session.send().
        """
        # Check that the data array is C Contiguous
        if not numpyVolume.flags['C_CONTIGUOUS']:
            raise ValueError('Expected data to be C_CONTINUGOUS but it was not')
        # Define resolution if not passed
        if resolution is None:
            resolution = 0

        # Check to see if this volume is larger than 1GB. If so, chunk it into
        # several smaller bites:
        if (
                (x_range[1] - x_range[0]) *
                (y_range[1] - y_range[0]) *
                (z_range[1] - z_range[0])
        ) > 1024 * 1024 * 32 * 2:
            blocks = block_compute(
                x_range[0], x_range[1],
                y_range[0], y_range[1],
                z_range[0], z_range[1],
                block_size=(1024, 1024, 32)
            )

            for b in blocks:
                _data = np.ascontiguousarray(
                    numpyVolume[
                        b[2][0] - z_range[0]: b[2][1] - z_range[0],
                        b[1][0] - y_range[0]: b[1][1] - y_range[0],
                        b[0][0] - x_range[0]: b[0][1] - x_range[0]
                    ],
                    dtype=numpyVolume.dtype
                )
                self.create_cutout(
                    resource, resolution, b[0], b[1], b[2] ,_data, None)
            return

        # Compress the data
        # NOTE: This is a convenient way for compressing/decompressing NumPy arrays, however
        # this method uses pickle/unpickle which means we make additional copies that consume
        # a bit of extra memory and time. 
        compressed = blosc.pack_array(numpyVolume)

        # Make the request
        resp = requests.post('{}/api/node/{}/{}/tile/xy/{}/{}_{}_{}'.format(
            self.base_url,
            resource.UUID,
            resource.name,
            resolution,
            x_range[0], y_range[0], z_range[0],
            data = compressed))

        if resp.status_code != 200 or resp.status_code == 201:
            msg = ('Create cutout failed on {}, got HTTP response: ({}) - {}'.format(
                resource.name, resp.status_code, resp.text))
            raise HTTPError(msg, response=resp)
        return