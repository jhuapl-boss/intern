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
This example shows how to manage metadata with the Boss API.  The Remote
class methods that being with 'metadata_' manipulate metadata.  These
methods are:
    metadata_list()
    metadata_create()
    metadata_get()
    metadata_update()
    metadata_delete()

All of these methods take a ndio.ndresource.boss.resource.Resource object, as
a minimum.  The resource object identifies which data model object's metadata
will be manipulated.
"""

from ndio.remote.boss.remote import Remote, LATEST_VERSION
from ndio.ndresource.boss.resource import *

rmt = Remote('example.cfg')
#rmt = Remote('test.cfg')

API_VER = LATEST_VERSION

# Turn off SSL cert verification.  This is necessary for interacting with
# developer instances of the Boss.
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rmt.project_service.session_send_opts = { 'verify': False }
rmt.metadata_service.session_send_opts = { 'verify': False }
rmt.volume_service.session_send_opts = { 'verify': False }

# First, create resource objects that identify the objects of interest in the
# data model.  Notice, that only the minimal information needed to identify
# the objects of interest is given to the resources' constructors.
coll = CollectionResource('gray', API_VER)
alpha_exp = ExperimentResource('alpha', 'gray', API_VER)
omega_chan = ChannelResource('omega', 'gray', 'alpha', API_VER)

# Add new metadata using metadata_create().
rmt.metadata_create(coll, { 'mark': 'two', 'ten': 'four'})
rmt.metadata_create(alpha_exp, { 'date': '04May2016', 'time': '13:00' })
rmt.metadata_create(
    omega_chan, { 'channel_prep': '342', 'microscope': 'sem4' })

# Retrieve metadata with metadata_get().
# Use a list with a single string if you only want a single value.
mark = rmt.metadata_get(coll, ['mark'])
print(mark['mark'])
omega_metadata = rmt.metadata_get(omega_chan, ['channel_prep', 'microscope'])
print('omega\'s key-values:')
for pair in omega_metadata.items():
    print('\t{}: {}'.format(pair[0], pair[1]))

# List existing metadata keys using metadata_list().
alpha_list = rmt.metadata_list(alpha_exp)
print('alpha\'s keys:')
for ka in alpha_list:
    print('\t{}'.format(ka))
omega_list = rmt.metadata_list(omega_chan)
print('omega\'s keys:')
for ko in omega_list:
    print('\t{}'.format(ko))

# Update metadata using metadata_update().
rmt.metadata_update(omega_chan, {'channel_prep': '345', 'microscope': 'sem5'})

# Confirm updated values.
omega_metadata = rmt.metadata_get(omega_chan, ['channel_prep', 'microscope'])
print(omega_metadata['channel_prep'])
print(omega_metadata['microscope'])

# Use metadata_delete() to remove keys and values.
rmt.metadata_delete(alpha_exp, ['date', 'time'])
rmt.metadata_delete(coll, ['mark', 'ten'])
rmt.metadata_delete(
    omega_chan, ['channel_prep', 'microscope'])
