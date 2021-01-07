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

from intern.resource.boss import ChannelResource, PartialChannelResourceError
from intern.service.boss import BossService
from intern.service.boss.v1.volume import VolumeService_1
from intern.service.boss.v1.volume import CacheMode

def check_channel(fcn):
    """Decorator that ensures a valid channel passed in.

    Args:
        fcn (function): Function that has a ChannelResource as its second argument.

    Returns:
        (function): Wraps given function with one that checks for a valid channel.
    """

    def wrapper(*args, **kwargs):
        if not isinstance(args[1], ChannelResource):
            raise RuntimeError('resource must be an instance of intern.resource.boss.ChannelResource.')

        if not args[1].cutout_ready:
            raise PartialChannelResourceError(
                    'ChannelResource not fully initialized.  Use intern.remote.BossRemote.get_channel({}, {}, {})'.format(
                        args[1].name, args[1].coll_name, args[1].exp_name))
        return fcn(*args, **kwargs)

    return wrapper


class VolumeService(BossService):
    """VolumeService routes calls to the appropriate API version.
    """
    def __init__(self, base_url, version):
        """Constructor.

        Args:
            base_url (string): Base url (host) of project service such as 'api.boss.io'.
            version (string): Version of Boss API to use.

        Raises:
            (KeyError): if given invalid version.
        """
        BossService.__init__(self)
        self.base_url = base_url
        self._versions = {
            'v1': VolumeService_1()
        }
        self.service = self.get_api_impl(version)

    @check_channel
    def create_cutout(
        self, resource, resolution, x_range, y_range, z_range, numpyVolume, time_range=None):
        """Upload a cutout to the volume service.

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            numpyVolume (numpy.array): A 3D or 4D (time) numpy matrix in (time)ZYX order.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
        """


        return self.service.create_cutout(
            resource, resolution, x_range, y_range, z_range, time_range, numpyVolume,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    @check_channel
    def create_cutout_to_black(
        self, resource, resolution, x_range, y_range, z_range, time_range=None):
        """Upload a black cutout to the volume service.

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
        """


        return self.service.create_cutout_to_black(
            resource, resolution, x_range, y_range, z_range, time_range,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    @check_channel
    def get_cutout(self, resource, resolution, x_range, y_range, z_range, time_range=None, id_list=[], access_mode=CacheMode.no_cache, parallel=True, **kwargs):
        """Get a cutout from the volume service.

        Args:
            resource (intern.resource.boss.resource.ChannelResource): Channel or layer resource.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            id_list (optional [list[int]]): list of object ids to filter the cutout by.
            no_cache (optional [boolean]): specifies the use of cache to be True or False. 
            access_mode (optional [Enum]): Identifies one of three cache access options:
                cache = Will check both cache and for dirty keys
                no_cache = Will skip cache check but check for dirty keys
                raw = Will skip both the cache and dirty keys check
            parallel (Union[int, bool]: True): Whether downloads should be parallelized using 
                multiprocessing. If set to True, will use all available CPUs. If set to False,
                will use only one CPU. If set to an integer, will spawn that number of threads.

        Returns:
            (numpy.array): A 3D or 4D (time) numpy matrix in (time)ZYX order.

        Raises:
            requests.HTTPError on error.
        """

        return self.service.get_cutout(
            resource, resolution, x_range, y_range, z_range, time_range, id_list,
            self.url_prefix, self.auth, self.session, self.session_send_opts, access_mode, parallel, **kwargs)

    @check_channel
    def reserve_ids(self, resource, num_ids):
        """Reserve a block of unique, sequential ids for annotations.

        Args:
            resource (intern.resource.Resource): Resource should be an annotation channel.
            num_ids (int): Number of ids to reserve.

        Returns:
            (int): First id reserved.

        """
        return self.service.reserve_ids(
            resource, num_ids,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    @check_channel
    def get_bounding_box(self, resource, resolution, id, bb_type='loose'):
        """Get bounding box containing object specified by id.

        Currently only supports 'loose' bounding boxes.  The bounding box
        returned is cuboid aligned.

        Args:
            resource (intern.resource.Resource): Resource compatible with annotation operations.
            resolution (int): 0 indicates native resolution.
            id (int): Id of object of interest.
            bb_type (optional[string]): Defaults to 'loose'.

        Returns:
            (dict): {'x_range': [0, 10], 'y_range': [0, 10], 'z_range': [0, 10], 't_range': [0, 10]}
        """
        return self.service.get_bounding_box(
            resource, resolution, id, bb_type,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    @check_channel
    def get_ids_in_region(
            self, resource, resolution,
            x_range, y_range, z_range, time_range=[0, 1]):
        """Get all ids in the region defined by x_range, y_range, z_range.

        Args:
            resource (intern.resource.Resource): An annotation channel.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.  Defaults to [0, 1].

        Returns:
            (list[int]): Example: [1, 2, 25].

        Raises:
            requests.HTTPError
            TypeError: if resource is not an annotation channel.
        """
        return self.service.get_ids_in_region(
            resource, resolution, x_range, y_range, z_range, time_range,
            self.url_prefix, self.auth, self.session, self.session_send_opts)

    @check_channel
    def get_neuroglancer_link(self, resource, resolution, x_range, y_range, z_range, **kwargs):
        """
        Get a neuroglancer link of the cutout specified from the host specified in the remote configuration step. 

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.

        Returns:
            (string): Return neuroglancer link.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.
        """
        return self.service.get_neuroglancer_link(resource, resolution, x_range, y_range, z_range, self.url_prefix, **kwargs)
