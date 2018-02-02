import intern
from intern.remote.boss import BossRemote
from intern.resource.boss.resource import ChannelResource
from intern.remote.dvid import DVIDRemote
import matplotlib.pyplot as plt
import numpy as np

#DVID Data fetch:
dvid = DVIDRemote({
	"protocol": "http",
	"host": "localhost:8000",
	})
chan_setup = dvid.ChannelResource('Xbrain_Proj','dyer15_3_maskim', 'masked_images', 'Data upload test')
proj = dvid.create_project(chan_setup)

# dvid.delete_project("8ef")
