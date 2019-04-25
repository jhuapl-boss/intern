import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from intern.resource.cv.resource import *
from intern.service.cv.service import *


gcp_path = '/kasthuri2015/test_dataset/em'

vol = CloudVolumeResource('gs', gcp_path, 
	num_channels = 1, 
	data_type = 'uint8',
	layer_type = 'image',
	encoding = 'raw',
	resolution = [1,1,1],
	voxel_offset = [0,0,0],
	chunk_size = [1100,700,1],
	volume_size = [1100,700,10],
	description = 'test with google cloud service')

for z in range(10):
	path = 'test_dataset/'
	img_name = 'image_{}.tiff'.format(z)
	image = Image.open(os.path.join(path, img_name))
	width, height = image.size
	IMarray = np.array(list(image.getdata()), dtype=np.uint8)
	IMarray = IMarray.reshape((1, height, width)).T
	vol.create_cutout(IMarray, [0, width], [0, height], [z,z+1])
	image.close()

cutout = vol.get_cutout([0,100], [0,100], [0,10])


for z in range(10):
	im = Image.fromarray(cutout[:,:,z,0])
	im.save('cutout_{}.png'.format(z)) 

print(CloudVolumeService.get_info(vol))
