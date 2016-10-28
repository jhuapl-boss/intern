from __future__ import absolute_import
from .enums import *
from .errors import *
import numpy

from .RAMONVolume import RAMONVolume


class RAMONSegment(RAMONVolume):
    """
    RAMONSegment Object for storing neuroscience data with a voxel volume
    """

    def __init__(self,
                 segmentclass=0,
                 neuron=0,
                 synapses=[],
                 organelles=[],

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
        Initialize a new `RAMONSegment`. Takes all arguments of `RAMONVolume`.

        Arguments:
            segmentclass (int: 0): The type of segment this is. See the online
                ndstore documentation for more details.
            neuron (int: 0): The neuron that this segment belongs to.
            synapses (int[]: []): List of synapses that fall in this segment
            organelles (int[]: []): List of organelles that fall in this seg
        """
        self.segmentclass = segmentclass
        self.neuron = neuron
        self.synapses = synapses
        self.organelles = organelles

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
