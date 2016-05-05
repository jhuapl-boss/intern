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

from abc import ABCMeta
from abc import abstractmethod

class Resource(metaclass=ABCMeta):
    """Base class used as a parameter by ndio.service.Service object methods.
    """

    @abstractmethod
    def valid_volume():
        """Returns True if resource is something that can access the volume service.
            Attributes:

            Returns:
                (bool) : True if calls to volume service may be made.
        """
