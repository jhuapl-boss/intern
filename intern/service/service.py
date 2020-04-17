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
import six
from abc import ABCMeta, abstractmethod


@six.add_metaclass(ABCMeta)
class Service(object):
    def __init__(self):
        self._auth = None
        self._base_url = ""
        self._base_protocol = "https"

    @abstractmethod
    def set_auth(self, **kwargs):
        pass

    @property
    def auth(self):
        return self._auth

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, value):
        self._base_url = value

    @property
    def base_protocol(self):
        return self._base_protocol

    @base_protocol.setter
    def base_protocol(self, value):
        self._base_protocol = value
