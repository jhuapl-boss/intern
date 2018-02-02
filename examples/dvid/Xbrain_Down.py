import intern
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import ChannelResource
from intern.remote.dvid import DVIDRemote
import matplotlib.pyplot as plt
import numpy as np

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})
volumeD = dvid.get_cutout(
	dvid.get_channel("8d68a4c667984f00a05c39a97d44bc48","dyer15_3_maskim"),0,
	[0,2560],[0,2560],[390,400]
	)

#Printing volumes:
print("Dvid volume: ")
print(volumeD)

#Graphing Dvid:
imgplot = plt.imshow(volumeD[3,:,:], cmap = "gray")
plt.show()
