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

rmt = Remote('test.cfg')

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
try:
    rmt.project_get(coll)
except HTTPError:
    if(not rmt.project_create(coll)):
        print('Couldn''t create collection {}, aborting.'.format(coll.name))
        sys.exit(1)

coord = CoordinateFrameResource('StdFrame', API_VER, 'Standard coordinate frame for xyz.')
try:
    coord_data = rmt.project_get(coord)
except HTTPError:
    if(not rmt.project_create(coord)):
        print('Couldn''t create coordinate frame {}, aborting.'.format(coord.name))
        sys.exit(1)
    coord_data = rmt.project_get(coord)

alpha_exp = ExperimentResource(
    'alpha', 'gray', API_VER, 'Alpha example experiment.', coord_data['id'])
try:
    rmt.project_get(alpha_exp)
except HTTPError:
    if(not rmt.project_create(alpha_exp)):
        print('Couldn''t create experiment {}, aborting.'.format(alpha_exp.name))
        sys.exit(1)

omega_chan = ChannelResource('omega', 'gray', 'alpha', API_VER, 'Example channel.')
try:
    rmt.project_get(omega_chan)
except HTTPError:
    if(not rmt.project_create(omega_chan)):
        print('Couldn''t create channel {}, aborting.'.format(omega_chan.name))
        sys.exit(1)


print('Data model for examples setup.')
