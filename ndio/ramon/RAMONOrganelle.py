from __future__ import absolute_import
from .enums import *
from .errors import *
import numpy

from .RAMONVolume import RAMONVolume


class RAMONOrganelle(RAMONVolume):
    """
    RAMONOrganelle Object for storing neuroscience data with a voxel volume
    """

    def __init__(self,
                 organelle_class=0,

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
        Initialize a new `RAMONOrganelle`. Organelles take all of the arguments
        of their parent `RAMONVolume` class.

        Arguments:
            organelle_class (int: 0): The organelle class to which this object
                belongs. For more details, see the online ndstore documentation
        """
        self.organelle_class = organelle_class

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
