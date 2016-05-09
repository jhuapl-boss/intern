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
from requests import Request

class BaseVersion(metaclass=ABCMeta):
    """BaseVersion is the base class for all versioned interfaces to the
    Boss API.
    """
    def __init__(self):
        pass

    @property
    @abstractmethod
    def version(self):
        """Implementers define the version of the Boss API the service uses.
        """

    @property
    @abstractmethod
    def endpoint(self):
        """Implementers define the name of the endpoint.
        """

    def get_headers(self, content_type, token):
        """Get headers to place in Request object.

        The auth token is added to the header for authenthication and
        authorization.

        Attributes:
            content_type (string):  HTTP content type of request.
            token (string):  Django Rest Framework token.

        Returns:
            (dictionary): Use as headers argument to the Request object.
        """
        return {
            'Authorization': 'Token ' + token,
            'Content-Type': content_type
        }

    def build_url(self, resource, url_prefix, proj_list_req):
        """Build the url to access the Boss API.

        Attributes:
            url_prefix (string): Do not end with a slash.  Example of expected value: https://api.theboss.io
            proj_list_req (bool): If True generate a list request for the project service.

        Returns:
            (string): Full URL to access API.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        if proj_list_req:
            suffix = resource.get_project_list_route()
        else:
            suffix = resource.get_route()

        url = (url_prefix + '/' + self.version + '/' + self.endpoint +
            '/' + suffix)
        return url

    def get_request(self, resource, method, content, url_prefix, token, proj_list_req=False, json=None):
        url = self.build_url(resource, url_prefix, proj_list_req)
        headers = self.get_headers(content, token)
        if(json is None):
            req = Request(method, url, headers = headers)
        else:
            req = Request(method, url, headers = headers, json = json)

        return req
