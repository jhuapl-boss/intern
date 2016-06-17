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

from .base import Base
from ndio.ndresource.boss.resource import *
from requests import HTTPError
import copy

class ProjectService_0_5(Base):
    """The Boss API v0.5 project service.
    """

    def __init__(self):
        super().__init__()

    @property
    def endpoint(self):
        return 'resource'

    def group_get(self, name, user_name, url_prefix, auth, session, send_opts):
        """Get information on the given group or whether or not a user is a member of the group.

        Args:
            name (string): Name of group to query.
            user_name (string): Supply None if not interested in determining if user is a member of the given group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (mixed): Dictionary if getting group information or bool if a user name is supplied.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'GET', 'application/x-www-form-urlencoded', url_prefix, auth, name, user_name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        msg = ('Get failed for group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))

        raise HTTPError(msg, request = req, response = resp)

    def group_create(self, name, url_prefix, auth, session, send_opts):
        """Create a new group.

        Args:
            name (string): Name of the group to create.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'POST', 'application/x-www-form-urlencoded', url_prefix, auth, name, None)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = ('Create failed for group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def group_delete(self, name, user_name, url_prefix, auth, session, send_opts):
        """Delete given group or delete user from given group.

        If user_name is provided, the user will be removed from the group.
        Otherwise, the group, itself, is deleted.

        Args:
            name (string): Name of group.
            user_name (optional[string]): Defaults to None.  User to remove from group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'DELETE', 'application/x-www-form-urlencoded', url_prefix, auth, name, user_name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Delete failed for group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def group_add_user(self, grp_name, user, url_prefix, auth, session, send_opts):
        """Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'POST', 'application/x-www-form-urlencoded', url_prefix, auth, grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = ('Failed adding user {} to group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def permissions_get(
        self, grp_name, resource, url_prefix, auth, session, send_opts):
        """
        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of permissions.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_permission_request(
            'GET', 'application/x-www-form-urlencoded', url_prefix, auth, 
            grp_name, resource)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            json = resp.json()
            return json.get('permissions', [])

        err = ('Failed getting permissions for group {}, got HTTP response: ({}) - {}'.format(
            grp_name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)


    def permissions_add(
        self, grp_name, resource, permissions, url_prefix, auth, session, 
        send_opts):
        """
        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            permissions (list): List of permissions to add to the given resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().
        """
        json = { 'permissions': permissions }
        req = self.get_permission_request(
            'POST', 'application/x-www-form-urlencoded', url_prefix, auth, 
            grp_name, resource, json)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = ('Failed adding permissions to group {}, got HTTP response: ({}) - {}'.format(
            grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def permissions_delete(
        self, grp_name, resource, permissions, url_prefix, auth, session, 
        send_opts):
        """
        Args:
            grp_name (string): Name of group.
            resource (ndio.ndresource.boss.Resource): Identifies which data model object to operate on.
            permissions (list): List of permissions to remove from the given resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        json = { 'permissions': permissions }
        req = self.get_permission_request(
            'DELETE', 'application/x-www-form-urlencoded', url_prefix, auth, 
            grp_name, resource, json)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return

        msg = ('Failed deleting permissions to group {}, got HTTP response: ({}) - {}'.format(
            grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_get_roles(self, user, url_prefix, auth, session, send_opts):
        """Get roles associated with the given user.

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of roles that user has.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_role_request(
            'GET', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        msg = (
            'Failed getting roles for user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_add_role(self, user, role, url_prefix, auth, session, send_opts):
        """Add role to given user.

        Args:
            user (string): User name.
            role (string): Role to assign.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_role_request(
            'POST', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user, role)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return

        msg = (
            'Failed adding role: {} to user: {}, got HTTP response: ({}) - {}'
            .format(role, user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_delete_role(self, user, role, url_prefix, auth, session, send_opts):
        """Remove role from given user.

        Args:
            user (string): User name.
            role (string): Role to remove.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_role_request(
            'DELETE', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user, role)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = (
            'Failed deleting role: {} from user: {}, got HTTP response: ({}) - {}'
            .format(role, user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_get(self, user, url_prefix, auth, session, send_opts):
        """Get user's data (first and last name, email, etc).

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'GET', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        msg = (
            'Failed getting user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_get_groups(self, user, url_prefix, auth, session, send_opts):
        """Get user's group memberships.

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'GET', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user)
        req.url = req.url + '/groups/'

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            groups = []
            for dict in resp.json():
                if 'name' in dict:
                    groups.append(dict['name'])
            return groups

        msg = (
            'Failed getting user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_add(
        self, user, first_name, last_name, email, password, 
        url_prefix, auth, session, send_opts):
        """Add a new user.

        Args:
            user (string): User name.
            first_name (string): User's first name.
            last_name (string): User's last name.
            email: (string): User's email address.
            password: (string): User's password.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'POST', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user, first_name, last_name, email, password)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = (
            'Failed adding user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def user_delete(self, user, url_prefix, auth, session, send_opts):
        """Delete the given user.

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'DELETE', 'application/x-www-form-urlencoded', url_prefix, auth, 
            user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = (
            'Failed deleting user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def list(self, resource, url_prefix, auth, session, send_opts):
        """List all resources of the same type as the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): List resources of the same type as this..
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of resources.  Each resource is a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_request(
            resource, 'GET', 'application/x-www-form-urlencoded', url_prefix, auth,
            proj_list_req = True)
            # json content-type currently broken.
            #resource, 'GET', 'application/json', url_prefix, auth,
            #proj_list_req = True)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        err = ('List failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def create(self, resource, url_prefix, auth, session, send_opts):
        """Create the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): Create a data model object with attributes matching those of the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (ndio.ndresource.boss.Resource): Returns resource of type requested on success.  Returns None on failure.

        Raises:
            requests.HTTPError on failure.
        """
        json = self._get_resource_params(resource)
        req = self.get_request(
            resource, 'POST', 'application/x-www-form-urlencoded', url_prefix, auth,
            data = json)
            # json content-type currently broken.
            #resource, 'POST', 'application/json', url_prefix, auth,
            #json = json)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 201:
            return self._create_resource_from_dict(resource, resp.json())

        err = ('Create failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def get(self, resource, url_prefix, auth, session, send_opts):
        """Get attributes of the given resource.

        Args:
            resource (ndio.ndresource.boss.Resource): Create a data model object with attributes matching those of the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (ndio.resource.boss.Resource): Returns resource of type requested on success.  Returns None on failure.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_request(
            resource, 'GET', 'application/json', url_prefix, auth)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return self._create_resource_from_dict(resource, resp.json())

        err = ('Get failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def update(self, resource_name, resource, url_prefix, auth, session, send_opts):
        """Updates an entity in the data model using the given resource.

        Args:
            resource_name (string): Current name of the resource (in case the resource is getting its name changed).
            resource (ndio.resource.boss.Resource): New attributes for the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (ndio.resource.boss.Resource): Returns updated resource of given type on success.  Returns None on failure.

        Raises:
            requests.HTTPError on failure.
        """

        # Create a copy of the resource and change its name to resource_name
        # in case the update includes changing the name of a resource.
        old_resource = copy.deepcopy(resource)
        old_resource.name = resource_name

        json = self._get_resource_params(resource)

        req = self.get_request(
            old_resource, 'PUT', 'application/x-www-form-urlencoded',
            url_prefix, auth, data = json)
            # json content-type currently broken.
            #old_resource, 'PUT', 'application/json', url_prefix, auth,
            #json = json)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            return self._create_resource_from_dict(resource, resp.json())

        err = ('Update failed on {}, got HTTP response: ({}) - {}'.format(
            old_resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)


    def delete(self, resource, url_prefix, auth, session, send_opts):
        """Deletes the entity described by the given resource.

        Args:
            resource (ndio.resource.boss.Resource)
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_request(
            resource, 'DELETE', 'application/json', url_prefix, auth)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        err = ('Delete failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def _get_resource_params(self, resource):
        """Get dictionary containing all parameters for the given resource.

        Args:
            resource (ndio.ndresource.boss.resource.Resource): A sub-class
                whose parameters will be extracted into a dictionary.

        Returns:
            (dictionary): A dictionary containing the resource's parameters as
            required by the Boss API.

        Raises:
            TypeError if resource is not a supported class.
        """
        if isinstance(resource, CollectionResource):
            return self._get_collection_params(resource)

        if isinstance(resource, ExperimentResource):
            return self._get_experiment_params(resource)

        if isinstance(resource, CoordinateFrameResource):
            return self._get_coordinate_params(resource)

        if isinstance(resource, LayerResource):
            return self._get_layer_params(resource)

        if isinstance(resource, ChannelResource):
            return self._get_channel_params(resource)

        raise TypeError('resource is not supported type.')

    def _get_collection_params(self, coll):
        return { 'name': coll.name, 'description': coll.description }

    def _get_experiment_params(self, exp):
        return {
            'name': exp.name,
            'description': exp.description ,
            'coord_frame': exp.coord_frame,
            'num_hierarchy_levels': exp.num_hierarchy_levels,
            'hierarchy_method': exp.hierarchy_method,
            'max_time_sample': exp.max_time_sample
        }

    def _get_coordinate_params(self, coord):
        return {
            'name': coord.name,
            'description': coord.description ,
            'x_start': coord.x_start,
            'x_stop': coord.x_stop,
            'y_start': coord.y_start,
            'y_stop': coord.y_stop,
            'z_start': coord.z_start,
            'z_stop': coord.z_stop,
            'x_voxel_size': coord.x_voxel_size,
            'y_voxel_size': coord.y_voxel_size,
            'z_voxel_size': coord.z_voxel_size,
            'voxel_unit': coord.voxel_unit,
            'time_step': coord.time_step,
            'time_step_unit': coord.time_step_unit
        }

    def _get_channel_params(self, chan):
        return {
            'name': chan.name,
            'description': chan.description ,
            'default_time_step': chan.default_time_step,
            'datatype': chan.datatype,
            'base_resolution': chan.base_resolution,
            'is_channel': True
        }

    def _get_layer_params(self, lyr):
        return {
            'name': lyr.name,
            'description': lyr.description ,
            'default_time_step': lyr.default_time_step,
            'datatype': lyr.datatype,
            'base_resolution': lyr.base_resolution,
            'is_channel': False,
            'channels': lyr.channels
        }

    def _create_resource_from_dict(self, resource, dict):
        """
        Args:
            resource (ndio.resource.boss.Resource): Used to determine type of resource to create.
            dict (dictionary): JSON data returned by the Boss API.

        Returns:
            (ndio.resource.boss.Resource): Instance populated with values from dict.

        Raises:
            KeyError if dict missing required key.
            TypeError if resource is not a supported class.
        """
        if isinstance(resource, CollectionResource):
            return self._get_collection(dict)

        if isinstance(resource, ExperimentResource):
            return self._get_experiment(dict, resource.coll_name)

        if isinstance(resource, CoordinateFrameResource):
            return self._get_coordinate(dict)

        if isinstance(resource, LayerResource):
            return self._get_layer(dict, resource.coll_name, resource.exp_name)

        if isinstance(resource, ChannelResource):
            return self._get_channel(dict, resource.coll_name, resource.exp_name)

        raise TypeError('resource is not supported type.')

    def _get_collection(self, dict):
        name = dict['name']
        description = dict['description']
        id = dict['id']
        creator = dict['creator']
        return CollectionResource(
            name, self.version, description, id, creator, raw=dict)

    def _get_experiment(self, dict, coll_name):
        exp_keys = [
            'id', 'name', 'description', 'creator', 'coord_frame', 
            'num_hierarchy_levels', 'hierarchy_method', 'max_time_sample'             
        ]

        filtered = { k:v for (k, v) in dict.items() if k in exp_keys }
        return ExperimentResource(
            version=self.version, collection_name=coll_name, raw=dict, **filtered)

    def _get_coordinate(self, dict):
        coord_keys = [
            'id', 'name', 'description', 'x_start', 'x_stop', 
            'y_start', 'y_stop', 'z_start', 'z_stop', 
            'x_voxel_size', 'y_voxel_size', 'z_voxel_size',
            'voxel_unit', 'time_step', 'time_step_unit'
        ]

        filtered = { k:v for (k, v) in dict.items() if k in coord_keys }
        return CoordinateFrameResource(version=self.version, raw=dict, **filtered)

    def _get_channel(self, dict, coll_name, exp_name):
        chan_keys = [
            'id', 'name', 'description', 'creator', 'default_time_step', 
            'datatype', 'base_resolution'
        ]

        filtered = { k:v for (k, v) in dict.items() if k in chan_keys }
        collection = coll_name
        return ChannelResource(
            version=self.version, collection_name=collection,
            experiment_name=exp_name, raw=dict, **filtered)

    def _get_layer(self, dict, coll_name, exp_name):
        layer_keys = [
            'id', 'name', 'description', 'creator', 'default_time_step', 
            'datatype', 'base_resolution'
        ]

        filtered = { k:v for (k, v) in dict.items() if k in layer_keys }
        collection = coll_name
        channels = dict['linked_channel_layers']
        return LayerResource(
            version=self.version, collection_name=collection,
            experiment_name=exp_name, channels=channels, raw=dict, **filtered)
