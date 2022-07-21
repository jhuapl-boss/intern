# Copyright 2020-2022 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    from intern.remote.cv.remote import *

    HAS_CLOUDVOLUME = True
except ImportError:
    HAS_CLOUDVOLUME = False

import os
import shutil
import numpy as np
import unittest

FILE_PATH = "test_data/images/"


class TestCloudVolumeRemote(unittest.TestCase):
    def setUp(self):
        os.makedirs(FILE_PATH, exist_ok=True)
        self.cv_remote = CloudVolumeRemote(
            {"protocol": "local", "cloudpath": FILE_PATH}
        )

    @unittest.skipIf(not HAS_CLOUDVOLUME, "cloud-volume not installed. Skipping test.")
    def test_cutout_uint8(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint8",
            resolution=(10, 10, 10),
            volume_size=(128, 128, 128),
            chunk_size=(32, 32, 32),
        )

        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.randint(0, 255, [128, 128, 128], dtype=np.uint8)
        self.cv_remote.create_cutout(resource, 0, [0, 128], [0, 128], [0, 128], data)

        # Download cutout and check for equivalence
        cutout = self.cv_remote.get_cutout(resource, 0, [32, 96], [32, 96], [32, 96])
        np.testing.assert_array_equal(data[32:96, 32:96, 32:96], cutout)

    @unittest.skipIf(not HAS_CLOUDVOLUME, "cloud-volume not installed. Skipping test.")
    def test_cutout_uint16(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint16",
            resolution=(10, 10, 10),
            volume_size=(128, 128, 128),
            chunk_size=(32, 32, 32),
        )

        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.randint(0, 255, [128, 128, 128], dtype=np.uint16)
        self.cv_remote.create_cutout(resource, 0, [0, 128], [0, 128], [0, 128], data)

        # Download cutout and check for equivalence
        cutout = self.cv_remote.get_cutout(resource, 0, [32, 96], [32, 96], [32, 96])
        np.testing.assert_array_equal(data[32:96, 32:96, 32:96], cutout)

    @unittest.skipIf(not HAS_CLOUDVOLUME, "cloud-volume not installed. Skipping test.")
    def test_cutout_float64(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="segmentation",
            data_type="float64",
            resolution=(10, 10, 10),
            volume_size=(128, 128, 128),
            chunk_size=(32, 32, 32),
        )

        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.rand(128, 128, 128)
        self.cv_remote.create_cutout(resource, 0, [0, 128], [0, 128], [0, 128], data)

        # Download cutout and check for equivalence
        cutout = self.cv_remote.get_cutout(resource, 0, [32, 96], [32, 96], [32, 96])
        np.testing.assert_array_equal(data[32:96, 32:96, 32:96], cutout)

    @unittest.skipIf(not HAS_CLOUDVOLUME, "cloud-volume not installed. Skipping test.")
    def test_multiple_mips(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint8",
            resolution=(10, 10, 10),
            volume_size=(128, 128, 128),
            chunk_size=(32, 32, 32),
            max_mip=1,
            factor=(2, 2, 1),
        )

        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)

        # Upload data to mip 0
        data_0 = np.random.randint(0, 255, [128, 128, 128], dtype=np.uint8)
        self.cv_remote.create_cutout(resource, 0, [0, 128], [0, 128], [0, 128], data_0)

        # Upload data to mip 1
        data_1 = np.random.randint(0, 255, [64, 64, 128], dtype=np.uint8)
        self.cv_remote.create_cutout(resource, 1, [0, 64], [0, 64], [0, 128], data_1)

        # Download cutout and check for equivalence
        cutout_0 = self.cv_remote.get_cutout(resource, 0, [0, 128], [0, 128], [0, 128])
        np.testing.assert_array_equal(data_0, cutout_0)

        # Download cutout and check for equivalence
        cutout_1 = self.cv_remote.get_cutout(resource, 1, [0, 64], [0, 64], [0, 128])
        np.testing.assert_array_equal(data_1, cutout_1)

    @unittest.skipIf(not HAS_CLOUDVOLUME, "cloud-volume not installed. Skipping test.")
    def test_metadata(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint8",
            resolution=(10, 10, 10),
            volume_size=(128, 128, 128),
            chunk_size=(32, 32, 32),
            max_mip=7,
        )

        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        self.cv_remote.set_provenance(
            resource,
            owners=["testing"],
            description="testing",
            sources=[1, 2, 3],
            processsing=[{"does": "this work"}],
        )

        self.assertEqual(info, self.cv_remote.get_info(resource))
        self.assertEqual(
            "file://" + os.path.join(os.getcwd(), "test_data/images"),
            self.cv_remote.get_cloudpath(resource),
        )
        self.assertEqual("images", self.cv_remote.get_layer(resource))
        self.assertEqual("test_data", self.cv_remote.get_dataset_name(resource))
        self.assertEqual(range(0, 8), self.cv_remote.list_res(resource))

    @unittest.skipIf(not HAS_CLOUDVOLUME, "cloud-volume not installed. Skipping test.")
    def test_delete(self):
        # Create Info JSON
        info = self.cv_remote.create_new_info(
            num_channels=1,
            layer_type="image",
            data_type="uint8",
            resolution=(10, 10, 10),
            volume_size=(128, 128, 128),
            chunk_size=(32, 32, 32),
        )

        # Instantiate a new cloudvolume resource
        resource = self.cv_remote.cloudvolume(info=info)
        # Upload data
        data = np.random.randint(0, 255, [128, 128, 128], dtype=np.uint8)
        self.cv_remote.create_cutout(resource, 0, [0, 128], [0, 128], [0, 128], data)

        # Delete data
        self.cv_remote.delete_data(resource, 0, [0, 64], [0, 64], [0, 64])

        np.testing.assert_array_equal(
            np.zeros([64, 64, 64]),
            self.cv_remote.get_cutout(resource, 0, [0, 64], [0, 64], [0, 64]),
        )

    def tearDown(self):
        shutil.rmtree(FILE_PATH)
