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
import six
from abc import ABCMeta
from six.moves import configparser
from intern.service.mesh.service import MeshService, VoxelUnits
import os

CONFIG_FILE ='~/.intern/intern.cfg'


@six.add_metaclass(ABCMeta)
class Remote(object):
    """Base class for communicating with remote data stores.

    Attributes:
        _volume (intern.service.Service): Class that communicates with the volume service.
        _metadata (intern.service.Service): Class that communicates with the metadata service.
        _project (intern.service.Service): Class that communicates with the project service.
        _object (intern.service.Service): Class that communicates with the object service.
    """

    def __init__(self, cfg_file_or_dict=None):
        """Constructor.

        Loads credentials in order from user provided dictionary > user provided file > default file > environment vars

        Args:
            cfg_file_or_dict (optional[str|dict]): Path to config file in INI format or a dict of config parameters.
        """

        # Service Objects
        self._volume = None
        self._metadata = None
        self._project = None
        self._object = None
        self._mesh = None

        # Configuration data loaded from file or passed directly to the constructor
        # Is available for children Remote classes to use as needed
        self._config = None

        # Tokens for Services
        self._token_project = None
        self._token_metadata = None
        self._token_volume = None
        self._token_object = None

        if cfg_file_or_dict is None:
            # Default to the config file in the user directory if no config file was provided
            cfg_file_or_dict = os.path.expanduser(CONFIG_FILE)

        if isinstance(cfg_file_or_dict, dict):
            # A config dictionary was provided directly. Keep things consistent by creating an INI string.
            cfg_str = "[Default]\n"
            for key in cfg_file_or_dict:
                cfg_str = "{}{} = {}\n".format(cfg_str, key, cfg_file_or_dict[key])
            self._config = self.load_config_file(six.StringIO(cfg_str))

        else:
            # A file path was provided by the user
            if os.path.isfile(os.path.expanduser(cfg_file_or_dict)):
                with open(os.path.expanduser(cfg_file_or_dict), 'r') as cfg_file_handle:
                    self._config = self.load_config_file(cfg_file_handle)
            else:
                # Provided file or default file do not exist.  Try loading from env variables
                if "INTERN_PROTOCOL" in os.environ and "INTERN_HOST" in os.environ and "INTERN_TOKEN" in os.environ:
                    cfg_str = "[Default]\n"
                    cfg_str = "{}{} = {}\n".format(cfg_str, "protocol", os.environ['INTERN_PROTOCOL'])
                    cfg_str = "{}{} = {}\n".format(cfg_str, "host", os.environ['INTERN_HOST'])
                    cfg_str = "{}{} = {}\n".format(cfg_str, "token", os.environ['INTERN_TOKEN'])

                    self._config = self.load_config_file(six.StringIO(cfg_str))
                else:
                    raise IOError("Configuration file not found: {}. Please provide credential file or set environment variables".format(cfg_file_or_dict))

        self._init_mesh_service()

    def load_config_file(self, config_handle):
        """Load config data for the Remote.

        Args:
            config_handle (io.StringIO): Config data encoded in a string.

        Returns:
            (configparser.ConfigParser)
        """
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read_file(config_handle)
        return cfg_parser

    def _init_mesh_service(self):
        """
        Method to initialize the Mesh Service

        Args:
            None

        Returns:
            None

        Raises:
            (KeyError): if given invalid version.
        """

        self._mesh = MeshService()

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

    @property
    def mesh_service(self):
        return self._mesh

    def list_project(self, **kwargs):
        """Perform list operation on the project.

        What this does is highly dependent on project's data model.

        Args:
            (**kwargs): Args are implementation dependent.

        Returns:
            (list)
        """
        return self._project.list(**kwargs)

    def get_cutout(self, resource, resolution, x_range, y_range, z_range, time_range=None, id_list=[], parallel: bool= True, **kwargs):
        """Get a cutout from the volume service.

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            id_list (optional [list]): list of object ids to filter the cutout by.
            parallel (bool: True): Whether downloads should be parallelized using multiprocessing

        Returns:
            (): Return type depends on volume service's implementation.

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.
        """

        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')
        return self._volume.get_cutout(
            resource, resolution,
            x_range, y_range, z_range, time_range,
            id_list, parallel = parallel, **kwargs
        )

    def create_cutout(self, resource, resolution, x_range, y_range, z_range, data, time_range=None):
        """Upload a cutout to the volume service.

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
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
        return self._volume.create_cutout(
            resource, resolution, x_range, y_range, z_range, data, time_range)

    def reserve_ids(self, resource, num_ids):
        """Reserve a block of unique, sequential ids for annotations.

        Args:
            resource (intern.resource.Resource): Resource compatible with annotation operations.
            num_ids (int): Number of ids to reserve.

        Returns:
            (int): First id reserved.

        """
        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')
        return self._volume.reserve_ids(resource, num_ids)

    def get_extents(self, resource):
        """Get extents of data volume

        Args:
            resource (intern.resource.Resource): Data platform resource.

        Returns:
            extents (array): [[x-min, max-x], [y-min, max-y], [z-min, max-z]]
        """
        return self._metadata.get_extents(resource)

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
        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')

        if bb_type != 'loose' and bb_type != 'tight':
            raise RuntimeError("bb_type must be either 'loose' or 'tight'.")

        return self._volume.get_bounding_box(resource, resolution, id, bb_type)

    def get_ids_in_region(
            self, resource, resolution,
            x_range, y_range, z_range, time_range=[0, 1]):
        """Get all ids in the region defined by x_range, y_range, z_range.

        Args:
            resource (intern.resource.Resource): Resource compatible with annotation operations.
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
        return self._volume.get_ids_in_region(
            resource, resolution, x_range, y_range, z_range, time_range)

    def mesh(self, resource, resolution, 
            x_range, y_range, z_range, time_range=None, 
            id_list=[], voxel_unit=VoxelUnits.nm, 
            voxel_size=[4,4,40], simp_fact = 0, max_simplification_error=60,
            normals=False, **kwargs):
        """Generate a mesh of the specified IDs

        Args:
            resource (intern.resource.Resource): Resource compatible with cutout operations.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            id_list (optional [list]): list of object ids to filter the volume by.
            voxel_unit (optional VoxelUnit): voxel unit of measurement to derive conversion factor. 
            voxel_size (optional [list]): list in form [x,y,z] of voxel size. Defaults to 4x4x40nm
            simp_fact (optional int): mesh simplification factor, reduces triangles by given factor
            max_simplification_error (optional int): Max tolerable error in physical distance
            normals (optional bool): if true will calculate normals

        Returns:
            mesh (intern.service.mesh.Mesh): mesh class

        Raises:
            RuntimeError when given invalid resource.
            Other exceptions may be raised depending on the volume service's implementation.

        """

        if not resource.valid_volume():
            raise RuntimeError('Resource incompatible with the volume service.')
        volume = self._volume.get_cutout(
            resource, resolution, x_range, y_range, z_range, time_range, id_list, **kwargs)
        mesh = self._mesh.create(
            volume, x_range, y_range, z_range, time_range, id_list, voxel_unit, voxel_size,
            simp_fact, max_simplification_error, normals)
        return mesh