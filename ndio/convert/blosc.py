from __future__ import absolute_import
import blosc
import numpy


def to_array(data):
    """
    Import a blosc array into a numpy array.

    Arguments:
        data: A blosc packed numpy array

    Returns:
        A numpy array with data from a blosc compressed array
    """
    try:
        numpy_data = blosc.unpack_array(data)
    except Exception as e:
        raise ValueError("Could not load numpy data. {}".format(e))

    return numpy_data


def from_array(array):
    """
    Export a numpy array to a blosc array.

    Arguments:
        array: The numpy array to compress to blosc array

    Returns:
        Bytes/String. A blosc compressed array
    """
    try:
        raw_data = blosc.pack_array(array)
    except Exception as e:
        raise ValueError("Could not compress data from array. {}".format(e))

    return raw_data
