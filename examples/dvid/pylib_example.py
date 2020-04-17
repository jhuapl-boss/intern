import json
import httplib
import numpy
from pydvid import voxels, general

connection = httplib.HTTPConnection("localhost:8001", timeout=5.0)

# Get detailed dataset info: /api/datasets/info
dataset_details = general.get_repos_info(connection)
# print json.dumps( dataset_details, indent=4 )

# Create a new remote volume
uuid = "25eb4d877a0d4f8391014fe1237ada8a"
voxels_metadata = voxels.VoxelsMetadata.create_default_metadata(
    (4, 0, 0, 0), numpy.uint8, "cxyz", 1.0, ""
)
# voxels.create_new( connection, uuid, "my_volume", voxels_metadata )
# Use the VoxelsAccessor convenience class to manipulate a particular data volume
dvid_volume = voxels.VoxelsAccessor(connection, uuid, "my_volume")
print(dvid_volume.axiskeys, dvid_volume.dtype, dvid_volume.minindex, dvid_volume.shape)

# Add some data
updated_data = numpy.ones(
    (4, 100, 100, 100), dtype=numpy.uint8
)  # Must include all channels.
# dvid_volume[:, 10:110, 20:120, 30:130] = updated_data
# OR:
dvid_volume.post_ndarray((0, 10, 20, 30), (4, 110, 120, 130), updated_data)

# Read from it (First axis is channel.)
cutout_array = dvid_volume[:, 10:110, 20:120, 30:130]
# OR:
cutout_array = dvid_volume.get_ndarray((0, 10, 20, 30), (4, 110, 120, 130))

assert isinstance(cutout_array, numpy.ndarray)
assert cutout_array.shape == (4, 100, 100, 100)
