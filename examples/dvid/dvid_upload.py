from intern.remote.dvid import DVIDRemote
from intern.resource.dvid import DataInstanceResource
import numpy as np

dvid = DVIDRemote({"protocol": "http", "host": "localhost:8001",})

# Prepare the data
data_cube = np.load("/My/dummy/dir/validation_grayscale.npy").astype(np.uint8)
data_cube = data_cube[0:512, 0:512, 0:512]
data_cube = data_cube.copy(order="C")
print(data_cube.dtype)
print(data_cube.shape)
# Create the project
instance_setup_up = DataInstanceResource(
    alias="local_dvid_test",
    type="uint8blk",
    name="validation",
    UUID=None,
    datatype="uint8",
)
chan_actual_up = dvid.create_project(instance_setup_up)
# Create the cutout
dvid.create_cutout(instance_setup_up, 0, [0, 512], [0, 512], [0, 512], data_cube)
print("Create cutout successful")
# Get the cutout
got_cutout = dvid.get_cutout(instance_setup_up, 0, [0, 512], [0, 512], [0, 1])
print(got_cutout.shape)

print("Arrays match: {}".format(np.array_equal(got_cutout, data_cube[0:1, :, :])))

