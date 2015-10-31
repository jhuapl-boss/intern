from ndio.ramon.RAMONBase import *
from ndio.ramon.RAMONGeneric import *
from ndio.ramon.RAMONNeuron import *
from ndio.ramon.RAMONOrganelle import *
from ndio.ramon.RAMONSegment import *
from ndio.ramon.RAMONSynapse import *
from ndio.ramon.RAMONVolume import *

from exceptions import *


"""

The enumerables in this file are to afford compatibility with CAJAL, which uses
integers as types. To convert from integer to string (for instance, if you want
to specify the ANNOTATION_TYPE in a RAMON hdf5 file), use:

    >>> AnnotationType.get_str(1)
    "GENERIC"

To convert from an integer to an actual RAMON type (say, if you want to create a
new RAMON object dynamically), use:

    >>> AnnotationType.get_class(1)
    ndio.ramon.RAMONGeneric.RAMONGeneric

So you can create a new RAMON object of dynamic type like this:

    >>> anno_type = 5
    >>> r = AnnotationType.get_class(anno_type)()
    >>> type(r)
    ndio.ramon.RAMONNeuron.RAMONNeuron

NOTE! If you already have an HDF5 file that contains a RAMON object, it is far
easier to use the prebuilt `hdf5_to_ramon()` function (below).

    >>> import h5py
    >>> f = h5py.File('myfile.hdf5', 'r')
    >>> r = hdf5_to_ramon(f)

"""

_types = {
    "GENERIC": 1,
    "SYNAPSE": 2,
    "SEED": 3,
    "SEGMENT": 4,
    "NEURON": 5,
    "ORGANELLE": 6,
    "ATTRIBUTEDREGION": 7,
    "VOLUME": 8
}

_reverse_types = {v: k for k, v in _types.items()}

_ramon_types = {
    _types["GENERIC"]: RAMONGeneric,
    _types["SYNAPSE"]: RAMONSynapse,
    _types["SEED"]:  None,
    _types["SEGMENT"]: RAMONSegment,
    _types["NEURON"]: RAMONNeuron,
    _types["ORGANELLE"]: RAMONOrganelle,
    _types["ATTRIBUTEDREGION"]: None,
    _types["VOLUME"]: RAMONVolume
}

class AnnotationType:
    GENERIC = _types["GENERIC"]
    SYNAPSE = _types["SYNAPSE"]
    SEED = _types["SEED"]
    SEGMENT = _types["SEGMENT"]
    NEURON = _types["NEURON"]
    ORGANELLE = _types["ORGANELLE"]
    ATTRIBUTEDREGION = _types["ATTRIBUTEDREGION"]
    VOLUME = _types["VOLUME"]

    @staticmethod
    def get_str(type):
        return _reverse_types[type]

    @staticmethod
    def get_class(type):
        return _ramon_types[type]


def hdf5_to_ramon(hdf5, anno_id=None):
    """
    Converts an HDF5 file to a RAMON object. Returns an object that is a child-
    -class of RAMON (though it's determined at run-time what type is returned).

    Accessing multiple IDs from the same file is not supported, because it's not
    dramatically faster to access every item in the hdf5 file at the same time.
    It's semantically and computationally easier to run this function several
    times on the same file.

    Arguments:
        hdf5 (h5py.File): A h5py File object that holds RAMON data
        anno_id (int): The ID of the RAMON object to extract from the file. This
            defaults to the first one (sorted numerically) if none is specified.

    Returns:
        ndio.RAMON object
    """

    if anno_id is None:
        # The user just wants the first item we find, so... Yeah.
        return hdf5_to_ramon(hdf5, hdf5.keys()[0])

    # First, get the actual object we're going to download.
    anno_id = str(anno_id)
    if anno_id not in hdf5.keys():
        raise ValueError("ID {} is not in this file. Options are: {}".format(
            anno_id,
            ", ".join(hdf5.keys())
        ))

    anno = hdf5[anno_id]
    # anno now holds just the RAMON of interest

    # This is the most complicated line in here: It creates an object whose
    # type is conditional on the ANNOTATION_TYPE of the hdf5 object.
    try:
        r = AnnotationType.get_class(anno['ANNOTATION_TYPE'][0])()
    except:
        raise InvalidRAMONError("This is not a valid RAMON type.")

    # All RAMON types definitely have these attributes:
    metadata = anno['METADATA']
    r.author =              metadata['AUTHOR'][0]
    r.confidence =          metadata['CONFIDENCE'][0]
    r.status =              metadata['STATUS'][0]
    r.id =                  anno_id

    # These are a little tougher, some RAMON types have special attributes:

    if type(r) in [RAMONNeuron, RAMONSynapse]:
        r.segments =        metadata['SEGMENTS'][()]

    if issubclass(type(r), RAMONVolume):
        r.cutout =          anno['CUTOUT'][()]
        r.xyz_offset =      anno['XYZOFFSET'][()]
        r.resolution =      anno['RESOLUTION'][0]

    if type(r) is RAMONSynapse:
        r.synapse_type =    metadata['SYNAPSETYPE'][0]
        r.weight =          metadata['WEIGHT'][0]

    if type(r) is RAMONSegment:
        r.neuron =          metadata['NEURON'][0]
        r.parent_seed =     metadata['PARENTSEED'][0]
        r.segment_class =   metadata['SEGMENTCLASS'][0]
        if 'SYNAPSES' in metadata:
            r.synapses =    metadata['SYNAPSES'][()]
        if 'ORGANELLES' in metadata:
            r.organelles =  metadata['ORGANELLES'][()]

    if type(r) is RAMONOrganelle:
        r.organelleclass =  metadata['ORGANELLECLASS'][0]

    return r
