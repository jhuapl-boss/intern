from enums import *
from errors import *
import numpy

from RAMONBase import RAMONBase


class RAMONVolume(RAMONBase):
    """
    RAMONVolume Object for storing neuroscience data with a voxel volume
    """
    def __init__(self,
                 xyz_offset=(0, 0, 0),
                 resolution=0,
                 cutout=None,
                 voxels=None,

                 id=DEFAULT_ID,
                 confidence=DEFAULT_CONFIDENCE,
                 dynamic_metadata=DEFAULT_DYNAMIC_METADATA,
                 status=DEFAULT_STATUS,
                 author=DEFAULT_AUTHOR):
        """
        Initialize a new RAMONVolume object. Inherits attributes from RAMONBase
        as well as:

        Arguments:
            xyz_offset (int[3] : (0, 0, 0)): x,y,z coordinates of the minimum
                corner of the cube (if data is a cutout), otherwise empty
            resolution (int : 0): level in the database resolution hierarchy
            cutout (numpy.ndarray): dense matrix of data
            voxels: Unused for now
        """

        self.xyz_offset = xyz_offset
        self.resolution = resolution
        self.cutout = cutout
        self.voxels = voxels

        RAMONBase.__init__(self, id=id, confidence=confidence,
                           dynamic_metadata=dynamic_metadata,
                           status=status, author=author)
