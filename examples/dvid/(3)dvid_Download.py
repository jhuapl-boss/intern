import intern
from intern.remote.dvid import DVIDRemote
import matplotlib.pyplot as plt

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})

chan = "UUID/ChannelName"
volumeD = dvid.get_cutout(
	dvid.get_channel(chan),0,
	[0,2560],[0,2560],[390,392]
	)
print(volumeD)

imgplot = plt.imshow(volumeD[0,:,:])
plt.show()
