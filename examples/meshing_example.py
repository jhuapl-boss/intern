from intern.remote.boss import BossRemote
import numpy as np

rmt = BossRemote({
"protocol": "https",
"host": "api.bossdb.io",
"token": "<token>",
})

COLL = "kharris15"
EXP = "apical"
CHAN = "anno"
MESH_ID=22

res = 0
x_rng = [4500, 5500]
y_rng = [3600, 4600]
z_rng = [0, 162]

# Define channel resource
ann_chan = rmt.get_channel(CHAN, COLL, EXP)

# Use resource to generate mesh from the Segmentation ID specified
# and the specified cutout volume ranges
# Save the output in a touple, raw_data and mesh_data will be returned. 
raw_data, mesh_data = rmt.mesh(ann_chan, res, x_rng, y_rng, z_rng, 
    id_list=[MESH_ID], voxel_unit="micrometers", simp_fact=100)

# Convert mesh data to obj
mesh_obj = rmt.obj_mesh(mesh_data)

# Convert mesh data to precompute format for neuroglancer
mesh_ng = rmt.ng_mesh(mesh_data)

# Write the mesh obj
with open('mesh_22.obj', 'wb') as fh:
    fh.write(mesh_obj)

#Write the Neuroglancer ready mesh
with open('mesh_ng', 'wb') as fh:
    fh.write(mesh_ng)