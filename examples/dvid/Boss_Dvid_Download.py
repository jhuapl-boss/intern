import intern
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import ChannelResource
from intern.remote.dvid import DVIDRemote
import matplotlib.pyplot as plt
import numpy as np


# BOSS Data fetch:
boss = BossRemote({
    "protocol": "https",
    "host": "api.theboss.io",
    "token": "db1cec2c865fc84e48772f4f4a5f010c0a180b88",
})
volumeB = boss.get_cutout(
    boss.get_channel("em", "pinky40", "v7"), 1,
    [10000, 10500], [10000, 10500], [500, 550],
)

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})
volumeD = dvid.get_cutout(
	dvid.get_channel("5cc94d532799484cb01788fcdb7cd9f0","grayscale"),0,
	[2300,4600],[2300,4600],[1380,1390]
	)

#Printing volumes:
print("Dvid volume: ")
print(volumeD)
print("Boss volume: ")
print(volumeB)

#Graphing Boss:
imgplot = plt.imshow(volumeB[0,:,:], cmap = "gray")
one = volumeB[0,:,:]
one_size = one.size
plt.show()

#Graphing Dvid:
imgplot = plt.imshow(volumeD[0,:,:], cmap = "gray")
one = volumeD[:,:,0]
one_size = one.size
plt.show()
