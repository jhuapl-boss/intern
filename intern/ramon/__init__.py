"""
The enumerables in this file are to afford compatibility with CAJAL, which uses
integers as types. To convert from integer to string (for instance, if you want
to specify the ANNOTATION_TYPE in a RAMON hdf5 file), use:

>>> AnnotationType.get_str(1)
"GENERIC"

To convert from an integer to an actual RAMON type (say, if you want to create
a new RAMON object dynamically), use:

>>> AnnotationType.get_class(1)
ndio.ramon.RAMONGeneric.RAMONGeneric

So you can create a new RAMON object of dynamic type like this:

>>> anno_type = 5
>>> r = AnnotationType.get_class(anno_type)()
>>> type(r)
ndio.ramon.RAMONNeuron.RAMONNeuron

NOTE! If you already have an HDF5 file that contains a RAMON object, it is far
easier to use the prebuilt `from_hdf5()` function (below).

>>> import h5py
>>> f = h5py.File('myfile.hdf5', 'r')
>>> r = from_hdf5(f)
"""

from __future__ import absolute_import
import tempfile
import json as jsonlib
import csv
try:
    from cStringIO import StringIO
except:
    from io import StringIO
import copy
import six

from ndio.ramon.RAMONBase import *
from ndio.ramon.RAMONGeneric import *
from ndio.ramon.RAMONNeuron import *
from ndio.ramon.RAMONOrganelle import *
from ndio.ramon.RAMONSegment import *
from ndio.ramon.RAMONSynapse import *
from ndio.ramon.RAMONVolume import *

from .errors import *


# str: int
_types = {
    "generic": 1,
    "synapse": 2,
    "seed": 3,
    "segment": 4,
    "neuron": 5,
    "organelle": 6,
    "attributedregion": 7,
    "volume": 8
}

# int: str
_reverse_types = {v: k for k, v in list(_types.items())}

# int: class type
_ramon_types = {
    _types["generic"]: RAMONGeneric,
    _types["synapse"]: RAMONSynapse,
    _types["seed"]:  None,
    _types["segment"]: RAMONSegment,
    _types["neuron"]: RAMONNeuron,
    _types["organelle"]: RAMONOrganelle,
    # _types["ATTRIBUTEDREGION"]: None,
    _types["volume"]: RAMONVolume
}

# class type: int
_reverse_ramon_types = {v: k for k, v in list(_ramon_types.items())}


class AnnotationType:
    """
    The annotation types (enumerable) plus convenience functions.
    """

    GENERIC = _types["generic"]
    SYNAPSE = _types["synapse"]
    SEED = _types["seed"]
    SEGMENT = _types["segment"]
    NEURON = _types["neuron"]
    ORGANELLE = _types["organelle"]
    ATTRIBUTEDREGION = _types["attributedregion"]
    VOLUME = _types["volume"]

    @staticmethod
    def get_str(typ):
        """
        From an integer, gets the string representation of a RAMON type.

        Arguments:
            typ (int): The type as an integer

        Returns:
            str: The type as a string
        """
        return _reverse_types[typ]

    @staticmethod
    def get_class(typ):
        """
        From an integer, gets the ndio class of a RAMON type.

        Arguments:
            typ (int): The type as an integer

        Returns:
            type: The type of RAMON object
        """
        return _ramon_types[typ]

    @staticmethod
    def get_int(typ):
        """
        From a string, gets the integer representation of a RAMON type.

        Arguments:
            typ (str): The type as an string

        Returns:
            int: The type as a integer
        """
        return _reverse_ramon_types[typ]

    @staticmethod
    def RAMON(typ):
        """
        Takes str or int, returns class type
        """
        if six.PY2:
            lookup = [str, unicode]
        elif six.PY3:
            lookup = [str]

        if type(typ) is int:
            return _ramon_types[typ]
        elif type(typ) in lookup:
            return _ramon_types[_types[typ]]


def to_dict(ramons, flatten=False):
    """
    Converts a RAMON object list to a JSON-style dictionary. Useful for going
    from an array of RAMONs to a dictionary, indexed by ID.

    Arguments:
        ramons (RAMON[]): A list of RAMON objects
        flatten (boolean: False): Not implemented

    Returns:
        dict: A python dictionary of RAMON objects.
    """
    if type(ramons) is not list:
        ramons = [ramons]

    out_ramons = {}
    for r in ramons:
        out_ramons[r.id] = {
            "id": r.id,
            "type": _reverse_ramon_types[type(r)],
            "metadata": vars(r)
        }
    return out_ramons


