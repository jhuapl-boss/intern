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
This example shows how to work with the Boss' groups.  Specifically, this
example demonstrates creating and deleting groups and managing the users that
belong to a group.  The Remote class methods that begin with 'group_' perform
group operations.

Groups are collections of users.  Permissions are associated with groups
and resources.  The three combined determine what a user may do with a
particular resource.
"""

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
from requests import HTTPError

rmt = BossRemote('example.cfg')

# Note spaces are not allowed in group names.
grp_name = 'my_group'

user_name = 'example_user'
print('Creating user . . .')
rmt.add_user(user_name, 'John', 'Doe', 'jd@example.com', 'secure_password')

print('Creating group . . .')
try:
    rmt.create_group(grp_name)
except HTTPError as h:
    # Assume group already exists if an exception raised.
    print(h.response.content)

print('Confirm group created . . .')
if rmt.get_group(grp_name):
    print('Confirmed')

#############################################################################
# The user needs to login before group operations can be performed.
# This is due to the Single-Sign On workflow requires a manual log into update
# the application database
#############################################################################

print('Add user to group . . .')
rmt.add_group_member(grp_name, user_name)

print('Confirm user is member of group . . .')
if rmt.get_is_group_member(grp_name, user_name):
    print('Confirmed')
else:
    print('NOT a member of the group')

print('Remove user from group . . .')
rmt.delete_group_member(grp_name, user_name)

print('Confirm user is not a member of group . . .')
if rmt.get_is_group_member(grp_name, user_name):
    print('Still a member of the group; removal must have failed')
else:
    print('Confirmed')

print('Deleting group . . .')
rmt.delete_group(grp_name)

print('\nClean up be deleting the user . . .')
rmt.delete_user(user_name)
