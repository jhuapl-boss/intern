from __future__ import absolute_import
from PIL import Image
import numpy
import os
import glob


def load(tiff_filename):
    """
    Import a TIFF file into a numpy array.

    Arguments:
        tiff_filename:  A string filename of a TIFF datafile

    Returns:
        A numpy array with data from the TIFF file
    """
    # Expand filename to be absolute
    tiff_filename = os.path.expanduser(tiff_filename)

    try:
        img = Image.open(tiff_filename)
    except Exception as e:
        raise ValueError("Could not load file {0} for conversion."
                         .format(tiff_filename))
        raise

    return numpy.array(img)


def save(tiff_filename, numpy_data):
    """
    Export a numpy array to a TIFF file.

    Arguments:
        tiff_filename:  A filename to which to save the TIFF data
        numpy_data:     The numpy array to save to TIFF

    Returns:
        String. The expanded filename that now holds the TIFF data
    """
    # Expand filename to be absolute
    tiff_filename = os.path.expanduser(tiff_filename)

    if type(numpy_data) is str:
        fp = open(png_filename, "wb")
        fp.write(numpy_data)
        fp.close()
        return png_filename

    try:
        img = Image.fromarray(numpy_data)
        img.save(tiff_filename)
    except Exception as e:
        raise ValueError("Could not save TIFF file {0}.".format(tiff_filename))

    return tiff_filename


def save_collection(tiff_filename_base, numpy_data, start_layers_at=1):
    """
    Export a numpy array to a set of TIFF files, with each Z-index 2D
    array as its own 2D file.

    Arguments:
        tiff_filename_base:     A filename template, such as "my-image-*.tiff"
                                which will lead to a collection of files named
                                "my-image-0.tiff", "my-image-1.tiff", etc.
        numpy_data:             The numpy array data to save to TIFF.

    Returns:
        Array. A list of expanded filenames that hold TIFF data.
    """
    file_ext = tiff_filename_base.split('.')[-1]
    if file_ext in ['tif', 'tiff']:
        # Filename is "name*.tif[f]", set file_base to "name*".
        file_base = '.'.join(tiff_filename_base.split('.')[:-1])
    else:
        # Filename is "name*", set file_base to "name*".
        # That is, extension wasn't included.
        file_base = tiff_filename_base
        file_ext = ".tiff"

    file_base_array = file_base.split('*')

    # The array of filenames to return
    output_files = []

    # Filename 0-padding
    i = start_layers_at
    for layer in numpy_data:
        layer_filename = (str(i).zfill(6)).join(file_base_array) + file_ext
        output_files.append(save(layer_filename, layer))
        i += 1

    return output_files


def load_tiff_multipage(tiff_filename, dtype='float32'):
    """
    Load a multipage tiff into a single variable in x,y,z format.

    Arguments:
        tiff_filename:     Filename of source data
        dtype:             data type to use for the returned tensor

    Returns:
        Array containing contents from input tiff file in xyz order
    """
    if not os.path.isfile(tiff_filename):
        raise RuntimeError('could not find file "%s"' % tiff_filename)

    # load the data from multi-layer TIF files
    data = Image.open(tiff_filename)

    im = []

    while True:

        Xi = numpy.array(data, dtype=dtype)
        if Xi.ndim == 2:
            Xi = Xi[numpy.newaxis, ...]  # add slice dimension
        im.append(Xi)

        try:
            data.seek(data.tell()+1)
        except EOFError:
            break  # this just means hit end of file (not really an error)

    im = numpy.concatenate(im, axis=0)  # list of 2d -> tensor
    im = numpy.rollaxis(im, 1)
    im = numpy.rollaxis(im, 2)

    return im


def load_collection(tiff_filename_base):
    """
    Import all files matching the filename base given via `tiff_filename_base`.
    Images are ordered by alphabetical order, which means that you *MUST* 0-pad
    your numbers if they span a power of ten (e.g. 0999-1000 or 09-10). This is
    handled automatically by the complement function, `save_collection`.
    Also, look at how nicely these documentation lines are all the same length!

    Arguments:
        tiff_filename_base:     An asterisk-wildcard string that should refer
                                to all TIFFs in the stack. All * are replaced
                                according to command-line expansion rules.
    Returns:
        A numpy array holding a 3D dataset
    """
    # We expect images to be indexed by their alphabetical order.
    files = glob.glob(tiff_filename_base)
    files.sort()

    numpy_data = []
    for f in files:
        numpy_data.append(load(f))

    return numpy.concatenate(numpy_data)
