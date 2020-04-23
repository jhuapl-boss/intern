from intern.remote.boss import BossRemote
from intern.service.mesh.service import MeshService, VoxelUnits
import numpy as np

rmt = BossRemote({"protocol": "https", "host": "api.bossdb.io", "token": "public",})

COLL = "kharris15"
EXP = "apical"
CHAN = "anno"
MESH_ID = 22

res = 0
x_rng = [4500, 4700]
y_rng = [3600, 3900]
z_rng = [0, 162]

###### Use MeshService from remote ######

# Define channel resource
ann_chan = rmt.get_channel(CHAN, COLL, EXP)

# Use resource to generate mesh from the Segmentation ID specified
# and the specified cutout volume ranges
# Save the output in a tuple, raw_data and mesh_data will be returned.
mesh = rmt.mesh(
    ann_chan,
    res,
    x_rng,
    y_rng,
    z_rng,
    id_list=[MESH_ID],
    voxel_unit=VoxelUnits.um,
    simp_fact=100,
)

# Convert mesh data to obj
mesh_obj = mesh.obj_mesh()

# Convert mesh data to precompute format for neuroglancer
mesh_ng = mesh.ng_mesh()

# Write the mesh obj
with open("mesh_22_test.obj", "wb") as fh:
    fh.write(mesh_obj)

# Write the Neuroglancer ready mesh
with open("mesh_ng_test", "wb") as fh:
    fh.write(mesh_ng)

###### Use MeshService from direct import ######
## No need for remote import.

# Define channel resource
ann_chan = rmt.get_channel(CHAN, COLL, EXP)

# Grab cutout volume
volume = rmt.get_cutout(ann_chan, res, x_rng, y_rng, z_rng)

# Initialize MeshService
mesh_serv = MeshService()

# Create mesh
mesh = mesh_serv.create(volume, x_rng, y_rng, z_rng)

# Convert mesh data to obj
mesh_obj = mesh.obj_mesh()

# Convert mesh data to precompute format for neuroglancer
mesh_ng = mesh.ng_mesh()

# Write the mesh obj
with open("mesh_22_test_serv.obj", "wb") as fh:
    fh.write(mesh_obj)

# Write the Neuroglancer ready mesh
with open("mesh_ng_test_serv", "wb") as fh:
    fh.write(mesh_ng)
