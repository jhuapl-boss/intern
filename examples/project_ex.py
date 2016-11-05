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
This example shows how to work with the Boss' data model.  The Remote
class methods that being with 'project_' operate on the data model. These
methods are:
    list_project()
    create_project()
    get_project()
    update_project()
    delete_project()

All of these methods take a intern.resource.boss.resource.Resource object, as
a minimum.  The resource object identifies where in the data model hierarchy
the operation should be performed.  For create and update operations, the
resource object also contains the parameters to place in the database.
"""

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *

rmt = BossRemote('example.cfg')

# List current collections.
coll_list = rmt.list_collections()
print("Collections: {}".format(coll_list))

# For resources below the collection level, the parents must be specified.
# For example to list all the channels that are part of the gray collection
# and alpha experiment:
chan_list = rmt.list_channels('gray', 'alpha')
print("Channels in Collection - gray and Experiment - alpha: {}".format(chan_list))

# When creating a new resource, the corresponding resource object will need
# the required attributes populated.
# For example, to add an "image" style channel named beta to the alpha experiment referenced
# in the previous example:
betaChan = ChannelResource('beta', 'gray', 'alpha', 'image')
newBetaChan = rmt.create_project(betaChan)

# Note that the create method returns a new instance of the ChannelResource.
# The new instance has its `raw` attribute populated with all the JSON data 
# returned by the Boss API.

# Display raw channel data from the Boss API:
print(newBetaChan.raw)

# We forgot, to indicate that this channel is related to the omega channel.
# Let's fix that by updating the channel.
newBetaChan.related = ['omega']
betaChanUpdated = rmt.update_project(newBetaChan.name, newBetaChan)

# Let's verify the data type was updated.
print(betaChanUpdated.related)

# To demonstrate the final method available for project operations, we will
# delete the beta channel.
rmt.delete_project(betaChan)

