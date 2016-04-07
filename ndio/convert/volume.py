from __future__ import absolute_import
import numpy


def to_voxels(array):
    """
    Converts an array to its voxel list.

    Arguments:
        array (numpy.ndarray): A numpy nd array. This must be boolean!

    Returns:
        A list of n-tuples
    """
    if type(array) is not numpy.ndarray:
        raise ValueError("array argument must be of type numpy.ndarray")
    return numpy.argwhere(array)


def from_voxels(voxels):
    """
    Converts a voxel list to an ndarray.

    Arguments:
        voxels (tuple[]): A list of coordinates indicating coordinates of
            populated voxels in an ndarray.

    Returns:
        numpy.ndarray The result of the transformation.
    """
    dimensions = len(voxels[0])

    for d in range(len(dimensions)):
        size.append(max([i[d] for i in voxels]))

    result = numpy.zeros(dimensions)

    for v in voxels:
        result[v] = 1

    return result
