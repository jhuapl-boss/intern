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
        """Build the url to access the Boss' project service.

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

    def build_metadata_url(self, resource, url_prefix, key, value=None):
        """Build the url to access the Boss' metadata service.

        Attributes:
            url_prefix (string): Do not end with a slash.  Example of expected value: https://api.theboss.io
            key (string): Key to get/create/update/delete.
            value (string): Value to assign to key or None.

        Returns:
            (string): Full URL to access API.
        """
        urlNoParams = self.build_url(resource, url_prefix, proj_list_req=False)
        urlWithKey = urlNoParams + '/?key=' + key
        if value is None:
            return urlWithKey
        return urlWithKey + '&value=' + value

    def get_request(self, resource, method, content, url_prefix, token, proj_list_req=False, json=None):
        """Create a request for accessing the Boss' services.

        Use for the project service or listing keys via the metadata service.

        Attributes:
            resource (ndio.ndresource.boss.Resource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            proj_list_req (bool): Set to True if performing a list operation on the project service.  Defaults to False.
            json (dict): POST body data.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.
        """
        url = self.build_url(resource, url_prefix, proj_list_req)
        headers = self.get_headers(content, token)
        if(json is None):
            req = Request(method, url, headers = headers)
        else:
            req = Request(method, url, headers = headers, json = json)

        return req

    def get_metadata_request(
        self, resource, method, content, url_prefix, token,
        key=None, value=None):

        """Create a request for accessing the Boss' metadata service.

        Do not use this method for list operations.  Instead, use the
        get_request() method.

        Attributes:
            resource (ndio.ndresource.boss.Resource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            key (string): Name of key to operate on.  Defaults to None.
            value (string): Value to assign to key  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.
        """
        url = self.build_metadata_url(resource, url_prefix, key, value)
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)