# Copyright 2017 The Johns Hopkins University Applied Physics Laboratory
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

from intern.resource import Resource
from abc import abstractmethod

class DVIDResource(Resource):

    """Base class for DVID resources.

    Attributes:
        name (string): Name of resource.  Used as identifier when talking to
        the DVID API.
        description (string): Text description of resource.
    """
    def __init__(self, name, description):
        """Constructor.

        Args:
            name (string): Name of resource.
            description (string): Description of resource.        """

        self.name = name
        self.description = description

    def valid_volume(self):
        return False

class CollectionResource(DVIDResource):
    """
        CollectionResource is not a valid DVID Resource.
        # TODO: Should this be a warning message at the parent level?
    """
    NotImplemented

class ExperimentResource(DVIDResource):
    """Top level container for DVID projects.
    """
    def __init__(self, name, UUID, description='', sync="", version="0"):
        """Constructor.

        Args:
            name (string): Parent experiment name.
            UUID (string): UUID of collection
            description (optional[string]): Layer description.  Defaults to empty.
        """
        DVIDResource.__init__(self, name, description)

        self.UUID, self.sync, self.version  = UUID, sync, version
        self.exp_name = name

class ChannelResource(DVIDResource):
    """Holds channel data.

    Attributes:
        UUID (string): UUID of resource.
        exp_name (string): Name of experiment containing this resource.
        description (string): Description of channel or layer.
        _valid_datatypes (list[string]): Allowed data type values (static variable).
        _valid_types (list[string]): Allowed types
        _datatype (string):
        _cutout_ready (bool): True if datatype specified during instantiation.
    """

    _valid_datatypes = ['uint8', 'uint16', 'uint64']
    _valid_types = ['image', 'imagetile', 'googlevoxels', 'keyvalue', 'roi','uint8blk','labelblk', 'labelvol', 'annotation', 'labelgraph', 'multichan16', 'rgba8blk']

    def __init__(self, name, UUID, experiment_name, type='uint8blk', description='', datatype='uint8', sync="", version="0"):
        """Constructor.

        Args:
            name (string): Channel name.
            UUID (string): UUID of collection.
            experiment_name (string): Parent experiment name.
            type (optional[string]): check _valid_types defaults to uint8blk
            description (optional[string]): Layer description.  Defaults to empty.
            datatype (optional[string]): 'uint8', 'uint16', 'uint64'  Defaults to 'uint8'.
            sync (string): related channel name
            version (string): version of channel if not 0
        """

        DVIDResource.__init__(self, name, description)
        self.UUID, self.sync, self.version  = UUID, sync, version
        self.exp_name = experiment_name
        self._type = self.validate_type(type)

        # Class is considered fully initialized if datatype set during
        # initialization.
        if datatype == '':
            self._cutout_ready = False
            # Default to uint8.
            datatype = 'uint8'
        else:
            self._cutout_ready = True
        self._datatype = self.validate_datatype(datatype)

    def valid_volume(self):
        """Channels and layers are valid resources for interacting with the volume service.
        """
        return True

    @property
    def cutout_ready(self):
        """Is this channel fully configured for doing cutouts?

        Returns:
            (bool) True if the datatype was explicitly set by the user.
        """
        return self._cutout_ready

    @property
    def datatype(self):
        """Channel bit depth.

        Returns:
            (string)
        """
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
        self._cutout_ready = True

    def validate_type(self, value):
        if value not in self._valid_types:
            raise ValueError('{} is not a valid type in DVID.'.format(value))
        else:
            return value

    def validate_datatype(self, value):
        lowered = value.lower()
        if lowered in ChannelResource._valid_datatypes:
            return lowered
        raise ValueError('{} is not a valid data type.'.format(value))