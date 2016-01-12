from __future__ import absolute_import
import numpy
from scipy import ndimage


def connected_components(data):
    """
    Run a jank implementation of connected-components on a bit of
    data. Probably shouldn't live here but it does for now.
    """
    mask = data > data.mean()
    label_im, nb_labels = ndimage.label(mask)
    return (label_im, nb_labels)
