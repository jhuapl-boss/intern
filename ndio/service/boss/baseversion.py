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

        Args:
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

        Args:
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

        Args:
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
        return urlWithKey + '&value=' + str(value)

    def build_cutout_url(
        self, resource, url_prefix, resolution, x_range, y_range, z_range, time_range):
        baseUrl = self.build_url(resource, url_prefix, proj_list_req=False)
        """Build the url to access the cutout function of the Boss' volume service.

        Args:
            url_prefix (string): Do not end with a slash.  Example of expected value: https://api.theboss.io
            resolution (int): 0 indicates native resolution.
            x_range (string): x range such as '10:20' which means x>=10 and x<20.
            y_range (string): y range such as '10:20' which means y>=10 and y<20.
            z_range (string): z range such as '10:20' which means z>=10 and z<20.
            time_range (string): None or time range such as 30:40 which means t>=30 and t<40.

        Returns:
            (string): Full URL to access API.
        """
        urlWithParams = (
            baseUrl + '/' + str(resolution) + '/' + x_range + '/' + y_range +
            '/' + z_range + '/')
        if time_range is None:
            return urlWithParams

        urlWithTime = urlWithParams + time_range + '/'
        return urlWithTime

    def get_request(self, resource, method, content, url_prefix, token, proj_list_req=False, json=None, data=None):
        """Create a request for accessing the Boss' services.

        Use for the project service or listing keys via the metadata service.

        Args:
            resource (ndio.ndresource.boss.Resource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            proj_list_req (bool): Set to True if performing a list operation on the project service.  Defaults to False.
            json (dict): POST body data.  Defaults to None.
            data (): Raw data.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        url = self.build_url(resource, url_prefix, proj_list_req)
        headers = self.get_headers(content, token)
        req = Request(method, url, headers = headers, json = json, data = data)

        return req

    def get_metadata_request(
        self, resource, method, content, url_prefix, token,
        key=None, value=None):

        """Create a request for accessing the Boss' metadata service.

        Do not use this method for list operations.  Instead, use the
        get_request() method.

        Args:
            resource (ndio.ndresource.boss.Resource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            key (string): Name of key to operate on.  Defaults to None.
            value (string): Value to assign to key  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        url = self.build_metadata_url(resource, url_prefix, key, value)
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)

    def get_cutout_request(
        self, resource, method, content, url_prefix, token, 
        resolution, x_range, y_range, z_range, time_range, numpyVolume=None):

        """Create a request for working with cutouts (part of the Boss' volume service).

        Args:
            resource (ndio.ndresource.boss.Resource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            resolution (int): 0 indicates native resolution.
            x_range (string): x range such as '10:20' which means x>=10 and x<20.
            y_range (string): y range such as '10:20' which means y>=10 and y<20.
            z_range (string): z range such as '10:20' which means z>=10 and z<20.
            time_range (string): None or time range such as 30:40 which means t>=30 and t<40.
            numpyVolume (numpy array): The data volume encoded in a numpy array.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        url = self.build_cutout_url(
            resource, url_prefix, resolution, x_range, y_range, z_range, time_range)
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers, data = numpyVolume)

    def get_group_request(self, method, content, url_prefix, token, name, user_name):
        """Get a request for getting group information.

        If a user name is supplied, will generate a request to /group-member/ 
        instead of /group/.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            name (string): Name of group.
            user_name (optional[string]): Defaults to None.  If given, will generate a group membership request.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        if user_name is None:
            url = url_prefix + '/' + self.version + '/group/' + name + '/'
        else:
            url = (url_prefix + '/' + self.version + '/group-member/' + name + '/' +
                   user_name + '/')
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)

    def get_permission_request(
        self, method, content, url_prefix, token, name, resource, data=None):
        """Generate a request for manipulating permissions of a data model object.

        Manipulate what members of the named group can do with the given data
        model object.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Resource to perform operation on.
            data (dict): POST body data.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """

        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        suffix = resource.get_route()
        url = (url_prefix + '/' + self.version + '/permission/' + name + '/' +
               suffix)
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers, data = data)

    def get_user_role_request(
        self, method, content, url_prefix, token, user, role=None):
        """Generate a request for manipulating permissions of a data model object.

        Manipulate what members of the named group can do with the given data
        model object.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            user (string): Name of user.
            role (optional[string]): Name of role.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """

        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = url_prefix + '/' + self.version + '/user-role/' + user
        if role is not None:
            url = url + '/' + role

        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)
