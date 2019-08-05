import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from intern.resource.cv.resource import *
from intern.service.cv.service import *


gcp_path = '/kasthuri2015/test_dataset/em'

vol = CloudVolumeResource('gs', gcp_path, False)

cutout = vol.get_cutout([0,100], [0,100], [0,10])

imgplot = plt.imshow(volumeD[0,:,:], cmap = "gray")
plt.show()