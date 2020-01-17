import os
import shutil
import numpy as np
import unittest
from intern.remote.cv.remote import *

FILE_PATH = "test_data/images/"

class TestCloudVolumeRemote(unittest.TestCase):
    def setUp(self):
        os.makedirs(FILE_PATH, exist_ok=True)
        self.cv_remote = CloudVolumeRemote({
        'protocol': 'local',
        'cloudpath': FILE_PATH
        })
    
    def test_cutout_uint8(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint8",
            resolution=(10,10,10),
            volume_size=(128,128,128),
            chunk_size=(32,32,32)
            )
        
        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.randint(0, 255, [128,128,128], dtype=np.uint8)
        self.cv_remote.create_cutout(resource, 0, [0,128], [0,128], [0,128], data)

        # Download cutout and check for equivalence 
        cutout = self.cv_remote.get_cutout(resource, 0, [32,96], [32,96], [32,96])[:,:,:,0]
        np.testing.assert_array_equal(data[32:96, 32:96, 32:96], cutout)

    def test_cutout_uint16(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint16",
            resolution=(10,10,10),
            volume_size=(128,128,128),
            chunk_size=(32,32,32)
            )
        
        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.randint(0, 255, [128,128,128], dtype=np.uint16)
        self.cv_remote.create_cutout(resource, 0, [0,128], [0,128], [0,128], data)

        # Download cutout and check for equivalence 
        cutout = self.cv_remote.get_cutout(resource, 0, [32,96], [32,96], [32,96])[:,:,:,0]
        np.testing.assert_array_equal(data[32:96, 32:96, 32:96], cutout)
    
    def test_cutout_float64(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="segmentation",
            data_type="float64",
            resolution=(10,10,10),
            volume_size=(128,128,128),
            chunk_size=(32,32,32)
            )
        
        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.rand(128,128,128)
        self.cv_remote.create_cutout(resource, 0, [0,128], [0,128], [0,128], data)

        # Download cutout and check for equivalence 
        cutout = self.cv_remote.get_cutout(resource, 0, [32,96], [32,96], [32,96])[:,:,:,0]
        np.testing.assert_array_equal(data[32:96, 32:96, 32:96], cutout)
    
    def test_metadata(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint8",
            resolution=(10,10,10),
            volume_size=(128,128,128),
            chunk_size=(32,32,32)
            )
        
        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        self.cv_remote.set_provenance(
            resource, 
            owners = ['testing'],
            description = "testing",
            sources = [1,2,3],
            processsing = [{'does': 'this work'}]
            )

        self.assertEqual(info, self.cv_remote.get_info(resource))
        self.assertEqual("images", self.cv_remote.get_layer(resource))
        self.assertEqual("test_data", self.cv_remote.get_dataset_name(resource))

    def tearDown(self):
        shutil.rmtree(FILE_PATH)
