from intern.remote.dvid import DVIDRemote
import matplotlib.pyplot as plt
import numpy as np

# DVID Data fetch:

# Define the remote
dvid = DVIDRemote({"protocol": "https", "host": "emdata.janelia.org",})
uuid = "822524777d3048b8bd520043f90c1d28"
name = "grayscale"
annos_name = "groundtruth"

print(dvid.get_extents(dvid.get_instance(uuid, name, datatype="uint8")))

# get cutout from actual dataset
volumeD = dvid.get_cutout(
    dvid.get_instance(uuid, name, datatype="uint8"),
    0,
    [3000, 3150],
    [3000, 3150],
    [2000, 2010],
)

# get annotations from dataset
annosD = dvid.get_cutout(
    dvid.get_instance(uuid, annos_name, datatype="uint64"),
    0,
    [3000, 3150],
    [3000, 3150],
    [2000, 2010],
)

# overlay the data
plt.imshow(volumeD[0, :, :], cmap="gray")
plt.imshow(annosD[0, :, :], cmap="gray", alpha=0.5)

plt.show()
