import intern
from intern.remote.dvid import DVIDRemote

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})

#This path leads to where your data is stored.
path = "/Users/rod/to/where/your/data/is"


#Creating Local Dvid Repository
#Specification include: name of container, container port,
#and port number along with path
repo = dvid.StartLocalDvid("xbrain_dvid11","xbrain_port11","8000",path)
