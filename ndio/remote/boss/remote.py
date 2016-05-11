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

from ndio.remote.remote import Remote as NdRemote
from ndio.service.boss.project import ProjectService
from ndio.service.boss.metadata import MetadataService
import configparser
import os

CONFIG_FILE='~/.ndio/ndio.cfg'
CONFIG_PROJECT_SECTION = 'Project Service'
CONFIG_METADATA_SECTION = 'Metadata Service'
CONFIG_VOLUME_SECTION = 'Volume Service'
CONFIG_PROTOCOL = 'protocol'
# CONFIG_HOST example: api.theboss.io
CONFIG_HOST = 'host'
CONFIG_TOKEN = 'token'


class Remote(NdRemote):
    def __init__(self, cfg_file=CONFIG_FILE):
        self._token_project = None
        self._token_metadata = None
        self._token_volume = None

        try:
            self._config = self.load_config_file(os.path.expanduser(cfg_file))
            self._init_project_service()
            self._init_metadata_service()
            self._init_volume_service()
        except FileNotFoundError:
            print('Config file {} not found.'.format(cfg_file))
        except KeyError as k:
            print('Could not find key {} in {}'.format(k, CONFIG_FILE))

    def _init_project_service(self):
        project_cfg = self._config[CONFIG_PROJECT_SECTION]
        self._token_project = project_cfg[CONFIG_TOKEN]
        proto = project_cfg[CONFIG_PROTOCOL]
        host = project_cfg[CONFIG_HOST]

        self._project = ProjectService(host)
        self._project.base_protocol = proto
        self._project.set_auth(self._token_project)

    def _init_metadata_service(self):
        metadata_cfg = self._config[CONFIG_METADATA_SECTION]
        self._token_metadata = metadata_cfg[CONFIG_TOKEN]
        proto = metadata_cfg[CONFIG_PROTOCOL]
        host = metadata_cfg[CONFIG_HOST]

        self._metadata = MetadataService(host)
        self._metadata.base_protocol = proto
        self._metadata.set_auth(self._token_metadata)

    def _init_volume_service(self):
        volume_cfg = self._config[CONFIG_VOLUME_SECTION]
        self._token_volume = volume_cfg[CONFIG_TOKEN]
        proto = volume_cfg[CONFIG_PROTOCOL]
        host = volume_cfg[CONFIG_HOST]

        self._volume = MetadataService(host)
        self._volume.base_protocol = proto
        self._volume.set_auth(self._token_volume)

    def load_config(self, config_str):
        """Load config data for the Remote.

        Attributes:
            config_str (string): Config data encoded in a string.

        Returns:
            (configparser.ConfigParser)
        """
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read_string(config_str)
        return cfg_parser

    def load_config_file(self, path):
        """Load config data for Remote from file.

        Attributes:
            path (string): Path (and filename) to config file.

        Returns:
            (configparser.ConfigParser)
        """
        with open(path, 'r') as f:
            data = f.read()
            return self.load_config(data)

    @property
    def token_project(self):
        return self._token_project

    @token_project.setter 
    def token_project(self, value):
        self._token_project = value

    @property
    def token_metadata(self):
        return self._token_metadata

    @token_metadata.setter 
    def token_metadata(self, value):
        self._token_metadata = value

    @property
    def token_volume(self):
        return self._token_volume

    @token_volume.setter 
    def token_volume(self, value):
        self._token_volume = value

    def project_list(self, resource):
        self.project_service.set_auth(self._token_project)
        return self.project_service.list(resource)

    def project_create(self, resource):
        self.project_service.set_auth(self._token_project)
        return self.project_service.create(resource)

    def project_get(self, resource):
        self.project_service.set_auth(self._token_project)
        return self.project_service.get(resource)

    def project_update(self, resource):
        self.project_service.set_auth(self._token_project)
        return self.project_service.update(resource)

    def project_delete(self, resource):
        self.project_service.set_auth(self._token_project)
        return self.project_service.delete(resource)

    def list_metadata(self, resource):
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.list(resource)

    def create_metadata(self, resource, key, val):
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.create(resource, key, val)

    def get_metadata(self, resource, key):
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.get(resource, key)

    def update_metadata(self, resource, key, val):
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.update(resource, key, val)

    def delete_metadata(self, resource, key):
        self.metadata_service.set_auth(self._token_metadata)
        return self.metadata_service.delete(resource, key)
