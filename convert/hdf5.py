import h5py
import numpy
import os

def import_hdf5(hdf5_filename):
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
        # OCP stores data inside the 'cutout' h5 dataset
        data_layers = f.get('CUTOUT')
    except Exception as e:
        print("Could not load file {0} for conversion.".format(hdf5_filename))
        raise

    return numpy.array(data_layers)



def export_hdf5(hdf5_filename, numpy_data):
    """
    Export a numpy array to a HDF5 file.

    Arguments:
        hdf5_filename:  A filename to which to save the HDF5 data
        numpy_data:     The numpy array to save to HDF5

    Returns:
        String. The expanded filename that now holds the HDF5 data
    """

    # Expand filename to be absolute
    hdf5_filename = os.path.expanduser(hdf5_filename)

    if os.path.exists(hdf5_filename):
        print("File {0} already exists, stopping...".format(hdf5_filename))
        return False

    try:
        h = h5py.File(hdf5_filename, "w")
        h.create_dataset('CUTOUT', data=numpy_data)
        h.close()
    except Exception as e:
        print("Could not save HDF5 file {0}.".format(hdf5_filename))

    return hdf5_filename
