from intern.remote.boss import BossRemote
from intern.remote.dvid import DVIDRemote
from intern.resource.boss.resource import *
import matplotlib.pyplot as plt
import numpy as np


# Define the BOSS remote
rmt = BossRemote({"protocol": "https", "host": "api.bossdb.io", "token": "public"})

ANN_COLL_NAME = "allan_johnson"
ANN_EXP_NAME = "gaj_17_40"

experiment = rmt.get_experiment(ANN_COLL_NAME, ANN_EXP_NAME)
print("Boss experiment extents: {}".format(rmt.get_extents(experiment)))


# Define the DVID remote
dvid = DVIDRemote({"protocol": "https", "host": "emdata.janelia.org",})
uuid = "822524777d3048b8bd520043f90c1d28"
name = "grayscale"
annos_name = "groundtruth"

print(
    "DVID data instance extents: {}".format(
        dvid.get_extents(dvid.get_instance(uuid, name, datatype="uint8"))
    )
)

