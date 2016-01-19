from __future__ import absolute_import
from .enums import *
from .errors import *
import numpy

from .RAMONBase import RAMONBase


class RAMONNeuron(RAMONBase):
    """
    RAMONNeuron Object for storing neuroscience data with a voxel volume
    """
    def __init__(self,
                 segments=None,

                 id=DEFAULT_ID,
                 confidence=DEFAULT_CONFIDENCE,
                 dynamic_metadata=DEFAULT_DYNAMIC_METADATA,
                 status=DEFAULT_STATUS,
                 author=DEFAULT_AUTHOR):

            self.segments = segments

            RAMONBase.__init__(self,
                                 id=id,
                                 confidence=confidence,
                                 dynamic_metadata=dynamic_metadata,
                                 status=status,
                                 author=author)
