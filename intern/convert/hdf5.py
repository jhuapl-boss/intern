from __future__ import absolute_import
import h5py
import numpy
import os


def load(hdf5_filename):
    """
    Import a HDF5 file into a numpy array.

    Arguments:
        hdf5_filename:  A string filename of a HDF5 datafile

    Returns:
        A numpy array with data from the HDF5 file
    """
    # Expand filename to be absolute
    hdf5_filename = os.path.expanduser(hdf5_filename)

    try:
        f = h5py.File(hdf5_filename, "r")
        # neurodata stores data inside the 'cutout' h5 dataset
        data_layers = f.get('image').get('CUTOUT')
    except Exception as e:
        raise ValueError("Could not load file {0} for conversion. {}".format(
                         hdf5_filename, e))
        raise

    return numpy.array(data_layers)


def save(hdf5_filename, array):
    """
    Export a numpy array to a HDF5 file.

    Arguments:
        hdf5_filename (str): A filename to which to save the HDF5 data
        array (numpy.ndarray): The numpy array to save to HDF5

    Returns:
        String. The expanded filename that now holds the HDF5 data
    """
    # Expand filename to be absolute
    hdf5_filename = os.path.expanduser(hdf5_filename)

    try:
        h = h5py.File(hdf5_filename, "w")
        h.create_dataset('CUTOUT', data=array)
        h.close()
    except Exception as e:
        raise ValueError("Could not save HDF5 file {0}.".format(hdf5_filename))

    return hdf5_filename
