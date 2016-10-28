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
                 kvpairs=DEFAULT_DYNAMIC_METADATA,
                 status=DEFAULT_STATUS,
                 author=DEFAULT_AUTHOR):
        """
        Initialize a new `RAMONNeuron`. Neurons take all of the arguments of
        `RAMONBase`.

        Arguments:
            segments (int[]: None): A list of RAMON IDs that make up the neuron
        """
        self.segments = segments

        RAMONBase.__init__(self,
                           id=id,
                           confidence=confidence,
                           kvpairs=kvpairs,
                           status=status,
                           author=author)
