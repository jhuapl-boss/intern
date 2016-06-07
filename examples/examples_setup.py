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

from ndio.remote.boss.remote import Remote
from ndio.ndresource.boss.resource import *
from requests import HTTPError
import sys

rmt = Remote('example.cfg')

API_VER = 'v0.4'

# Turn off SSL cert verification.  This is necessary for interacting with
# developer instances of the Boss.
import requests
from requests import Session
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rmt.project_service.session_send_opts = { 'verify': False }
rmt.metadata_service.session_send_opts = { 'verify': False }
rmt.volume_service.session_send_opts = { 'verify': False }

coll = CollectionResource('gray', API_VER, 'Collection used for examples.')
if rmt.project_get(coll) is None:
    rmt.project_create(coll)

coord = CoordinateFrameResource('StdFrame', API_VER, 'Standard coordinate frame for xyz.')
coord_actual = rmt.project_get(coord)
if coord_actual is None:
    rmt.project_create(coord)
    coord_actual = rmt.project_get(coord)

alpha_exp = ExperimentResource(
    'alpha', 'gray', API_VER, 'Alpha example experiment.', coord_actual.id, max_time_sample=600)
if rmt.project_get(alpha_exp) is None:
    rmt.project_create(alpha_exp)

omega_chan = ChannelResource(
    'omega', 'gray', 'alpha', API_VER, 'Example channel.', datatype='uint16')
omega_actual = rmt.project_get(omega_chan)
if omega_actual is None:
    rmt.project_create(omega_chan)
    omega_actual = rmt.project_get(omega_chan)

rho_layer = LayerResource(
    'rho', 'gray', 'alpha', API_VER, 'Example layer.', datatype='uint64', 
    channels=omega_actual.id)
rho_actual = rmt.project_get(rho_layer)
if rho_actual is None:
    rmt.project_create(rho_layer)

print('Data model for examples setup.')
