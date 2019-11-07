import intern
from intern.remote.dvid import DVIDRemote
import matplotlib.pyplot as plt

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8001",
	})

chan = "e40eecdd01074320b829da1255c4b4a5/Test_channel"
volumeD = dvid.get_cutout(
	dvid.get_channel(chan),0,
	[0,2560],[0,2560],[390,392]
	)
print(volumeD)

imgplot = plt.imshow(volumeD[0,:,:], cmap = "gray")
plt.show()
