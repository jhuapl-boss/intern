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


class HTTPErrorList(Exception):
    """HTTPErrorList stores a list of requests.HTTPError exceptions.

    When performing operations on multiple key-value pairs, this exception
    allows reporting of multiple failures.

    Attributes:
        http_errors (list): A list of requests.HTTPError exceptions.
    """

    def __init__(self, message):
        super(Exception, self).__init__(self, message)
        self.http_errors = []

    def __str__(self):
        lines = []
        lines.append(super().__str__())
        for i in self.http_errors:
            lines.append('\t{}'.format(i.__str__()))
        return '\n'.join(lines)
