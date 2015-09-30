import os, shutil

FILE_FORMATS = {
    # Format.lower()    # File extension. By convention, use the first by default
    'hdf5':             ['hdf5', 'h5', 'hdf'],
    'tiff':             ['tiff', 'tif'],
    'png':              ['png'],
    'ramon':            ['m'],
    'matlab':           ['m', 'mat'],
}


# This is not simply FILE_FORMATS in 'reverse', because while we may be able
# to get the file extension for a RAMON object (.m) we can't guess a datatype
# from the ambiguous extension ".m".


def _fail_pair_conversion(i, o):
    """
    Helper-function to print failure and pass back False.
    """
    print("Conversion from {0} to {1} is not currently supported.".format(i, o))
    return False


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

    if os.path.exists(out_file):
        raise IOError("Output file {0} already exists, stopping...".format(out_file))
    if not os.path.exists(in_file):
        raise IOError("Input file {0} does not exist, stopping...".format(in_file))

    # Get formats, either by explicitly naming them or by guessing.
    # TODO: It'd be neat to check here if an explicit fmt matches the guess.
    in_fmt = in_fmt.lower() or _guess_format_from_extension(
             in_file.split('.')[-1].lower())
    out_fmt = out_fmt.lower() or _guess_format_from_extension(
              out_file.split('.')[-1].lower())

    if not in_fmt or not out_fmt:
        print("Cannot determine conversion formats.")
        return False

    if in_fmt is out_fmt:
        # This is the case when this module (intended for LONI) is used
        # indescriminately to 'funnel' data into one format.
        shutil.copyfileobj(in_file, out_file)
        return out_file


    ## Import
    if in_fmt == 'hdf5':
        import hdf5
        data = hdf5.import_hdf5(in_file)
    elif in_fmt == 'tiff':
        import tiff
        data = tiff.import_tiff(in_file)
    elif in_fmt == 'png':
        import png
        data = png.import_png(in_file)
    else:
        return _fail_pair_conversion(in_fmt, out_fmt)

    ## Export
    if out_fmt == 'hdf5':
        import hdf5
        return hdf5.export_hdf5(out_file, data)
    elif out_fmt == 'tiff':
        import tiff
        return tiff.export_tiff(out_file, data)
    elif out_fmt == 'png':
        import png
        return png.export_png(out_file, data)
    else:
        return _fail_pair_conversion(in_fmt, out_fmt)


    return _fail_pair_conversion(in_fmt, out_fmt)
