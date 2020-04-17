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

from intern.resource import Resource


class DVIDResource(Resource):

    """Base class for DVID resources.

    Attributes:
        name (str): Name of resource.  Used as identifier when talking to
        the DVID API.
        description (str): Text description of resource.
    """

    def __init__(self, name, description):
        """Constructor.

        Args:
            name (str): Name of resource.
            description (str): Description of resource.        """

        self.name = name
        self.description = description

    def valid_volume(self):
        return False


class RepositoryResource(DVIDResource):
    """Top level container for DVID projects.
    """

    def __init__(self, UUID=None, alias="", description="", sync="", version="0"):
        """Constructor.

        Args:
            UUID (str): UUID of repository (necessary during deletions, not necessary during creation)
            alias (str): alias for the UUID Repository
            description (optional[str]): Layer description.  Defaults to empty.
            sync(str): data instance related to this one
            version(str) : version of data instance
        """
        DVIDResource.__init__(self, alias, description)

        self.UUID, self.alias, self.sync, self.version = UUID, alias, sync, version


class DataInstanceResource(DVIDResource):
    """Holds data instance data.

    Attributes:
        name (str): Name of data instance containing this resource.
        UUID (str): UUID of resource.
        alias (str): alias for the UUID Repository
        description (str): Description of data instance or layer.
        sync (str): related data instance name
        version (str): version of data instance if not 0
        _valid_datatypes (list[str]): Allowed data type values (static variable).
        _valid_types (list[str]): Allowed types
        _datatype (str):
        _cutout_ready (bool): True if datatype specified during instantiation.
    """

    _valid_datatypes = ["uint8", "uint16", "uint64"]
    _valid_types = [
        "image",
        "imagetile",
        "googlevoxels",
        "keyvalue",
        "roi",
        "uint8blk",
        "uint16blk",
        "uint64blk",
        "labelblk",
        "labelvol",
        "annotation",
        "labelgraph",
        "multichan16",
        "rgba8blk",
    ]

    def __init__(
        self,
        name,
        UUID=None,
        type="uint8blk",
        alias="",
        description="",
        datatype="",
        sync="",
        version="0",
    ):
        """Constructor.

        Args:
            name (str): Data instance name.
            UUID (str): UUID of Repository where this DataInstance lives. If None it will create one
            alias (str): alias for the UUID Repository
            type (optional[str]): check _valid_types defaults to uint8blk
            description (optional[str]): Layer description.  Defaults to empty.
            datatype (optional[str]): 'uint8', 'uint16', 'uint64'  Defaults to 'uint8'.
            sync (str): related data instance name
            version (str): version of data instance if not 0
        """

        DVIDResource.__init__(self, name, description)
        self.UUID, self.alias, self.sync, self.version = UUID, alias, sync, version
        self.name = name
        self._type = self.validate_type(type)

        # Class is considered fully initialized if datatype set during
        # initialization.
        if datatype == "":
            self._cutout_ready = False
            # Default to uint8.
            datatype = "uint8"
        else:
            self._cutout_ready = True
        self._datatype = self.validate_datatype(datatype)

    def valid_volume(self):
        """data instances and layers are valid resources for interacting with the volume service.
        """
        return True

    @property
    def cutout_ready(self):
        """Is this data instance fully configured for doing cutouts?

        Returns:
            (bool) True if the datatype was explicitly set by the user.
        """
        return self._cutout_ready

    @property
    def datatype(self):
        """Data instance bit depth.

        Returns:
            (str)
        """
        return self._datatype

    @datatype.setter
    def datatype(self, value):
        """
        Args:
            value (str): 'uint8', 'uint16', 'uint64'
        Raises:
            ValueError
        """
        self._datatype = self.validate_datatype(value)
        self._cutout_ready = True

    def validate_type(self, value):
        if value not in self._valid_types:
            raise ValueError("{} is not a valid type in DVID.".format(value))
        else:
            return value

    def validate_datatype(self, value):
        lowered = value.lower()
        if lowered in DataInstanceResource._valid_datatypes:
            return lowered
        raise ValueError("{} is not a valid data type.".format(value))

