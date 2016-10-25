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
This example shows how to manipulate permissions for resources.  The Remote
class methods that begin with 'permission_' provide this functionality.

Permissions are assigned to groups at the resource level.  For example,
assume Orange University is collaborating with the Purple Lab on an experiment
called Blue Mouse.  If Purple Lab is the owner of the experiment, it might
assign all permissions to users that are members of the Purple Lab group.  For
members of the Orange University group, it might only give read permissions to
the Blue Mouse experiment.
"""

from ndio.remote.boss import BossRemote, LATEST_VERSION
from ndio.resource.boss.resource import *

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

grp_name = 'example_group'

coll = CollectionResource('gray')
exp = ExperimentResource('alpha', coll.name, 'StdFrame')
chan = ChannelResource('omega', coll.name, exp.name)
lyr = LayerResource('rho', coll.name, exp.name)

# Manipulate permissions at the collection level.

print('Add all permissions to the {} collection . . .'.format(coll.name))
all_perms = ['read', 'add', 'update', 'delete', 'assign_group', 'remove_group']
rmt.permissions_add(grp_name, coll, all_perms)

print('Visually confirm permissions added to the {} collection . . .'.format(coll.name))
print(rmt.permissions_get(grp_name, coll))

print('Remove the `remove_group` permission from the {} collection . . .'.format(coll.name))
rmt.permissions_delete(grp_name, coll, ['remove_group'])

print('Visually confirm removal of `remove_group` permission . . .')
print(rmt.permissions_get(grp_name, coll))


# Manipulate permissions at the experiment level.

print('\nAdd permissions to the {} experiment . . .'.format(exp.name))
rmt.permissions_add(grp_name, exp, ['add', 'read'])

print('Visually confirm permissions added to the {} experiment . . .'.format(exp.name))
print(rmt.permissions_get(grp_name, exp))

# Note that adding a new permission adds to the existing permissions assigned
# to the group.
print('Add `update` permission to the {} experiment . . .'.format(exp.name))
rmt.permissions_add(grp_name, exp, ['update'])

print('Visually confirm permission added to the {} experiment . . .'.format(exp.name))
print(rmt.permissions_get(grp_name, exp))


# Channels and layers have three additional permissions: 
# 'add_volumetric_data'
# 'read_volumetric_data'
# 'delete_volumetric_data'

all_vol_perms = [
    'add_volumetric_data', 'read_volumetric_data', 'delete_volumetric_data']

print('\nAdd all permissions to the {} channel . . .'.format(chan.name))
rmt.permissions_add(grp_name, chan, all_perms + all_vol_perms)

print('Visually confirm permissions added to the {} channel . . .'.format(chan.name))
print(rmt.permissions_get(grp_name, chan))

print('Remove all delete permissions from the channel . . .')
rmt.permissions_delete(grp_name, chan, ['delete', 'delete_volumetric_data'])

print('Visually confirm permissions removed from the {} channel . . .'.format(chan.name))
print(rmt.permissions_get(grp_name, chan))

