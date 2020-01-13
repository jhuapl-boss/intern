"""
GCP Services Test
"""
from intern.remote.cv.remote import *

gcp_path = 'kasthuri2015/test_dataset/em'

cv_remote = CloudVolumeRemote({
	'protocol': 'gcp',
	'cloudpath': gcp_path
})

vol = cv_remote.cloudvolume()
print('Get Info')
print(cv_remote.get_info(vol))
print('Get Provenance')
print(cv_remote.get_provenance(vol))
print('Resolution')
print(cv_remote.list_res(vol))
print('Get Channel')
print(cv_remote.get_layer(vol))
print('Get Experiment')
print(cv_remote.get_dataset_name(vol))