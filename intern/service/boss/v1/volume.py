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
from intern.service.boss import BaseVersion
from intern.service.boss.v1 import BOSS_API_VERSION
from intern.resource.boss.resource import *
from intern.utils.parallel import *
from requests import HTTPError
import multiprocessing
import blosc
import numpy as np
from enum import Enum

class CacheMode(str, Enum):
    cache = 'cache'
    no_cache = 'no-cache'
    raw = 'raw'

class VolumeService_1(BaseVersion):
    def __init__(self):
        BaseVersion.__init__(self)

    @property
    def version(self):
        """Return the API Version for this implementation
        """
        return BOSS_API_VERSION

    def get_bit_width(self, resource):
        """Method to return the bit width for blosc based on the Resource"""
        datatype = resource.datatype

        if "uint" in datatype:
            bit_width = int(datatype.split("uint")[1])
        else:
            raise ValueError("Unsupported datatype: {}".format(datatype))

        return bit_width

    def create_cutout(
        self, resource, resolution, x_range, y_range, z_range, time_range, numpyVolume,
        url_prefix, auth, session, send_opts):
        """Upload a cutout to the Boss data store.

        Args:
            resource (intern.resource.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            numpyVolume (numpy.array): A 3D or 4D (time) numpy matrix in (time)ZYX order.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().
        """

        if numpyVolume.ndim == 3:
            # Can't have time
            if time_range is not None:
                raise ValueError(
                    "You must provide a 4D matrix if specifying a time range")
        elif numpyVolume.ndim == 4:
            # must have time
            if time_range is None:
                raise ValueError(
                    "You must specifying a time range if providing a 4D matrix")
        else:
            raise ValueError(
                "Invalid data format. Only 3D or 4D cutouts are supported. " +
                "Number of dimensions: {}".format(numpyVolume.ndim)
            )

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
                    resource, resolution, b[0], b[1], b[2],
                    time_range, _data, url_prefix, auth, session, send_opts
                )
            return

        compressed = blosc.compress(
            numpyVolume, typesize=self.get_bit_width(resource)
        )
        req = self.get_cutout_request(
            resource, 'POST', 'application/blosc',
            url_prefix, auth,
            resolution, x_range, y_range, z_range, time_range, numpyVolume=compressed)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 201:
            return

        msg = ('Create cutout failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def get_cutout(
            self, resource, resolution, x_range, y_range, z_range, time_range, id_list,
            url_prefix, auth, session, send_opts, access_mode=CacheMode.no_cache, parallel: bool = True, **kwargs
        ):
        """
        Upload a cutout to the Boss data store.

        Args:
            resource (intern.resource.resource.Resource): Resource compatible
                with cutout operations
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range ([list[int]]|None): time range such as [30, 40] which means t>=30 and t<40.
            id_list (list[int]): list of object ids to filter the cutout by.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().
            access_mode (optional [Enum]): Identifies one of three cache access options:
                cache = Will check both cache and for dirty keys
                no_cache = Will skip cache check but check for dirty keys
                raw = Will skip both the cache and dirty keys check
            chunk_size (optional Tuple[int, int, int]): The chunk size to request
            parallel (bool: True): Whether downloads should be parallelized using multiprocessing


        Returns:
            (numpy.array): A 3D or 4D numpy matrix in ZXY(time) order.

        Raises:
            requests.HTTPError
        """
        chunk_size = kwargs.pop("chunk_size", (512, 512, 16 * 8))
        # TODO: magic number
        chunk_limit = (chunk_size[0] * chunk_size[1] * chunk_size[2]) * 1.2

        # Check to see if this volume is larger than a single request. If so,
        # chunk it into several smaller bites:
        if time_range:
            cutout_size = (
                (x_range[1] - x_range[0]) *
                (y_range[1] - y_range[0]) *
                (z_range[1] - z_range[0]) *
                (time_range[1] - time_range[0])
            )
        else:
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

            if parallel:
                pool = multiprocessing.Pool(processes=parallel if isinstance(parallel, int) and parallel > 0 else multiprocessing.cpu_count())
                chunks = pool.starmap(self.get_cutout, [
                    (
                        resource, resolution, b[0], b[1], b[2],
                        time_range, id_list, url_prefix, auth, session, send_opts,
                        access_mode
                        # TODO: kwargs
                    )
                 for b in blocks])

                for b, data in zip(blocks, chunks):
                    result[
                        b[2][0] - z_range[0] : b[2][1] - z_range[0],
                        b[1][0] - y_range[0] : b[1][1] - y_range[0],
                        b[0][0] - x_range[0] : b[0][1] - x_range[0]
                    ] = data
            else:
                for b in blocks:
                    _data = self.get_cutout(
                        resource, resolution, b[0], b[1], b[2],
                        time_range, id_list, url_prefix, auth, session, send_opts,
                        access_mode, **kwargs
                    )

                    result[
                        b[2][0] - z_range[0] : b[2][1] - z_range[0],
                        b[1][0] - y_range[0] : b[1][1] - y_range[0],
                        b[0][0] - x_range[0] : b[0][1] - x_range[0]
                    ] = _data

            return result

        req = self.get_cutout_request(
            resource, 'GET', 'application/blosc',
            url_prefix, auth,
            resolution, x_range, y_range, z_range, time_range, access_mode=access_mode,
            id_list=id_list, **kwargs
        )
        prep = session.prepare_request(req)
        # Hack in Accept header for now.
        prep.headers['Accept'] = 'application/blosc'
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            raw_data = blosc.decompress(resp.content)
            data_mat = np.fromstring(raw_data, dtype=resource.datatype)

            if time_range:
                # Reshape including time
                return np.reshape(data_mat,
                                  (time_range[1] - time_range[0],
                                   z_range[1] - z_range[0],
                                   y_range[1] - y_range[0],
                                   x_range[1] - x_range[0]),
                                  order='C')
            else:
                # Reshape without including time
                return np.reshape(data_mat,
                                  (z_range[1] - z_range[0],
                                   y_range[1] - y_range[0],
                                   x_range[1] - x_range[0]),
                                  order='C')

        msg = ('Get cutout failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def reserve_ids(
            self, resource, num_ids,
            url_prefix, auth, session, send_opts):
        """Reserve a block of unique, sequential ids for annotations.

        Args:
            resource (intern.resource.Resource): Resource should be an annotation channel.
            num_ids (int): Number of ids to reserve.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (int): First id reserved.

        Raises:
            (TypeError): resource is not a channel or not an annotation channel.

        """
        if not isinstance(resource, ChannelResource):
            raise TypeError('resource must be ChannelResource')
        if resource.type != 'annotation':
            raise TypeError('Channel is not an annotation channel')

        req = self.get_reserve_request(
            resource, 'GET', 'application/json', url_prefix, auth, num_ids)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            json_data = resp.json()
            return int(json_data['start_id'])

        msg = ('Reserve ids failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def get_bounding_box(
            self, resource, resolution, _id, bb_type,
            url_prefix, auth, session, send_opts):
        """Get bounding box containing object specified by id.

        Currently only supports 'loose' bounding boxes.  The bounding box
        returned is cuboid aligned.

        Args:
            resource (intern.resource.Resource): Resource compatible with annotation operations.
            resolution (int): 0 indicates native resolution.
            _id (int): Id of object of interest.
            bb_type (string): Defaults to 'loose'.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dict): {'x_range': [0, 10], 'y_range': [0, 10], 'z_range': [0, 10], 't_range': [0, 10]}

        Raises:
            requests.HTTPError
            TypeError: if resource is not an annotation channel.
        """
        if not isinstance(resource, ChannelResource):
            raise TypeError('resource must be ChannelResource')
        if resource.type != 'annotation':
            raise TypeError('Channel is not an annotation channel')

        req = self.get_bounding_box_request(
            resource, 'GET', 'application/json', url_prefix, auth, resolution,
            _id, bb_type)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            json_data = resp.json()
            return json_data

        msg = ('Get bounding box failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def get_ids_in_region(
            self, resource, resolution, x_range, y_range, z_range, time_range,
            url_prefix, auth, session, send_opts):
        """Get all ids in the region defined by x_range, y_range, z_range.

        Args:
            resource (intern.resource.Resource): An annotation channel.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list[int]): Example: [1, 2, 25].

        Raises:
            requests.HTTPError
            TypeError: if resource is not an annotation channel.
        """
        if not isinstance(resource, ChannelResource):
            raise TypeError('resource must be ChannelResource')
        if resource.type != 'annotation':
            raise TypeError('Channel is not an annotation channel')

        req = self.get_ids_request(
            resource, 'GET', 'application/json', url_prefix, auth,
            resolution, x_range, y_range, z_range, time_range)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            json_data = resp.json()
            id_str_list = json_data['ids']
            id_int_list = [int(i) for i in id_str_list]
            return id_int_list

        msg = ('Get bounding box failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def get_neuroglancer_link(self, resource, resolution, x_range, y_range, z_range, url_prefix, **kwargs):
        """
        Get a neuroglancer link of the cutout specified from the host specified in the remote configuration step.

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            url_prefix (string): Protocol + host such as https://api.theboss.io

        Returns:
            (string): Return neuroglancer link.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.
        """
        link = "https://neuroglancer.theboss.io/#!{'layers':{'" + str(resource.name)   + "':{'type':'" + resource.type + "'_'source':" + "'boss://" + url_prefix+ "/" + resource.coll_name + "/" + resource.exp_name + "/" + resource.name + "'}}_'navigation':{'pose':{'position':{'voxelCoordinates':[" + str(x_range[0]) + "_" + str(y_range[0]) + "_" + str(z_range[0]) + "]}}}}"
        return link
