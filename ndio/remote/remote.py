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

from abc import ABCMeta
from abc import abstractmethod

class Remote(metaclass=ABCMeta):
    """Base class for communicating with remote neuro data stores.

    Attributes:
        _volume (ndio.service.service.Service): Class that communicates with the volume service.
        _metadata (ndio.service.service.Service): Class that communicates with the metadata service.
        _project (ndio.service.service.Service): Class that communicates with the project service.
        _object (ndio.service.service.Service): Class that communicates with the volume service.
    """

    def __init__(self):
        self._volume = None
        self._metadata = None
        self._project = None
        self._object = None

    @property
    def volume_service(self):
        return self._volume
    @property
    def project_service(self):
        return self._project
    @property
    def metadata_service(self):
        return self._metadata

    @property
    def object_service(self):
        return self._object

    def cutout_get(self, resource, resolution, x_range, y_range, z_range, time_range=None):
        """Get a cutout from the volume service.

        Args:
            resource (ndio.ndresource.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.

        Returns:
            (): Return type depends on volume service's implementation.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.
        """

        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')
        return self._volume.cutout_get(
            resource, resolution, x_range, y_range, z_range, time_range)

    def cutout_create(self, resource, resolution, x_range, y_range, z_range, data, time_range=None):
        """Upload a cutout to the volume service.

        Args:
            resource (ndio.ndresource.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            data (object): Type depends on implementation.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.

        Returns:
            (): Return type depends on volume service's implementation.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.
        """

        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')
        return self._volume.cutout_create(
            resource, resolution, x_range, y_range, z_range, data, time_range)
