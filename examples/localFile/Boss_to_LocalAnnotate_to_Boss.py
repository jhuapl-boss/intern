import intern
from intern.remote.localFile import LocalRemote
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
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
#Local Upload
local = LocalRemote({
    "host": "/Users/rodrilm2/InternRel/",
    "datastore":"LocalBossDummy"
    })
print local
chan_setup = local.get_channel('em','pinky40')
proj = local.create_project(chan_setup)
volume = local.create_cutout(proj,'v1',volumeB)

#LocalMetadata updates
Channel1 = local.retrieve('em')
Collection1 = local.retrieve('em/pinky40')

coll_data = {'poc': 'Jane Doe'}
local.create_metadata(Channel1, coll_data)

exp_data = {'weight': '20g', 'diet': 'C2', 'date': '23-May-2016'}
local.create_metadata(Collection1, exp_data)

chan_new_data = {'weight': '45g', 'date': '23-May-2017'}
local.update_metadata(Collection1, chan_new_data)

local.delete_metadata(Channel1, ['poc'])

CollectionMeta= local.list_metadata(Collection1)
print CollectionMeta

#Data processing can also be done here before re-upload

#Local to Boss upload of annotated data
chan_setup = get_channel('CHAN_NAME', 'COLL_NAME', 'EXP_NAME', 'image', datatype='uint16')
chan = BossRemote.create_project(chan_setup)
xspan = [0, 200]
yspan = [0, 90]
zspan = [0, 20]

VolumeLmeta.astype(numpy.uint16)
BossRemote.create_cutout(chan, 0, xspan, yspan, zspan, VolumeLMeta)
