import resource as cvr

cv_resource = cvr.CloudVolumeResource()

info = {'num_channels':1,
		'layer_type':'image',
		'data_type':'uint8',
		'encoding':'raw',
		'resolution':[1,1,1],
		'voxel_offset':[0,0,0],
		'chunk_size':[1100,700,1],
		'volume_size':[1100,700,10]}
abs_path = '/Users/dxenes/Projects/idealintern/cv_remote/test_dataset'
description = "test with kasthuri data"
cv_resource.create_CV('local', abs_path, description, 
	num_channels = 1, 
	data_type = 'uint8',
	layer_type = 'image',
	encoding = 'raw',
	resolution = [1,1,1],
	voxel_offset = [0,0,0],
	chunk_size = [1100,700,1],
	volume_size = [1100,700,10],
	owners = None)


	
