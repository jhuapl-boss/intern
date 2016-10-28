from __future__ import absolute_import
import nibabel as nib
import numpy
import os
import glob


def load(nifti_filename):
    """
    Import a nifti file into a numpy array. TODO:  Currently only
    transfers raw data for compatibility with annotation and ND formats

    Arguments:
        nifti_filename (str):  A string filename of a nifti datafile

    Returns:
        A numpy array with data from the nifti file
    """
    # Expand filename to be absolute
    nifti_filename = os.path.expanduser(nifti_filename)

    try:
        data = nib.load(nifti_filename)
        img = data.get_data()

    except Exception as e:
        raise ValueError("Could not load file {0} for conversion."
                         .format(nifti_filename))
        raise

    return numpy.array(img)


def save(nifti_filename, numpy_data):
    """
    Export a numpy array to a nifti file.  TODO: currently using dummy
    headers and identity matrix affine transform. This can be expanded.

    Arguments:
        nifti_filename (str): A filename to which to save the nifti data
        numpy_data (numpy.ndarray): The numpy array to save to nifti

    Returns:
        String. The expanded filename that now holds the nifti data
    """
    # Expand filename to be absolute
    nifti_filename = os.path.expanduser(nifti_filename)

    try:
        nifti_img = nib.Nifti1Image(numpy_data, numpy.eye(4))
        nib.save(nifti_img, nifti_filename)

    except Exception as e:
        raise ValueError("Could not save file {0}.".format(nifti_filename))
    return nifti_filename
