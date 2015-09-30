from enums import *
from exceptions import *
import numpy

from RAMONVolume import RAMONVolume

class RAMONSynapse(RAMONVolume):
    """
    RAMONSynapse Object for storing neuroscience data with a voxel volume
    """
    def __init__(self,
                synapse_type = 0,
                weight = 0,
                segments = None,
                    xyz_offset = (0, 0, 0),
                    resolution = 0,
                    cutout = None,
                    voxels = None,
                        id = DEFAULT_ID,
                        confidence = DEFAULT_CONFIDENCE,
                        dynamic_metadata = DEFAULT_DYNAMIC_METADATA,
                        status = DEFAULT_STATUS,
                        author = DEFAULT_AUTHOR):

            self.synapse_type = synapse_type
            self.weight = weight
            self.segments = segments

            RAMONVolume.__init__(self,
                            xyz_offset = xyz_offset,
                            resolution = resolution,
                            cutout = cutout,
                            voxels = voxels,
                            id = id,
                            confidence = confidence,
                            dynamic_metadata = dynamic_metadata,
                            status = status,
                            author = author)
