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
from intern.resource.boss.resource import CoordinateFrameResource
from requests import Request

@six.add_metaclass(ABCMeta)
class BaseVersion(object):
    """BaseVersion is the base class for all versioned interfaces to the
    Boss API.
    """
    def __init__(self):
        self._token = None

    @property
    @abstractmethod
    def version(self):
        """Implementers define the version of the Boss API the service uses.
        """
        raise NotImplemented

    def convert_int_list_to_comma_sep_str(self, int_list):
        """Convert list of ints to comma separated stringj.

        Args:
            int_list (list[int]): list of ints.

        Returns:
            (string): Example: [1, 7, 9] => '1, 7, 9'

        """
        if len(int_list) == 1:
            return str(int_list[0])

        str_list = []
        for n in int_list:
            str_list.append(str(n))

        return (',').join(str_list)

    def convert_int_list_range_to_str(self, int_list):
        """Convert range in list of two ints to string representation.

        Returned string can then be placed in URL as a query parameter.

        Args:
            int_list (list[int]): range such as [10, 20] which means x>=10 and x<20.

        Returns:
            (string): [10, 20] => '10:20'

        Raises:
            (RuntimeError): if given invalid range.
        """
        if len(int_list) != 2:
            raise RuntimeError('int_list must contain exactly two values.')

        if int_list[0] > int_list[1]:
            raise RuntimeError('Invalid range: int_list[0] > int_list[1].')

        return '{}:{}'.format(int_list[0], int_list[1])

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

    def build_url(self, resource, url_prefix, service, req_type='normal'):
        """Build the url to access the Boss' project service.

        Args:
            url_prefix (string): Do not end with a slash.  Example of expected value: https://api.theboss.io
            service (string): Name of service to access, such as collection, meta, coord, etc.
            req_type (optional[string]): Valid values ['normal', 'list', 'cutout'].  Defaults to 'normal'.

        Returns:
            (string): Full URL to access API.

        Raises:
            (RuntimeError): if invalid req_type given or url_prefix not given.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        if req_type == 'normal':
            suffix = resource.get_route()
        elif req_type == 'list':
            # No suffix required for a list request.
            suffix = resource.get_list_route()
        elif req_type == 'cutout':
            suffix = resource.get_cutout_route()
        else:
            raise RuntimeError('Invalid request type: {}'.format(req_type))

        url = (url_prefix + '/' + self.version + '/' + service + '/' + suffix)
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
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        suffix = resource.get_meta_route()
        urlNoParams = (url_prefix + '/' + self.version + '/meta/' + suffix)
        if key is None:
            return urlNoParams

        urlWithKey = urlNoParams + '/?key=' + key
        if value is None:
            return urlWithKey

        return urlWithKey + '&value=' + str(value)

    def build_cutout_url(
        self, resource, url_prefix, resolution, x_range, y_range, z_range, time_range=None, id_list=[], access_mode=None):
        """Build the url to access the cutout function of the Boss' volume service.

        Args:
            url_prefix (string): Do not end with a slash.  Example of expected value: https://api.theboss.io
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.
            id_list (optional [list[int]]): list of object ids to filter the cutout by.
            access_mode (optional [Enum]): Identifies one of three cache access options:
                cache = Will check both cache and for dirty keys
                no_cache = Will skip cache check but check for dirty keys
                raw = Will skip both the cache and dirty keys check
                NOTE: No default here since when building a cutout url to create_cutout there is no need for access_mode

        Returns:
            (string): Full URL to access API.

        Raises:
            (RuntimeError): if *_range invalid.
        """
        baseUrl = self.build_url(resource, url_prefix, 'cutout', req_type='cutout')
        x_rng_lst = self.convert_int_list_range_to_str(x_range)
        y_rng_lst = self.convert_int_list_range_to_str(y_range)
        z_rng_lst = self.convert_int_list_range_to_str(z_range)

        urlWithParams = (
            baseUrl + '/' + str(resolution) + '/' + x_rng_lst + '/' + y_rng_lst +
            '/' + z_rng_lst + '/')

        if time_range is not None:
            t_rng_lst = self.convert_int_list_range_to_str(time_range)
            urlWithParams += t_rng_lst + '/'

        queryParamDict = {}
        if len(id_list) > 0:
            queryParamDict['filter'] = self.convert_int_list_to_comma_sep_str(id_list)
    
        # If creating a cutout, the url will not include the access_mode otherwise it will
        if access_mode is not None:
            queryParamDict['access-mode'] = access_mode.value 
        """
        TODO: LMR
        The following could be done using urlib.urlencode(urlWithParams += '?' + urllib.parse.urlencode(queryParamDict,safe=",")),
        however urllib's python2 version of this function does not take in the 'safe' parameter and thus we can not use the 
        function interchangable for python2/3. In order to keep our python2/3 compatability, we do not use urllib. 
        """
        if queryParamDict:
            # The first time include '?'
            urlWithParams += '?'
            for k, v in queryParamDict.items():
                # if this is the first run through, last char in str will be ?, so don't include '&'
                if urlWithParams[len(urlWithParams)-1] == '?':
                    pass
                # otherwise use '&'
                else:
                    urlWithParams += '&'
                # Add key and value members
                urlWithParams += '{}={}'.format(k,v)
        return urlWithParams

    def get_request(self, resource, method, content, url_prefix, token, proj_list_req=False, json=None, data=None):
        """Create a request for accessing the Boss' data model services.

        Use for the project service or listing keys via the metadata service.

        Args:
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
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
        if isinstance(resource, CoordinateFrameResource):
            service = 'coord'
        else:
            service = 'collection'

        if proj_list_req:
            req_type = 'list'
        else:
            req_type = 'normal'

        url = self.build_url(resource, url_prefix, service, req_type)
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
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
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
        resolution, x_range, y_range, z_range, time_range,  numpyVolume=None, id_list=[], access_mode=None,):

        """Create a request for working with cutouts (part of the Boss' volume service).

        Args:
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (list[int]): time range such as [30, 40] which means t>=30 and t<40.
            numpyVolume (optional numpy array): The data volume encoded in a numpy array.
            id_list (optional [list[int]]): list of object ids to filter the cutout by.
            access_mode (optional [Enum]): Identifies one of three cache access options:
                cache = Will check both cache and for dirty keys
                no_cache = Will skip cache check but check for dirty keys
                raw = Will skip both the cache and dirty keys check

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        url = self.build_cutout_url(
            resource, url_prefix, resolution, x_range, y_range, z_range,  time_range, id_list, access_mode)
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers, data = numpyVolume)

    def get_group_request(self, method, content, url_prefix, token, name=None):
        """Get a request for getting group information.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            name (optional[string|None]): Name of group.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = url_prefix + '/' + self.version + '/groups/'
        if name is not None:
            url += name + '/'
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)

    def get_group_members_request(
        self, method, content, url_prefix, token, group_name, user_name=None):
        """Get a request object for working with group membership.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            group_name (string): Name of group.
            user_name (optional[string]): Provide a user name if not doing a list operation.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = url_prefix + '/' + self.version + '/groups/' + group_name + '/members/'
        if user_name is not None:
            url += user_name
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)

    def get_group_maintainers_request(
        self, method, content, url_prefix, token, group_name, user_name=None):
        """Get a request object for working with group maintainers.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            group_name (string): Name of group.
            user_name (optional[string]): Provide a user name if not doing a list operation.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = url_prefix + '/' + self.version + '/groups/' + group_name + '/maintainers/'
        if user_name is not None:
            url += user_name
        headers = self.get_headers(content, token)
        return Request(method, url, headers = headers)

    def get_permission_request(self, method, content, url_prefix, token, query_params=None, post_data=None):
        """Generate a request for manipulating permissions of a data model object.

        Manipulate what members of the named group can do with the given data
        model object.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            query_params (dict): Query params for GET requests.  Defaults to None.
            post_data (dict): POST body data.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = (url_prefix + '/' + self.version + '/permissions/')
        headers = self.get_headers(content, token)

        if method == "GET" or method == "DELETE":
            return Request(method, url, headers=headers, params=query_params)
        else:
            # Assuming POST or PATCH
            return Request(method, url, headers=headers, json=post_data)

    def get_user_role_request(
        self, method, content, url_prefix, token, user, role=None):
        """Generate a request for manipulating roles for a user.

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

        url = url_prefix + '/' + self.version + '/sso/user-role/' + user
        if role is not None:
            url = url + '/' + role

        headers = self.get_headers(content, token)
        return Request(method, url, headers=headers)

    def get_user_request(
        self, method, content, url_prefix, token, user, first_name=None,
        last_name=None, email=None, password=None):
        """Generate a request for working with the /sso endpoint.

        Args:
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            user (string): Name of user.
            first_name (optional[string]): User's first name.  Defaults to None.
            last_name (optional[string]): User's last name.  Defaults to None.
            email: (optional[string]): User's email address.  Defaults to None.
            password: (optional[string]): User's password.  Defaults to None.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        data = {}

        url = url_prefix + '/' + self.version + '/sso/user/' + user

        if first_name is not None:
            data['first_name'] = first_name

        if last_name is not None:
            data['last_name'] = last_name

        if email is not None:
            data['email'] = email

        if password is not None:
            data['password'] = password

        headers = self.get_headers(content, token)
        return Request(method, url, headers=headers, json=data)

    def get_reserve_request(
            self, resource, method, content, url_prefix, token, num_ids):
        """

        Args:
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            num_ids (int): Number of ids to reserve.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = (url_prefix + '/' + self.version + '/reserve/' +
               resource.get_reserve_route() + '/{}'.format(num_ids))
        headers = self.get_headers(content, token)
        return Request(method, url, headers=headers)

    def get_bounding_box_request(
            self, resource, method, content, url_prefix, token, resolution,
            id, bb_type):
        """

        Args:
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            resolution (int): 0 = default resolution.
            id (int): Annotation object id.
            bb_type (string): 'loose' | 'tight'.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        if url_prefix is None or url_prefix == '':
            raise RuntimeError('url_prefix required.')

        url = (url_prefix + '/' + self.version + '/boundingbox/' +
               resource.get_cutout_route() + '/{}/{}/?type={}'.format(
            resolution, id, bb_type))
        headers = self.get_headers(content, token)
        return Request(method, url, headers=headers)

    def build_ids_url(
            self, resource, url_prefix, resolution,
            x_range, y_range, z_range, time_range=None):
        """Build the url to access the ids function of the Boss' volume service.

        Args:
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
            url_prefix (string): Do not end with a slash.  Example of expected value: https://api.theboss.io
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (optional [list[int]]): time range such as [30, 40] which means t>=30 and t<40.

        Returns:
            (string): Full URL to access API.

        Raises:
            (RuntimeError): if *_range invalid.
        """
        base_url = self.build_url(resource, url_prefix, 'ids', req_type='cutout')
        x_rng_lst = self.convert_int_list_range_to_str(x_range)
        y_rng_lst = self.convert_int_list_range_to_str(y_range)
        z_rng_lst = self.convert_int_list_range_to_str(z_range)

        url_with_params = (
            base_url + '/' + str(resolution) + '/' + x_rng_lst + '/' + y_rng_lst +
            '/' + z_rng_lst + '/')

        if time_range is not None:
            t_rng_lst = self.convert_int_list_range_to_str(time_range)
            url_with_params += t_rng_lst + '/'

        return url_with_params

    def get_ids_request(
            self, resource, method, content, url_prefix, token,
            resolution, x_range, y_range, z_range, time_range):
        """Create a request for getting ids in a region (part of the Boss' volume service).

        Args:
            resource (intern.resource.boss.BossResource): Resource to perform operation on.
            method (string): HTTP verb such as 'GET'.
            content (string): HTTP Content-Type such as 'application/json'.
            url_prefix (string): protocol + initial portion of URL such as https://api.theboss.io  Do not end with a forward slash.
            token (string): Django Rest Framework token for auth.
            resolution (int): 0 indicates native resolution.
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.
            time_range (list[int]): time range such as [30, 40] which means t>=30 and t<40.

        Returns:
            (requests.Request): A newly constructed Request object.

        Raises:
            RuntimeError if url_prefix is None or an empty string.
        """
        url = self.build_ids_url(
            resource, url_prefix, resolution, x_range, y_range, z_range, time_range)
        headers = self.get_headers(content, token)
        return Request(method, url, headers=headers)
