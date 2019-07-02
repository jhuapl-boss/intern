"""
# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
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
"""
from intern.remote import Remote
from intern.resource.cv.resource import *
from intern.service.cv.service import *

LATEST_VERSION = 'v1'

class CloudVolumeRemote(Remote):
    def __init__(self, version=None):
        if version is None:
            version = LATEST_VERSION

    def cloudvolume(self, protocol, path, new_layer = True, **params):
        return CloudVolumeResource(protocol, path, new_layer, **params)

    def create_cutout(self, cv, data, xrang, yrang, zrang):
        return cv.create_cutout(data, xrang, yrang, zrang)

    def get_cutout(self, cv, xrang, yrang, zrang):
        return cv.get_cutout(data, xrang, yrang, zrang)

    def get_info(self, cv):
        return CloudVolumeService.get_info(cv)

    def get_cloudpath(self, cv):
        return CloudVolumeService.get_cloudpath(cv)

    def get_provenance(self, cv):
        return CloudVolumeService.get_provenance(cv)

    def delete_data(self, cv, xrang, yrang, zrang):
        return CloudVolumeService.deleta_data(cv)
