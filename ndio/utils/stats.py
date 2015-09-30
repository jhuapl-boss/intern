import numpy
from scipy import ndimage

def connected_components(data):
    mask = data > data.mean()
    label_im, nb_labels = ndimage.label(mask)
    return (label_im, nb_labels)
