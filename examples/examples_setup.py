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

# This script sets up the data model used by the example scripts.

from intern.remote.boss import BossRemote, LATEST_VERSION
from intern.resource.boss.resource import *
from requests import HTTPError
import sys

API_VER = LATEST_VERSION
rmt = BossRemote(cfg_file='example.cfg')
#rmt = BossRemote(cfg_file='test.cfg')
rmt.group_perm_api_version = API_VER

# Turn off SSL cert verification.  This is necessary for interacting with
# developer instances of the Boss.
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rmt.project_service.session_send_opts = { 'verify': False }
rmt.metadata_service.session_send_opts = { 'verify': False }
rmt.volume_service.session_send_opts = { 'verify': False }

coll = CollectionResource('gray', 'Collection used for examples.')
try:
    rmt.get_project(coll)
except HTTPError:
    rmt.create_project(coll)

coord = CoordinateFrameResource(
    'StdFrame', 'Standard coordinate frame for xyz.', 0, 50, 0, 50, 0, 50)
try:
    coord_actual = rmt.get_project(coord)
except HTTPError:
    coord_actual = rmt.create_project(coord)

alpha_exp = ExperimentResource(
    'alpha', 'gray', coord_actual.name, 'Alpha example experiment.',
try:
    rmt.get_project(alpha_exp)
except HTTPError:
    rmt.create_project(alpha_exp)

omega_chan = ChannelResource(
    'omega', 'gray', 'alpha', 'Example channel.', datatype='uint16')
try:
    omega_actual = rmt.get_project(omega_chan)
except HTTPError:
    omega_actual = rmt.create_project(omega_chan)

rho_layer = LayerResource(
    'rho', 'gray', 'alpha', 'Example layer.', datatype='uint64',
    channels=omega_actual.id)
try:
    rmt.get_project(rho_layer)
except HTTPError:
    rmt.create_project(rho_layer)

grp_name = 'example_group'
if not rmt.get_group(grp_name):
    rmt.create_group(grp_name)

print('Data model for examples setup.')
