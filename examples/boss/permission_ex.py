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

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *

# Here we pass in a config file to provide credentials.  There are multiple ways to provide credentials, which are
# described in the intern docs on GitHub
rmt = BossRemote('example.cfg')

# Group names are unique, so a conflict may occur if another user ran this example.
grp_name = 'example_group'

# Create some resource instances that we can add permissions to
coll = CollectionResource('gray')
exp = ExperimentResource('alpha', coll.name, 'StdFrame')
chan = ChannelResource('omega', coll.name, exp.name)

# Manipulate permissions at the collection level.
# Attach a group, to a collection with a set of permissions
print('Add all permissions to the {} collection . . .'.format(coll.name))
all_perms = ['read', 'add', 'update', 'delete', 'assign_group', 'remove_group']
rmt.add_permissions(grp_name, coll, all_perms)

print('Visually confirm permissions added to the {} collection . . .'.format(coll.name))
print(rmt.get_permissions(grp_name, coll))

print('Remove the assigned permissions from the {} collection . . .'.format(coll.name))
rmt.delete_permissions(grp_name, coll)

print('Visually confirm removal of `remove_group` permission . . .')
print(rmt.get_permissions(grp_name, coll))


# Manipulate permissions at the experiment level.
print('\nAdd permissions to the {} experiment . . .'.format(exp.name))
rmt.add_permissions(grp_name, exp, ['add', 'read'])

print('Visually confirm permissions added to the {} experiment . . .'.format(exp.name))
print(rmt.get_permissions(grp_name, exp))

# Update the permissions. Not update operation overwrite the permission set
print('Add `update` permission to the {} experiment . . .'.format(exp.name))
rmt.update_permissions(grp_name, exp, ['update', 'add', 'read'])

print('Visually confirm permission added to the {} experiment . . .'.format(exp.name))
print(rmt.get_permissions(grp_name, exp))

print('Remove all delete permissions from the experiment . . .')
rmt.delete_permissions(grp_name, exp)


# Channels have three additional permissions:
# 'add_volumetric_data'
# 'read_volumetric_data'
# 'delete_volumetric_data'

all_vol_perms = [
    'add_volumetric_data', 'read_volumetric_data', 'delete_volumetric_data']

print('\nAdd all permissions to the {} channel . . .'.format(chan.name))
rmt.add_permissions(grp_name, chan, all_perms + all_vol_perms)

print('Visually confirm permissions added to the {} channel . . .'.format(chan.name))
print(rmt.get_permissions(grp_name, chan))

print('Remove all delete permissions from the channel . . .')
rmt.delete_permissions(grp_name, chan)

print('Visually confirm permissions removed from the {} channel . . .'.format(chan.name))
print(rmt.get_permissions(grp_name, chan))

