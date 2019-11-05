from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *
import numpy as np
from requests import HTTPError

rmt = BossRemote('neurodata.cfg')

xmax = 8
ymax = 4
zmax = 5
tmax = 10

COLL_NAME = 'gray'
EXP_NAME = 'timeseries_test'
CHAN_NAME = 'Ch1'

COORD_FRAME = COLL_NAME + '_' + EXP_NAME

coord = CoordinateFrameResource(
    COORD_FRAME, '', 0, xmax, 0, ymax, 0, zmax)
try:
    coord_actual = rmt.get_project(coord)
except HTTPError:
    coord_actual = rmt.create_project(coord)


# Create or get experiment
chan_setup = ExperimentResource(
    EXP_NAME, COLL_NAME, coord_frame=COORD_FRAME,
    num_time_samples=tmax, time_step=1)
try:
    chan_actual = rmt.get_project(chan_setup)
except HTTPError:
    chan_actual = rmt.create_project(chan_setup)


# Create or get a channel to write to
chan_setup = ChannelResource(
    CHAN_NAME, COLL_NAME, EXP_NAME, 'image', '', datatype='uint16')
try:
    chan_actual = rmt.get_project(chan_setup)
except HTTPError:
    chan_actual = rmt.create_project(chan_setup)

x_rng = [0, xmax]
y_rng = [0, ymax]
z_rng = [0, zmax]
t_rng = [0, tmax]

print('Data model setup.')

data = np.random.randint(1, 3000, (tmax, zmax, ymax, xmax))
data = data.astype(np.uint16)

# Upload the cutout to the channel.
rmt.create_cutout(chan_actual, 0, x_rng, y_rng, z_rng, data,
                  time_range=t_rng)

cutout_data = rmt.get_cutout(
    chan_actual, 0, x_rng, y_rng, z_rng, time_range=t_rng)

np.testing.assert_array_equal(data, cutout_data)

print(np.shape(cutout_data))
# (10, 5, 4, 8)
