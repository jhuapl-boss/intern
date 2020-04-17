import os
import numpy as np
import matplotlib.pyplot as plt

from intern.remote.cv.remote import *


gcp_path = "kasthuri2015/test_dataset/em"

cv_remote = CloudVolumeRemote({"protocol": "gcp", "cloudpath": gcp_path})

cv_resource = cv_remote.cloudvolume()

cutout = cv_remote.get_cutout(cv_resource, 0, [0, 100], [0, 100], [0, 10])
print(cutout.shape, cutout.dtype)
