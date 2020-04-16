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
from typing import Union, Tuple
from collections import namedtuple

# Pip-installable imports
import numpy as np

import blosc
import requests

from intern.resource.boss.resource import (
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


class VolumeProvider:
    def get_channel(self, channel: str, collection: str, experiment: str):
        return self.boss.get_channel(channel, collection, experiment)

    def get_project(self, resource):
        return self.boss.get_project(resource)


class InternVolumeProvider(VolumeProvider):
    def __init__(self, boss: BossRemote):
        self.boss = boss

    def get_cutout(
        self,
        channel: ChannelResource,
        resolution: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):
        return self.boss.get_cutout(channel, resolution, xs, ys, zs)


def _construct_boss_url(boss, col, exp, chan, res, xs, ys, zs) -> str:
    # TODO: use boss host
    return f"https://api.theboss.io/v1/cutout/{col}/{exp}/{chan}/{res}/{xs[0]}:{xs[1]}/{ys[0]}:{ys[1]}/{zs[0]}:{zs[1]}"


class RawVolumeProvider(VolumeProvider):
    def __init__(self, boss: BossRemote = None):
        if not boss:
            self.boss = BossRemote()
        else:
            self.boss = boss

        self._token = self.boss.token_volume

    def get_cutout(
        self,
        channel: ChannelResource,
        resolution: int,
        xs: Tuple[int, int],
        ys: Tuple[int, int],
        zs: Tuple[int, int],
    ):

        result = requests.get(
            _construct_boss_url(
                self.boss,
                channel.coll_name,
                channel.exp_name,
                channel.name,
                resolution,
                xs,
                ys,
                zs,
            ),
            headers={"Authorization": f"token {self._token}"},
        )
        if not result.ok:
            raise ValueError(result, result.content)
        return np.frombuffer(
            blosc.decompress(result.content), dtype=channel.datatype
        ).reshape(zs[1] - zs[0], ys[1] - ys[0], xs[1] - xs[0])


DEFAULT_VOLUME_PROVIDER = RawVolumeProvider


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
        return bossdbURI(t[0], t[1], t[2], 0)
    if len(t) is 4:
        return bossdbURI(t[0], t[1], t[2], int(t[3]))
    raise ValueError(f"Cannot parse URI {uri}.")


class AxisOrder:
    XYZ = "XYZ"
    ZYX = "ZYX"


class array:
    """
    An intern/bossDB-backed numpy array.

    Like a numpy.memmap array, an emboss.array is backed by data that lives out
    of conventional memory. The data can live in, for example, a bossDB that
    lives in AWS, or it can live in a local or remote bossphorus instance.

    Data are downloaded when a request is made. This means that the emboss
    library does not work when the bossDB-like API is unavailable (as in cases
    where AWS is inaccessible or a bossphorus instance is offline).

    In the future, emboss will support local cache using bossphorus and Docker.
    For now, it is recommended that you use your own pass-through bossphorus
    instance to improve runtime of indexing requests.

    """

    def __init__(
        self,
        channel: Union[ChannelResource, Tuple],
        resolution: int = 0,
        volume_provider: VolumeProvider = None,
        axis_order: str = AxisOrder.ZYX,
    ) -> None:
        """
        Construct a new emboss.array.

        Arguments:
            channel (intern.resource.boss.ChannelResource): The channel from
                which data will be downloaded.
            backend (bossphorus.StorageManager): The storage manager to use
                for data-cache.
            use_backend (boolean: False): If no backend is specified, this may
                be set to True to construct a FilesystemBackend on the fly.
            volume_provider (VolumeProvider): TODO
        """
        self.axis_order = axis_order

        # Handle custom Remote:
        self.volume_provider = volume_provider
        if volume_provider is None:
            self.volume_provider = DEFAULT_VOLUME_PROVIDER()

        self.resolution = resolution
        # If the channel is set as a Resource, then use that resource.
        if isinstance(channel, ChannelResource):
            self._channel = channel
        # If it is set as a string, then parse the channel and generate an
        # intern.Resource from a bossDB URI.
        elif isinstance(channel, str):
            uri = parse_bossdb_uri(channel)
            self.resolution = uri.resolution
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
                    / 2 ** self.resolution
                ),
                int(
                    (self._coord_frame.x_stop - self._coord_frame.x_start)
                    / 2 ** self.resolution
                ),
                (self._coord_frame.z_stop - self._coord_frame.z_start),
            )
        elif self.axis_order == AxisOrder.ZYX:
            return (
                (self._coord_frame.z_stop - self._coord_frame.z_start),
                int(
                    (self._coord_frame.y_stop - self._coord_frame.y_start)
                    / 2 ** self.resolution
                ),
                int(
                    (self._coord_frame.x_stop - self._coord_frame.x_start)
                    / 2 ** self.resolution
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
            return (
                self._coord_frame.x_voxel_size,
                self._coord_frame.y_voxel_size,
                self._coord_frame.z_voxel_size,
            )
        elif self.axis_order == AxisOrder.ZYX:
            return (
                self._coord_frame.z_voxel_size,
                self._coord_frame.y_voxel_size,
                self._coord_frame.x_voxel_size,
            )

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
