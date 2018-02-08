import intern
from intern.remote.dvid import DVIDRemote

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})

#Creating Project, and chanel to store boxed data in
proj = dvid.create_project('Xbrain_Proj1','Data upload test')
print("This is your UUID:" + proj)
chan_setup = dvid.ChannelResource(proj, "MaskedImg1")

#Uploading data
dataU = dvid.create_cutout(chan_setup,"xbrain_port9",0,0,390,"/*.tif")
