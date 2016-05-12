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

from ndio.remote.boss.remote import Remote
from ndio.ndresource.boss.resource import *

rmt = Remote('test.cfg')

API_VER = 'v0.4'

# Turn off SSL cert verification
import requests
from requests import Session
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
rmt.project_service.session_send_opts = { 'verify': False }
rmt.metadata_service.session_send_opts = { 'verify': False }
rmt.volume_service.session_send_opts = { 'verify': False }

# List current collections.
# In general, when performing a list operation, any resource may be used as 
# long as it is the same type.
# For example, to list collections, a CollectionResource without a name (an 
# empty string) may be used.
coll = CollectionResource('', API_VER)
coll_list = rmt.project_list(coll)

# For resources below the collection level, the parents must be specified.
# For example to list all the channels that are part of the gray collection 
# and alpha experiment:
channels = ChannelResource('', 'gray', 'alpha', API_VER)
chan_list = rmt.project_list(channels)

# When creating a new resource, the corresponding resource object will need
# the required attributes populated.
# For example, to add a channel named beta to the alpha experiment referenced
# in the previous example:
betaChan = ChannelResource('beta', 'gray', 'alpha', API_VER, 'test channel')
if(not rmt.project_create(betaChan)):
    print('Creating beta channel failed.')
