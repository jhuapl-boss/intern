import numpy


def snap_to_cube(q_start, q_stop, chunk_depth=16, q_index=1):
    """
    For any q in {x, y, z, t}
    Takes in a q-range and returns a 1D bound that starts at a cube
    boundary and ends at another cube boundary and includes the volume
    inside the bounds. For instance, snap_to_cube(2, 3) = (1, 17)

    Arguments:
        :q_start:       `int` The lower bound of the q bounding box of volume
        :q_stop:        `int` The upper bound of the q bounding box of volume
        :chunk_depth:   `int : CHUNK_DEPTH` The size of the chunk in this volume (use ``get_info()``)
        :q_index:       `int : 1` The starting index of the volume (in q)
    Returns:
        :2-tuple: ``(lo, hi)`` bounding box for the volume
    """
    lo = 0; hi = 0
    # Start by indexing everything at zero for our own sanity
    q_start -= q_index; q_stop -= q_index

    if q_start % chunk_depth == 0:
        lo = q_start
    else:
        lo = q_start - (q_start % chunk_depth)

    if q_stop % chunk_depth == 0:
        hi = q_stop
    else:
        hi = q_stop + (chunk_depth - q_stop % chunk_depth)

    return [lo + q_index, hi + q_index + 1]


def block_compute(x_start, x_stop,
                  y_start, y_stop,
                  z_start, z_stop,
                  origin=(0, 0, 1),
                  block_size=(256, 256, 16)):
    """
    Get bounding box coordinates (in 3D) of small cutouts to request in
    order to reconstitute a larger cutout.

    Arguments:
        :Q_start:               ``int`` The lower bound of dimension 'Q'
        :Q_stop:                ``int`` The upper bound of dimension 'Q'

    Returns:
        :[((x_start, x_stop), (y_start, y_stop), (z_start, z_stop)), ... ]:
    """
    # First, snap to block in each direction. Then we can divide sans
    # modulo without having to worry about remainders.
    bounds = [snap_to_cube(x_start, x_stop, block_size[0], origin[0]),
              snap_to_cube(y_start, y_stop, block_size[1], origin[1]),
              snap_to_cube(z_start, z_stop, block_size[2], origin[2])]

    chunks = []
    for q in range(3):
        chunks.append([(q_start, q_start + block_size[q]) for q_start in range(bounds[q][0], bounds[q][1], block_size[q])[:-1]])

    # There's a way to list-comprehensionify the above and the below, but...
    # a story for a different day.
    return [(chunks[0][x], chunks[1][y], chunks[2][z]) \
        for x in range(len(chunks[0])) \
        for y in range(len(chunks[1])) \
        for z in range(len(chunks[2]))]
