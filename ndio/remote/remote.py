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
    def __init__(self):
        self._resource = None
        self._volume = None
        self._metadata = None
        self._project = None
        self._object = None

    @abstractmethod
    def set_resource(self, **kwargs):
        """
        Sets self._resource to pass to other operations.  For the Boss, this
        could be a:
            collection, experiment, channel, or layer.
        """
        pass

    @property
    def resource(self):
        return self._resource

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

    def get_cutout(
        self, resolution, x_range, y_range, z_range):

        if not self._resource.valid_volume():
            raise some_err
        return self._volume.get_cutout(
            self._resource, channel, resolution, x_range, y_range, z_range)

    def create_cutout(
        self, resolution, x_range, y_range, z_range, data):

        if not self._resource.valid_volume():
            raise some_err
        self._volume.create_cutout(
            self._resource, x_range, y_range, z_range, data)
