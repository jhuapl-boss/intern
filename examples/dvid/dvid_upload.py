import blosc
from PIL import Image
import requests
import numpy as np
import matplotlib.pyplot as plt

import json

import intern
from intern.remote.dvid import DVIDRemote
from intern.resource.dvid.resource import DataInstanceResource
from intern.resource.dvid.resource import RepositoryResource

#DVID Data fetch:
rmt = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8001",
	})

fPath = "/Users/rodrilm2/Desktop/humans/{}.png".format(0)

img = Image.open("/Users/rodrilm2/Desktop/humans/0.png")
data_tile = np.asarray(img)
print(data_tile.shape)
data_tile = np.expand_dims(data_tile,axis=0)

data_tile = data_tile.copy(order="C")
print(data_tile.shape)
print(data_tile)
img = data_tile[0,:,:]
plt.imshow(img, 'gray')
plt.show()
compressed = blosc.pack_array(data_tile)

instance_setup = DataInstanceResource("Sample_Tiles", None, 'imagetile',"Testing Upload", 'Example upload.', datatype='uint8')
instance_uuid = rmt.create_project(instance_setup)

print(rmt.get_info(instance_setup))

print(instance_uuid)


meta = requests.post("http://localhost:8001/api/node/{}/Sample_Tiles/metadata".format(instance_uuid), 
	data = json.dumps({
		"MinTileCoord": [0, 0, 0],
		"MaxTileCoord": [128, 128, 5],
		"Levels": {
			"0": {  
				"Resolution": [0, 0, 0], 
				"TileSize": [128, 128, 1] }
			}
		}))

print(meta.status_code)
print(meta.content)

resp = requests.post("http://localhost:8001/api/node/{}/Sample_Tiles/tile/xy/0/0_0_0".format(instance_uuid), data = compressed)
print(resp.status_code)

octet_stream = (requests.get("http://localhost:8001/api/node/{}/Sample_Tiles/tile/xy/0/0_0_0".format(instance_uuid))).content

#Converts obtained octet-stream into a numpy array of specified type uint8
block = blosc.unpack_array(octet_stream)

print(block.shape)

if (block == data_tile).all():
	print("You did it!")

##### UPLOAD A NUMPY ####

from intern.remote.dvid import DVIDRemote
from intern.resource.dvid import DataInstanceResource
import numpy as np
dvid = DVIDRemote({
    "protocol": "http",
    "host": "localhost:8001",
    })
# Prepare the data
data_cube = np.load('<PATH>/validation_grayscale.npy').astype(np.uint8)
data_cube = data_cube[0:512,0:512,0:512]
data_cube = data_cube.copy(order="C")
print(data_cube.dtype)
print(data_cube.shape)
# Create the project
instance_setup_up = DataInstanceResource(alias='local_dvid_test', type='uint8blk', name='validation', UUID = None, datatype='uint8')
chan_actual_up = dvid.create_project(instance_setup_up)
# Create the cutout
dvid.create_cutout(instance_setup_up, 0, [0,512],[0,512],[0,512], data_cube)
print("Create cutout successful")
# Get the cutout
got_cutout = dvid.get_cutout(instance_setup_up, 0, [0,512],[0,512],[0,1])
print(got_cutout.shape)

print("Arrays match: {}".format(np.array_equal(got_cutout, data_cube[0:1,:,:])))