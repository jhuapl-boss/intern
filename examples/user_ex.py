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
This example demonstrates user management.
To run this example, you must have a user with the user-manager role!
"""
from intern.remote.boss import BossRemote

rmt = BossRemote('example.cfg')

user = 'example_user'

# Create a user. Note that users are unique, so you may need to change
# the user name for this example to run.
print('Creating user . . .')
rmt.add_user(user, 'John', 'Doe', 'jd@example.com', 'secure_password')

print('\nGet the user just created . . .')
user_data = rmt.get_user(user)
print(user_data)

#############################################################################
# The user needs to login before group operations can be performed.
# This is due to the Single-Sign On workflow requires a manual log into update
# the application database
#############################################################################

print('\nMake the user a resource manager . . .')
rmt.add_user_role(user, 'resource-manager')

print('\nList the user\'s roles . . .')
print(rmt.get_user_roles(user))

print('\nRemove the resource manager role . . .')
rmt.delete_user_role(user, 'resource-manager')

print('\nList the user\'s roles again. . .')
print(rmt.get_user_roles(user))

print('\nClean up be deleting the user . . .')
rmt.delete_user(user)
