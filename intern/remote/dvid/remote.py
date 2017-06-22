from intern.remote import Remote
import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy
# from StringIO import StringIO
#From service.DVID. x
	#where x are either the project the metadata file or the volume

# class UUIDResource(Resource):
#     def __init__(self, dataset_uuid):
#         self.uuid = dataset_uuid
#     def
#         if not resource.valid_volume():
#         raise RuntimeError('Resource incompatible with the volume service.')
#         return self._volume.create_cutout(
#             resource, resolution, x_range, y_range, z_range, data, time_range)

class DVIDRemote(Remote):

	# def __init__()
	# 	pass

	def get_cutout(ID, scale, typev, shape, xpix, ypix, xo, yo, zo):
	    #ID MUST BE STRING ""
	    #SCALE MUST BE STRING "" - "GRAYSCALE"
	    #TYPEV MUST BE STRING "" - "RAW"
	    #SHAPE MUST BE STRING "" - 'XY'
	    #self.resource = resource
	    # self.resolution = resolution
	    # self.x_range = x_range
	    # self.y_range = y_range
	    # self.z_range = z_range
	    #shape = "xy"
	    #xpix = "x" how much pixels traveled in x
	    #ypix = "y" how much pixels traveled in y
	    #xo, yo, zo (x,y,z offsets)
	    #type = "raw"
	    #scale = "grayscale"
	    size = str(xpix) + "_" + str(ypix)
	    offset = str(xo) + "_" + str(yo) + "_" + str(zo)

	    address = "http://34.200.231.1/api/node/" + ID + "/" + scale + "/" + typev + "/" + shape + "/" + size + "/" + offset
	    r = requests.get(address)
	    bytes1 = r.content
	    stream = BytesIO(bytes1)
	    img = Image.open(stream)
	    a = numpy.asarray(img)
	    return a

	# def create_cutout(self, resource, resolution, x_range, y_range, z_range, data, time_range=None):
	       
 #        if not resource.valid_volume():
 #            raise RuntimeError('Resource incompatible with the volume service.')
 #        return self._volume.create_cutout(
 #            resource, resolution, x_range, y_range, z_range, data, time_range)



    # def get_cutout(self, UUIDResource, x_range, y_range, z_range, resolution):
    #     # this is a secret between you and the computer

    #     download_url = "https://dvid.org/" + uuid + "/download_data/"
    #     # look up how to use `requests` library to download binary data
    #     return requests.get(download_url).data