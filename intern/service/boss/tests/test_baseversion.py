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
from intern.service.boss.baseversion import BaseVersion
from intern.service.boss.v1.volume import CacheMode
from intern.resource.boss.resource import CollectionResource
from intern.resource.boss.resource import ChannelResource
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
        return 'collection'

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
        self.resource = CollectionResource('coll1')
        self.chanResource = ChannelResource(
            'chan1', 'coll1', 'exp1', 'image', 'null descr', 0, 'uint8', 0)
        self.annoResource = ChannelResource(
            'annChan', 'coll1', 'exp1', 'annotation', 'null descr',
            0, 'uint64', 0, sources=['chan1'])
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
        actual = self.test_project.build_url(
            self.resource, self.url_prefix, 'collection', req_type='list')
        self.assertEqual(
            self.url_prefix + '/' + self.test_project.version + '/' +
            self.test_project.endpoint + '/' + self.resource.name + '/',
            actual)

    def test_build_url_for_cutout(self):
        """Cutout URLs are also different than standard operations."""
        actual = self.test_project.build_url(
            self.chanResource, self.url_prefix, 'cutout', req_type='cutout')
        coll = self.chanResource.coll_name
        exp = self.chanResource.exp_name
        chan = self.chanResource.name
        self.assertEqual(
            self.url_prefix + '/' + self.test_project.version + '/' +
            'cutout/' + coll + '/' + exp + '/' + chan,
            actual)

    def test_build_url_for_cutout_to_black(self):
        """
        Test cutout to black URL
        """
        actual = self.test_project.build_url(
        self.chanResource, self.url_prefix, 'cutout/to_black', req_type='cutout')
        coll = self.chanResource.coll_name
        exp = self.chanResource.exp_name
        chan = self.chanResource.name
        expected = "/".join(
            [
                self.url_prefix,
                self.test_project.version,
                "cutout/to_black",
                coll,
                exp,
                chan,
            ]
        )

        self.assertEqual(expected, actual)

    def test_build_url_normal(self):
        """Test standard use of BaseVersion.build_url().
        """
        actual = self.test_project.build_url(
            self.resource, self.url_prefix, 'collection', req_type='normal')
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

        expected = '{}/{}/groups/{}/'.format(
            url_prefix, self.test_project.version, grp_name)

        actual = self.test_project.get_group_request(
            'GET', 'application/json', url_prefix, token, grp_name)

        self.assertEqual(expected, actual.url)

    def test_get_permission_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        grp_name = 'fire'
        post_data = {"group": grp_name,
                     "permissions": ['update', 'add', 'delete'],
                     }
        post_data.update(self.chanResource.get_dict_route())

        expected = '{}/{}/permissions/'.format(url_prefix, self.test_volume.version)

        actual = self.test_project.get_permission_request(
            'GET', 'application/json', url_prefix, token, post_data=post_data)

        self.assertEqual(expected, actual.url)

    def test_get_user_role_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        role = 'admin'

        expected = '{}/{}/sso/user-role/{}/{}'.format(
            url_prefix, self.test_project.version, user, role)

        actual = self.test_project.get_user_role_request(
            'POST', 'application/json', url_prefix, token, user, role)

        self.assertEqual(expected, actual.url)

    def test_get_user_role_request_no_role(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'

        expected = '{}/{}/sso/user-role/{}'.format(
            url_prefix, self.test_project.version, user)

        actual = self.test_project.get_user_role_request(
            'POST', 'application/json', url_prefix, token, user)

        self.assertEqual(expected, actual.url)

    def test_get_user_request_just_username(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'

        expected = '{}/{}/sso/user/{}'.format(
            url_prefix, self.test_project.version, user)

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user)

        self.assertEqual(expected, actual.url)

    def test_get_user_request_with_firstname(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        first = 'Roger'

        expected = '{}/{}/sso/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'first_name': first }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, first)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.json)

    def test_get_user_request_with_lastname(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        last = 'Roger'

        expected = '{}/{}/sso/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'last_name': last }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, last_name=last)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.json)

    def test_get_user_request_with_email(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        email = 'Roger@me.com'

        expected = '{}/{}/sso/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'email': email }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, email=email)

    def test_get_user_request_with_password_and_user(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        password = 'password'

        expected = '{}/{}/sso/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = { 'password': password }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, password=password)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.json)

    def test_get_user_request_with_password_and_email(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        user = 'fire'
        first = 'Roger'
        last = 'Dodger'
        email = 'Roger@me.com'
        password = 'password'

        expected = '{}/{}/sso/user/{}'.format(
            url_prefix, self.test_project.version, user)

        expectedData = {
            'first_name': first, 'last_name': last, 'email': email,
            'password': password }

        actual = self.test_project.get_user_request(
            'POST', 'application/json', url_prefix, token, user, first, last,
            email, password)

        self.assertEqual(expected, actual.url)
        self.assertDictEqual(expectedData, actual.json)

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
            '{}/{}/{}/{}/?key={}'.format(url_prefix, self.test_meta.version,
             self.test_meta.endpoint, self.resource.name, key),
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

    def test_build_cutout_to_black_url_no_time_range(self):
        res = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = None
        actual = self.test_volume.build_cutout_to_black_url(
            self.chanResource, self.url_prefix,
            res, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst)

        expected = '/'.join([
            self.url_prefix,
            self.test_volume.version,
            "cutout/to_black",
            self.chanResource.coll_name,
            self.chanResource.exp_name,
            self.chanResource.name,
            str(res),
            x_range,
            y_range,
            z_range,
        ]) + '/'

        self.assertEqual(expected, actual)

    def test_build_cutout_url_no_time_range_with_ids(self):
        res = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = None
        id_list = [2, 7]
        id_list_str = '2,7'
        actual = self.test_volume.build_cutout_url(
            self.chanResource, self.url_prefix,
            res, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst, id_list)

        self.assertEqual(
            self.url_prefix + '/' + self.test_volume.version + '/' + self.test_volume.endpoint +
            '/' + self.chanResource.coll_name + '/' + self.chanResource.exp_name +
            '/' + self.chanResource.name + '/' + str(res) + '/' + x_range + '/' +
            y_range + '/' + z_range + '/?filter=' + id_list_str,
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

    def test_build_cutout_to_black_url_with_time_range(self):
        res = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = [10, 25]
        time_range = '10:25'
        actual = self.test_volume.build_cutout_to_black_url(
            self.chanResource, self.url_prefix,
            res, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst)

        expected = '/'.join([
            self.url_prefix,
            self.test_volume.version,
            "cutout/to_black",
            self.chanResource.coll_name,
            self.chanResource.exp_name,
            self.chanResource.name,
            str(res),
            x_range,
            y_range,
            z_range,
            time_range,
        ]) + '/'

        self.assertEqual(expected, actual)

    def test_build_cutout_url_with_time_range_and_ids(self):
        res = 0
        x_rng_lst = [20, 40]
        x_range = '20:40'
        y_rng_lst = [50, 70]
        y_range = '50:70'
        z_rng_lst = [30, 50]
        z_range = '30:50'
        t_rng_lst = [10, 25]
        time_range = '10:25'
        id_list = [2, 7]
        id_list_str = '2,7'
        actual = self.test_volume.build_cutout_url(
            self.chanResource, self.url_prefix,
            res, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst, id_list)

        self.assertEqual(
            self.url_prefix + '/' + self.test_volume.version + '/' + self.test_volume.endpoint +
            '/' + self.chanResource.coll_name + '/' + self.chanResource.exp_name +
            '/' + self.chanResource.name + '/' + str(res) + '/' + x_range + '/' +
            y_range + '/' + z_range + '/' + time_range + '/?filter=' + id_list_str,
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

    def test_get_cutout_request_with_ids(self):
        """Test request generated for a filtered cutout."""
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
        id_list = [10, 5]
        id_list_str = '10,5'
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)

        actual = self.test_volume.get_cutout_request(
            self.chanResource, 'GET', 'application/blosc-python', url_prefix, token,
            resolution, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst, id_list=id_list)
        self.assertEqual(
            '{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/?filter={}'.format(url_prefix, self.test_volume.version,
            self.test_volume.endpoint, self.chanResource.coll_name,
            self.chanResource.exp_name, self.chanResource.name, resolution,
            x_range, y_range, z_range, time_range, id_list_str),
            actual.url)
        self.assertEqual('Token {}'.format(token), actual.headers['Authorization'])
        self.assertEqual('application/blosc-python', actual.headers['Content-Type'])

    def test_get_cutout_request_with_ids_and_access_mode(self):
        """Test request generated for a filtered cutout."""
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
        id_list = [10, 5]
        id_list_str = '10,5'
        data = numpy.random.randint(0, 3000, (15, 20, 20, 20), numpy.uint16)

        actual = self.test_volume.get_cutout_request(
            self.chanResource, 'GET', 'application/blosc-python', url_prefix, token,
            resolution, x_rng_lst, y_rng_lst, z_rng_lst, t_rng_lst, id_list=id_list, access_mode=CacheMode.no_cache)
        self.assertEqual(
            '{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/{}/?filter={}&access-mode=no-cache'.format(url_prefix, self.test_volume.version,
            self.test_volume.endpoint, self.chanResource.coll_name,
            self.chanResource.exp_name, self.chanResource.name, resolution,
            x_range, y_range, z_range, time_range, id_list_str),
            actual.url)
        self.assertEqual('Token {}'.format(token), actual.headers['Authorization'])
        self.assertEqual('application/blosc-python', actual.headers['Content-Type'])

    def test_get_reserve_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        num_ids = 20

        actual = self.test_volume.get_reserve_request(
            self.annoResource, 'GET', 'application/json', url_prefix, token,
            num_ids)

        expected = '{}/{}/reserve/{}/{}/{}/{}'.format(
            url_prefix, self.test_volume.version, self.annoResource.coll_name,
            self.annoResource.exp_name, self.annoResource.name, num_ids)

        self.assertEqual(expected, actual.url)

    def test_get_bounding_box_request_loose(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        resolution = 0
        bb_type = 'loose'
        id = 55555

        actual = self.test_volume.get_bounding_box_request(
            self.annoResource, 'GET', 'application/json', url_prefix, token,
            resolution, id, bb_type)

        expected = '{}/{}/boundingbox/{}/{}/{}/{}/{}/?type={}'.format(
            url_prefix, self.test_volume.version, self.annoResource.coll_name,
            self.annoResource.exp_name, self.annoResource.name, resolution,
            id, bb_type)

        self.assertEqual(expected, actual.url)

    def test_build_ids_url(self):
        url_prefix = 'https://api.theboss.io'
        resolution = 0
        x_range = [0, 100]
        x_range_str = '0:100'
        y_range = [10, 50]
        y_range_str = '10:50'
        z_range = [20, 42]
        z_range_str = '20:42'
        t_range = [0, 1]
        t_range_str = '0:1'

        actual = self.test_volume.build_ids_url(
            self.annoResource, url_prefix, resolution,
            x_range, y_range, z_range, t_range)

        expected = '{}/{}/ids/{}/{}/{}/{}/{}/{}/{}/{}/'.format(
            url_prefix, self.test_volume.version, self.annoResource.coll_name,
            self.annoResource.exp_name, self.annoResource.name,
            resolution, x_range_str, y_range_str, z_range_str, t_range_str)

        self.assertEqual(expected, actual)

    def test_get_ids_request(self):
        url_prefix = 'https://api.theboss.io'
        token = 'foobar'
        resolution = 0
        x_range = [0, 100]
        x_range_str = '0:100'
        y_range = [10, 50]
        y_range_str = '10:50'
        z_range = [20, 42]
        z_range_str = '20:42'
        t_range = [0, 1]
        t_range_str = '0:1'

        actual = self.test_volume.get_ids_request(
            self.annoResource, 'GET', 'application/json', url_prefix, token,
            resolution, x_range, y_range, z_range, t_range)

        expected = '{}/{}/ids/{}/{}/{}/{}/{}/{}/{}/{}/'.format(
            url_prefix, self.test_volume.version, self.annoResource.coll_name,
            self.annoResource.exp_name, self.annoResource.name,
            resolution, x_range_str, y_range_str, z_range_str, t_range_str)

        self.assertEqual(expected, actual.url)

    def test_convert_int_list_to_comma_sep_str_1_ele(self):
        """Test with a list with one element."""
        expected = '2'
        actual = self.test_volume.convert_int_list_to_comma_sep_str([2])
        self.assertEqual(expected, actual)

    def test_convert_int_list_to_comma_sep_str_multi_ele(self):
        """Test with a list with multiple elements."""
        expected = '2,6,9'
        actual = self.test_volume.convert_int_list_to_comma_sep_str([2, 6, 9])
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
