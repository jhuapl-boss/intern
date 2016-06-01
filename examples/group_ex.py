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
This example shows how to work with the Boss' groups.  The Remote
class methods that being with 'group_' perform group operations.
"""

from ndio.remote.boss.remote import Remote
from ndio.ndresource.boss.resource import *

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

# Note spaces are not allowed in group names.
grp_name = 'my_group'

# Boss user names still in flux.
user_name = 'dce21e38-a316-4ab4-accb-79029e'

print('Creating group . . .')
if not rmt.group_create(grp_name):
    print('Failed to create group {}'.format(grp_name))

print('Get info about group . . .')
data = rmt.group_get(grp_name)
print(data)

print('Add user to group . . .')
if not rmt.group_add_user(grp_name, user_name):
    print('Failed to add {} to group {}'.format(user_name, grp_name))

print('Confirm user is member of group . . .')
if rmt.group_get(grp_name, user_name):
    print('Confirmed')
else:
    print('NOT a member of the group')

print('Remove user from group . . .')
if not rmt.group_delete(grp_name, user_name):
    print('Failed removing user from group')

print('Confirm user is not a member of group . . .')
if rmt.group_get(grp_name, user_name):
    print('Still a member of the group; removal must have failed')
else:
    print('Confirmed')

print('Deleting group . . .')
if not rmt.group_delete(grp_name):
    print('Failed to delete group {}'.format(grp_name))
