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

from ndio.remote.boss.remote import Remote, LATEST_VERSION
from ndio.ndresource.boss.resource import *
from requests import HTTPError
import sys

API_VER = LATEST_VERSION
rmt = Remote('example.cfg')
#rmt = Remote('test.cfg')
rmt.group_perm_api_version = API_VER

# Turn off SSL cert verification.  This is necessary for interacting with
# developer instances of the Boss.
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rmt.project_service.session_send_opts = { 'verify': False }
rmt.metadata_service.session_send_opts = { 'verify': False }
rmt.volume_service.session_send_opts = { 'verify': False }

coll = CollectionResource('gray', API_VER, 'Collection used for examples.')
try:
    rmt.project_get(coll)
except HTTPError:
    rmt.project_create(coll)

coord = CoordinateFrameResource(
    'StdFrame', API_VER, 'Standard coordinate frame for xyz.', 0, 50, 0, 50, 0, 50)
try:
    coord_actual = rmt.project_get(coord)
except HTTPError:
    coord_actual = rmt.project_create(coord)

alpha_exp = ExperimentResource(
    'alpha', 'gray', coord_actual.name, API_VER, 'Alpha example experiment.',
try:
    rmt.project_get(alpha_exp)
except HTTPError:
    rmt.project_create(alpha_exp)

omega_chan = ChannelResource(
    'omega', 'gray', 'alpha', API_VER, 'Example channel.', datatype='uint16')
try:
    omega_actual = rmt.project_get(omega_chan)
except HTTPError:
    omega_actual = rmt.project_create(omega_chan)

rho_layer = LayerResource(
    'rho', 'gray', 'alpha', API_VER, 'Example layer.', datatype='uint64', 
    channels=omega_actual.id)
try:
    rmt.project_get(rho_layer)
except HTTPError:
    rmt.project_create(rho_layer)

grp_name = 'example_group'
if not rmt.group_get(grp_name):
    rmt.group_create(grp_name)

print('Data model for examples setup.')
