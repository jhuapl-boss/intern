"""
Copyright 2018-2022 The Johns Hopkins University Applied Physics Laboratory.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Standard imports
from typing import List, Optional, Union, Tuple
import abc
import json
from collections import namedtuple
from urllib.parse import unquote
import warnings

from intern.service.boss.httperrorlist import HTTPErrorList

from .uri import parse_fquri


# Pip-installable imports
import numpy as np

from intern.remote.boss import BossRemote

from intern.resource import Resource
from intern.resource.boss.resource import (
    BossResource,
    CollectionResource,
    ChannelResource,
    CoordinateFrameResource,
    ExperimentResource,
)

HAS_CLOUDVOLUME = True
try:
    from intern.remote.cv import CloudVolumeRemote
    from intern.resource.cv.resource import CloudVolumeResource
except ModuleNotFoundError:
    HAS_CLOUDVOLUME = False

warnings.simplefilter('once', 'CloudVolume')

# A named tuple that represents a bossDB URI.
bossdbURI = namedtuple(
    "bossdbURI", ["collection", "experiment", "channel", "resolution"]
)

cvURI = namedtuple(
    "cvURI",
    [
        "protocol",
        "source",
        "bucket",
        "collection",
        "experiment",
        "channel",
        "resolution",
    ],
)

URI = Union[cvURI, bossdbURI]

_DEFAULT_BOSS_OPTIONS = {
    "protocol": "https",
    "host": "api.bossdb.io",
    "token": "public",
}


class VolumeProvider(abc.ABC):
    """
    A provider for the common get/put cutout operations on a Remote.

    TODO: This should ultimately be subsumed back into the Remote API.

    """

    def get_channel(self, channel: str, collection: str, experiment: str) -> Resource:
        ...

    def get_project(self, resource) -> Resource:
        ...

    def create_project(self, resource):
        ...

    def get_cutout(
        self,
        channel: ChannelResource,
        resolution: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ) -> np.ndarray:
        ...

    def create_cutout(
        self,
        channel: ChannelResource,
        resolution: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
        data,
    ):
        ...

    def get_vp_type(self) -> str:
        ...

    def get_axis_order(self) -> str:
        ...

    def get_shape(self, channel: Resource, resolution: int = 0) -> Tuple[int, int, int]:
        ...

    def get_voxel_size(
        self, channel: Resource, resolution: int = 0
    ) -> Tuple[float, float, float]:
        ...

    def get_voxel_unit(self, channel: Resource, resolution: int = 0) -> str:
        ...

    def get_available_resolutions(self, channel: Resource) -> List[int]:
        ...


class _BossDBVolumeProvider(VolumeProvider):
    """
    A VolumeProvider that backends the intern.BossRemote API.

    This is used instead of directly accessing the BossRemote so that the
    convenience `array` can be easily stripped out. (The array module was
    originally a visitor from another Python package called `emboss`, so moving
    VolumeProvider endpoints back into the Remote API is an outstanding TODO.)
    """

    def __init__(self, boss: BossRemote = None):
        if boss is None:
            try:
                boss = BossRemote()
            except:
                boss = BossRemote(_DEFAULT_BOSS_OPTIONS)
        self.boss = boss

    def get_vp_type(self) -> str:
        return "bossdb"

    def get_axis_order(self) -> str:
        return AxisOrder.ZYX

    def get_remote(self):
        return self.boss

    def get_channel(self, channel: str, collection: str, experiment: str):
        return self.boss.get_channel(channel, collection, experiment)

    def get_project(self, resource) -> Resource:
        return self.boss.get_project(resource)

    def create_project(self, resource):
        return self.boss.create_project(resource)

    def get_cutout(
        self,
        channel: ChannelResource,
        resolution: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ) -> np.ndarray:
        return self.boss.get_cutout(channel, resolution, xs, ys, zs)

    def create_cutout(
        self,
        channel: ChannelResource,
        resolution: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
        data,
    ):
        return self.boss.create_cutout(channel, resolution, xs, ys, zs, data)

    def get_shape(
        self, channel: ChannelResource, resolution: int = 0
    ) -> Tuple[int, int, int]:
        # Get the experiment:
        experiment = self.get_project(
            ExperimentResource(channel.exp_name, channel.coll_name)
        )
        # Get the coordinate frame:
        cf = self.get_project(CoordinateFrameResource(experiment.coord_frame))

        # Return the bounds of the coordinate frame:
        return (
            (cf.z_stop - cf.z_start),
            int((cf.y_stop - cf.y_start) / (2**resolution)),
            int((cf.x_stop - cf.x_start) / (2**resolution)),
        )

    def get_voxel_size(
        self, channel: ChannelResource, resolution: int = 0
    ) -> Tuple[float, float, float]:
        experiment = self.get_project(
            ExperimentResource(channel.exp_name, channel.coll_name)
        )
        # Get the coordinate frame:
        cf = self.get_project(CoordinateFrameResource(experiment.coord_frame))
        return (cf.x_voxel_size, cf.y_voxel_size, cf.z_voxel_size)

    def get_voxel_unit(self, channel: ChannelResource, resolution: int = 0) -> str:
        experiment = self.get_project(
            ExperimentResource(channel.exp_name, channel.coll_name)
        )
        # Get the coordinate frame:
        cf = self.get_project(CoordinateFrameResource(experiment.coord_frame))
        return cf.voxel_unit

    def get_available_resolutions(self, channel: Resource) -> List[int]:
        experiment = self.get_project(
            ExperimentResource(channel.exp_name, channel.coll_name)
        )
        return list(range(experiment.num_hierarchy_levels))

if HAS_CLOUDVOLUME:
    class _CloudVolumeOpenDataVolumeProvider(VolumeProvider):
        """
        A volume provider that backends the intern.CloudVolumeRemote API."""

        def __init__(self, cv_config: dict = None):
            self.cv_config = cv_config or {
                "protocol": "s3",
                "cloudpath": "",
                "bucket": "bossdb-open-data",
            }
            self._cv = CloudVolumeRemote(self.cv_config)

        def get_remote(self):
            return self._cv

        def get_vp_type(self) -> str:
            return "CloudVolumeOpenData"

        def get_axis_order(self) -> str:
            return AxisOrder.XYZ

        def get_channel(self, channel: str, collection: str, experiment: str):
            cloudpath = (
                self.cv_config["cloudpath"] or f"{collection}/{experiment}/{channel}"
            )
            return CloudVolumeResource(
                self.cv_config["protocol"],
                f"{self.cv_config['bucket']}/{cloudpath}",
            )

        def get_project(self, resource) -> CloudVolumeResource:
            raise NotImplementedError(
                "CloudVolumeOpenDataVolumeProvider does not support get_project"
            )

        def create_project(self, resource):
            raise NotImplementedError(
                "CloudVolumeOpenDataVolumeProvider does not support create_project"
            )

        def get_cutout(
            self,
            uri: str,
            resolution: int,
            xs: Tuple[int, int],
            ys: Tuple[int, int],
            zs: Tuple[int, int],
        ) -> np.ndarray:
            return self._cv.get_cutout(uri, resolution, zs, ys, xs)

        def get_shape(
            self, channel: CloudVolumeResource, resolution: int = 0
        ) -> Tuple[int, int, int]:
            return tuple(channel.cloudvolume.scales[resolution]["size"])

        def get_voxel_size(
            self, channel: CloudVolumeResource, resolution: int = 0
        ) -> Tuple[float, float, float]:
            return tuple(channel.cloudvolume.resolution)

        def get_voxel_unit(self, channel: CloudVolumeResource) -> str:
            return "nanometers"

        def get_available_resolutions(self, channel: CloudVolumeResource) -> List[int]:
            return list(channel.cloudvolume.available_mips)


def _construct_boss_url(boss, col, exp, chan, res, xs, ys, zs) -> str:
    # TODO: use boss host
    return f"https://api.theboss.io/v1/cutout/{col}/{exp}/{chan}/{res}/{xs[0]}:{xs[1]}/{ys[0]}:{ys[1]}/{zs[0]}:{zs[1]}"


def _parse_bossdb_uri(uri: str) -> URI:
    """
    Parse a bossDB URI and handle malform errors.

    Arguments:
        uri (str): URI of the form bossdb://<collection>/<experiment>/<channel>

    Returns:
        bossdbURI

    """
    t = uri.split("://")[-1].split("/")
    if len(t) == 3:
        return bossdbURI(t[-3], t[-2], t[-1], None)
    if len(t) == 4:
        return bossdbURI(t[-4], t[-3], t[-2], int(t[-1]))
    raise ValueError(f"Cannot parse URI {uri}.")


def _parse_cloudvolume_uri(uri: str) -> URI:
    """
    Parse a CloudVolume URI and handle malform errors.

    Arguments:
        uri (str): URI of the form s3://<bucket>/<path>

    Returns:
        dict

    """
    if uri.startswith("bossdb://"):
        return _parse_bossdb_uri(uri)
    protocol, source, path = uri.split("://")
    bucket, col, exp, chan = path.split("/")
    return cvURI(protocol, source, bucket, col, exp, chan, None)


class AxisOrder:
    XYZ = "XYZ"
    ZYX = "ZYX"


class Metadata:
    def __init__(self, resource: Union[BossResource, str], remote: BossRemote = None):
        self._remote = remote or BossRemote(_DEFAULT_BOSS_OPTIONS)
        if isinstance(resource, str):
            resource = resource.split("://")[-1]
            path_items = resource.split("/")
            if len(path_items) == 1:
                self._resource = self._remote.get_project(
                    CollectionResource(path_items[0])
                )
            elif len(path_items) == 2:
                self._resource = self._remote.get_project(
                    ExperimentResource(path_items[1], path_items[0])
                )
            elif len(path_items) == 3:
                self._resource = self._remote.get_project(
                    ChannelResource(path_items[2], path_items[0], path_items[1])
                )
            else:
                raise ValueError(f"Invalid resource path: {resource}")
        else:
            self._resource = resource

    def __truediv__(self, path: str):
        return Metadata(self._resource.get_list_route() + path, remote=self._remote)

    def keys(self):
        return self._remote.list_metadata(self._resource)

    def items(self):
        for key in self.keys():
            yield (key, self[key])

    def __delitem__(self, key):
        return self._remote.delete_metadata(self._resource, [key])

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __getitem__(self, key):
        try:
            return self._remote.get_metadata(self._resource, [key])[key]
        except HTTPErrorList as err:
            raise KeyError(
                f"The key {key!s} was not found in the metadata database."
            ) from err

    def __setitem__(self, key, value):
        return self._remote.create_metadata(self._resource, {key: value})

    def update_item(self, key, value):
        return self._remote.update_metadata(self._resource, {key: value})

    def bulk_update(self, items: dict):
        return self._remote.create_metadata(self._resource, items)

    def bulk_delete(self, keys: list):
        return self._remote.delete_metadata(self._resource, keys)

    def to_dict(self):
        return {k: v for k, v in self.items()}


def _infer_volume_provider(channel: Union[ChannelResource, str, Tuple]):
    if isinstance(channel, ChannelResource):
        # Check if the channel is backed by CloudVolume and cloudvolume is installed.
        if channel.raw["storage_type"] == "cloudvol" and HAS_CLOUDVOLUME:
            return _CloudVolumeOpenDataVolumeProvider(
                {
                    "protocol": "s3",
                    "bucket": channel.raw["bucket"],
                    "cloudpath": channel.raw["cv_path"],
                }
            )
        else:
            warnings.warn("CloudVolume is not installed. Accessing channel using CVDB.", ImportWarning)
        return _BossDBVolumeProvider()

    if isinstance(channel, str):
        if channel.startswith("bossdb://"):
            channel_uri = _parse_bossdb_uri(channel)
            channel_obj = _BossDBVolumeProvider().get_channel(
                channel_uri.channel, channel_uri.collection, channel_uri.experiment
            )
            if channel_obj.raw["storage_type"] == "cloudvol" and HAS_CLOUDVOLUME:
                return _CloudVolumeOpenDataVolumeProvider(
                    {
                        "protocol": "s3",
                        "bucket": channel_obj.raw["bucket"],
                        "cloudpath": channel_obj.raw["cv_path"],
                    }
                )
            else:
                warnings.warn("CloudVolume is not installed. Accessing channel using CVDB.", ImportWarning)
            return _BossDBVolumeProvider()

        if channel.startswith("s3://") or channel.startswith("precomputed://"):
            if HAS_CLOUDVOLUME:
                return _CloudVolumeOpenDataVolumeProvider()
            else:
                raise ModuleNotFoundError("CloudVolume is not installed.")
    return None


class array:
    """
    An intern/bossDB-backed numpy array.

    Like a numpy.memmap array, an `intern.array` is backed by data that lives
    outside of conventional memory. The data can live in, for example, a bossDB
    that lives in AWS, or it can live in a local or remote bossphorus instance.

    Data are downloaded when a request is made. This means that even "simple"
    commands like `array#[:]sum()` are very network-heavy (don't do this!).

    Examples:

    >>> import intern.array
    >>> data = array("bossdb://collection/experiment/channel")
    >>> downloaded_sample = data[100, 100:200, 100:200]

    """

    def __init__(
        self,
        channel: Union[ChannelResource, Tuple, str],
        resolution: int = 0,
        volume_provider: VolumeProvider = None,
        axis_order: str = AxisOrder.ZYX,
        create_new: bool = False,
        description: Optional[str] = None,
        dtype: Optional[str] = None,
        extents: Optional[Tuple[int, int, int]] = None,
        voxel_size: Optional[Tuple[int, int, int]] = None,
        voxel_unit: Optional[str] = None,
        downsample_levels: int = 6,
        downsample_method: Optional[str] = "anisotropic",
        coordinate_frame_name: Optional[str] = None,
        coordinate_frame_desc: Optional[str] = None,
        collection_desc: Optional[str] = None,
        experiment_desc: Optional[str] = None,
        source_channel: Optional[str] = None,
        boss_config: Optional[dict] = None,
    ) -> None:
        """
        Construct a new intern-backed array.

        Arguments:
            channel (intern.resource.boss.ChannelResource): The channel from
                which data will be downloaded.
            resolution (int: 0): The native resolution or MIP to use
            volume_provider (VolumeProvider): The remote-like to use
            axis_order (str = AxisOrder.ZYX): The axis-ordering to use for data
                cutouts. Defaults to ZYX. DOES NOT affect the `voxel_size` or
                `extents` arguments to this constructor.
            create_new (bool: False): Whether to create new Resources if they
                do not exist. Does not work with public token.
            dtype (str): Only required if `create_new = True`. Specifies the
                numpy-style datatype for this new dataset (e.g. "uint8").
            description (str): Only required if `create_new = True`. Sets the
                description for the newly-created collection, experiment,
                channel, and coordframe resources.
            extents: Optional[Tuple[int, int, int]]: Only required if
                `create_new = True`. Specifies the total dataset extents of
                this new dataset, in ZYX order.
            voxel_size: Optional[Tuple[int, int, int]]: Only required if
                `create_new = True`. Specifies the voxel dimensions of this new
                dataset, in ZYX order.
            voxel_unit: Optional[str]: Only required if `create_new = True`.
                Specifies the voxel-dimension unit. For example, "nanometers".
            downsample_levels (int: 6): The number of downsample levels.
            downsample_method (Optional[str]): The type of downsample to use.
                If unset, defaults to 'anisotropic'.
            coordinate_frame_name (Optional[str]): If set, the name to use for
                the newly created coordinate frame. If not set, the name of the
                coordinate frame will be chosen automatically.
            coordinate_frame_desc (Optional[str]): If set, the description text
                to use for the newly created coordinate frame. If not set, the
                description will be chosen automatically.
            collection_desc (Optional[str]): The description text to use for a
                newly created collection. If not set, the description will be
                chosen automatically.
            experiment_desc (Optional[str]): The description text to use for a
                newly created experiment. If not set, the description will be
                chosen automatically.
            source_channel (Optional[str]): The channel to use as the source
                for this new channel, if `create_new` is True and this is
                going to be an annotation channel (dtype!=uint8).
            boss_config (Optional[dict]): The BossRemote configuration dict to
                use in order to authenticate with a BossDB remote. This option
                is mutually exclusive with the VolumeProvider configuration. If
                the `volume_provider` arg is set, this will be ignored.

        """
        self.axis_order = axis_order

        # Handle inferring the remote from the channel:
        volume_provider = volume_provider or _infer_volume_provider(channel)
        if volume_provider is None:
            if boss_config:
                volume_provider = _BossDBVolumeProvider(BossRemote(boss_config))
            else:
                volume_provider = _BossDBVolumeProvider()

        # Handle custom Remote:
        self.volume_provider = volume_provider

        if create_new:

            if self.volume_provider.get_vp_type() != "bossdb":
                raise ValueError(
                    "Creating new resources with a non-bossdb volume provider is not currently supported."
                )

            # We'll need at least `extents` and `voxel_size`.
            description = description or "Created with intern"
            dtype = dtype or "uint8"

            if extents is None:
                raise ValueError(
                    "If `create_new` is True, you must specify the extents of the new coordinate frame as a [x, y, z]."
                )
            if voxel_size is None:
                raise ValueError(
                    "If `create_new` is True, you must specify the voxel_size of the new coordinate frame as a [x, y, z]."
                )

            uri = _parse_bossdb_uri(channel)

            # create collection if it doesn't exist:
            try:
                # Try to get an existing collection:
                collection = self.volume_provider.get_project(
                    CollectionResource(uri.collection)
                )
            except:
                # Create the collection:
                collection = CollectionResource(
                    uri.collection, description=collection_desc or description
                )
                self.volume_provider.create_project(collection)

            # create coordframe if it doesn't exist:
            try:
                # Try to get an existing coordframe:
                coordframe = self.volume_provider.get_project(
                    CoordinateFrameResource(
                        coordinate_frame_name or f"CF_{uri.collection}_{uri.experiment}"
                    )
                )
            except:
                # Default to nanometers if a voxel unit isn't provided
                voxel_unit = voxel_unit or "nanometers"
                # Create the coordframe:
                coordframe = CoordinateFrameResource(
                    coordinate_frame_name or f"CF_{uri.collection}_{uri.experiment}",
                    description=coordinate_frame_desc or description,
                    x_start=0,
                    y_start=0,
                    z_start=0,
                    x_stop=extents[2],
                    y_stop=extents[1],
                    z_stop=extents[0],
                    x_voxel_size=voxel_size[2],
                    y_voxel_size=voxel_size[1],
                    z_voxel_size=voxel_size[0],
                    voxel_unit=voxel_unit,
                )
                self.volume_provider.create_project(coordframe)

            # create experiment if it doesn't exist:
            try:
                # Try to get an existing experiment:
                experiment = self.volume_provider.get_project(
                    ExperimentResource(uri.experiment, uri.collection)
                )
            except:
                # Create the experiment:
                experiment = ExperimentResource(
                    uri.experiment,
                    uri.collection,
                    description=experiment_desc or description,
                    coord_frame=coordframe.name,
                    num_hierarchy_levels=downsample_levels,
                    hierarchy_method=downsample_method,
                )
                self.volume_provider.create_project(experiment)

            # create channel if it doesn't exist:
            try:
                # Try to get an existing channel:
                channel = self.volume_provider.get_project(
                    ChannelResource(uri.channel, uri.collection, uri.experiment)
                )
            except:
                # Create the channel:
                channel = ChannelResource(
                    uri.channel,
                    uri.collection,
                    uri.experiment,
                    description=description,
                    type="image" if dtype in ["uint8", "uint16"] else "annotation",
                    datatype=dtype,
                    sources=[source_channel] if source_channel else [],
                )
                self.volume_provider.create_project(channel)

        self.resolution = resolution
        # If the channel is set as a Resource, then use that resource.
        if isinstance(channel, ChannelResource):
            self._channel = channel
        # If it is set as a string, then parse the channel and generate an
        # intern.Resource from a bossDB URI.
        else:  # if isinstance(channel, str):
            uri = {
                "bossdb": _parse_bossdb_uri,
                "cloudvolumeopendata": _parse_cloudvolume_uri,
            }[self.volume_provider.get_vp_type().lower()](channel)
            self.resolution = (
                uri.resolution if not (uri.resolution is None) else self.resolution
            )
            self._channel = self.volume_provider.get_channel(
                uri.channel, uri.collection, uri.experiment
            )

        # Set col/exp/chan based upon the channel or URI provided.
        self.collection_name = self._channel.coll_name
        self.experiment_name = self._channel.exp_name
        self.channel_name = self._channel.name

        # Create a pointer to the metadata for the channel.
        self._channel_metadata = Metadata(self._channel)

    @property
    def remote(self):
        return self.volume_provider.get_vp_type()

    @property
    def metadata(self):
        """
        Returns a pointer to the metadata provider.
        """
        return self._channel_metadata

    @property
    def dtype(self):
        """
        Return the datatype of the array.

        Will default to the dtype of the channel.
        """
        return self._channel.datatype

    @property
    def url(self):
        """
        Get a pointer to this Channel on the BossDB page.
        """
        return f"{self.volume_provider.boss._project._base_protocol}://{self.volume_provider.boss._project._base_url}/v1/mgmt/resources/{self.collection_name}/{self.experiment_name}/{self.channel_name}"

    @property
    def visualize(self):
        """
        Get a pointer to this Channel on the BossDB page.
        """
        return "https://neuroglancer.bossdb.io/#!{'layers':{'image':{'source':'boss://__replace_me__'}}}".replace(
            "__replace_me__",
            f"{self.volume_provider.boss._project._base_protocol}://{self.volume_provider.boss._project._base_url}/{self.collection_name}/{self.experiment_name}/{self.channel_name}",
        )

    @property
    def shape(self) -> Tuple[int, int, int]:
        """
        Get the dimensions (numpy-flavored) of the array.

        Will return (1, 1, 1) if a coordinate frame does not exist (as in cases
        of pre-v2 bossphorus instances); this will not restrict indexing.
        """
        # From the coordinate frame, get the x, y, and z sizes. Note that this
        # is the SIZE, not the extents; in other words, a cframe that starts at
        # x=10 and extends to x=110 will have a size of 100 here.
        if self.axis_order == self.volume_provider.get_axis_order():
            return self.volume_provider.get_shape(self._channel, self.resolution)
        else:
            # elif self.axis_order == AxisOrder.ZYX: # TODO: Support other Axis orderings?
            shape = self.volume_provider.get_shape(self._channel, self.resolution)
            return shape[2], shape[1], shape[0]

    @property
    def voxel_size(self):
        """
        Get the dimensions (numpy-flavored) of the array.

        Will return (1, 1, 1) if a coordinate frame does not exist (as in cases
        of pre-v2 bossphorus instances); this will not restrict indexing.
        """

        if self.axis_order == self.volume_provider.get_axis_order():
            return self.volume_provider.get_voxel_size(self._channel)
        else:
            # elif self.axis_order == AxisOrder.ZYX: # TODO: Support other Axis orderings?
            voxel_size = self.volume_provider.get_voxel_size(self._channel)
            return voxel_size[2], voxel_size[1], voxel_size[0]

    @property
    def voxel_unit(self):
        return self.volume_provider.get_voxel_unit(self._channel)

    @property
    def downsample_status(self):
        """
        Return the downsample status of the underlying channel.
        """
        return self._channel.downsample_status

    @property
    def available_resolutions(self):
        """
        Return a list of available resolutions for this channel.

        Arguments:
            None

        Returns:
            List[int]: A list of resolutions at which this dataset can be downloaded

        """
        return self.volume_provider.get_available_resolutions(self._channel)

    def __getitem__(self, key: Tuple) -> np.ndarray:
        """
        Get a subarray or subvolume.

        Uses one of two indexing methods:
            1. Start/Stop (`int:int`)
            2. Single index (`int`)

        Each element of the key can be one of those two options. For example,

            myarray[1, 1:100, 2]

        """
        # If the user has requested XYZ mode, the first thing to do is reverse
        # the array indices. Then you can continue this fn without any
        # additional changes.
        if self.axis_order != self.volume_provider.get_axis_order():
            key = (key[2], key[1], key[0])

        # Now we can begin. There is a wide variety of indexing options
        # available, including single-integer indexing, tuple-of-slices
        # indexing, tuple-of-int indexing...

        # First we'll address if the user presents a single integer.
        # ```
        # my_array[500]
        # ```
        # In this case, the user is asking for a single Z slice (or single X
        # slice if in XYZ order... But that's a far less common use case.)
        # We will get the full XY extents and download a single 2D array:
        if isinstance(key, int):
            # Get the full Z slice:
            xs = (0, self.shape[2])
            ys = (0, self.shape[1])
            zs = (key, key + 1)
        else:
            # We also support indexing with units. For example, you can ask for
            # ```
            # my_array[0:10, 0:10, 0:10, "nanometers"]
            # ```
            # which will download as many pixels as are required in order to
            # download 10nm in each dimension. We do this by storing a
            # "normalized units" measure which is a rescale factor for each
            # dimension (in the same order, e.g. ZYX, as the array).
            _normalize_units = (1, 1, 1)
            if isinstance(key[-1], str) and len(key) == 4:
                if key[-1] != self.volume_provider.get_voxel_unit():
                    raise NotImplementedError(
                        "Can only reference voxels in native size format which is "
                        f"{self.volume_provider.get_voxel_unit()} for this dataset."
                    )
                _normalize_units = self.voxel_size

            # We will now do the following codeblock three times, for X,Y,Z:
            # First, we check to see if this index is a single integer. If so,
            # the user is requesting a 2D array with zero depth along this
            # dimension. For example, if the user asks for
            # ```
            # my_data[0:120, 0:120, 150]
            # ```
            # Then "150" suggests that the user just wants one single X slice.
            if isinstance(key[2], int):
                xs = (key[2], key[2] + 1)
            else:
                # If the key is a Slice, then it has .start and .stop attrs.
                # (The user is requesting an array with more than one slice
                # in this dimension.)
                start = key[2].start if key[2].start else 0
                stop = key[2].stop if key[2].stop else self.shape[0]

                start = int(start / _normalize_units[0])
                stop = int(stop / _normalize_units[0])

                # Cast the coords to integers (since Boss needs int coords)
                xs = (int(start), int(stop))

            # Do the same thing again for the next dimension: Either a single
            # integer, or a slice...
            if isinstance(key[1], int):
                ys = (key[1], key[1] + 1)
            else:
                start = key[1].start if key[1].start else 0
                stop = key[1].stop if key[1].stop else self.shape[1]

                start = start / _normalize_units[1]
                stop = stop / _normalize_units[1]

                ys = (int(start), int(stop))

            # Do the same thing again for the last dimension: Either a single
            # integer, or a slice...
            if isinstance(key[0], int):
                zs = (key[0], key[0] + 1)
            else:
                start = key[0].start if key[0].start else 0
                stop = key[0].stop if key[0].stop else self.shape[2]

                start = start / _normalize_units[2]
                stop = stop / _normalize_units[2]

                zs = (int(start), int(stop))

        # Finally, we can perform the cutout itself, using the x, y, and z
        # coordinates that we computed in the previous step.
        cutout = self.volume_provider.get_cutout(
            self._channel, self.resolution, xs, ys, zs
        )

        # Data are returned in ZYX order:
        if self.axis_order != self.volume_provider.get_axis_order():
            data: np.ndarray = np.swapaxes(cutout, 0, 2)
            # data = np.rollaxis(np.rollaxis(cutout, 1), 2)
        else:  # if self.axis_order == AxisOrder.ZYX:
            data: np.ndarray = cutout

        # If any of the dimensions are of length 1, it's because the user
        # requested a single slice in their key; flatten the array in that
        # dimension. For example, if you request `[10, 0:10, 0:10]` then the
        # result should be 2D (no Z component).
        _shape = data.shape
        if _shape[0] == 1:
            data = data[0, :, :]
        if _shape[1] == 1:
            data = data[:, 0, :]
        if _shape[2] == 1:
            data = data[:, :, 0]
        return data

    def __setitem__(self, key: Tuple, value: np.ndarray) -> None:
        """
        Set a subarray or subvolume.

        Uses one of two indexing methods:
            1. Start/Stop (`int:int`)
            2. Single index (`int`)

        Each element of the key can be one of those two options. For example,

            myarray[1, 1:100, 2]

        Start-only (`10:`) or stop-only (`:10`) indexing is unsupported.
        """

        if self.axis_order != self.volume_provider.get_axis_order():
            key = (key[2], key[1], key[0])

        _normalize_units = (1, 1, 1)
        if isinstance(key[-1], str) and len(key) == 4:
            if key[-1] != self.volume_provider.get_voxel_unit():
                raise NotImplementedError(
                    "Can only reference voxels in native size format which is "
                    f"{self.volume_provider.get_voxel_unit()} for this dataset."
                )
            _normalize_units = self.voxel_size

        if isinstance(key[2], int):
            xs = (key[2], key[2] + 1)
        else:
            start = key[2].start if key[2].start else 0
            stop = key[2].stop if key[2].stop else self.shape[0]

            start = start / _normalize_units[0]
            stop = stop / _normalize_units[0]

            xs = (int(start), int(stop))

        if isinstance(key[1], int):
            ys = (key[1], key[1] + 1)
        else:
            start = key[1].start if key[1].start else 0
            stop = key[1].stop if key[1].stop else self.shape[1]

            start = start / _normalize_units[1]
            stop = stop / _normalize_units[1]

            ys = (int(start), int(stop))

        if isinstance(key[0], int):
            zs = (key[0], key[0] + 1)
        else:
            start = key[0].start if key[0].start else 0
            stop = key[0].stop if key[0].stop else self.shape[2]

            start = start / _normalize_units[2]
            stop = stop / _normalize_units[2]

            zs = (int(start), int(stop))

        if len(value.shape) == 2:
            # TODO: Support other 2D shapes as well
            value = np.array([value])

        self.volume_provider.create_cutout(
            self._channel, self.resolution, xs, ys, zs, value
        )


def arrays_from_neuroglancer(url: str):
    """
    Construct array(s) from a neuroglancer link.

    Arguments:
        url (str): The neuroglancer link to parse

    Returns:
        Dict[str, array]: A dictionary of arrays, where each is keyed by
            the name of the channel in neuroglancer.

    """
    ngl_state = json.loads(unquote(url).split("#!")[1])

    arrays = {}
    for source in ngl_state["layers"]:
        source_url = ""
        if "boss://" in source["source"]:
            source_url = source["source"]
        elif (
            isinstance(source["source"], dict) and "boss://" in source["source"]["url"]
        ):
            source_url = source["source"]["url"]
        else:
            continue
        remote, channel = parse_fquri(source_url)
        arrays[source["name"]] = array(
            channel=channel, volume_provider=_BossDBVolumeProvider(remote)
        )
    return arrays


def volumes_from_neuroglancer(
    url: str, radius_zyx: Tuple[int, int, int] = (10, 1024, 1024)
):
    """
    Download numpy arrays from BossDB based upon a neuroglancer URL.

    Arguments:
        url (str): The neuroglancer link to parse
        radius_zyx (Tuple[int, int, int]): The amount of data along each axis
            to download, centered at the position from the URL.

    Returns:
        Dict[str, np.ndarray]: A dictionary of np.arrays, where each is keyed
            by the name of the channel in neuroglancer.


    """
    ngl_state = json.loads(unquote(url).split("#!")[1])

    x, y, z = ngl_state["position"]
    zr, yr, xr = radius_zyx

    arrays = arrays_from_neuroglancer(url)
    return {
        key: dataset[z - zr : z + zr, y - yr : y + yr, x - xr : x + xr]
        for key, dataset in arrays.items()
    }
