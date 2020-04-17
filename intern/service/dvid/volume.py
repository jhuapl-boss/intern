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

from intern.resource.dvid import DataInstanceResource, RepositoryResource
from intern.service.dvid import DVIDService
from intern.utils.parallel import *
from requests import HTTPError
import requests
import numpy as np
import json
import blosc


def check_data_instance(fcn):
    """Decorator that ensures a valid data instance is passed in.

    Args:
        fcn (function): Function that has a DataInstanceResource as its second argument.

    Returns:
        (function): Wraps given function with one that checks for a valid data instance.
    """

    def wrapper(*args, **kwargs):
        if not isinstance(args[1], DataInstanceResource):
            raise RuntimeError(
                "resource must be an instance of intern.resource.intern.DataInstanceResource."
            )
        return fcn(*args, **kwargs)

    return wrapper


class VolumeService(DVIDService):
    """VolumeService for DVID service.
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

    @check_data_instance
    def get_cutout(self, resource, resolution, x_range, y_range, z_range, **kwargs):

        """Download a cutout from DVID data store.

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
        x_size = x_range[1] - x_range[0]
        y_size = y_range[1] - y_range[0]
        z_size = z_range[1] - z_range[0]
        # Make the request
        resp = requests.get(
            "{}/api/node/{}/{}/raw/0_1_2/{}_{}_{}/{}_{}_{}/octet-stream".format(
                self.base_url,
                resource.UUID,
                resource.name,
                x_size,
                y_size,
                z_size,
                x_range[0],
                y_range[0],
                z_range[0],
            )
        )

        if resp.status_code != 200 or resp.status_code == 201:
            msg = "Get cutout failed on {}, got HTTP response: ({}) - {}".format(
                resource.name, resp.status_code, resp.text
            )
            raise HTTPError(msg, response=resp)

        block = np.frombuffer(resp.content, dtype=resource.datatype)
        cutout = block.reshape(z_size, y_size, x_size)
        return cutout

    @check_data_instance
    def create_cutout(
        self, resource, resolution, x_range, y_range, z_range, numpyVolume, send_opts
    ):
        """Upload a cutout to the volume service.
            NOTE: This method will fail if no metadata has been added to the data instance.

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
        blktypes = ["uint8blk", "labelblk", "rgba8blk"]

        if not numpyVolume.flags["C_CONTIGUOUS"]:
            numpyVolume = np.ascontiguousarray(numpyVolume)

        if resource._type == "tile":
            # Compress the data
            # NOTE: This is a convenient way for compressing/decompressing NumPy arrays, however
            # this method uses pickle/unpickle which means we make additional copies that consume
            # a bit of extra memory and time.
            compressed = blosc.pack_array(numpyVolume)
            url_req = "{}/api/node/{}/{}/tile/xy/{}/{}_{}_{}".format(
                self.base_url,
                resource.UUID,
                resource.name,
                resolution,
                x_range[0],
                y_range[0],
                z_range[0],
            )
            out_data = compressed

        # Make the request
        elif resource._type in blktypes:
            numpyVolume = numpyVolume.tobytes(order="C")
            url_req = "{}/api/node/{}/{}/raw/0_1_2/{}_{}_{}/{}_{}_{}".format(
                self.base_url,
                resource.UUID,
                resource.name,
                x_range[1] - x_range[0],
                y_range[1] - y_range[0],
                z_range[1] - z_range[0],
                x_range[0],
                y_range[0],
                z_range[0],
            )
            out_data = numpyVolume
        else:
            raise NotImplementedError(
                "{} type is not yet implemented in create_cutout".format(resource._type)
            )

        resp = requests.post(url_req, data=out_data)

        if resp.status_code != 200 or resp.status_code == 201:
            msg = "Create cutout failed on {}, got HTTP response: ({}) - {}".format(
                resource.name, resp.status_code, resp.text
            )
            raise HTTPError(msg, response=resp)
        return
