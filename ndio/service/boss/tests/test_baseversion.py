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

import unittest
from ndio.service.boss.baseversion import BaseVersion
from ndio.ndresource.boss.resource import CollectionResource
from ndio.ndresource.boss.resource import ChannelResource
import numpy

VER = 'v0.7'

class ProjectImpl(BaseVersion):
    """Create a concrete implementation of BaseVersion so it can be tested.
    """

    @property
    def version(self):
        return VER

    @property
    def endpoint(self):
        return 'resource'

class MetadataImpl(BaseVersion):
    """Create a concrete implementation of BaseVersion so it can be tested.
    """

    @property
    def version(self):
        return VER

    @property
    def endpoint(self):
        return 'meta'

class VolumeImpl(BaseVersion):
    """Create a concrete implementation of BaseVersion so it can be tested.
    """

    @property
    def version(self):
        return VER

    @property
    def endpoint(self):
        return 'cutout'

class BaseVersionTest(unittest.TestCase):
    def setUp(self):
        self.resource = CollectionResource('coll1', VER)
        self.chanResource = ChannelResource(
            'chan1', 'coll1', 'exp1', 'image', VER, 'null descr', 0, 'uint8', 0)
        self.test_project = ProjectImpl()
        self.test_meta = MetadataImpl()
        self.test_volume = VolumeImpl()
        self.url_prefix = 'https://api.theboss.io'

    ##
    ## Methods used for the project service.
    ##

    def test_build_url_for_list(self):
        """A list operation's URL is different than any other operation.  It
        uses the plural form of the resource's type name rather than the
        resource's name.
        """
        actual = self.test_project.build_url(self.resource, self.url_prefix, proj_list_req=True)
        self.assertEqual(
            self.url_prefix + '/' + self.test_project.version + '/' + 
            self.test_project.endpoint + '/collections',
            actual)

    def test_build_url_not_list(self):
        """Test standard use of BaseVersion.build_url().
        """
        actual = self.test_project.build_url(self.resource, self.url_prefix, proj_list_req=False)
        self.assertEqual(
            self.url_prefix + '/' + self.test_project.version + '/' +
            self.test_project.endpoint + '/' + self.resource.name,
            actual)

    def test_get_headers_gives_dict_with_content_type(self):
        actual = self.test_project.get_headers('application/json', 'my_token')
        self.assertTrue('Content-Type' in actual)
        self.assertEqual('application/json', actual['Content-Type'])

    def test_get_headers_gives_dict_with_authorization(self):
        actual = self.test_project.get_headers('application/json', 'my_token')
        self.assertTrue('Authorization' in actual)
        self.assertEqual('Token my_token', actual['Authorization'])

    def test_get_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        actual = self.test_project.get_request(
            self.resource, 'GET', 'application/json', url_prefix, token, 
            proj_list_req=False)
        self.assertEqual(
            '{}/{}/{}/{}'.format(url_prefix, self.test_project.version, self.test_project.endpoint, self.resource.name), 
            actual.url)
        self.assertEqual('Token {}'.format(token), actual.headers['Authorization'])
        self.assertEqual('application/json', actual.headers['Content-Type'])

    def test_get_group_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        grp_name = 'fire'

        expected = '{}/{}/group/{}/'.format(
            url_prefix, self.test_project.version, grp_name)

        actual = self.test_project.get_group_request(
            'GET', 'application/json', url_prefix, token, grp_name, None)

        self.assertEqual(expected, actual.url)

    def test_get_group_request_user(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        grp_name = 'fire'
        user_name = 'fox'

        expected = '{}/{}/group-member/{}/{}/'.format(
            url_prefix, self.test_project.version, grp_name, user_name)

        actual = self.test_project.get_group_request(
            'GET', 'application/json', url_prefix, token, grp_name, user_name)

        self.assertEqual(expected, actual.url)

    def test_get_permission_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        grp_name = 'fire'
        resrc_path = self.chanResource.get_route()
        data = { 'permissions': ['update', 'add', 'delete'] }

        expected = '{}/{}/permission/{}/{}'.format(
            url_prefix, self.test_volume.version, grp_name, resrc_path)

        actual = self.test_project.get_permission_request(
            'GET', 'application/json', url_prefix, token, grp_name, 
            self.chanResource, data)

        self.assertEqual(expected, actual.url)
        self.assertEqual(data, actual.data)

    def test_get_user_role_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        role = 'admin'

        expected = '{}/{}/user-role/{}/{}'.format(
            url_prefix, self.test_project.version, user, role)

        actual = self.test_project.get_user_role_request(
            'POST', 'application/json', url_prefix, token, user, role)

        self.assertEqual(expected, actual.url)

    def test_get_user_role_request_no_role(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'

        expected = '{}/{}/user-role/{}'.format(
            url_prefix, self.test_project.version, user)

        actual = self.test_project.get_user_role_request(
            'POST', 'application/json', url_prefix, token, user)

        self.assertEqual(expected, actual.url)

    def test_get_user_request_just_username(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'

        expected = '{}/{}/user/{}'.format(
            url_prefix, self.test_project.version, user)

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user)

        self.assertEqual(expected, actual.url)

    def test_get_user_request_with_firstname(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        first = 'Roger'

        expected = '{}/{}/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'first_name': first }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, first)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.data)

    def test_get_user_request_with_lastname(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        last = 'Roger'

        expected = '{}/{}/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'last_name': last }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, last_name=last)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.data)

    def test_get_user_request_with_email(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        email = 'Roger@me.com'

        expected = '{}/{}/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'email': email }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, email=email)

    def test_get_user_request_with_password(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        password = 'password'

        expected = '{}/{}/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'password': password }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, password=password)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.data)

    def test_get_user_request_with_password(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        first = 'Roger'
        last = 'Dodger'
        email = 'Roger@me.com'
        password = 'password'

        expected = '{}/{}/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = {
            'first_name': first, 'last_name': last, 'email': email, 
            'password': password }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, first, last,
            email, password)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.data)

    ##
    ## Methods used for the metadata service.
    ##

    def test_build_metadata_url_no_value(self):
        key = 'foo'
        actual = self.test_meta.build_metadata_url(
            self.resource, self.url_prefix, key)
        self.assertEqual(
            self.url_prefix + '/' + self.test_meta.version + '/' + 
            self.test_meta.endpoint + '/' + self.resource.name + '/?key=' + key,
            actual)

    def test_build_metadata_url_key_and_value(self):
        key = 'foo'
        value = 'bar'
        actual = self.test_meta.build_metadata_url(
            self.resource, self.url_prefix, key, value)
        self.assertEqual(
            self.url_prefix + '/' + self.test_meta.version + '/' + 
            self.test_meta.endpoint + '/' + self.resource.name + '/?key=' + 
            key + '&value=' + value,
            actual)

    def test_get_metadata_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        key = 'version'
        actual = self.test_meta.get_metadata_request(
            self.resource, 'GET', 'application/json', url_prefix, token, key)
        self.assertEqual(
            '{}/{}/{}/{}/?key={}'.format(url_prefix, self.test_meta.version, self.test_meta.endpoint, self.resource.name, key), 
            actual.url)
        self.assertEqual('Token {}'.format(token), actual.headers['Authorization'])
        self.assertEqual('application/json', actual.headers['Content-Type'])

    ##
    ## Methods used for the volume service.
    ##

    def test_convert_int_list_range_to_str(self):
        exp = '2:7'
        actual = self.test_volume.convert_int_list_range_to_str([2,7])
        self.assertEqual(exp, actual)
        
    def test_convert_int_list_range_to_str_bad_range(self):
        with self.assertRaises(RuntimeError):
            self.test_volume.convert_int_list_range_to_str([7,5])

    def test_convert_int_list_range_to_str_wrong_number_of_elements(self):
        with self.assertRaises(RuntimeError):
            self.test_volume.convert_int_list_range_to_str([5, 7, 9])

    def test_convert_int_list_range_to_str_no_list(self):
        with self.assertRaises(RuntimeError):
            self.test_volume.convert_int_list_range_to_str('5, 7')

    def test_build_cutout_url_no_time_range(self):
        res = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = None
        actual = self.test_volume.build_cutout_url(
            self.chanResource, self.url_prefix,
            res, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst)

        self.assertEqual(
            self.url_prefix + '/' + self.test_volume.version + '/' + self.test_volume.endpoint +
            '/' + self.chanResource.coll_name + '/' + self.chanResource.exp_name +
            '/' + self.chanResource.name + '/' + str(res) + '/' + x_range + '/' +
            y_range + '/' + z_range + '/',
            actual)

    def test_build_cutout_url_with_time_range(self):
        res = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = [10, 25]
        time_range = '10:25'
        actual = self.test_volume.build_cutout_url(
            self.chanResource, self.url_prefix,
            res, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst)

        self.assertEqual(
            self.url_prefix + '/' + self.test_volume.version + '/' + self.test_volume.endpoint +
            '/' + self.chanResource.coll_name + '/' + self.chanResource.exp_name +
            '/' + self.chanResource.name + '/' + str(res) + '/' + x_range + '/' +
            y_range + '/' + z_range + '/' + time_range + '/',
            actual)

    def test_get_cutout_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        resolution = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = [10, 25]
        time_range = '10:25'
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)

        actual = self.test_volume.get_cutout_request(
            self.chanResource, 'GET', 'application/blosc-python', url_prefix, token,
            resolution, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst, data)
        self.assertEqual(
            '{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/'.format(url_prefix, self.test_volume.version,
            self.test_volume.endpoint, self.chanResource.coll_name, 
            self.chanResource.exp_name, self.chanResource.name, resolution, 
            x_range, y_range, z_range, time_range), 
            actual.url)
        self.assertEqual('Token {}'.format(token), actual.headers['Authorization'])
        self.assertEqual('application/blosc-python', actual.headers['Content-Type'])


if __name__ == '__main__':
    unittest.main()
