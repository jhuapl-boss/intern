﻿# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
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

from ndio.ndresource.resource import Resource as NdResource
from . import BOSS_DEFAULT_VERSION
from abc import abstractmethod

class Resource(NdResource):
    """Base class for Boss resources.

    Attributes:
        name (string): Name of resource.  Used as identifier when talking to
        the Boss API.
        description (string): Text description of resource.
        version (string): API version of Boss to use.
    """
    def __init__(self, name, description, version=BOSS_DEFAULT_VERSION):
        # ToDo: validate version.
        self.version = version
        self.name = name
        self.description = description

    def valid_volume(self):
        return False

    @abstractmethod
    def get_route(self):
        """Get the resource as a route to pass as an HTTP request.

        Returns:
            (string): A string that can be appended to the location of an
            endpoint such as 'mycollection/experiment1/channel1'
        """

    @abstractmethod
    def get_project_list_route(self):
        """Get the route, to list resources of this type, to pass as an HTTP request.

        Getting a list from the project service uses a slightly different URL
        than the other operations.  It uses the plural form of the resource's
        type such as 'collections' and 'channels'.

        Returns:
            (string): A string that can be appended to the location of an
            endpoint such as 'mycollection/experiment1/channels'
        """


class CollectionResource(Resource):
    """Top level container for Boss projects.
    """
    def __init__(self, name, version=BOSS_DEFAULT_VERSION, description=''):
        super().__init__(name, description, version)

    def get_route(self):
        return self.name

    def get_project_list_route(self):
        return 'collections'


class ExperimentResource(Resource):
    """Experiments reside inside a collection and contain channels and
    layers.

    Attributes:
        coord_frame (int):
        num_hierarchy_levels (int):
        hierarchy_method (string):
        max_time_sample (int):
    """
    def __init__(self, name, collection_name,
        version=BOSS_DEFAULT_VERSION, description='', coord_frame=0,
        num_hierarchy_levels=1, hierarchy_method='near_iso',
        max_time_sample=0):
        
        super().__init__(name, description, version)
        self.coll_name = collection_name

        self._valid_hierarchy_methods = ['near_iso', 'iso', 'slice']

        #ToDo: validate data types.
        self.coord_frame = coord_frame
        self.num_hierarchy_levels = num_hierarchy_levels
        self._hierarchy_method = self.validate_hierarchy_method(
            hierarchy_method)
        self.max_time_sample = max_time_sample

    @property
    def hierarchy_method(self):
        return self._hierarchy_method

    @hierarchy_method.setter
    def hierarchy_method(self, value):
        """
        Args:
            value (string): Valid values: 'near_iso', 'iso', 'slice'
        Raises:
            ValueError
        """
        self._hierarchy_method = self.validate_hierarchy_method(value)

    def get_route(self):
        return self.coll_name + '/' + self.name

    def get_project_list_route(self):
        return self.coll_name + '/experiments'

    def validate_hierarchy_method(self, value):
        lowered = value.lower()
        if lowered in self._valid_hierarchy_methods:
            return lowered
        raise ValueError('{} is not a valid hierarchy method.'.format(value))


class CoordinateFrameResource(Resource):
    def __init__(
        self, name, version=BOSS_DEFAULT_VERSION, description='',
        x_start=0, x_stop=1, y_start=0, y_stop=1, z_start=0, z_stop=1,
        x_voxel_size=1, y_voxel_size=1, z_voxel_size=1, voxel_unit='nanometers',
        time_step=0, time_step_unit='seconds'):

        super().__init__(name, description, version)

        self._valid_voxel_units = [
            'nanometers', 'micrometers', 'millimeters', 'centimeters']

        self._valid_time_units = [
            'nanoseconds', 'microseconds', 'milliseconds', 'seconds']

        self.x_start = x_start
        self.x_stop = x_stop
        self.y_start = y_start 
        self.y_stop = y_stop
        self.z_start = z_start
        self.z_stop = z_stop
        self.x_voxel_size = x_voxel_size
        self.y_voxel_size = y_voxel_size
        self.z_voxel_size = z_voxel_size
        self._voxel_unit = self.validate_voxel_units(voxel_unit)
        self.time_step = time_step
        self._time_step_unit = self.validate_time_units(time_step_unit)

    def get_route(self):
        return 'coordinateframes/' + self.name

    def get_project_list_route(self):
        return 'coordinateframes/'

    @property
    def voxel_unit(self):
        return self._voxel_unit

    @voxel_unit.setter
    def voxel_unit(self, value):
        """
        Args:
            value (string): Valid values: 'nanometers', 'micrometers', 'millimeters', 'centimeters'
        Raises:
            ValueError
        """
        self._voxel_unit = self.validate_voxel_units(value)

    @property
    def time_step_unit(self):
        return self._time_step_unit

    @time_step_unit.setter
    def time_step_unit(self, value):
        """
        Args:
            value (string): 'nanoseconds', 'microseconds', 'milliseconds', 'seconds'
        Raises:
            ValueError
        """
        self._time_step_unit = self.validate_time_units(value)

    def validate_voxel_units(self, value):
        lowered = value.lower()
        if lowered in self._valid_voxel_units:
            return lowered
        raise ValueError('{} is not a valid voxel unit.'.format(value))

    def validate_time_units(self, value):
        lowered = value.lower()
        if lowered in self._valid_time_units:
            return lowered
        raise ValueError('{} is not a valid time unit.'.format(value))


