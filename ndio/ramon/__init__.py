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


def hdf5_to_ramon(hdf5):
    """
    Converts an HDF5 file to a RAMON object. Returns an object that is a
    child-class of RAMON (though it's determined at run-time what type
    exactly is returned.)

    Arguments:
        hdf5:           A h5py File object that holds RAMON data
    Returns:
        RAMON object
    Raises:
        A whole lotta errors.
    """
    raise NotImplementedError("WIP")
    metadata = hdf5[str(anno_id)]['METADATA']
    r.author =          metadata['AUTHOR'][0]
    r.confidence =      metadata['CONFIDENCE'][0]
    r.neuron =          metadata['NEURON'][0]
    r.parent_seed =     metadata['PARENTSEED'][0]
    r.segment_class =   metadata['SEGMENTCLASS'][0]
    r.status =          metadata['STATUS'][0]
    r.synapses =        metadata['SYNAPSES'][()]
    r.xyz_offset =      hdf5[str(anno_id)]['XYZOFFSET'][()]
    r.resolution =      hdf5[str(anno_id)]['RESOLUTION'][0]
    r.cutout =          hdf5[str(anno_id)]['CUTOUT'][()]
