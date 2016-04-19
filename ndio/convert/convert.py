from __future__ import absolute_import
import os
import shutil
from PIL import Image


FILE_FORMATS = {
    # Format.lower()    # File ext. By convention, use the first by default
    'hdf5':             ['hdf5', 'h5', 'hdf'],
    'tiff':             ['tiff', 'tif'],
    'png':              ['png'],
    'ramon':            ['m'],
    'matlab':           ['m', 'mat'],
}


def _fail_pair_conversion(i, o):
    """
    Helper-function to print failure and pass back False.
    """
    raise ValueError("Conversion from {0} to {1} " +
                     "is not currently supported.".format(i, o))


def _get_extension_for_format(fmt):
    """
    Get the appropriate file extension for a given format.

    Arguments:
        fmt:        The format to find an extension for

    Returns:
        String. The format (without leading period),
                or False if none was found.
    """
    if fmt in FILE_FORMATS:
        # Use first file extension by default
        return FILE_FORMATS[fmt][0]

    # Otherwise, we don't recognize the format...
    return False


def _guess_format_from_extension(ext):
    """
    Guess the appropriate data type from file extension.

    Arguments:
        ext:        The file extension (period optional)

    Returns:
        String. The format (without leading period),
                or False if none was found or couldn't be guessed
    """
    ext = ext.strip('.')

    # We look through FILE_FORMATS for this extension.
    # - If it appears zero times, return False. We can't guess.
    # - If it appears once, we can simply return that format.
    # - If it appears more than once, we can't guess (it's ambiguous,
    #   e.g .m = RAMON or MATLAB)

    formats = []
    for fmt in FILE_FORMATS:
        if ext in FILE_FORMATS[fmt]:
            formats.append(fmt)

    if formats == [] or len(formats) > 1:
        return False

    return formats[0]


def open(in_file, in_fmt=None):
    """
    Reads in a file from disk.

    Arguments:
        in_file: The name of the file to read in
        in_fmt: The format of in_file, if you want to be explicit

    Returns:
        numpy.ndarray
    """
    fmt = in_file.split('.')[-1]
    if in_fmt:
        fmt = in_fmt
    fmt = fmt.lower()

    if fmt in ['png', 'jpg', 'tiff', 'tif', 'jpeg']:
        return Image.open(in_file)
    else:
        raise NotImplementedError("Cannot open file of type {fmt}".format(fmt))


def convert(in_file, out_file, in_fmt="", out_fmt=""):
    """
    Converts in_file to out_file, guessing datatype in the absence of
    in_fmt and out_fmt.

    Arguments:
        in_file:    The name of the (existing) datafile to read
        out_file:   The name of the file to create with converted data
        in_fmt:     Optional. The format of incoming data, if not guessable
        out_fmt:    Optional. The format of outgoing data, if not guessable

    Returns:
        String. Output filename
    """
    # First verify that in_file exists and out_file doesn't.
    in_file = os.path.expanduser(in_file)
    out_file = os.path.expanduser(out_file)

    if not os.path.exists(in_file):
        raise IOError("Input file {0} does not exist, stopping..."
                      .format(in_file))

    # Get formats, either by explicitly naming them or by guessing.
    # TODO: It'd be neat to check here if an explicit fmt matches the guess.
    in_fmt = in_fmt.lower() or _guess_format_from_extension(
             in_file.split('.')[-1].lower())
    out_fmt = out_fmt.lower() or _guess_format_from_extension(
              out_file.split('.')[-1].lower())

    if not in_fmt or not out_fmt:
        raise ValueError("Cannot determine conversion formats.")
        return False

    if in_fmt is out_fmt:
        # This is the case when this module (intended for LONI) is used
        # indescriminately to 'funnel' data into one format.
        shutil.copyfileobj(in_file, out_file)
        return out_file

    # Import
    if in_fmt == 'hdf5':
        from . import hdf5
        data = hdf5.load(in_file)
    elif in_fmt == 'tiff':
        from . import tiff
        data = tiff.load(in_file)
    elif in_fmt == 'png':
        from . import png
        data = png.load(in_file)
    else:
        return _fail_pair_conversion(in_fmt, out_fmt)

    # Export
    if out_fmt == 'hdf5':
        from . import hdf5
        return hdf5.save(out_file, data)
    elif out_fmt == 'tiff':
        from . import tiff
        return tiff.save(out_file, data)
    elif out_fmt == 'png':
        from . import png
        return png.export_png(out_file, data)
    else:
        return _fail_pair_conversion(in_fmt, out_fmt)

    return _fail_pair_conversion(in_fmt, out_fmt)
