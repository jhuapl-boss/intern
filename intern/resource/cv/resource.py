from intern.resource import Resource
from cloudvolume import CloudVolume
import numpy as np
from os import path

class CloudVolumeResource(Resource):

    """Base class for CloudVolume resources.
    Attributes:
        name (string): Name of resource.  Used as identifier when talking to
        the cloud volume APO. 
        description (string): Text description of resource.
        creator (string): Resource creator.
        raw (dictionary): Holds JSON data returned by DVID on a POST (create) or GET operation.
    """

    def __init__(self):
        """
            Initializes intern.Resource parent class
        """
        Resource.__init__(self)

    def valid_volume(self):
        """Returns True if resource is something that can access the volume service.
        Args:
        Returns:
            (bool) : True if calls to volume service may be made.
        """
        return True

    @classmethod
    def create_CV(self, protocol, path, description = None, **kwargs):
        """
        Creates a cloud volume instance with keyword parameters. 

        """
        info = CloudVolume.create_new_info(
            num_channels = kwargs['num_channels'],
            layer_type = kwargs['layer_type'], # 'image' or 'segmentation'
            data_type = kwargs['data_type'], # can pick any popular uint
            encoding = kwargs['encoding'], # other options: 'jpeg', 'compressed_segmentation' (req. uint32 or uint64)
            resolution = kwargs['resolution'], # X,Y,Z values in nanometers
            voxel_offset = kwargs['voxel_offset'], # values X,Y,Z values in voxels
            chunk_size = kwargs['chunk_size'], # rechunk of image X,Y,Z in voxels
            volume_size = kwargs['volume_size'], # X,Y,Z size in voxels)
        )
        # If you're using amazon or the local file system, you can replace 'gs' with 's3' or 'file'
        if protocol == 'local':
            vol = CloudVolume('file://' + path, info=info)
            vol.provenance.description = description
            vol.provenance.owners = kwargs['owners'] # list of contact email addresses
            return vol

        elif protocol == 'gs':
            pass

        elif protocol == 's3':
            pass

    def create_cutout(self, data, volume, xrang, yrang, zrang):
        vol[xrang[0]:xrang[1], yrang[0]:yrang[1], zrang[0]:zrang[1]] = data
        return "Your data is uploading..."

    def get_cutout(self, volume, xrang, yrang, zrang):
        data = vol[xrang[0]:xrang[1], yrang[0]:yrang[1], zrang[0]:zrang[1]]
        return data
        