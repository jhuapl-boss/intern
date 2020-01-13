import numpy as np

from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
from intern.remote.cv import CloudVolumeRemote

config = {"protocol": "https",
          "host": "api.bossdb.io",
          "token": "82789c99fa9f5746a584c8bf5401a2704ccb536b"}

boss_rmt = BossRemote(config)

COLL_NAME = 'neuroproof_examples'
EXP_NAME = 'training_sample'
CHAN_NAME = 'images'

chan = ChannelResource(
    CHAN_NAME, COLL_NAME, EXP_NAME, 'image', datatype='uint8')

x_rng = [0, 250]
y_rng = [0, 250]
z_rng = [0, 250]

# Use base resolution.
res = 0

# Download the cutout from the channel.
data = boss_rmt.get_cutout(chan, res, x_rng, y_rng, z_rng)

# cloud-volume likes data in X Y Z format 
data = np.transpose(data)

# Set up cloud-volume remote
cv_config = {
	"protocol": "gcp",
	"cloudpath": "neuroproof_examples/training_sample/images"
	}
cv_rmt = CloudVolumeRemote(cv_config)

# create a new info (aka new coordinate frame)
info = cv_rmt.create_new_info(
	num_channels = 1,
	layer_type = 'image',
	data_type = 'uint8',
	resolution = (8,8,8),
	volume_size = (250,250,250),
	chunk_size = (64,64,64)
)