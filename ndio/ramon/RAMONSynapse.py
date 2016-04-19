from __future__ import absolute_import
from .enums import *
from .errors import *
import numpy

from .RAMONVolume import RAMONVolume


class RAMONSynapse(RAMONVolume):
    """
    RAMONSynapse Object for storing neuroscience data with a voxel volume
    """

    def __init__(self,
                 synapse_type=0,
                 weight=0,
                 segments=None,

                 xyz_offset=(0, 0, 0),
                 resolution=0,
                 cutout=None,
                 voxels=None,

                 id=DEFAULT_ID,
                 confidence=DEFAULT_CONFIDENCE,
                 kvpairs=DEFAULT_DYNAMIC_METADATA,
                 status=DEFAULT_STATUS,
                 author=DEFAULT_AUTHOR):
        """
        Initialize a new `RAMONSynapse` object. Takes all arguments of the
        `RAMONVolume` parent class.

        Arguments:
            synapse_type (int: 0): The synapse type. See the online ndstore
                documentation for more details.
            weight (int: 0): The weight of this synapse (arbitrarily defined)
            segments (int[]: None): A list of segments that belong to this obj
        """
        self.synapse_type = synapse_type
        self.weight = weight
        self.segments = segments

        RAMONVolume.__init__(self,
                             xyz_offset=xyz_offset,
                             resolution=resolution,
                             cutout=cutout,
                             voxels=voxels,
                             id=id,
                             confidence=confidence,
                             kvpairs=kvpairs,
                             status=status,
                             author=author)
