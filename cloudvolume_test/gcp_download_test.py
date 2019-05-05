import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from intern.resource.cv.resource import *
from intern.service.cv.service import *


gcp_path = '/kasthuri2015/test_dataset/em'

vol = CloudVolumeResource('gs', gcp_path, False)

cutout = vol.get_cutout([0,100], [0,100], [0,10])

for z in range(10):
	im = Image.fromarray(cutout[:,:,z,0])
	im.save('cutout_{}.png'.format(z)) 
