#Before running this program you should make sure to have the correct version of intern installed on your device.
from intern.remote.dvid import DVIDRemote
import intern
import os
import platform
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy
import requests
import time


#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})

UUID = "5cc94d532799484cb01788fcdb7cd9f0"

#Getting information on the UUID
info = dvid.get_info(UUID)
print(info)

# Demonstration of obtaining and updating the log
log = dvid.get_log(UUID)
print(log)
logP = dvid.post_log(UUID,"This repository contains images used for testing2")
log = dvid.get_log(UUID)
print(log)


#Gets 3d volume data
volumeD = dvid.get_cutout(
	dvid.get_channel("5cc94d532799484cb01788fcdb7cd9f0","grayscale"),
	[2300,4600],[2300,4600],[1380,1390]
	)
print(volumeD)

imgplot = plt.imshow(volumeD[9,:,:])
plt.show()
