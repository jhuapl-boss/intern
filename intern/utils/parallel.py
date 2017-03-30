# Copyright 2016 NeuroData (http://neurodata.io)
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

from __future__ import absolute_import
import numpy
from six.moves import range


def snap_to_cube(q_start, q_stop, chunk_depth=16, q_index=1):
    """
    For any q in {x, y, z, t}
    Takes in a q-range and returns a 1D bound that starts at a cube
    boundary and ends at another cube boundary and includes the volume
    inside the bounds. For instance, snap_to_cube(2, 3) = (1, 17)

    Arguments:
        q_start (int): The lower bound of the q bounding box of volume
        q_stop (int): The upper bound of the q bounding box of volume
        chunk_depth (int : CHUNK_DEPTH) The size of the chunk in this
            volume (use ``get_info()``)
        q_index (int : 1): The starting index of the volume (in q)

    Returns:
        2-tuple: (lo, hi) bounding box for the volume
    """
    lo = 0
    hi = 0
    # Start by indexing everything at zero for our own sanity
    q_start -= q_index
    q_stop -= q_index

    if q_start % chunk_depth == 0:
        lo = q_start
    else:
        lo = q_start - (q_start % chunk_depth)

    if q_stop % chunk_depth == 0:
        hi = q_stop
    else:
        hi = q_stop + (chunk_depth - q_stop % chunk_depth)

    return [lo + q_index, hi + q_index + 1]


def block_compute(x_start, x_stop,
                  y_start, y_stop,
                  z_start, z_stop,
                  origin=(0, 0, 0),
                  block_size=(512, 512, 16)):
    """
    Get bounding box coordinates (in 3D) of small cutouts to request in
    order to reconstitute a larger cutout.

    Arguments:
        x_start (int): The lower bound of dimension x
        x_stop (int): The upper bound of dimension x
        y_start (int): The lower bound of dimension y
        y_stop (int): The upper bound of dimension y
        z_start (int): The lower bound of dimension z
        z_stop (int): The upper bound of dimension z


    Returns:
        [((x_start, x_stop), (y_start, y_stop), (z_start, z_stop)), ... ]
    """
    # x
    x_bounds = range(origin[0], x_stop + block_size[0], block_size[0])
    x_bounds = [x for x in x_bounds if (x > x_start and x < x_stop)]
    if len(x_bounds) is 0:
        x_slices = [(x_start, x_stop)]
    else:
        x_slices = []
        for start_x in x_bounds[:-1]:
            x_slices.append((start_x, start_x + block_size[0]))
        x_slices.append((x_start, x_bounds[0]))
        x_slices.append((x_bounds[-1], x_stop))

    # y
    y_bounds = range(origin[1], y_stop + block_size[1], block_size[1])
    y_bounds = [y for y in y_bounds if (y > y_start and y < y_stop)]
    if len(y_bounds) is 0:
        y_slices = [(y_start, y_stop)]
    else:
        y_slices = []
        for start_y in y_bounds[:-1]:
            y_slices.append((start_y, start_y + block_size[1]))
        y_slices.append((y_start, y_bounds[0]))
        y_slices.append((y_bounds[-1], y_stop))

    # z
    z_bounds = range(origin[2], z_stop + block_size[2], block_size[2])
    z_bounds = [z for z in z_bounds if (z > z_start and z < z_stop)]
    if len(z_bounds) is 0:
        z_slices = [(z_start, z_stop)]
    else:
        z_slices = []
        for start_z in z_bounds[:-1]:
            z_slices.append((start_z, start_z + block_size[2]))
        z_slices.append((z_start, z_bounds[0]))
        z_slices.append((z_bounds[-1], z_stop))

    # alright, yuck. but now we have {x, y, z}_slices, each of which hold the
    # start- and end-points of each cube-aligned boundary. For instance, if you
    # requested z-slices 4 through 20, it holds [(4, 16), (16, 20)].

    # For my next trick, I'll convert these to a list of:
    # ((x_start, x_stop), (y_start, y_stop), (z_start, z_stop))

    chunks = []
    for x in x_slices:
        for y in y_slices:
            for z in z_slices:
                chunks.append((x, y, z))
    return chunks
