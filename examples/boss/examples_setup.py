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
This script sets up the data model resource used by the example scripts.
To run this example (and create new resources), you must have a user with the resource-manager role!
"""

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
from requests import HTTPError


rmt = BossRemote('example.cfg')

coll = CollectionResource('gray', 'Collection used for examples.')
try:
    rmt.get_project(coll)
except HTTPError:
    rmt.create_project(coll)

coord = CoordinateFrameResource(
    'StdFrame', 'Standard coordinate frame for xyz.', 0, 2048, 0, 2048, 0, 64)
try:
    coord_actual = rmt.get_project(coord)
except HTTPError:
    coord_actual = rmt.create_project(coord)

alpha_exp = ExperimentResource(
    'alpha', 'gray', coord_actual.name, 'Alpha example experiment.',
    num_time_samples=10)
try:
    rmt.get_project(alpha_exp)
except HTTPError:
    rmt.create_project(alpha_exp)

omega_chan = ChannelResource(
    'omega', 'gray', 'alpha', 'image', 'Example channel.', datatype='uint16')
try:
    omega_actual = rmt.get_project(omega_chan)
except HTTPError:
    omega_actual = rmt.create_project(omega_chan)

rho_layer = ChannelResource(
    'rho', 'gray', 'alpha', 'annotation', 'Example layer.', datatype='uint64',
    sources=[omega_actual.name])
try:
    rmt.get_project(rho_layer)
except HTTPError:
    rmt.create_project(rho_layer)

grp_name = 'example_group'
try:
    rmt.get_group(grp_name)
except HTTPError:
    rmt.create_group(grp_name)

print('Data model for examples setup.')
