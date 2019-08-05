from intern.remote.dvid import DVIDRemote
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import *


config = {"protocol": "https",
          "host": "api.bossdb.org",
          "token": "9feb8eedea069626a7e96336d5dd8229a61cc99a"}

# BOSS Data fetch:
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
volumeB = boss_rmt.get_cutout(chan, res, x_rng, y_rng, z_rng)

#UPLOAD TO DVID REPOSITORY
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
    })

chan_setup = dvid.ChannelResource('images_kasthuri','remote_test', 'Data uploaded from Boss to dvid')
proj = dvid.create_project(chan_setup)
UUID = chan_setup.split("/")
UUID = UUID[0]

xrang = [0, 500]
yrang = [0, 500]
zrang = [0,10]

dvid.create_cutout(proj,xrang,yrang,zrang,volumeB)

volumeD = dvid.get_cutout(
    dvid.get_channel(UUID), 0,
    [0,200],[0,200],[32,33]
    )
print(volumeD)
