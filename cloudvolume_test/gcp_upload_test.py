import numpy as np

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
from intern.remote.cv import CloudVolumeRemote

config = {"protocol": "https",
          "host": "api.bossdb.org",
          "token": "9feb8eedea069626a7e96336d5dd8229a61cc99a"}

boss_rmt = BossRemote(config)

COLL_NAME = 'Kasthuri'
EXP_NAME = 'em'
CHAN_NAME = 'images'

chan = ChannelResource(
    CHAN_NAME, COLL_NAME, EXP_NAME, 'image', datatype='uint8')

# Ranges use the Python convention where the second number is the stop
# value.  Thus, x_rng specifies x values where: 0 <= x < 8.
x_rng = [5990, 7824]
y_rng = [6059, 7892]
z_rng = [610, 620]

# Use 1X downsampled resolution.
res = 1

# Download the cutout from the channel.
data = boss_rmt.get_cutout(chan, res, x_rng, y_rng, z_rng)

#Cloudvolume likes data in Z Y X format 
data = np.transpose(data)

#Intialize CloudVolume Remote 
cv_rmt = CloudVolumeRemote()

#Define where you want the data to be uploaded in GCP Buckets
gcp_path = '/kasthuri2015/test_dataset/em'

#Intialize Resource Object
vol = cv_rmt.cloudvolume('gs', gcp_path, 
	num_channels = 1, 
	data_type = 'uint8',
	layer_type = 'image',
	encoding = 'raw',
	resolution = [6,6,24],
	voxel_offset = [0,0,0],
	chunk_size = [1834,1833,1],
	volume_size = [1834,1833,10],
	description = 'test with google cloud service')

#Upload to GCP
cv_rmt.create_cutout(vol, data)

#Local Mesh Service???
