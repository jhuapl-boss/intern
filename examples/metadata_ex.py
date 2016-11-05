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
    list_metadata()
    create_metadata()
    get_metadata()
    update_metadata()
    delete_metadata()

All of these methods take a intern.resource.boss.resource.Resource object, as
a minimum.  The resource object identifies which data model object's metadata
will be manipulated.
"""

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *


rmt = BossRemote('example.cfg')

# First, create resource objects that identify the objects of interest in the
# data model.  Notice, that only the minimal information needed to identify
# the objects of interest is given to the resources' constructors.
coll = CollectionResource('gray')
alpha_exp = ExperimentResource('alpha', 'gray', 'StdFrame')
omega_chan = ChannelResource('omega', 'gray', 'alpha', 'image')

# Add new metadata using create_metadata().
rmt.create_metadata(coll, {'mark': 'two', 'ten': 'four'})
rmt.create_metadata(alpha_exp, {'date': '04May2016', 'time': '13:00'})
rmt.create_metadata(omega_chan, {'channel_prep': '342', 'microscope': 'sem4'})

# Retrieve metadata with get_metadata().
# Use a list with a single string if you only want a single value.
mark = rmt.get_metadata(coll, ['mark'])
print(mark['mark'])
omega_metadata = rmt.get_metadata(omega_chan, ['channel_prep', 'microscope'])
print('omega\'s key-values:')
for pair in omega_metadata.items():
    print('\t{}: {}'.format(pair[0], pair[1]))

# List existing metadata keys using list_metadata().
alpha_list = rmt.list_metadata(alpha_exp)
print('alpha\'s keys:')
for ka in alpha_list:
    print('\t{}'.format(ka))
omega_list = rmt.list_metadata(omega_chan)
print('omega\'s keys:')
for ko in omega_list:
    print('\t{}'.format(ko))

# Update metadata using update_metadata().
rmt.update_metadata(omega_chan, {'channel_prep': '345', 'microscope': 'sem5'})

# Confirm updated values.
omega_metadata = rmt.get_metadata(omega_chan, ['channel_prep', 'microscope'])
print(omega_metadata['channel_prep'])
print(omega_metadata['microscope'])

# Use delete_metadata() to remove keys and values.
rmt.delete_metadata(alpha_exp, ['date', 'time'])
rmt.delete_metadata(coll, ['mark', 'ten'])
rmt.delete_metadata(omega_chan, ['channel_prep', 'microscope'])
