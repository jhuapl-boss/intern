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
This example demonstrates user management.  To run this example, you must have 
a user with either the user-manager role or the admin role.
"""

from ndio.remote.boss import BossRemote, LATEST_VERSION
from ndio.ndresource.boss.resource import *
from requests import HTTPError

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

user = 'example_user'

print('Creating user . . .')
rmt.user_add(user, 'John', 'Doe', 'jd@me.com', 'secure_password')

print('\nGet the user just created . . .')
user_data = rmt.user_get(user)
print(user_data)

print('\nMake the user a resource manager . . .')
rmt.user_add_role(user, 'resource-manager')

print('\nList the user\'s roles . . .')
print(rmt.user_get_roles(user))

print('\nRemove the resource manager role . . .')
rmt.user_delete_role(user, 'resource-manager')

print('\nList the user\'s roles again. . .')
print(rmt.user_get_roles(user))

print('\nList the user\'s groups . . .')
print(rmt.user_get_groups(user))

print('\nClean up be deleting the user . . .')
rmt.user_delete(user)