def to_json(ramons, flatten=False):
    """
    Converts RAMON objects into a JSON string which can be directly written out
    to a .json file. You can pass either a single RAMON or a list. If you pass
    a single RAMON, it will still be exported with the ID as the key. In other
    words:

        type(from_json(to_json(ramon))) # ALWAYS returns a list

    ...even if `type(ramon)` is a RAMON, not a list.

    Arguments:
        ramons (RAMON or list): The RAMON object(s) to convert to JSON.
        flatten (bool : False): If ID should be used as a key. If not, then
            a single JSON document is returned.

    Returns:
        str: The JSON representation of the RAMON objects, in the schema:
            ```
            {
                <id>: {
                    type: . . . ,
                    metadata: {
                        . . .
                    }
                },
            }
            ```

    Raises:
        ValueError: If an invalid RAMON is passed.
    """
    if type(ramons) is not list:
        ramons = [ramons]

    out_ramons = {}
    for r in ramons:
        out_ramons[r.id] = {
            "id": r.id,
            "type": _reverse_ramon_types[type(r)],
            "metadata": vars(r)
        }

    if flatten:
        return jsonlib.dumps(out_ramons.values()[0])

    return jsonlib.dumps(out_ramons)


def from_json(json, cutout=None):
    """
    Converts JSON to a python list of RAMON objects. if `cutout` is provided,
    the `cutout` attribute of the RAMON object is populated. Otherwise, it's
    left empty. `json` should be an ID-level dictionary, like so:

        {
            16: {
                type: "segment",
                metadata: {
                    . . .
                }
            },
        }

    NOTE: If more than one item is in the dictionary, then a Python list of
    RAMON objects is returned instead of a single RAMON.

    Arguments:
        json (str or dict): The JSON to import to RAMON objects
        cutout: Currently not supported.

    Returns:
        [RAMON]
    """
    if type(json) is str:
        json = jsonlib.loads(json)

    out_ramons = []
    for (rid, rdata) in six.iteritems(json):
        _md = rdata['metadata']
        r = AnnotationType.RAMON(rdata['type'])(
            id=rid,
            author=_md['author'],
            status=_md['status'],
            confidence=_md['confidence'],
            kvpairs=copy.deepcopy(_md['kvpairs'])
        )

        if rdata['type'] == 'segment':
            if 'segmentclass' in _md:
                r.segmentclass = _md['segmentclass']
            if 'neuron' in _md:
                r.neuron = _md['neuron']
            if 'synapses' in _md:
                r.synapses = _md['synapses'][:]
            if 'organelles' in _md:
                r.organelles = _md['organelles'][:]

        elif rdata['type'] == 'neuron':
            r.segments = _md['segments'][:]

        elif rdata['type'] == 'organelle':
            r.organelle_class = _md['organelleclass'][:]

        elif rdata['type'] == 'synapse':
            if 'synapse_type' in _md:
                r.synapse_type = _md['synapse_type']
            if 'weight' in _md:
                r.weight = _md['weight']
            if 'segments' in _md:
                r.segments = _md['segments'][:]

        out_ramons.append(r)

    return out_ramons


