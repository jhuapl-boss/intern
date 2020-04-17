# Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
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

import unittest
from intern.resource.dvid.resource import RepositoryResource

class TestRepositoryResource(unittest.TestCase):
    def setUp(self):

        UUID = "822524777d3048b8bd520043f90c1d28"
        ALIAS = "grayscale"

        self.uuid = UUID
        self.alias = ALIAS
    
    def testNone(self):
        ## No tests for this Resource Object
        NotImplemented

if __name__ == '__main__':
    unittest.main()
