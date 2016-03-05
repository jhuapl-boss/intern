from __future__ import absolute_import
import blosc
import numpy


def import_blosc(raw_data):
    """
    Import a blosc array into a numpy array.

    Arguments:
        raw_data:  A blosc packed numpy array

    Returns:
        A numpy array with data from a blosc compressed array
    """

    try:
        numpy_data = blosc.unpack_array(raw_array)
    except Exception as e:
        raise ValueError("Could not load numpy data. {}".format(e))

    return numpy_data


def export_blosc(numpy_data):
    """
    Export a numpy array to a blosc array.

    Arguments:
        numpy_data:     The numpy array to compress to blosc array

    Returns:
        Bytes/String. A blosc compressed array
    """

    try:
        raw_data = blosc.pack_array(numpy_data)
    except Exception as e:
        raise ValueError("Could not compress data from array. {}".format(e))

    return raw_data
