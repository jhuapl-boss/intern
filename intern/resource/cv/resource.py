from intern.resource import Resource
from cloudvolume import CloudVolume
import numpy as np
from os import path

class CloudVolumeResource(Resource):

    """Base class for CloudVolume resources.
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
    def create_CV(self, protocol, path, description = None, **params):
        """
        Creates a cloud volume instance with keyword parameters. 

        """
        info = CloudVolume.create_new_info(
            num_channels = params['num_channels'],
            layer_type = params['layer_type'], # 'image' or 'segmentation'
            data_type = params['data_type'], # can pick any popular uint
            encoding = params['encoding'], # other options: 'jpeg', 'compressed_segmentation' (req. uint32 or uint64)
            resolution = params['resolution'], # X,Y,Z values in nanometers
            voxel_offset = params['voxel_offset'], # values X,Y,Z values in voxels
            chunk_size = params['chunk_size'], # rechunk of image X,Y,Z in voxels
            volume_size = params['volume_size'], # X,Y,Z size in voxels)
        )
        if protocol == 'local':
            vol = CloudVolume('file://' + path, info=info)

        elif protocol == 'gs':
            vol = CloudVolume('gs:/' + path, info = info)

        elif protocol == 's3':
            pass
            
        else:
            print('Not a valid protocol')

        vol.provenance.description = description
        # vol.provenance.owners = params['owners'] # list of contact email addresses
        return vol

    def create_cutout(self, data, volume, xrang, yrang, zrang):
        volume[xrang[0]:xrang[1], yrang[0]:yrang[1], zrang[0]:zrang[1]] = data
        print("Your data is uploading...")

    def get_cutout(self, volume, xrang, yrang, zrang):
        data = volume[xrang[0]:xrang[1], yrang[0]:yrang[1], zrang[0]:zrang[1]]
        return data
        