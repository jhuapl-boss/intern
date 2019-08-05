"""
GCP Services Test
"""
from intern.remote.cv.remote import *

gcp_path = '/kasthuri2015/test_dataset/em'

cv_remote = CloudVolumeRemote()

vol = cv_remote.cloudvolume('gs', gcp_path, False)

print('Get Info')
print(cv_remote.get_info(vol))
print('Get Provenance')
print(cv_remote.get_provenance(vol))
print('Resolution')
print(cv_remote.which_res(vol))
print('Get Channel')
print(cv_remote.get_channel(vol))
print('Get Experiment')
print(cv_remote.get_experiment(vol))