class ChannelLayerBaseResource(Resource):
    """
    Holds data common to both channels and layers.

    Attributes:
        coll_name (string): Name of collection containing this resource.
        exp_name (string): Name of experiment containing this resource.
        default_time_step (int):
        _datatype (string):
        base_resolution (int):
    """
    def __init__(self, name, collection_name, experiment_name,
        version=BOSS_DEFAULT_VERSION,
        description='', default_time_step=0, datatype='uint8',
        base_resolution=0):

        super().__init__(name, description, version)
        self.coll_name = collection_name
        self.exp_name = experiment_name

        self._valid_datatypes = ['uint8', 'uint16', 'uint64']

        #ToDo: validate data types.
        self.default_time_step = default_time_step
        self._datatype = self.validate_datatype(datatype)
        self.base_resolution = base_resolution

    def get_route(self):
        return self.coll_name + '/' + self.exp_name + '/' + self.name

    def valid_volume(self):
        """Channels and layers are valid resources for interacting with the volume service.
        """
        return True

    @property
    def datatype(self):
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        """
        Args:
            value (string): 'uint8', 'uint16', 'uint64'
        Raises:
            ValueError
        """
        self._datatype = self.validate_datatype(value)

    def validate_datatype(self, value):
        lowered = value.lower()
        if lowered in self._valid_datatypes:
            return lowered
        raise ValueError('{} is not a valid data type.'.format(value))


class ChannelResource(ChannelLayerBaseResource):
    """
    ToDo: provide some way to list layers associated with the channel.
    """
    def __init__(self, name, collection_name, experiment_name,
        version=BOSS_DEFAULT_VERSION,
        description='', default_time_step=0, datatype='uint8',
        base_resolution=0):
        """Constructor.

        Args:
            name (string): Channel name.
            collection_name (string): Parent collection name.
            experiment_name (string): Parent experiment name.
            version (optional[string]): API version to use.
            description (optional[string]): Layer description.
            default_time_step (optional[int]): Defaults to 0.
            datatype (optional[string]): 'uint8', 'uint16', 'uint64'
            base_resolution (optional[int]): Defaults to 0 (native).
        """

        super().__init__(name, collection_name, experiment_name, version,
            description, default_time_step, datatype, base_resolution)

    def get_project_list_route(self):
        return self.coll_name + '/' + self.exp_name + '/channels'


class LayerResource(ChannelLayerBaseResource):
    """
    Layers contain annotation data.
    They must be associated with at least one channel.

    Attributes:
        channels (list): Ids of linked channels.
    """
    def __init__(self, name, collection_name, experiment_name,
        version=BOSS_DEFAULT_VERSION,
        description='', default_time_step=0, datatype='uint8',
        base_resolution=0, channels=[]):
        """Constructor.

        Args:
            name (string): Layer name.
            collection_name (string): Parent collection name.
            experiment_name (string): Parent experiment name.
            version (optional[string]): API version to use.
            description (optional[string]): Layer description.
            default_time_step (optional[int]): Defaults to 0.
            datatype (optional[string]): 'uint8', 'uint16', 'uint64'
            base_resolution (optional[int]): Defaults to 0 (native).
            channels (optional[list]): Ids of linked channels.
        """

        super().__init__(name, collection_name, experiment_name, version,
            description, default_time_step, datatype, base_resolution)
        self.channels = channels


    def get_project_list_route(self):
        return self.coll_name + '/' + self.exp_name + '/layers'