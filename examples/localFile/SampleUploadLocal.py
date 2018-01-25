import intern
from intern.remote.localFile import LocalRemote
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import ChannelResource
import matplotlib.pyplot as plt
import numpy as np

# BOSS Data fetch which we will upload to the Local Storage:
boss = BossRemote({
    "protocol": "https",
    "host": "api.theboss.io",
    "token": "db1cec2c865fc84e48772f4f4a5f010c0a180b88",
})
volumeB = boss.get_cutout(
    boss.get_channel("em", "pinky40", "v7"), 1,
    [10000, 10200], [10000, 10090], [500, 520],
)

#First start remote with path to be adressed and datastore name
#If the datastore name does not exist in the specified path, it will be create_dataset
#otherwise you may continue.
local = LocalRemote({
    "host": "/Users/rodrilm2/InternRel/",
    "datastore":"LocalBossDummy2"
    })

chan_setup = local.get_channel('em','pinky40')
proj = local.create_project(chan_setup)
volume = local.create_cutout(proj,'v1',volumeB)

#To download the data you can use the get_cutout function just as in the boss remote
volumeL = local.get_cutout(
    local.get_channel('em', 'pinky40', 'v1'), 1,
    [0, 200], [0, 90], [0, 20]
)

#Showing a slice of the volume
imgplot = plt.imshow(volumeL[0,:,:])
plt.show()

#Creating a extra collection and channel for demonstration purposes
chan_setup = local.get_channel('MouseBrain','testSet')
proj = local.create_project(chan_setup)

chan_setup = local.get_channel('FlyBrain','testSet1')
proj = local.create_project(chan_setup)

chan_setup = local.get_channel('FlyBrain','testSet2')
proj = local.create_project(chan_setup)

#Additional possible functions
print 'This is a list of all the posible files you can access within this local datastore:'
print local.list()

print 'Using local.retrieve you can get the HDF5 dataset saved on the requested path:'
print local.retrieve('em/pinky40/v1')