def from_hdf5(hdf5, anno_id=None):
    """
    Converts an HDF5 file to a RAMON object. Returns an object that is a child-
    -class of RAMON (though it's determined at run-time what type is returned).

    Accessing multiple IDs from the same file is not supported, because it's
    not dramatically faster to access each item in the hdf5 file at the same
    time It's semantically and computationally easier to run this function
    several times on the same file.

    Arguments:
        hdf5 (h5py.File): A h5py File object that holds RAMON data
        anno_id (int): The ID of the RAMON obj to extract from the file. This
            defaults to the first one (sorted) if none is specified.

    Returns:
        ndio.RAMON object
    """
    if anno_id is None:
        # The user just wants the first item we find, so... Yeah.
        return from_hdf5(hdf5, list(hdf5.keys())[0])

    # First, get the actual object we're going to download.
    anno_id = str(anno_id)
    if anno_id not in list(hdf5.keys()):
        raise ValueError("ID {} is not in this file. Options are: {}".format(
            anno_id,
            ", ".join(list(hdf5.keys()))
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
    r.author = metadata['AUTHOR'][0]
    r.confidence = metadata['CONFIDENCE'][0]
    r.status = metadata['STATUS'][0]
    r.id = anno_id

    # These are a little tougher, some RAMON types have special attributes:

    if type(r) in [RAMONNeuron, RAMONSynapse]:
        r.segments = metadata['SEGMENTS'][()]

    if 'KVPAIRS' in metadata:
        kvs = metadata['KVPAIRS'][()][0].split()
        if len(kvs) != 0:

            for i in kvs:
                k, v = str(i).split(',')
                r.kvpairs[str(k)] = str(v)
        else:
            r.kvpairs = {}

    if issubclass(type(r), RAMONVolume):
        if 'CUTOUT' in anno:
            r.cutout = anno['CUTOUT'][()]
        if 'XYZOFFSET' in anno:
            r.cutout = anno['XYZOFFSET'][()]
        if 'RESOLUTION' in anno:
            r.cutout = anno['RESOLUTION'][()]

    if type(r) is RAMONSynapse:
        r.synapse_type = metadata['SYNAPSE_TYPE'][0]
        r.weight = metadata['WEIGHT'][0]

    if type(r) is RAMONSegment:
        if 'NEURON' in metadata:
            r.neuron = metadata['NEURON'][0]
        if 'PARENTSEED' in metadata:
            r.parent_seed = metadata['PARENTSEED'][0]
        if 'SEGMENTCLASS' in metadata:
            r.segmentclass = metadata['SEGMENTCLASS'][0]
        if 'SYNAPSES' in metadata:
            r.synapses = metadata['SYNAPSES'][()]
        if 'ORGANELLES' in metadata:
            r.organelles = metadata['ORGANELLES'][()]

    if type(r) is RAMONOrganelle:
        r.organelle_class = metadata['ORGANELLECLASS'][0]

    return r


def to_hdf5(ramon, hdf5=None):
    """
    Exports a RAMON object to an HDF5 file object.

    Arguments:
        ramon (RAMON): A subclass of RAMONBase
        hdf5 (str): Export filename

    Returns:
        hdf5.File

    Raises:
        InvalidRAMONError: if you pass a non-RAMON object
    """
    if issubclass(type(ramon), RAMONBase) is False:
        raise InvalidRAMONError("Invalid RAMON supplied to ramon.to_hdf5.")

    import h5py
    import numpy

    if hdf5 is None:
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
    else:
        tmpfile = hdf5

    with h5py.File(tmpfile.name, "a") as hdf5:

        # First we'll export things that all RAMON objects have in
        # common, starting with the Group that encompasses each ID:
        grp = hdf5.create_group(str(ramon.id))

        grp.create_dataset("ANNOTATION_TYPE", (1,),
                           numpy.uint32,
                           data=AnnotationType.get_int(type(ramon)))

        if hasattr(ramon, 'cutout'):
            if ramon.cutout is not None:
                grp.create_dataset('CUTOUT', ramon.cutout.shape,
                                   ramon.cutout.dtype, data=ramon.cutout)
                grp.create_dataset('RESOLUTION', (1,),
                                   numpy.uint32, data=ramon.resolution)
                grp.create_dataset('XYZOFFSET', (3,),
                                   numpy.uint32, data=ramon.xyz_offset)

        # Next, add general metadata.
        metadata = grp.create_group('METADATA')

        metadata.create_dataset('AUTHOR', (1,),
                                dtype=h5py.special_dtype(vlen=str),
                                data=ramon.author)
        # kvpairs = ' '.join(
        #     ','.join([k,v]) for k, v in six.iteritems(ramon.kvpairs)
        # )

        fstring = StringIO()
        csvw = csv.writer(fstring, delimiter=',')
        csvw.writerows([r for r in six.iteritems(ramon.kvpairs)])

        metadata.create_dataset('KVPAIRS', (1,),
                                dtype=h5py.special_dtype(vlen=str),
                                data=fstring.getvalue())
        metadata.create_dataset('CONFIDENCE', (1,), numpy.float,
                                data=ramon.confidence)
        metadata.create_dataset('STATUS', (1,), numpy.uint32,
                                data=ramon.status)

        # Finally, add type-specific metadata:

        if hasattr(ramon, 'segments'):
            metadata.create_dataset('SEGMENTS',
                                    data=numpy.asarray(ramon.segments,
                                                       dtype=numpy.uint32))

        if hasattr(ramon, 'synapse_type'):
            metadata.create_dataset('SYNAPSE_TYPE', (1,), numpy.uint32,
                                    data=ramon.synapse_type)

        if hasattr(ramon, 'weight'):
            metadata.create_dataset('WEIGHT', (1,),
                                    numpy.float, data=ramon.weight)

        if hasattr(ramon, 'neuron'):
            metadata.create_dataset('NEURON', (1,),
                                    numpy.uint32, data=ramon.neuron)

        if hasattr(ramon, 'segmentclass'):
            metadata.create_dataset('SEGMENTCLASS', (1,), numpy.uint32,
                                    data=ramon.segmentclass)

        if hasattr(ramon, 'synapses'):
            metadata.create_dataset('SYNAPSES', (len(ramon.synapses),),
                                    numpy.uint32, data=ramon.synapses)

        if hasattr(ramon, 'organelles'):
            metadata.create_dataset('ORGANELLES',
                                    (len(ramon.organelles),),
                                    numpy.uint32,
                                    data=ramon.organelles)

        if hasattr(ramon, 'organelle_class'):
            metadata.create_dataset('ORGANELLECLASS', (1,),
                                    numpy.uint32,
                                    data=ramon.organelle_class)
        hdf5.flush()
        tmpfile.seek(0)
        return tmpfile
    return False
