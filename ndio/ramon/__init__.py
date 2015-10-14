from ndio.ramon.RAMONBase import *
from ndio.ramon.RAMONGeneric import *
from ndio.ramon.RAMONOrganelle import *
from ndio.ramon.RAMONSegment import *
from ndio.ramon.RAMONSynapse import *
from ndio.ramon.RAMONVolume import *


def metadata_to_ramon(metadata):
    """
    Get as much info about a RAMON object as possible
    from metadata.

    Might have been downloaded using a function like
    `ndio.remote.OCP.get_ramon_metadata()`, etc
    """
    raise NotImplementedError()
    pass
