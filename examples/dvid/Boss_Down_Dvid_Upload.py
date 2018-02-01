import intern
from intern.remote.dvid import DVIDRemote
from intern.remote.boss import BossRemote
from PIL import Image
import numpy as np
import os
import matplotlib.pyplot as plt

# BOSS Data fetch:
boss = BossRemote({
    "protocol": "https",
    "host": "api.theboss.io",
    "token": "token",
})
volumeB = boss.get_cutout(
    boss.get_channel("em", "pinky40", "v7"), 2,
    [10000, 10200], [10000, 10200], [501, 502],
)

#UPLOAD TO DVID REPOSITORY
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
    })

chan_setup = dvid.ChannelResource('pinky40','BossData RemoteTest', 'Data uploaded from Boss to dvid')
proj = dvid.create_project(chan_setup)
UUID = chan_setup.split("/")
UUID = UUID[0]

xrang = [0, 32]
yrang = [0, 32]
zrang = [32,64]

volume = dvid.create_cutout(proj,xrang,yrang,zrang,volumeB)

#Check DVID Data:
volumeD = dvid.get_cutout(
	dvid.get_channel(UUID,"pinky40","Medulla"), 0,
	[0,200],[0,200],[32,33]
	)
print(volumeD)

imgplot = plt.imshow(volumeD[:,:,0], cmap = "gray")
plt.show()
