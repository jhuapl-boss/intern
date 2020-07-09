"""
Copyright 2018-2020 The Johns Hopkins University Applied Physics Laboratory.

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
from typing import Optional, Union, Tuple
import abc
from collections import namedtuple

# Pip-installable imports
import numpy as np

import blosc
import requests

from intern.resource.boss.resource import (
    CollectionResource,
    ChannelResource,
    CoordinateFrameResource,
    ExperimentResource,
)
from intern.remote.boss import BossRemote
from intern.utils.parallel import block_compute

# A named tuple that represents a bossDB URI.
bossdbURI = namedtuple(
    "bossdbURI", ["collection", "experiment", "channel", "resolution"]
)

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

    def get_channel(self, channel: str, collection: str, experiment: str):
        ...

    def get_project(self, resource):
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
    ):
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


class _InternVolumeProvider(VolumeProvider):
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

    def get_channel(self, channel: str, collection: str, experiment: str):
        return self.boss.get_channel(channel, collection, experiment)

    def get_project(self, resource):
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
    ):
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


def _construct_boss_url(boss, col, exp, chan, res, xs, ys, zs) -> str:
    # TODO: use boss host
    return f"https://api.theboss.io/v1/cutout/{col}/{exp}/{chan}/{res}/{xs[0]}:{xs[1]}/{ys[0]}:{ys[1]}/{zs[0]}:{zs[1]}"


def parse_bossdb_uri(uri: str) -> bossdbURI:
    """
    Parse a bossDB URI and handle malform errors.

    Arguments:
        uri (str): URI of the form bossdb://<collection/<experiment/<channel>

    Returns:
        bossdbURI

    """
    t = uri.split("://")[1].split("/")
    if len(t) is 3:
        return bossdbURI(t[0], t[1], t[2], None)
    if len(t) is 4:
        return bossdbURI(t[0], t[1], t[2], int(t[3]))
    raise ValueError(f"Cannot parse URI {uri}.")


class AxisOrder:
    XYZ = "XYZ"
    ZYX = "ZYX"


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

        """
        self.axis_order = axis_order

        # Handle custom Remote:
        self.volume_provider = volume_provider
        if volume_provider is None:
            self.volume_provider = _InternVolumeProvider()

        if create_new:

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

            uri = parse_bossdb_uri(channel)

            # create collection if it doesn't exist:
            try:
                # Try to get an existing collection:
                collection = self.volume_provider.get_project(
                    CollectionResource(uri.collection)
                )
            except:
                # Create the collection:
                collection = CollectionResource(uri.collection, description=description)
                self.volume_provider.create_project(collection)

            # create coordframe if it doesn't exist:
            try:
                # Try to get an existing coordframe:
                coordframe = self.volume_provider.get_project(
                    CoordinateFrameResource(f"CF_{uri.collection}_{uri.experiment}")
                )
            except:
                # Create the coordframe:
                coordframe = CoordinateFrameResource(
                    f"CF_{uri.collection}_{uri.experiment}",
                    description=description,
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
                    description=description,
                    coord_frame=coordframe.name,
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
                    type="image" if dtype == "uint8" else "annotation",
                    datatype=dtype,
                )
                self.volume_provider.create_project(channel)

        self.resolution = resolution
        # If the channel is set as a Resource, then use that resource.
        if isinstance(channel, ChannelResource):
            self._channel = channel
        # If it is set as a string, then parse the channel and generate an
        # intern.Resource from a bossDB URI.
        elif isinstance(channel, str):
            uri = parse_bossdb_uri(channel)
            self.resolution = (
                uri.resolution if not (uri.resolution is None) else self.resolution
            )
            self._channel = self.volume_provider.get_channel(
                uri.channel, uri.collection, uri.experiment
            )
        else:
            raise NotImplementedError(
                "You must specify a channel of the form "
                "'bossdb://collection/experiment/channel' or you must "
                "provide an intern.Remote."
            )

        # Set empty experiment (will be dict)
        self._exp = None
        # Set empty coordframe (will be dict)
        self._coord_frame = None

        # Set col/exp/chan based upon the channel or URI provided.
        self.collection_name = self._channel.coll_name
        self.experiment_name = self._channel.exp_name
        self.channel_name = self._channel.name

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
    def shape(self):
        """
        Get the dimensions (numpy-flavored) of the array.

        Will return (1, 1, 1) if a coordinate frame does not exist (as in cases
        of pre-v2 bossphorus instances); this will not restrict indexing.
        """
        # Set experiment if unset:
        if self._exp is None:
            self._populate_exp()

        # Set cframe if unset:
        if self._coord_frame is None:
            self._populate_coord_frame()

        # From the coordinate frame, get the x, y, and z sizes. Note that this
        # is the SIZE, not the extents; in other words, a cframe that starts at
        # x=10 and extends to x=110 will have a size of 100 here.
        if self.axis_order == AxisOrder.XYZ:
            return (
                int(
                    (self._coord_frame.y_stop - self._coord_frame.y_start)
                    / (2 ** self.resolution)
                ),
                int(
                    (self._coord_frame.x_stop - self._coord_frame.x_start)
                    / (2 ** self.resolution)
                ),
                (self._coord_frame.z_stop - self._coord_frame.z_start),
            )
        elif self.axis_order == AxisOrder.ZYX:
            return (
                (self._coord_frame.z_stop - self._coord_frame.z_start),
                int(
                    (self._coord_frame.y_stop - self._coord_frame.y_start)
                    / (2 ** self.resolution)
                ),
                int(
                    (self._coord_frame.x_stop - self._coord_frame.x_start)
                    / (2 ** self.resolution)
                ),
            )

    @property
    def voxel_size(self):
        """
        Get the dimensions (numpy-flavored) of the array.

        Will return (1, 1, 1) if a coordinate frame does not exist (as in cases
        of pre-v2 bossphorus instances); this will not restrict indexing.
        """
        # Set experiment if unset:
        if self._exp is None:
            self._populate_exp()

        # Set cframe if unset:
        if self._coord_frame is None:
            self._populate_coord_frame()

        if self.axis_order == AxisOrder.XYZ:
            vox_size = (
                self._coord_frame.x_voxel_size,
                self._coord_frame.y_voxel_size,
                self._coord_frame.z_voxel_size,
            )
        elif self.axis_order == AxisOrder.ZYX:
            vox_size = (
                self._coord_frame.z_voxel_size,
                self._coord_frame.y_voxel_size,
                self._coord_frame.x_voxel_size,
            )
        return (vox_size, self._coord_frame.voxel_unit)

    def _populate_exp(self):
        """
        Populate the experiment component of this array.

        Cache the results for later.
        """
        self._exp = self.volume_provider.get_project(
            ExperimentResource(self._channel.exp_name, self._channel.coll_name)
        )

    def _populate_coord_frame(self):
        """
        Populate the array coordinate frame.

        Cache the results for later.
        """
        self._coord_frame = self.volume_provider.get_project(
            CoordinateFrameResource(self._exp.coord_frame)
        )

    def __getitem__(self, key: Tuple) -> np.array:
        """
        Get a subarray or subvolume.

        Uses one of two indexing methods:
            1. Start/Stop (`int:int`)
            2. Single index (`int`)

        Each element of the key can be one of those two options. For example,

            myarray[1, 1:100, 2]

        Start-only (`10:`) or stop-only (`:10`) indexing is unsupported.
        """
        if self.axis_order == AxisOrder.XYZ:
            key = (key[2], key[1], key[0])

        # Set experiment if unset:
        if self._exp is None:
            self._populate_exp()

        # Set cframe if unset:
        if self._coord_frame is None:
            self._populate_coord_frame()

        _normalize_units = (1, 1, 1)
        if isinstance(key[-1], str) and len(key) == 4:
            if key[-1] != self._coord_frame.voxel_unit:
                raise NotImplementedError(
                    "Can only reference voxels in native size format which is "
                    f"{self._coord_frame.voxel_unit} for this dataset."
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

        cutout = self.volume_provider.get_cutout(
            self._channel, self.resolution, xs, ys, zs
        )

        # Data are returned in ZYX order, which is probably not what you want.
        # TODO: Permit ZYX ordering
        # Commented out March 19, 2019. Now returns in ZYX.
        if self.axis_order == AxisOrder.XYZ:
            data = np.rollaxis(np.rollaxis(cutout, 1), 2)
        elif self.axis_order == AxisOrder.ZYX:
            data = cutout

        # If any of the dimensions are of length 1, it's because the user
        # requested a single slice in their key; flatten the array in that
        # dimension. (For example, if you request `[10, 0:10, 0:10]` then the
        # result should be 2D (no X component).)
        _shape = data.shape
        if _shape[0] == 1:
            data = data[0, :, :]
        if _shape[1] == 1:
            data = data[:, 0, :]
        if _shape[2] == 1:
            data = data[:, :, 0]
        return data

    def __setitem__(self, key: Tuple, value: np.array) -> np.array:
        """
        Set a subarray or subvolume.

        Uses one of two indexing methods:
            1. Start/Stop (`int:int`)
            2. Single index (`int`)

        Each element of the key can be one of those two options. For example,

            myarray[1, 1:100, 2]

        Start-only (`10:`) or stop-only (`:10`) indexing is unsupported.
        """

        if self.axis_order == AxisOrder.XYZ:
            key = (key[2], key[1], key[0])

        # Set experiment if unset:
        if self._exp is None:
            self._populate_exp()

        # Set cframe if unset:
        if self._coord_frame is None:
            self._populate_coord_frame()

        _normalize_units = (1, 1, 1)
        if isinstance(key[-1], str) and len(key) == 4:
            if key[-1] != self._coord_frame.voxel_unit:
                raise NotImplementedError(
                    "Can only reference voxels in native size format which is "
                    f"{self._coord_frame.voxel_unit} for this dataset."
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

        cutout = self.volume_provider.create_cutout(
            self._channel, self.resolution, xs, ys, zs, value
        )
