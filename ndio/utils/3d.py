import mcubes

def export_to_dae(filename, data, level=0):
    """
    Converts a dense annotation to a DAE, using Marching Cubes (PyMCubes).

    Arguments:
        filename (str): The filename to write out to
        data (numpy.ndarray): The dense annotation
        level (int): The level at which to run mcubes

    Returns:
        boolean success
    """

    if ".dae" not in filename:
        filename = filename + ".dae"

    vs, fs = mcubes.marching_cubes(cutout, level)
    mcubes.export_mesh(vs, fs, filename, "ndioexport")
