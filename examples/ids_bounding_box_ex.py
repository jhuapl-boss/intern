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

"""
This example demonstrates the object services supplied by the Boss.
"""
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
import numpy
from requests import HTTPError


rmt = BossRemote('example.cfg')

COLL_NAME = 'gray'
EXP_NAME = 'alpha'
CHAN_NAME = 'ex_EM'
ANN_CHAN_NAME = 'ex_EM_ann'

# Create or get a source channel for the annotation channel.
chan_setup = ChannelResource(
    CHAN_NAME, COLL_NAME, EXP_NAME, 'image', 'Example channel.', datatype='uint16')
try:
    chan_actual = rmt.get_project(chan_setup)
except HTTPError:
    chan_actual = rmt.create_project(chan_setup)

# Create the annotation channel.
# Note that annotation channels must be uint64.
ann_chan_setup = ChannelResource(
    ANN_CHAN_NAME, COLL_NAME, EXP_NAME, 'annotation',
    'Example annotation channel.', datatype='uint64', sources=[CHAN_NAME])
try:
    ann_chan_actual = rmt.get_project(ann_chan_setup)
except HTTPError:
    ann_chan_actual = rmt.create_project(ann_chan_setup)

print('Data model setup.')

# Ranges use the Python convention where the number after the : is the stop
# value.  Thus, x_rng specifies x values where: 0 <= x < 100.
x_rng = [0, 100]
y_rng = [0, 100]
z_rng = [0, 10]

# Make sure our numpy array dimensions match the ranges we will use for our
# annotation data.
np_size = (z_rng[1]-z_rng[0], y_rng[1]-y_rng[0], x_rng[1]-x_rng[0])

# Reserve a block of 10 ids.
start_id = rmt.reserve_ids(ann_chan_actual, 10)

# Note that the numpy matrix is in Z, Y, X order.
ann_data = numpy.random.randint(start_id, start_id+10, np_size, dtype='uint64')
# Make sure start_id is used at least once.
ann_data[0][1][1] = start_id

# 0 is native resolution.
res = 0

# Upload annotation data to the channel.
rmt.create_cutout(ann_chan_actual, res, x_rng, y_rng, z_rng, ann_data)

# Verify that the cutout uploaded correctly.
ann_cutout_data = rmt.get_cutout(ann_chan_actual, res, x_rng, y_rng, z_rng)
numpy.testing.assert_array_equal(ann_data, ann_cutout_data)

print('Annotation data uploaded and verified.')

# Get ids in the region.
ids = rmt.get_ids_in_region(ann_chan_actual, res, x_rng, y_rng, z_rng)

print('Ids in region are:')
print(ids)

# Get the loose bounding box for id start_id.  This should be the bounds of the
# first cuboid (512, 512, 16).

loose = rmt.get_bounding_box(ann_chan_actual, res, start_id, bb_type='loose')

print('Loose bounding box for {}:'.format(start_id))
print(loose)

# Get the tight bounding box for id start_id.
tight = rmt.get_bounding_box(ann_chan_actual, res, start_id, bb_type='tight')

print('Tight bounding box for {}:'.format(start_id))
print(tight)

# Clean up.
rmt.delete_project(ann_chan_actual)
rmt.delete_project(chan_actual)
