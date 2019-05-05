"""
GCP Services Test
"""

import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from intern.resource.cv.resource import *
from intern.service.cv.service import *


gcp_path = '/kasthuri2015/test_dataset/em'

vol = CloudVolumeResource('gs', gcp_path, False)

print(CloudVolumeService.get_info(vol))
print(CloudVolumeService.get_provenance(vol))
print(CloudVolumeService._chunks_exist(vol, [0,25], [0,25],[0,10]))
#print(CloudVolumeService._chunks_exist(vol, [1120,1140], [20,25],[10,12]))
